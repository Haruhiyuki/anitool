<template>
  <footer class="relative mt-auto w-full glass-panel border-t z-20" style="border-top-color: var(--border-glass)">
    <!-- 顶部微光线条 -->
    <div class="pointer-events-none absolute inset-x-0 -top-px h-px bg-gradient-to-r from-transparent via-purple-500/20 to-transparent"></div>

    <div class="mx-auto max-w-6xl px-6">
      <div class="flex flex-col gap-10 py-12 md:flex-row md:items-start md:gap-24 lg:gap-32">
        
        <!-- 左侧：项目身份 -->
        <div class="flex items-start gap-4 shrink-0">
          <div class="h-14 w-14 flex items-center justify-center rounded-full border overflow-hidden shrink-0" style="background: rgba(168,85,247,0.05); border-color: var(--border-glass)">
             <!-- 你可以用 img 标签替换这里的文字 -->
            <img 
               src="/haruhi-logo-192.png" 
               alt="Haruhifanclub" 
               class="h-full w-full object-cover opacity-90 group-hover:opacity-100 transition-opacity"
             />
          </div>
          <div class="leading-tight pt-1">
            <div class="text-base font-bold tracking-wide drop-shadow-md" style="color: var(--text-primary)">
              凉宫春日应援团
            </div>
            <div class="text-xs font-mono mb-2" style="color: var(--text-accent)">Haruhifanclub</div>
            <div class="text-xs font-medium leading-relaxed" style="color: var(--text-secondary)">
              非营利的凉宫春日粉丝团体。
            </div>
          </div>
        </div>

        <!-- 右侧：链接组 (完全恢复) -->
        <div class="flex flex-col gap-8 text-xs md:flex-row md:items-start md:gap-12 flex-1">
          
          <!-- 社交平台 -->
          <div class="flex flex-col gap-4 shrink-0">
            <span class="text-[10px] uppercase tracking-[0.2em] font-bold select-none" style="color: var(--text-secondary); opacity: 0.6">
              社交平台
            </span>
            <div class="flex flex-col gap-2">
              <a href="https://space.bilibili.com/201296348" target="_blank" class="footer-link-pill w-fit group">
                <i class="ph-fill ph-television-simple text-pink-400 group-hover:text-white transition-colors"></i>
                <span>哔哩哔哩</span>
              </a>
              <a href="https://xhslink.com/m/8u0JGkC5KUE" target="_blank" class="footer-link-pill w-fit group">
                <i class="ph-fill ph-book-bookmark text-red-400 group-hover:text-white transition-colors"></i>
                <span>小红书</span>
              </a>
            </div>
          </div>

          <!-- 主要站点 -->
          <div class="flex flex-col gap-4">
            <span class="text-[10px] uppercase tracking-[0.2em] font-bold select-none" style="color: var(--text-secondary); opacity: 0.6">
              主要站点
            </span>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-x-4 gap-y-2">
              <a href="https://tts.haruyuki.cn" target="_blank" class="footer-link-pill w-fit group">
                <i class="ph-fill ph-microphone text-blue-400 group-hover:text-white transition-colors"></i>
                AI语音合成
              </a>
              <a href="https://rvc.haruyuki.cn" target="_blank" class="footer-link-pill w-fit group">
                <i class="ph-fill ph-waveform text-cyan-400 group-hover:text-white transition-colors"></i>
                AI声线转换
              </a>
              <a href="https://haruhifanclub.notion.site/anitabi" target="_blank" class="footer-link-pill w-fit group">
                <i class="ph-fill ph-camera text-yellow-400 group-hover:text-white transition-colors"></i>
                圣地巡礼照片墙
              </a>
              <a href="https://haruyuki.cn/library" target="_blank" class="footer-link-pill w-fit group">
                <i class="ph-fill ph-books text-emerald-400 group-hover:text-white transition-colors"></i>
                长门有希的书架
              </a>
            </div>
          </div>

          <!-- 加入我们 -->
          <div class="flex flex-col gap-4">
            <span class="text-[10px] uppercase tracking-[0.2em] font-bold select-none" style="color: var(--text-secondary); opacity: 0.6">
              加入我们
            </span>
            <div class="flex flex-wrap gap-2">
              <a href="https://qm.qq.com/q/CVssyL3Pj2" target="_blank" class="footer-link-pill group">
                <i class="ph-fill ph-users text-green-400 group-hover:text-white transition-colors"></i>
                超能力者群
              </a>
              <a href="https://qm.qq.com/q/JcS7yXYoU2" target="_blank" class="footer-link-pill group">
                <i class="ph-fill ph-planet text-purple-400 group-hover:text-white transition-colors"></i>
                异世界人群
              </a>
              <a href="https://qm.qq.com/q/8nYNs7rFwA" target="_blank" class="footer-link-pill group">
                <i class="ph-fill ph-rocket text-orange-400 group-hover:text-white transition-colors"></i>
                宇宙人群
              </a>
            </div>
          </div>
        </div>
      </div>

      <!-- 下半部分：版权 & 说明 -->
      <div class="flex flex-col items-center justify-between gap-4 border-t py-8 text-[10px] sm:flex-row" style="border-color: var(--border-glass); color: var(--text-secondary)">
        <div class="text-center sm:text-left font-mono opacity-60 hover:opacity-100 transition-opacity">
          © 2025 凉宫春日应援团 · Non-profit fan project
        </div>
        <div class="text-center sm:text-right opacity-60 hover:opacity-100 transition-opacity">
          本项目与原作/版权方无关，仅供学习交流与粉丝互动使用
        </div>
      </div>
    </div>

    <!-- 回到顶部按钮 -->
    <button 
      @click="scrollToTop"
      class="group absolute -top-5 left-1/2 flex h-10 w-10 -translate-x-1/2 items-center justify-center rounded-full border shadow-lg hover:-translate-y-1 transition-all duration-300"
      style="background: var(--bg-glass); border-color: var(--border-glass); color: var(--text-accent)"
      aria-label="回到顶部"
    >
      <i class="ph-bold ph-arrow-up group-hover:scale-110 transition-transform"></i>
    </button>
  </footer>
</template>

<script setup>
const scrollToTop = () => {
  const scrollContainer = document.querySelector('.overflow-y-auto');
  if (scrollContainer) {
    scrollContainer.scrollTo({ top: 0, behavior: 'smooth' });
  } else if (typeof window !== 'undefined') {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }
};
</script>