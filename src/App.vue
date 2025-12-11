<template>
  <!-- 根容器：保持 themeClass 逻辑以适配画面搜索的深色模式需求 -->
  <div class="w-full h-full relative z-10 overflow-y-auto no-scrollbar transition-colors duration-1000"
       :class="themeClass">
    
    <!-- 背景层：修改此处，使用计算属性 backgroundScope 而不是直接用 searchScope -->
    <BackgroundSystem :scope="backgroundScope" />
    
    <!-- 头部 -->
    <AppHeader :current-view="currentView" @navigate="handleNavigate" />

    <main class="flex-1 w-full max-w-4xl mx-auto px-4 py-12 flex flex-col items-center relative z-10 min-h-screen justify-start pt-32 gap-6 transition-all duration-500">
      
      <!-- 主页视图 -->
      <template v-if="currentView === 'home'">
          
          <!-- 标题区 -->
          <div 
            class="text-center transition-all duration-700 ease-in-out overflow-hidden transform origin-top shrink-0"
            :class="hasSearched ? 'max-h-0 opacity-0 scale-95' : 'max-h-48 opacity-100 scale-100 animate-[float_6s_ease-in-out_infinite]'"
          >
            <!-- 动态标题 -->
            <h1 class="text-4xl md:text-6xl font-bold mb-2 drop-shadow-lg tracking-tight bg-clip-text text-transparent bg-gradient-to-r"
                :style="{ backgroundImage: searchScope === 1 
                    ? 'linear-gradient(to right, #a855f7, #f3e8ff, #38bdf8)' 
                    : 'linear-gradient(to bottom right, #0ea5e9, #06b6d4, #facc15, #f97316)' }">
                {{ searchScope === 1 ? '凉宫春日台词匹配' : '京阿尼台词匹配' }}
            </h1>
            
            <!-- 动态副标题 -->
            <p class="font-medium text-lg tracking-widest uppercase" style="color: var(--text-secondary); opacity: 0.9; text-shadow: 0 1px 2px rgba(255,255,255,0.5)">
                {{ searchScope === 1 ? '我要找宇宙人，未来人和超能力者！' : '京都有鸟，其名为凤；淋漓如烛，浴火重生。' }}
            </p>
          </div>

          <!-- 搜索组件 -->
          <SearchSection 
            v-model="searchText"
            v-model:mode="currentMode"
            v-model:topK="topK"
            v-model:scope="searchScope"
            :is-loading="isLoading"
            @search="handleSearch"
            class="z-20 w-full relative transition-all duration-500 shrink-0" 
          />

          <!-- 结果展示组件 -->
          <ResultCard
            v-if="hasSearched"
            :is-loading="isLoading"
            :results="results"
            class="z-10 w-full"
          />
      </template>

      <!-- 画面/场景搜索视图 -->
      <template v-if="currentView === 'scene'">
          <div class="text-center animate-[float_6s_ease-in-out_infinite] shrink-0">
              <h2 class="text-3xl md:text-5xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-pink-400 to-purple-400 drop-shadow-sm">
                  凉宫春日画面搜索
              </h2>
          </div>
          <SceneSearchPage />
      </template>

      <!-- 关于页视图 -->
      <transition name="fade" mode="out-in">
        <AboutPage v-if="currentView === 'about'" @go-back="currentView = 'home'" />
      </transition>

    </main>
    
    <!-- 页脚 -->
    <FooterBar class="w-full mt-16" />

  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import BackgroundSystem from './components/StarBackground.vue';
import AppHeader from './components/AppHeader.vue';
import SearchSection from './components/SearchSection.vue';
import ResultCard from './components/ResultCard.vue';
import AboutPage from './components/AboutPage.vue';
import FooterBar from './components/FooterBar.vue';
import SceneSearchPage from './components/SceneSearchPage.vue';
import { API_BASE_URL, ENDPOINTS, IMAGE_BASE_URL } from './config';

