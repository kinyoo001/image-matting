import base64
import sys
import time
from io import BytesIO
from pathlib import Path

import numpy as np
import onnxruntime as ort
import requests
from PIL import Image
from conf.config import config

BASE_DIR = Path(__file__).resolve().parent.parent

try:
    from utilities.log import logger
    from utilities.utils import refine_foreground
except ImportError:
    sys.path.append(str(BASE_DIR))
    from utilities.log import logger
    from utilities.utils import refine_foreground


# 下载模型
# AutoModelForImageSegmentation.from_pretrained("briaai/RMBG-1.4", trust_remote_code=True).save_pretrained("RMBG-1_4")


# 各模型的前处理/输出差异注册表
# rmbg-1.4: 输出即单通道 mask；
# rmbg-2.0(BiRefNet 架构): 官方 onnx 只有一个输出 alphas，已是 [0,1] 概率图，无需 sigmoid。
#   若换用自导出的多路 side-output 版本，才需要 take_last_output + apply_sigmoid。
MODELS = {
    "rmbg-1.4": {
        "dir": "briaai/RMBG-1.4",
        "mean": [0.5, 0.5, 0.5],
        "std": [1.0, 1.0, 1.0],
        "take_last_output": False,
        "apply_sigmoid": False,
    },
    "rmbg-2.0": {
        "dir": "briaai/RMBG-2.0",
        "mean": [0.485, 0.456, 0.406],
        "std": [0.229, 0.224, 0.225],
        "take_last_output": True,
        "apply_sigmoid": False,
    },
}


