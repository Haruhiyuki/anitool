<template>
  <div class="w-full flex flex-col items-center gap-8 animate-fade-in">
    
    <!-- 顶部：功能切换 Tabs -->
    <div class="glass-panel p-1 rounded-full flex relative z-20">
      <button 
        v-for="tab in tabs" 
        :key="tab.id"
        @click="currentTab = tab.id"
        class="px-6 py-2 rounded-full text-sm font-bold transition-all duration-300 flex items-center gap-2"
        :class="currentTab === tab.id ? 'text-white shadow-md' : 'text-slate-400 hover:text-white'"
        :style="currentTab === tab.id ? { background: 'var(--text-accent)' } : {}"
      >
        <i :class="tab.icon"></i> {{ tab.name }}
      </button>
    </div>

    <!-- TAB 1: 描述搜图 (主模式) -->
    <div v-if="currentTab === 'search'" class="w-full max-w-3xl flex flex-col items-center">
      <div class="glass-panel rounded-3xl p-2 flex items-center shadow-lg w-full transition-all duration-300 hover:shadow-2xl hover:border-purple-500/30">
        <input 
          v-model="singleQuery"
          @keydown.enter="searchScene(singleQuery)"
          type="text" 
          placeholder="描述一个画面，例如：夕阳与列车"
          class="flex-1 bg-transparent border-none outline-none px-6 py-3 text-lg font-medium"
          style="color: var(--text-primary)"
        />
        <button 
          @click="searchScene(singleQuery)"
          class="px-6 py-3 rounded-2xl font-bold text-white transition-transform active:scale-95 m-1"
          style="background: var(--btn-gradient)"
        >
          <i class="ph-bold ph-magnifying-glass"></i>
        </button>
      </div>
      
      <p class="mt-4 text-xs font-mono opacity-50 text-center max-w-lg leading-relaxed" style="color: var(--text-secondary)">
        直接描述画面内容，检索近似图片，对角色的识别效果并非100%精确。
      </p>
    </div>

    <!-- TAB 2: 文章智能配图 (高级模式) -->
    <div v-else-if="currentTab === 'analyze'" class="w-full max-w-4xl flex flex-col gap-6">
      
      <!-- 输入区域 -->
      <div class="glass-panel rounded-3xl p-6 transition-all duration-300">
        <label class="block text-sm font-bold mb-3 ml-1" style="color: var(--text-secondary)">
          <i class="ph-fill ph-article mr-1"></i> 第一步：粘贴小说/文章
        </label>
        <textarea 
          v-model="articleText"
          rows="8"
          placeholder="在此处粘贴完整的小说章节或文章内容..."
          class="w-full bg-black/10 rounded-xl p-4 text-base outline-none border border-transparent focus:border-purple-500/50 transition-colors resize-y"
          style="color: var(--text-primary)"
        ></textarea>
        
        <div class="flex justify-end mt-4">
          <button 
            @click="analyzeArticle"
            :disabled="isAnalyzing || !articleText"
            class="px-6 py-2 rounded-full font-bold text-white shadow-lg flex items-center gap-2 transition-transform active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed"
            style="background: var(--btn-gradient)"
          >
            <i v-if="isAnalyzing" class="ph ph-spinner animate-spin"></i>
            <i v-else class="ph-bold ph-magic-wand"></i>
            <span>分析并提取场景</span>
          </button>
        </div>
      </div>

      <!-- 场景选择区域 -->
      <transition name="fade">
        <div v-if="extractedScenes.length > 0" class="glass-panel rounded-3xl p-6">
          <label class="block text-sm font-bold mb-4 ml-1" style="color: var(--text-secondary)">
            <i class="ph-fill ph-film-strip mr-1"></i> 第二步：点击选择一个场景进行检索
          </label>
          <div class="flex flex-wrap gap-3">
            <button
              v-for="(scene, idx) in extractedScenes"
              :key="idx"
              @click="searchScene(scene)"
              class="text-left px-4 py-3 rounded-xl border transition-all duration-200 text-sm leading-relaxed hover:shadow-lg hover:-translate-y-0.5"
              :class="selectedScene === scene ? 'bg-purple-500/20 border-purple-400 shadow-inner' : 'bg-white/5 border-white/10 hover:bg-white/10'"
              :style="{ color: selectedScene === scene ? 'var(--text-accent)' : 'var(--text-primary)' }"
            >
              {{ scene }}
            </button>
          </div>
        </div>
      </transition>

    </div>

    <!-- 结果展示区域 (通用) -->
    <div v-if="hasSearched" class="w-full max-w-6xl mt-4">
      
      <div v-if="isSearching" class="flex flex-col items-center justify-center py-20">
        <i class="ph ph-spinner-gap text-5xl animate-spin" style="color: var(--text-accent)"></i>
        <p class="mt-4 text-sm font-mono opacity-70" style="color: var(--text-primary)">正在从向量空间检索...</p>
      </div>

      <div v-else-if="results.length === 0" class="text-center py-20 opacity-60">
        <i class="ph ph-mask-sad text-4xl mb-2"></i>
        <p>未找到匹配的图片结果</p>
      </div>

      <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div 
          v-for="(item, idx) in results" 
          :key="idx"
          class="group relative rounded-2xl overflow-hidden glass-panel border border-white/10 hover:border-purple-500/30 transition-all duration-300 hover:shadow-2xl hover:-translate-y-1"
        >
          <!-- 图片 -->
          <div class="aspect-video w-full bg-black/50 overflow-hidden cursor-pointer" @click="previewImage(item.image)">
            <img 
              :src="item.image" 
              class="w-full h-full object-cover opacity-90 group-hover:opacity-100 transition-opacity duration-500 hover:scale-105 transform"
              loading="lazy"
            />
          </div>

          <!-- 信息遮罩 -->
          <div class="p-4">
            <div class="text-xs font-mono opacity-50 mb-1" style="color: var(--text-secondary)">
              Score: {{ item.score.toFixed(4) }}
            </div>
          </div>
          
          <!-- 下载按钮 -->
          <a 
            :href="item.image" 
            download 
            class="absolute top-3 right-3 w-8 h-8 rounded-full bg-black/50 hover:bg-purple-600 text-white flex items-center justify-center opacity-0 group-hover:opacity-100 transition-all backdrop-blur-md"
            title="保存原图"
            @click.stop
          >
            <i class="ph-bold ph-download-simple"></i>
          </a>
        </div>
      </div>

    </div>

  </div>
