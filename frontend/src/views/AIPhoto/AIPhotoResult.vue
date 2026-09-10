<template>
    <div class="relative overflow-x-auto w-full h-full flex flex-col items-center justify-center">
        <div class="flex items-center justify-center h-[calc(100vh-260px)] min-h-[200px] max-h-[450px] w-auto">
            <img :src="imageSrc" :class="{ 'img-transparent-bg': selectedColor === 'transparent' }"
                class="relative z-10 border border-indigo-600 object-contain" :style="containerStyle"
                style="max-width: 100%;max-height: 100%; width: auto; height: auto;" />
        </div>
        <div class="flex space-x-2 mb-4 mt-4 ">
            <button @click="selectColor('transparent')"
                :class="{ 'border-2 border-black': selectedColor === 'transparent' }"
                class="bg-transparent w-10 h-10 border img-transparent-bg">
                <div class="w-full h-full"></div>
            </button>
            <button @click="selectColor('#FFFFFF')" :class="{ 'border-2 border-black': selectedColor === '#FFFFFF' }"
                class="bg-white w-10 h-10 border"></button>
            <button @click="selectColor('#808080')" :class="{ 'border-2 border-black': selectedColor === '#808080' }"
                class="bg-gray-500 w-10 h-10 border"></button>
            <button @click="selectColor('#0000FF')" :class="{ 'border-2 border-black': selectedColor === '#0000FF' }"
                class="bg-blue-500 w-10 h-10 border"></button>
            <button @click="selectColor('#FF0000')" :class="{ 'border-2 border-black': selectedColor === '#FF0000' }"
                class="bg-red-500 w-10 h-10 border"></button>

            <button @click="selectColor('#008000')" :class="{ 'border-2 border-black': selectedColor === '#008000' }"
                class="bg-green-500 w-10 h-10 border"></button>

            <div class="relative w-10 h-10 border stacked-linear">
                <input type="color" v-model="backgroundColor" @change="handleColorChange"
                    class="absolute top-0 left-0 w-full h-full opacity-0 cursor-pointer" />
                <!-- <div class="w-full h-full bg-gray-500"></div> -->
            </div>
            <!-- <input type="color" v-model="backgroundColor" @change="handleColorChange"
                class="w-12 h-12   border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500" /> -->
        </div>
        <div class="flex justify-center space-x-4 mt-4">
            <button @click="goBack()" class="bg-green-500 text-white px-4 py-2 rounded-full">
                {{ t('common.btn_back') }}
            </button>
            <button @click="downloadImage()" class="bg-green-500 text-white px-4 py-2 rounded-full">
                {{ t('common.btn_download') }}
            </button>
            <button @click="openPrintDialog()" class="bg-green-500 text-white px-4 py-2 rounded-full">
                {{ t('print.print_btn') }}
            </button>
            <button @click="showPopup = true" class="bg-green-500 text-white px-4 py-2 rounded-full">
                {{ t('common.btn_edit') }}
            </button>
        </div>
        <!-- 调用弹窗组件，并传递 showModal 属性和标题 -->
        <ModalPopup v-model="showPopup" :title="t('common.btn_edit')" :showCancelButton="true" :showConfirmButton="false">
            <!-- 在弹窗插槽中放入图片编辑器内容 -->
            <ImageEditor :initialBase64="imageSrc" :originBase64="originImgUrl" @exportImage="handleExportImage" />
        </ModalPopup>
        <!-- 打印对话框 -->
        <ModalPopup v-model="showPrintPopup" :title="t('print.title')" :showCancelButton="true" :showConfirmButton="false">
            <div class="w-[320px] space-y-4 text-sm">
                <div v-if="!printSupported" class="text-red-500 text-center py-2">{{ t('print.not_supported') }}</div>
                <template v-else>
                    <div class="flex items-center justify-between gap-3">
                        <span class="text-zinc-600 dark:text-zinc-300 whitespace-nowrap">{{ t('print.printer') }}</span>
                        <div class="flex items-center gap-2 flex-1">
                            <select v-model="printForm.printer" @change="onPrinterChange"
                                class="select select-sm select-bordered flex-1 rounded-lg bg-neutral-50 dark:bg-zinc-950 h-9 min-h-0">
                                <option value="">{{ t('print.no_printer') }}</option>
                                <option v-for="p in printers" :key="p.name" :value="p.name">
                                    {{ p.name }}{{ p.state !== 'idle' ? ` (${p.state})` : '' }}
                                </option>
                            </select>
                            <button @click="loadPrinters()" class="text-blue-500 hover:underline text-xs whitespace-nowrap">
                                {{ t('print.refresh') }}
                            </button>
                        </div>
                    </div>
                    <div v-if="printers.length === 0" class="text-amber-600 text-xs text-center">{{ t('print.no_printer_tip') }}</div>
                    <div class="flex items-center justify-between gap-3">
                        <span class="text-zinc-600 dark:text-zinc-300 whitespace-nowrap">{{ t('print.copies') }}</span>
                        <input type="number" min="1" max="99" v-model.number="printForm.copies"
                            class="input input-sm input-bordered w-32 rounded-lg bg-neutral-50 dark:bg-zinc-950 h-9 min-h-0" />
                    </div>
                    <div class="flex items-center justify-between gap-3">
                        <span class="text-zinc-600 dark:text-zinc-300 whitespace-nowrap">{{ t('print.media') }}</span>
                        <select v-model="printForm.media"
                            class="select select-sm select-bordered w-48 rounded-lg bg-neutral-50 dark:bg-zinc-950 h-9 min-h-0">
                            <option v-for="m in mediaSizes" :key="m" :value="m">{{ m }}</option>
                        </select>
                    </div>
                    <div class="flex items-center justify-between gap-3">
                        <span class="text-zinc-600 dark:text-zinc-300 whitespace-nowrap">{{ t('print.orientation') }}</span>
                        <select v-model="printForm.orientation"
                            class="select select-sm select-bordered w-48 rounded-lg bg-neutral-50 dark:bg-zinc-950 h-9 min-h-0">
                            <option value="portrait">{{ t('print.portrait') }}</option>
                            <option value="landscape">{{ t('print.landscape') }}</option>
                        </select>
                    </div>
                    <label class="flex items-center justify-between gap-3 cursor-pointer">
                        <span class="text-zinc-600 dark:text-zinc-300">{{ t('print.fit_to_page') }}</span>
                        <input type="checkbox" v-model="printForm.fit_to_page" class="toggle toggle-primary toggle-sm" />
                    </label>
                    <button @click="doPrint()" :disabled="printing || printers.length === 0"
                        class="w-full bg-green-500 hover:bg-green-600 disabled:bg-gray-300 text-white px-4 py-2 rounded-full">
                        {{ printing ? t('print.printing') : t('print.print_btn') }}
                    </button>
                </template>
            </div>
        </ModalPopup>
    </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useRoute } from 'vue-router';
