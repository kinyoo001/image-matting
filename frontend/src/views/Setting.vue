<template>
  <div class="flex h-full w-full overflow-hidden select-none bg-white dark:bg-zinc-900 rounded-xl border border-neutral-200/60 dark:border-zinc-800/40">
    <!-- Left Navigation Sidebar -->
    <div class="w-[180px] flex-shrink-0 border-r border-neutral-200/60 dark:border-zinc-800/40 bg-neutral-50/50 dark:bg-zinc-900/50 p-3 flex flex-col gap-1">
      <button 
        v-for="tab in tabs" 
        :key="tab.id"
        @click="activeTab = tab.id"
        class="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-all duration-200"
        :class="activeTab === tab.id 
          ? 'bg-[#007aff] text-white font-medium shadow-sm shadow-[#007aff]/15' 
          : 'text-zinc-600 dark:text-zinc-400 hover:bg-neutral-200/50 dark:hover:bg-zinc-800/40'"
      >
        <i :class="tab.icon" class="w-4 flex justify-center"></i>
        <span>{{ tab.name }}</span>
      </button>
    </div>

    <!-- Right Content Panel -->
    <div class="flex-grow flex flex-col min-w-0 h-full overflow-hidden">
      <!-- Active Tab Header -->
      <div class="flex-shrink-0 px-6 py-4 border-b border-neutral-200/50 dark:border-zinc-800/40 bg-white dark:bg-zinc-900 flex justify-between items-center">
        <h3 class="text-base font-semibold text-zinc-800 dark:text-zinc-100">
          {{ activeTabName }}
        </h3>
      </div>

      <!-- Settings Content -->
      <div class="flex-grow overflow-y-auto p-6 space-y-6">
        <!-- Tab 1: General Preferences -->
        <div v-if="activeTab === 'general'" class="space-y-4">
          <!-- Row 1: Language -->
          <div class="flex items-center justify-between py-2 border-b border-neutral-100 dark:border-zinc-800/60 pb-4 gap-4">
            <div class="flex flex-col pr-4">
              <span class="text-sm font-medium text-zinc-800 dark:text-zinc-200">{{ t('setting.language') }}</span>
              <span class="text-xs text-zinc-400 dark:text-zinc-500 mt-0.5">Choose your preferred display language for the workspace</span>
            </div>
            <select id="language" v-model="settingInfo.language" class="select select-sm select-bordered w-48 rounded-lg text-sm bg-neutral-50 dark:bg-zinc-950 focus:border-blue-500 h-9 min-h-0">
              <option v-for="(key, val, index) in languageList" :key="index" :value="val">{{ key }}</option>
            </select>
          </div>

          <!-- Row 2: Export Format -->
          <div class="flex items-center justify-between py-2 border-b border-neutral-100 dark:border-zinc-800/60 pb-4 gap-4">
            <div class="flex flex-col pr-4">
              <span class="text-sm font-medium text-zinc-800 dark:text-zinc-200">{{ t('setting.export_format') }}</span>
              <span class="text-xs text-zinc-400 dark:text-zinc-500 mt-0.5">Select the default file extension when saving matting results</span>
            </div>
            <select id="export_format" v-model="settingInfo.export_format" class="select select-sm select-bordered w-48 rounded-lg text-sm bg-neutral-50 dark:bg-zinc-950 focus:border-blue-500 h-9 min-h-0">
              <option value="png">PNG</option>
              <option value="psd">PSD</option>
              <option value="jpg">JPG</option>
            </select>
          </div>

          <!-- Row 3: Matting Model -->
          <div class="flex items-center justify-between py-2 border-b border-neutral-100 dark:border-zinc-800/60 pb-4 gap-4">
            <div class="flex flex-col pr-4">
              <span class="text-sm font-medium text-zinc-800 dark:text-zinc-200">{{ t('setting.matting_model') }}</span>
              <span class="text-xs text-zinc-400 dark:text-zinc-500 mt-0.5">{{ t('setting.matting_model_desc') }}</span>
            </div>
            <select id="matting_model" v-model="settingInfo.matting_model.name" class="select select-sm select-bordered w-48 rounded-lg text-sm bg-neutral-50 dark:bg-zinc-950 focus:border-blue-500 h-9 min-h-0">
              <option value="rmbg-1.4">RMBG-1.4({{ t('setting.matting_model_fast') }})</option>
              <option value="rmbg-2.0">RMBG-2.0({{ t('setting.matting_model_quality') }})</option>
            </select>
          </div>

          <!-- Row 4: Default Printer -->
          <div class="flex items-center justify-between py-2 border-b border-neutral-100 dark:border-zinc-800/60 pb-4 gap-4">
            <div class="flex flex-col pr-4">
              <span class="text-sm font-medium text-zinc-800 dark:text-zinc-200">{{ t('print.printer') }}</span>
              <span class="text-xs text-zinc-400 dark:text-zinc-500 mt-0.5">{{ t('print.no_printer_tip') }}</span>
            </div>
            <select id="default_printer" v-model="settingInfo.printer.printer_name" class="select select-sm select-bordered w-48 rounded-lg text-sm bg-neutral-50 dark:bg-zinc-950 focus:border-blue-500 h-9 min-h-0">
              <option value="">{{ t('print.no_printer') }}</option>
              <option v-for="p in printers" :key="p.name" :value="p.name">{{ p.name }}</option>
            </select>
          </div>

          <!-- Row 5: Print Copies & Media -->
          <div class="flex items-center justify-between py-2 border-b border-neutral-100 dark:border-zinc-800/60 pb-4 gap-4">
            <div class="flex flex-col pr-4">
              <span class="text-sm font-medium text-zinc-800 dark:text-zinc-200">{{ t('print.copies') }} / {{ t('print.media') }}</span>
              <span class="text-xs text-zinc-400 dark:text-zinc-500 mt-0.5">{{ t('print.title') }}</span>
            </div>
            <div class="flex items-center gap-2">
              <input type="number" min="1" max="99" v-model.number="settingInfo.printer.copies"
                class="input input-sm input-bordered w-20 rounded-lg bg-neutral-50 dark:bg-zinc-950 focus:border-blue-500 text-sm h-9 min-h-0" />
              <select v-model="settingInfo.printer.media" class="select select-sm select-bordered w-32 rounded-lg text-sm bg-neutral-50 dark:bg-zinc-950 focus:border-blue-500 h-9 min-h-0">
                <option v-for="m in mediaSizes" :key="m" :value="m">{{ m }}</option>
              </select>
            </div>
          </div>
        </div>

        <!-- Tab 2: Tinify Compression -->
        <div v-if="activeTab === 'tinify'" class="space-y-4">
          <!-- Row 1: Tinify key -->
          <div class="flex items-center justify-between py-2 border-b border-neutral-100 dark:border-zinc-800/60 pb-4 gap-4">
            <div class="flex flex-col pr-4">
              <span class="text-sm font-medium text-zinc-800 dark:text-zinc-200">{{ t('setting.tinify_key') }}</span>
              <span class="text-xs text-zinc-400 dark:text-zinc-500 mt-0.5">Used for API-based image compression. Hover to show key</span>
            </div>
            <div class="flex flex-col items-end gap-1.5 w-64 flex-shrink-0">
              <input ref="apiKeyInput" id="api_key" v-on:mouseenter="handleMouseEnter" v-on:mouseleave="handleMouseLeave"
                type="password" v-model="settingInfo.tinify.tinify_key" class="input input-sm input-bordered w-full rounded-lg bg-neutral-50 dark:bg-zinc-950 focus:border-blue-500 text-sm h-9 min-h-0" placeholder="Tinypng Key..." />
              <span class="text-[11px] text-blue-500 hover:underline cursor-pointer flex items-center gap-0.5" @click="openLink('https://tinypng.com/developers')" target="_blank">
                <i class="fa-solid fa-up-right-from-square text-[9px]"></i> Get API Key
              </span>
            </div>
          </div>

          <!-- Row 2: Used count -->
          <div class="flex items-center justify-between py-2 border-b border-neutral-100 dark:border-zinc-800/60 pb-4 gap-4">
            <div class="flex flex-col pr-4">
              <span class="text-sm font-medium text-zinc-800 dark:text-zinc-200">{{ t('setting.tinify_used_count') }}</span>
              <span class="text-xs text-zinc-400 dark:text-zinc-500 mt-0.5">Number of compressions processed this month</span>
            </div>
            <input id="tinify_used_count" disabled type="text" v-model="settingInfo.tinify.compression_count"
              class="input input-sm input-bordered w-48 rounded-lg bg-neutral-100 dark:bg-zinc-900 text-zinc-500 dark:text-zinc-400 cursor-not-allowed text-center text-sm h-9 min-h-0" />
          </div>

          <!-- Row 3: Preserve Metadata -->
          <div class="flex items-center justify-between py-2 border-b border-neutral-100 dark:border-zinc-800/60 pb-4 gap-4">
            <div class="flex flex-col pr-4">
              <span class="text-sm font-medium text-zinc-800 dark:text-zinc-200">{{ t('setting.tinify_preserving') }}</span>
              <span class="text-xs text-zinc-400 dark:text-zinc-500 mt-0.5">Preserve image metadata fields when saving</span>
            </div>
            <div class="w-64 flex-shrink-0">
              <MultiSelect id="preserve" v-model="settingInfo.tinify.preserve"
                :options="['copyright', 'creation', 'location']" />
            </div>
          </div>
        </div>

        <!-- Tab 3: Advanced Optimization -->
        <div v-if="activeTab === 'advanced'" class="space-y-4">
          <!-- Row 1: Edge Optimization Switch -->
          <div class="flex flex-col gap-3 py-2 border-b border-neutral-100 dark:border-zinc-800/60 pb-4">
            <div class="flex items-center justify-between">
              <div class="flex flex-col">
                <span class="text-sm font-medium text-zinc-850 dark:text-zinc-200">{{ t('setting.edge_optimization') }}</span>
                <span class="text-xs text-zinc-400 dark:text-zinc-500 mt-0.5">Refine and smooth boundaries for transparent image edges</span>
              </div>
              <input type="checkbox" class="toggle toggle-primary toggle-sm" id="edge_optimization"
                v-model="settingInfo.edge_optimization.is_edge_optimization" />
            </div>
            <div class="pl-2 transition-all duration-300 ease-in-out flex items-center justify-between" v-if="settingInfo.edge_optimization.is_edge_optimization">
              <span class="text-xs text-zinc-500 dark:text-zinc-400">{{ t('setting.edge_r') }}</span>
              <input type="number" id="edge_r" v-model="settingInfo.edge_optimization.r"
                class="input input-sm input-bordered w-32 rounded-lg bg-neutral-50 dark:bg-zinc-950 focus:border-blue-500 text-sm h-9 min-h-0" />
            </div>
          </div>

          <!-- Row 2: API Server Switch -->
          <div class="flex flex-col gap-3 py-2 border-b border-neutral-100 dark:border-zinc-800/60 pb-4">
            <div class="flex items-center justify-between">
              <div class="flex flex-col">
                <div class="flex items-center gap-2">
                  <span class="text-sm font-medium text-zinc-850 dark:text-zinc-200">{{ t('setting.api_server') }}</span>
                  <div v-if="settingInfo.api_server.is_enable" class="badge badge-warning badge-xs rounded p-1 text-[9px] font-semibold tracking-wide uppercase">
                    {{ t('setting.restart_notice') }}
                </div>
                </div>
                <span class="text-xs text-zinc-400 dark:text-zinc-500 mt-0.5">Host a local REST API endpoint to trigger AI Matting programmatically</span>
              </div>
              <input type="checkbox" class="toggle toggle-primary toggle-sm" id="api_server"
                v-model="settingInfo.api_server.is_enable" />
            </div>
            <div class="pl-2 space-y-2 transition-all duration-300 ease-in-out flex items-center justify-between" v-if="settingInfo.api_server.is_enable">
              <span class="text-xs text-zinc-500 dark:text-zinc-400 flex flex-wrap items-center gap-1">
                {{ t('setting.api_server_port') }}
                <span class="text-xs text-blue-500 hover:underline cursor-pointer flex items-center gap-0.5 ml-1" @click="openLink(`http://localhost:${settingInfo.api_server.port}/api/docs`)">
                  <i class="fa-solid fa-up-right-from-square text-[9px]"></i> (Docs)
                </span>
              </span>
              <input type="number" id="api_port" v-model="settingInfo.api_server.port"
                class="input input-sm input-bordered w-32 rounded-lg bg-neutral-50 dark:bg-zinc-950 focus:border-blue-500 text-sm h-9 min-h-0" />
            </div>
          </div>
        </div>
      </div>

      <!-- Save Actions Footer -->
      <div class="flex-shrink-0 px-6 py-4 border-t border-neutral-200/50 dark:border-zinc-800/40 bg-neutral-50/30 dark:bg-zinc-900/30 flex justify-end">
        <button @click="saveSettings" class="btn bg-blue-500 hover:bg-blue-600 border-none text-white px-8 rounded-full py-1.5 shadow-sm hover:shadow transition-all text-sm flex items-center gap-2 h-9 min-h-0">
          <i class="fa-solid fa-floppy-disk text-xs"></i>
          {{ t('setting.save_btn') }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref, watch, computed } from 'vue'