class ImageSegmentation:
    def __init__(
        self,
        model_name="rmbg-1.4",
        model_path=None,
        model_input_size=[1024, 1024],
    ):
        if model_name not in MODELS:
            raise ValueError(f"Unknown model: {model_name}, available: {list(MODELS)}")
        if model_input_size is not None and (
            not isinstance(model_input_size, list) or len(model_input_size) != 2
        ):
            raise ValueError("model_input_size must be a list with two elements")
        if model_input_size is not None and any(
            not isinstance(size, int) or size <= 0 for size in model_input_size
        ):
            raise ValueError("model_input_size elements must be positive integers")

        spec = MODELS[model_name]
        self.model_name = model_name
        self.mean = np.array(spec["mean"], dtype=np.float32)
        self.std = np.array(spec["std"], dtype=np.float32)
        self.take_last_output = spec["take_last_output"]
        self.apply_sigmoid = spec["apply_sigmoid"]
        if model_path is None:
            model_path = str(BASE_DIR / "hub_model" / spec["dir"] / "model.onnx")
        if not isinstance(model_path, str) or not model_path.endswith(".onnx"):
            raise ValueError("model_path must be a valid ONNX model file path")
        if not Path(model_path).exists():
            raise RuntimeError(
                f"Model file not found: {model_path} "
                f"(model={model_name}). Please download it first, "
                f"see hub_model/download.py"
            )

        # Initialize model path and input size
        self.model_path = model_path
        self.model_input_size = model_input_size
        try:
            logger.info("Loading model...")
            star_time = time.time()
            providers = self.get_available_providers()
            if 'DmlExecutionProvider' in providers:
                so = ort.SessionOptions()
                so.enable_mem_pattern = False
                so.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
                self.ort_session = ort.InferenceSession(model_path, providers=providers, sess_options=so)
            else:
                self.ort_session = ort.InferenceSession(model_path, providers=providers)
            logger.info(f"Model loaded in {time.time() - star_time:.2f} seconds")
        except Exception as e:
            raise RuntimeError(f"Failed to load ONNX model: {e}")

    def get_available_providers(self):
        """获取可用的执行设备"""
        available_providers = ort.get_available_providers()
        if "CUDAExecutionProvider" in available_providers:
            return ["CUDAExecutionProvider", "CPUExecutionProvider"]
        if "DmlExecutionProvider" in available_providers:
            return ["DmlExecutionProvider", "CPUExecutionProvider"]
        return ["CPUExecutionProvider"]

    def preprocess_image(self, im: np.ndarray) -> np.ndarray:
        # If the image is grayscale, add a dimension to make it a color image
        if len(im.shape) < 3:
            im = im[:, :, np.newaxis]
        # Resize the image to match the model input size
        try:
            im_resized = np.array(
                Image.fromarray(im).resize(self.model_input_size, Image.BILINEAR)
            )
        except Exception as e:
            raise RuntimeError(f"Error resizing image: {e}")
        # Normalize image pixel values to the [0, 1] range
        image = im_resized.astype(np.float32) / 255.0
        # Further normalize image data
        image = (image - self.mean) / self.std
        # Convert the image to the required shape
        image = image.transpose(
            2, 0, 1
        )  # Change dimension order (channels, height, width)
        return np.expand_dims(image, axis=0)  # Add batch dimension

    def postprocess_image(self, result: np.ndarray, im_size: list) -> np.ndarray:
        # Resize the result image to match the original image size
        result = np.squeeze(result).astype(np.float32)
        if self.apply_sigmoid:
            # BiRefNet 系模型输出 logits，先转概率(已在 [0,1] 内，不做 min-max 拉伸)
            result = 1.0 / (1.0 + np.exp(-result))
            normalize = False
        else:
            normalize = True
        try:
            result = np.array(Image.fromarray(result).resize(im_size, Image.BILINEAR))
        except Exception as e:
            raise RuntimeError(f"Error resizing result image: {e}")
        if normalize:
            # Normalize the result image data
            ma = result.max()
            mi = result.min()
            result = (result - mi) / (ma - mi + 1e-8)
        else:
            result = np.clip(result, 0, 1)
        # Convert to uint8 image
        im_array = (result * 255).astype(np.uint8)
        return im_array

    def read_image(self, img: str) -> Image.Image:
        if img.startswith("http"):
            response = requests.get(img)
            return Image.open(BytesIO(response.content))
        elif ";base64," in img:
            base64_string = img.split(";base64,")[-1]
            image_data = base64.b64decode(base64_string)
            return Image.open(BytesIO(image_data))
        elif Path(img).exists():
            return Image.open(fp=img, mode="r")
        else:
            raise FileNotFoundError(f"File {img} not found.")

    def segment_image(self, img_obj: str) -> Image.Image:
        # 读取图像
        orig_image = self.read_image(img_obj)
        # 去除alpha通道
        input_image = orig_image.convert("RGB")
        image_array = np.array(input_image)
        image_size = (input_image.size[0], input_image.size[1])

        image_preprocessed = self.preprocess_image(image_array)

        ort_inputs = {self.ort_session.get_inputs()[0].name: image_preprocessed}
        try:
            ort_outs = self.ort_session.run(None, ort_inputs)
        except Exception as e:
            raise RuntimeError(f"ONNX inference failed: {e}")
        # BiRefNet 系模型输出多路 side-output，取最后一路最精细的结果
        result = ort_outs[-1] if self.take_last_output else ort_outs[0]
        # 后处理
        result_image = self.postprocess_image(result[0][0], image_size)
        is_edge_optimization = config.get("edge_optimization.is_edge_optimization")
        r = config.get("edge_optimization.r")
        pil_im = Image.fromarray(result_image)
        if is_edge_optimization:
            try:
                no_bg_image = refine_foreground(orig_image, pil_im, r=r)
                return no_bg_image
            except Exception as e:
                logger.error(f"Error processing images: {e}")
        else:
            no_bg_image = Image.new("RGBA", pil_im.size, (0, 0, 0, 0))
            no_bg_image.paste(orig_image, mask=pil_im)
            return no_bg_image


if __name__ == "__main__":
    # 示例使用：
    segmentation = ImageSegmentation()
    base_path = BASE_DIR / "hub_model" / "test_images"
    test_imgs = [
        "test.jpg",
        "car.jpg",
        "input.jpg",
    ]
    for img_name in test_imgs:
        img_path = str(base_path / img_name)
        file_name = img_name.split(".")[0]
        no_bg_image = segmentation.segment_image(img_path)
        no_bg_image.save(str(base_path / f"no_bg_{file_name}.png"))
        logger.info(f"Image {img_name} has been processed successfully.")