import { useI18n } from 'vue-i18n'
import baseAPI from '@/api/base'
import message from '@/utils/message.js'

import ImageEditor from '@/views/components/ImageEditor.vue';
import ModalPopup from '@/views/components/ModalPopup.vue';
import { printAPI } from '@/api/print';
import { settingAPI } from '@/api/user';

const showPopup = ref(false)
const showPrintPopup = ref(false)
const printing = ref(false)
const printSupported = ref(true)
const printers = ref([])
const mediaSizes = ref(['A4'])
const printForm = ref({
    printer: '',
    copies: 1,
    media: 'A4',
    orientation: 'portrait',
    fit_to_page: true,
})


const { t } = useI18n()
const route = useRoute();
const imageSrc = ref(route.query.imgUrl);
const originImgUrl = ref(route.query.originImgUrl);
const backgroundColor = ref('transparent');
const selectedColor = ref('transparent');

const containerStyle = computed(() => ({
    backgroundColor: backgroundColor.value,
}));

// 导出编辑后的图片
const handleExportImage = (base64_data) => {
   showPopup.value = false;
   imageSrc.value = base64_data;
}

// const isTransparent = computed(() => backgroundColor.value === 'transparent');

const handleColorChange = (e) => {
    selectColor(e.target.value);
};

const selectColor = (color) => {
    backgroundColor.value = color;
    selectedColor.value = color;
};