import { settingAPI } from '@/api/user';
import { printAPI } from '@/api/print';
import MultiSelect from '@/views/components/MultiSelect.vue';
import baseAPI from '@/api/base';
import { languageList } from '@/locales/index'
import { useI18n } from 'vue-i18n'
const { locale } = useI18n();
import message from '@/utils/message.js'
const { t } = useI18n()

const activeTab = ref('general')

const tabs = computed(() => [
  { id: 'general', name: t('about.system_info') || 'General', icon: 'fa-solid fa-sliders' },
  { id: 'tinify', name: 'Tinify Key', icon: 'fa-solid fa-compress' },
  { id: 'advanced', name: 'Advanced', icon: 'fa-solid fa-gears' },
])

const activeTabName = computed(() => {
  const current = tabs.value.find(tab => tab.id === activeTab.value)
  return current ? current.name : ''
})

const settingInfo = ref({
  'language': '',
  'export_format': '',
  'matting_model': {
    'name': 'rmbg-1.4',
  },
  'tinify': {
    'tinify_key': '',
    'preserve': [],
    'compression_count': 0,
  },
  'edge_optimization': {
    'is_edge_optimization': true,
    'r': 90
  },
  'api_server': {
    'is_enable': false,
    'port': 11111,
  },
  'printer': {
    'printer_name': '',
    'copies': 1,
    'media': 'A4',
    'orientation': 'portrait',
    'fit_to_page': true,
  }
})