// 状态管理
const currentView = ref('home');
const searchText = ref('');
const isLoading = ref(false);
const hasSearched = ref(false);
const currentMode = ref(1);
const topK = ref(3);
const searchScope = ref(2); 
const results = ref([]);

// 计算属性：控制主题类名
const themeClass = computed(() => {
    if (currentView.value === 'scene') return 'theme-haruhi'; 
    return searchScope.value === 1 ? 'theme-haruhi' : 'theme-lemon';
});

// 新增计算属性：控制背景 Scope
// 逻辑：如果当前视图是画面搜索，强制使用 Scope 1 (星空背景)；否则跟随用户选择的 Scope
const backgroundScope = computed(() => {
    if (currentView.value === 'scene') return 1;
    return searchScope.value;
});

// 视图切换处理
const handleNavigate = (view) => {
    currentView.value = view;
};

// 辅助函数：格式化时间
const formatTime = (seconds) => {
    if (!seconds && seconds !== 0) return 'Unknown';
    const min = Math.floor(seconds / 60);
    const sec = Math.floor(seconds % 60);
    const ms = Math.floor((seconds % 1) * 1000);
    return `${min.toString().padStart(2, '0')}:${sec.toString().padStart(2, '0')}.${ms.toString().padStart(3, '0')}`;
};

// 辅助函数：处理图片路径
const resolveImageUrl = (path) => {
  if (!path) return "";
  if (path.startsWith("http")) return path;
  let cleanPath = path.startsWith("/") ? path : `/${path}`;
  if (!cleanPath.startsWith("/images/")) {
    cleanPath = `/images${cleanPath}`;
  }
  return `${API_BASE_URL}${cleanPath}`;
};

// 搜索逻辑
const handleSearch = async () => {
  if (!searchText.value.trim()) return;

  isLoading.value = true;
  hasSearched.value = true;
  results.value = [];

  const apiEndpoint = currentMode.value === 1 ? ENDPOINTS.MATCH : ENDPOINTS.REPLY;
  const url = `${API_BASE_URL}${apiEndpoint}`;

  try {
      const response = await fetch(url, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
              query: searchText.value,
              top_k: topK.value,
              scope: searchScope.value 
          })
      });

      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      const data = await response.json();
      
      if (!data.results || data.results.length === 0) {
          alert("未找到相关结果");
          hasSearched.value = false;
          return;
      }

      results.value = data.results.map(item => {
          const workName = item.work_name || "未知作品";
          const episode = item.episode_index ? `第 ${item.episode_index} 集` : "未知集数";
          const score = item.coarse_score ? (item.coarse_score * 100).toFixed(1) : 0;
          const rerank = item.rerank_score || 0;
          
          let resultData = {};
          let imgUrl = "";

          if (currentMode.value === 1) {
              imgUrl = resolveImageUrl(item.image_path);
              resultData = {
                  "作品名称": workName,
                  "集数": episode,
                  "章节标题": item.episode_title || "-",
                  "时间戳": formatTime(item.time_s),
                  "匹配台词": item.text,
                  "精排得分": item.rerank_score?.toFixed(4),
              };
          } else {
              imgUrl = resolveImageUrl(item.answer_image_path);
              resultData = {
                  "作品名称": workName,
                  "集数": episode,
                  "时间戳": formatTime(item.answer_time_s),
                  "上文提问": item.question_text,
                  "匹配回复": item.answer_text,
                  "精排得分": item.rerank_score?.toFixed(4),
              };
          }

          return {
              image: imgUrl,
              data: resultData,
              confidence: `${score}%`,
              confidenceValue: Number(score),
              rerankValue: Number(rerank)
          };
      });

  } catch (error) {
      console.error("Search Error:", error);
      alert(`连接服务器失败: ${error.message}`);
      hasSearched.value = false;
  } finally {
      isLoading.value = false;
  }
};
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>