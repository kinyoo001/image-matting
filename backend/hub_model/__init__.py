from .rmbg_model import ImageSegmentation, MODELS
from .migan import MiganInpainting

migan = MiganInpainting()


class _SegmentationProxy:
    """抠图模型的懒加载代理：按配置中的模型名加载，切换配置后下次调用自动重载，无需重启。"""

    def __init__(self):
        self._impl = None
        self._loaded_name = None

    def _get_impl(self):
        from conf.config import config

        try:
            from utilities.log import logger
        except ImportError:
            import logging

            logger = logging.getLogger("image-matting")

        name = config.get("matting_model.name", "rmbg-1.4")
        if name not in MODELS:
            logger.warning(f"Unknown matting model '{name}', fallback to rmbg-1.4")
            name = "rmbg-1.4"
        if self._impl is None or name != self._loaded_name:
            if self._impl is not None:
                logger.info(f"Switching matting model: {self._loaded_name} -> {name}")
                try:
                    del self._impl
                except Exception:
                    pass
                import gc

                gc.collect()
            self._impl = ImageSegmentation(model_name=name)
            self._loaded_name = name
        return self._impl

    def __getattr__(self, item):
        return getattr(self._get_impl(), item)


segmentation = _SegmentationProxy()

__all__ = ["ImageSegmentation", "MODELS", "segmentation", "MiganInpainting", "migan"]