const printers = ref([])
const mediaSizes = ref(['A4', 'Letter', '4x6in', '5x7in', 'A5'])

const formData = ref({
  'language': '',
  'export_format': '',
  'matting_model.name': 'rmbg-1.4',
  'tinify.tinify_key': '',
  'tinify.preserve': [],
  'edge_optimization.is_edge_optimization': true,
  'edge_optimization.r': 90,
  'api_server.is_enable': false,
  'api_server.port': 11111,
  'printer.printer_name': '',
  'printer.copies': 1,
  'printer.media': 'A4',
  'printer.orientation': 'portrait',
  'printer.fit_to_page': true
})

const openLink = async (url) => {
  await baseAPI('open_link', url)
}

const apiKeyInput = ref(null)

// 鼠标移出隐藏API密钥
const handleMouseLeave = () => {
  apiKeyInput.value.type = 'password'
}
// 鼠标移入显示API密钥
const handleMouseEnter = () => {
  apiKeyInput.value.type = 'text'
}

// 获取设置信息
const getSettingInfo = async () => {
  const res = await settingAPI('get', '')
  settingInfo.value = res.data
  if (!settingInfo.value.printer) {
    settingInfo.value.printer = { printer_name: '', copies: 1, media: 'A4', orientation: 'portrait', fit_to_page: true }
  }
  console.log(settingInfo.value)
  locale.value = settingInfo.value.language
  await loadPrinters()
}