// 返回
const goBack = () => {
    window.history.back();
};

// 下载图像
async function downloadImage() {
    console.log(selectedColor.value, "selectedColor")
    const response = await baseAPI('save_png_add_bg_dialog', { "base64_data": imageSrc.value, "hex_color": selectedColor.value })
    if (response.code === 200) {
        message.info(t('common.download_success'));
    } else {
        message.error(t('common.download_error'));
    }
}

// 打开打印对话框
async function openPrintDialog() {
    showPrintPopup.value = true;
    await loadPrinters();
}

// 加载打印机列表及默认设置
async function loadPrinters() {
    try {
        const res = await printAPI('get_printers', {});
        if (res.code === 200) {
            printSupported.value = res.data.supported;
            printers.value = res.data.printers || [];
            const setting = await settingAPI('get', '');
            const saved = (setting.code === 200 && setting.data.printer) || {};
            printForm.value.copies = saved.copies || 1;
            printForm.value.media = saved.media || 'A4';
            printForm.value.orientation = saved.orientation || 'portrait';
            printForm.value.fit_to_page = saved.fit_to_page !== false;
            printForm.value.printer = saved.printer_name || res.data.default_printer || (printers.value[0] ? printers.value[0].name : '');
            await onPrinterChange();
        }
    } catch (e) {
        console.error(e);
    }
}

// 切换打印机时刷新纸张列表
async function onPrinterChange() {
    if (!printForm.value.printer) return;
    try {
        const res = await printAPI('get_printer_options', { printer_name: printForm.value.printer });
        if (res.code === 200 && res.data.media_sizes && res.data.media_sizes.length > 0) {
            mediaSizes.value = res.data.media_sizes;
            if (!mediaSizes.value.includes(printForm.value.media)) {
                printForm.value.media = res.data.default_media || mediaSizes.value[0];
            }
        }
    } catch (e) {
        console.error(e);
    }
}

// 提交打印
async function doPrint() {
    if (printing.value || printers.value.length === 0) return;
    printing.value = true;
    try {
        const response = await printAPI('print_image', {
            base64_data: imageSrc.value,
            hex_color: selectedColor.value,
            printer: printForm.value.printer,
            copies: printForm.value.copies,
            media: printForm.value.media,
            orientation: printForm.value.orientation,
            fit_to_page: printForm.value.fit_to_page,
        });
        if (response.code === 200) {
            message.info((response.data && response.data.tip) || t('print.print_success'));
            showPrintPopup.value = false;
        } else {
            message.error(`${t('print.print_error')}: ${response.error_msg || ''}`);
        }
    } catch (e) {
        message.error(t('print.print_error'));
    } finally {
        printing.value = false;
    }
}



</script>

<style scoped>
img {
    width: 100%;
    height: 100%;
}

.img-transparent-bg {
    background-size: 20px 20px;
    background-position: 0 0, 10px 10px;
    background-image: linear-gradient(45deg, #eee 25%, transparent 0, transparent 75%, #eee 0, #eee), linear-gradient(45deg, #eee 25%, #fff 0, #fff 75%, #eee 0, #eee);
}

.stacked-linear {
    background: linear-gradient(217deg,
            rgba(255, 0, 0, 0.8),
            rgba(255, 0, 0, 0) 70.71%),
        linear-gradient(127deg, rgba(0, 255, 0, 0.8), rgba(0, 255, 0, 0) 70.71%),
        linear-gradient(336deg, rgba(0, 0, 255, 0.8), rgba(0, 0, 255, 0) 70.71%);
}
</style>