</template>

<script setup>
import { ref } from 'vue';
import { API_BASE_URL } from '../config';

// 调整 Tabs 顺序，将“直接搜图”放在第一位
const tabs = [
  { id: 'search', name: '描述搜图', icon: 'ph-bold ph-image' },
  { id: 'analyze', name: '文章配图 (高级)', icon: 'ph-bold ph-book-open-text' }
];

// 默认选中 'search'
const currentTab = ref('search');
const articleText = ref('');
const extractedScenes = ref([]);
const selectedScene = ref('');
const singleQuery = ref('');
const results = ref([]);

const isAnalyzing = ref(false);
const isSearching = ref(false);
const hasSearched = ref(false);

// 1. 分析文章提取场景
const analyzeArticle = async () => {
  if (!articleText.value) return;
  isAnalyzing.value = true;
  extractedScenes.value = [];
  
  try {
    const res = await fetch(`${API_BASE_URL}/scene/analyze`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text: articleText.value })
    });
    const data = await res.json();
    extractedScenes.value = data.scenes || [];
  } catch (e) {
    alert('分析失败: ' + e.message);
  } finally {
    isAnalyzing.value = false;
  }
};

// 2. 搜索场景 (共用)
const searchScene = async (query) => {
  if (!query) return;
  selectedScene.value = query; // 如果是点击 tag
  isSearching.value = true;
  hasSearched.value = true;
  results.value = [];

  try {
    const res = await fetch(`${API_BASE_URL}/scene/search`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query: query, top_k: 12 })
    });
    const data = await res.json();
    
    // 处理图片路径，确保是完整 URL
    results.value = data.results.map(r => ({
      ...r,
      image: r.image.startsWith('http') ? r.image : `${API_BASE_URL}${r.image}`
    }));
  } catch (e) {
    console.error(e);
  } finally {
    isSearching.value = false;
  }
};

const previewImage = (url) => {
  window.open(url, '_blank');
};
</script>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity 0.3s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>