// 加载打印机列表供默认打印机选择
const loadPrinters = async () => {
  try {
    const res = await printAPI('get_printers', {})
    if (res.code === 200) {
      printers.value = res.data.printers || []
      const current = settingInfo.value.printer.printer_name
      if (current) {
        const opt = await printAPI('get_printer_options', { printer_name: current })
        if (opt.code === 200 && opt.data.media_sizes && opt.data.media_sizes.length > 0) {
          mediaSizes.value = opt.data.media_sizes
        }
      }
    }
  } catch (e) {
    console.error(e)
  }
}
// 切换语言
const changeLanguage = (lang) => {
  locale.value = lang;
};

// 保存设置
const saveSettings = async () => {
  console.log(settingInfo.value)
  formData.value.language = settingInfo.value.language
  formData.value.export_format = settingInfo.value.export_format
  formData.value['matting_model.name'] = settingInfo.value.matting_model.name
  formData.value['tinify.tinify_key'] = settingInfo.value.tinify.tinify_key
  formData.value['tinify.preserve'] = settingInfo.value.tinify.preserve
  formData.value['edge_optimization.is_edge_optimization'] = settingInfo.value.edge_optimization.is_edge_optimization
  formData.value['edge_optimization.r'] = settingInfo.value.edge_optimization.r
  formData.value['api_server.is_enable'] = settingInfo.value.api_server.is_enable
  formData.value['api_server.port'] = settingInfo.value.api_server.port
  formData.value['printer.printer_name'] = settingInfo.value.printer.printer_name
  formData.value['printer.copies'] = settingInfo.value.printer.copies
  formData.value['printer.media'] = settingInfo.value.printer.media
  formData.value['printer.orientation'] = settingInfo.value.printer.orientation
  formData.value['printer.fit_to_page'] = settingInfo.value.printer.fit_to_page
  const res = await settingAPI('put', formData.value)
  if (res.code === 200) {
    message.info(res.msg);
    changeLanguage(settingInfo.value.language)
  } else {
    message.error(res.err_msg);
  }
}


onMounted(async () => {
  await getSettingInfo();
})

</script>

<style scoped>
</style>