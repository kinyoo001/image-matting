<template>
  <div class="w-full max-w-lg px-6 py-8 flex flex-col items-center mx-auto select-none">
    <!-- App Branding header -->
    <div class="flex flex-col items-center text-center mb-6 flex-shrink-0">
      <h2 class="text-xl font-bold text-zinc-800 dark:text-zinc-100 leading-tight">
        {{ t('about.title') }}
      </h2>
      <span class="px-2 py-0.5 bg-neutral-100 dark:bg-zinc-800 text-zinc-500 dark:text-zinc-400 rounded-full text-xs font-medium border border-neutral-200/40 dark:border-zinc-700/30 mt-2">
        Version {{ systemInfo.version }}
      </span>
    </div>

    <!-- Info List -->
    <div class="w-full space-y-4 select-text mb-8">
      <div class="border-t border-neutral-200/50 dark:border-zinc-800/40 pt-4 space-y-3 text-sm">
        <div class="flex justify-between items-center py-1">
          <span class="text-zinc-500 dark:text-zinc-400 font-medium text-xs">{{ t('about.author') }}</span>
          <span class="font-medium text-zinc-900 dark:text-zinc-100">{{ systemInfo.author }}</span>
        </div>

        <div class="flex justify-between items-center py-1">
          <span class="text-zinc-500 dark:text-zinc-400 font-medium text-xs">{{ t('about.email') }}</span>
          <span class="font-medium text-zinc-900 dark:text-zinc-100">{{ systemInfo.email }}</span>
        </div>

        <div v-if="systemInfo.github" class="flex flex-col py-1 border-t border-neutral-100 dark:border-zinc-800/20 pt-2.5">
          <span class="text-zinc-500 dark:text-zinc-400 font-medium text-xs mb-1.5">{{ t('about.github') }}</span>
          <span class="text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 hover:underline cursor-pointer text-xs font-semibold break-all" @click="openLink(systemInfo.github)">
            {{ systemInfo.github }}
          </span>
        </div>

        <div class="flex flex-col py-1 border-t border-neutral-100 dark:border-zinc-800/20 pt-2.5">
          <span class="text-zinc-500 dark:text-zinc-400 font-medium text-xs mb-1.5">{{ t('about.website') }}</span>
          <span class="text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 hover:underline cursor-pointer text-xs font-semibold break-all" @click="openLink(systemInfo.website)">
            {{ systemInfo.website }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import baseAPI from '@/api/base';


const { locale } = useI18n();
const { t } = useI18n()
const systemInfo = ref({
  'author': '',
  'email': '',
  'version': '',
  'github': '',
  'website': '',
})


const openLink = async (url) => {
  await baseAPI('open_link', url)
}


// 获取系统信息
const getSystemInfo = async () => {
  const res = await baseAPI('get_system_info')
  if (res.code === 200) {
    systemInfo.value = res.data
  }
}

onMounted(async () => {
  await getSystemInfo();
})

</script>

<style scoped>
</style>