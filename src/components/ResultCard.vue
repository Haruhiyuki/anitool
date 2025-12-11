<template>
  <div class="w-full mt-12 pb-20">
    <transition-group name="list" tag="div" class="flex flex-col gap-16">
      
      <!-- 加载中 -->
      <template v-if="isLoading">
        <div class="flex flex-col items-center w-full animate-pulse">
          <div class="w-full max-w-3xl h-72 rounded-3xl mb-6 shadow-inner border flex items-center justify-center glass-panel">
            <i class="ph ph-planet text-6xl animate-spin-slow" style="color: var(--text-accent); opacity: 0.5;"></i>
          </div>
        </div>
      </template>

      <!-- 结果列表 -->
      <template v-else>
        <div v-for="(item, index) in results" :key="index" class="w-full flex flex-col items-center gap-8">
          
          <div v-if="results.length > 1" class="flex items-center gap-4 w-full max-w-3xl opacity-50">
            <div class="h-px flex-1" style="background-color: var(--border-glass)"></div>
            <span class="text-xs font-mono border px-2 py-1 rounded" style="color: var(--text-accent); border-color: var(--border-glass); background-color: var(--bg-glass)">
              RESULT #{{ String(index + 1).padStart(2, '0') }}
            </span>
            <div class="h-px flex-1" style="background-color: var(--border-glass)"></div>
          </div>

          <!-- 图片展示 -->
          <div class="w-full max-w-4xl p-3 rounded-[2rem] border backdrop-blur-sm transition-colors" 
               style="background-color: var(--bg-glass-hover); border-color: var(--border-glass); box-shadow: 0 0 40px var(--shadow-color)">
            <div class="relative w-full rounded-[1.5rem] overflow-hidden group">
              <img
                v-if="item.image"
                :src="item.image"
                alt="Anime Result"
                class="w-full h-auto object-cover opacity-90 group-hover:opacity-100 transition-opacity duration-500"
                loading="lazy"
              >
              <div
                v-else
                class="w-full h-60 flex items-center justify-center text-sm bg-black/30 text-white"
              >
                暂无图片结果
              </div>

              <div class="absolute inset-0 bg-gradient-to-t from-black via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex flex-col justify-end p-6">
                <p class="font-mono tracking-widest text-lg drop-shadow-md text-white">
                  <i class="ph-fill ph-clock mr-2"></i>{{ item.data['时间戳'] || '--:--.---' }}
                </p>
              </div>
            </div>

            <div class="flex items-center justify-end gap-3 px-4 py-4 mt-1">
              <span
                v-if="item.confidenceValue < 75"
                class="text-amber-400 text-xs font-bold mr-auto animate-pulse flex items-center gap-1"
              >
                <i class="ph-fill ph-warning"></i> <span class="hidden sm:inline">匹配度可能较低</span>
              </span>
              
              <span class="text-xs font-mono border px-2 py-1 rounded mr-2 sm:mr-0" style="color: var(--text-secondary); border-color: var(--border-glass); background-color: rgba(0,0,0,0.1)">
                 置信度：{{ item.confidence }}
              </span>

              <button
                class="flex items-center gap-2 px-5 py-2.5 border rounded-xl text-sm font-bold transition disabled:opacity-40"
                style="border-color: var(--text-accent); color: var(--text-primary); background: transparent"
                @click="handleCopyLine(item)"
                :disabled="!getMainLine(item.data)"
              >
                <i class="ph ph-copy"></i> <span class="hidden sm:inline">复制台词</span>
              </button>

              <button
                class="flex items-center gap-2 px-5 py-2.5 text-white rounded-xl text-sm font-bold transition disabled:opacity-40"
                style="background: var(--btn-gradient); box-shadow: 0 0 15px var(--shadow-color)"
                @click="handleSaveImage(item.image)"
                :disabled="!item.image"
              >
                <i class="ph ph-download-simple"></i> <span class="hidden sm:inline">保存图片</span>
              </button>
            </div>
          </div>

          <!-- 详细信息 -->
          <div class="w-full max-w-4xl">
            <div class="glass-panel rounded-3xl p-8 shadow-xl w-full">
              <h3 class="text-xl font-bold mb-6 flex items-center gap-3 border-b pb-4" style="color: var(--text-primary); border-color: var(--border-glass)">
                <i class="ph-fill ph-sparkle" style="color: var(--text-accent)"></i> 识别详情
              </h3>
              <ul class="space-y-4">
                <li
                  v-for="(value, key) in item.data"
                  :key="key"
                  class="flex flex-col md:flex-row md:items-start gap-2 group"
                >
                  <div class="min-w-[140px] pt-2">
                    <span class="text-xs font-bold uppercase tracking-widest flex items-center gap-2 transition-colors" style="color: var(--text-accent); opacity: 0.7">
                      <i class="ph-fill ph-star-four text-[10px]"></i> {{ key }}
                    </span>
                  </div>
                  <div class="flex-1">
                    <span class="block w-full font-medium px-5 py-3 rounded-xl border leading-relaxed transition-all duration-300"
                          style="color: var(--text-primary); background-color: var(--bg-glass-hover); border-color: var(--border-glass)">
                      {{ value }}
                    </span>
                  </div>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </template>
    </transition-group>
  </div>
</template>

<script setup>
defineProps({
  isLoading: Boolean,
  results: {
    type: Array,
    default: () => []
  }
});

const getMainLine = (data) => {
  if (!data) return '';
  return data['匹配台词'] || data['匹配回复'] || '';
};

const handleCopyLine = async (item) => {
  const text = getMainLine(item.data);
  if (!text) return;

  try {
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(text);
    } else {
      const textarea = document.createElement('textarea');
      textarea.value = text;
      textarea.style.position = 'fixed';
      textarea.style.left = '-9999px';
      document.body.appendChild(textarea);
      textarea.focus();
      textarea.select();
      document.execCommand('copy');
      document.body.removeChild(textarea);
    }
    alert('台词已复制到剪贴板');
  } catch (err) {
    console.error('复制失败:', err);
    alert('复制失败，请手动选择文本复制');
  }
};

const handleSaveImage = async (imageUrl) => {
  if (!imageUrl) return;

  try {
    const response = await fetch(imageUrl);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);

    const blob = await response.blob();
    const url = URL.createObjectURL(blob);

    const a = document.createElement('a');
    a.href = url;

    const urlObj = new URL(imageUrl, window.location.origin);
    const pathname = urlObj.pathname;
    const guessedName = pathname.split('/').filter(Boolean).slice(-1)[0] || 'anime_frame.jpg';

    a.download = guessedName;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  } catch (err) {
    console.error('保存图片失败:', err);
    alert('保存图片失败，请尝试右键/长按图片手动保存');
  }
};
</script>