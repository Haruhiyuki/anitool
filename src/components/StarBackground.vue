<template>
  <div class="fixed inset-0 z-0 overflow-hidden pointer-events-none bg-slate-900">
      
      <!-- 1. 凉宫春日背景 (Scope 1) -->
      <div class="absolute inset-0 bg-transition" :class="scope === 1 ? 'opacity-100 z-10' : 'opacity-0 z-0'">
          <div class="absolute inset-0 bg-gradient-to-b from-slate-900 via-purple-950 to-slate-950"></div>
          <div v-for="star in stars" :key="'s'+star.id" class="star" 
              :style="{ top: star.top, left: star.left, width: star.size, height: star.size, '--duration': star.duration, '--delay': star.delay, boxShadow: '0 0 ' + star.glow + 'px ' + star.color }">
          </div>
          <div v-for="meteor in meteors" :key="'m'+meteor.id" class="shooting-star" :style="{ top: meteor.top, right: meteor.right, '--duration': meteor.duration, width: '100px' }"></div>
      </div>

      <!-- 2. 京阿尼背景 (Scope 2 - 升级版) -->
      <div class="absolute inset-0 bg-transition" :class="scope === 2 ? 'opacity-100 z-10' : 'opacity-0 z-0'">
          
          <!-- 背景色: 左上角深橙色 -> 右下角深天蓝 -->
          <div class="absolute inset-0 bg-gradient-to-br from-orange-500 via-orange-100 to-sky-600"></div>

          <!-- 自然光效 (God Rays) -->
          <div class="absolute top-0 left-0 w-full h-full pointer-events-none overflow-hidden">
              <div class="absolute -top-[20%] -left-[10%] w-[60%] h-[150%] bg-gradient-to-b from-white/40 to-transparent transform -rotate-[35deg] origin-top animate-[beam-sway_8s_ease-in-out_infinite] blur-3xl"></div>
              <div class="absolute -top-[20%] left-[10%] w-[30%] h-[150%] bg-gradient-to-b from-white/30 to-transparent transform -rotate-[30deg] origin-top animate-[beam-sway_12s_ease-in-out_infinite_reverse] blur-2xl"></div>
              <!-- 顶部橙色光晕 -->
              <div class="absolute top-0 left-0 w-[800px] h-[800px] bg-orange-400/40 rounded-full blur-[120px] pointer-events-none"></div>
          </div>

          <!-- 装饰层：左上角柠檬与叶片 -->
          <div class="absolute top-0 left-0">
              <div class="absolute top-[-20px] left-[-20px] w-64 h-64 opacity-80 animate-[float-medium_12s_ease-in-out_infinite]">
                   <svg viewBox="0 0 100 100" fill="none" class="drop-shadow-lg" transform="rotate(30)">
                       <path d="M50 90 Q10 70 10 30 Q10 10 50 5 Q90 10 90 30 Q90 70 50 90 Z" fill="#86efac" />
                       <path d="M50 5 L50 90" stroke="#16a34a" stroke-width="1.5" opacity="0.4" />
                       <path d="M50 25 L80 15 M50 45 L80 35 M50 65 L80 55" stroke="#16a34a" stroke-width="1" opacity="0.3" fill="none"/>
                       <path d="M50 25 L20 15 M50 45 L20 35 M50 65 L20 55" stroke="#16a34a" stroke-width="1" opacity="0.3" fill="none"/>
                   </svg>
              </div>
              <div class="absolute top-8 left-8 w-72 h-72 animate-[float-slow_9s_ease-in-out_infinite]">
                   <svg viewBox="0 0 200 200" fill="none" xmlns="http://www.w3.org/2000/svg" class="drop-shadow-2xl">
                      <circle cx="100" cy="100" r="90" fill="#facc15" /> 
                      <circle cx="100" cy="100" r="84" fill="#fefce8" /> 
                      <circle cx="100" cy="100" r="80" fill="#fef08a" /> 
                      <g fill="#fbbf24" stroke="#fefce8" stroke-width="3">
                          <path d="M100 100 L100 25 A75 75 0 0 1 165 62 Z" />
                          <path d="M100 100 L165 62 A75 75 0 0 1 175 100 A75 75 0 0 1 165 138 Z" />
                          <path d="M100 100 L165 138 A75 75 0 0 1 100 175 Z" />
                          <path d="M100 100 L100 175 A75 75 0 0 1 35 138 Z" />
                          <path d="M100 100 L35 138 A75 75 0 0 1 25 100 A75 75 0 0 1 35 62 Z" />
                          <path d="M100 100 L35 62 A75 75 0 0 1 100 25 Z" />
                      </g>
                      <circle cx="125" cy="75" r="4" fill="#ffffff" opacity="0.6"/>
                      <circle cx="75" cy="125" r="2" fill="#ffffff" opacity="0.4"/>
                  </svg>
              </div>
          </div>

          <!-- 右下角：夏日特饮杯 -->
          <div class="absolute -bottom-10 -right-10 w-[400px] h-[500px] animate-[float-slow_12s_ease-in-out_infinite_reverse]">
              <svg viewBox="0 0 200 300" fill="none" class="drop-shadow-2xl">
                  <path d="M120 280 L180 20" stroke="#f43f5e" stroke-width="12" stroke-linecap="round" opacity="0.9"/>
                  <path d="M120 280 L180 20" stroke="#fce7f3" stroke-width="3" stroke-dasharray="12 12" opacity="0.8"/>
                  <path d="M40 20 L60 260 Q65 290 100 290 L140 290 Q175 290 180 260 L200 20" fill="rgba(255,255,255,0.1)" stroke="rgba(255,255,255,0.8)" stroke-width="3"/>
                  <defs>
                      <linearGradient id="drinkGradient" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="0%" stop-color="#fbbf24" stop-opacity="0.8"/> <!-- 琥珀黄 -->
                          <stop offset="100%" stop-color="#ea580c" stop-opacity="0.95"/> <!-- 烈日橙 -->
                      </linearGradient>
                  </defs>
                  <path d="M48 60 L62 258 Q66 280 100 280 L140 280 Q174 280 178 258 L192 60 Q120 70 48 60 Z" fill="url(#drinkGradient)" />
                  <rect x="80" y="100" width="40" height="40" rx="5" fill="white" fill-opacity="0.4" transform="rotate(15 100 120)" stroke="white" stroke-width="1.5"/>
                  <rect x="110" y="160" width="35" height="35" rx="5" fill="white" fill-opacity="0.4" transform="rotate(-10 127 177)" stroke="white" stroke-width="1.5"/>
                   <circle cx="55" cy="120" r="3" fill="white" opacity="0.7"/>
                   <circle cx="180" cy="180" r="4" fill="white" opacity="0.6"/>
              </svg>
          </div>

          <!-- 气泡层 -->
          <div v-for="bubble in bubbles" :key="'b'+bubble.id" class="bubble"
              :style="{ left: bubble.left + '%', width: bubble.size + 'px', height: bubble.size + 'px', '--duration': bubble.duration + 's', '--end-height': bubble.endHeight + '%' }">
          </div>
          
          <!-- 视差海浪 -->
          <div class="waves-container">
              <svg class="w-full h-full" viewBox="0 24 150 28" preserveAspectRatio="none" shape-rendering="auto">
                  <defs>
                      <path id="gentle-wave" d="M-160 44c30 0 58-18 88-18s 58 18 88 18 58-18 88-18 58 18 88 18 v44h-352z" />
                  </defs>
                  <g class="parallax">
                      <use xlink:href="#gentle-wave" x="48" y="0" fill="rgba(224, 242, 254, 0.7)" />
                      <use xlink:href="#gentle-wave" x="48" y="3" fill="rgba(186, 230, 253, 0.5)" />
                      <use xlink:href="#gentle-wave" x="48" y="5" fill="rgba(125, 211, 252, 0.3)" />
                      <use xlink:href="#gentle-wave" x="48" y="7" fill="rgba(56, 189, 248, 0.2)" />
                  </g>
              </svg>
          </div>

      </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue';

const props = defineProps({
  scope: Number
});

const stars = ref([]);
const meteors = ref([]);
let meteorTimeout = null;
const bubbles = ref([]);
let bubbleInterval = null;

const initStars = () => {
  const newStars = [];
  for (let i = 0; i < 80; i++) {
      newStars.push({
          id: i,
          top: Math.random() * 100 + '%',
          left: Math.random() * 100 + '%',
          size: Math.random() * 3 + 'px',
          duration: (Math.random() * 3 + 2) + 's',
          delay: Math.random() * 5 + 's',
          glow: Math.random() * 5,
          color: Math.random() > 0.8 ? '#e9d5ff' : '#ffffff'
      });
  }
  stars.value = newStars;
};

const spawnMeteor = () => {
  if (props.scope !== 1) {
      meteorTimeout = setTimeout(spawnMeteor, 2000);
      return;
  }
  const id = Date.now();
  const durationVal = Math.random() * 1.5 + 1.5;
  
  meteors.value.push({
      id,
      top: Math.random() * 60 - 10 + '%',
      right: Math.random() * 80 - 10 + '%',
      duration: durationVal + 's'
  });

  setTimeout(() => {
      meteors.value = meteors.value.filter(m => m.id !== id);
  }, durationVal * 1000 + 100);

  meteorTimeout = setTimeout(spawnMeteor, Math.random() * 4000 + 1000);
};

const spawnBubble = () => {
  if (props.scope !== 2) return;

  const id = Date.now();
  const size = Math.random() * 25 + 8;
  const duration = Math.random() * 6 + 4;
  const endHeight = Math.random() * 50 + 40;
  
  bubbles.value.push({
      id,
      left: Math.random() * 100,
      size,
      duration,
      endHeight
  });

  setTimeout(() => {
      bubbles.value = bubbles.value.filter(b => b.id !== id);
  }, duration * 1000 + 100);
};

watch(() => props.scope, (newVal) => {
  if (newVal === 2) {
      if (!bubbleInterval) {
          for(let i=0; i<5; i++) spawnBubble();
          bubbleInterval = setInterval(spawnBubble, 600);
      }
  } else {
      if (bubbleInterval) {
          clearInterval(bubbleInterval);
          bubbleInterval = null;
      }
      bubbles.value = [];
  }
}, { immediate: true });

onMounted(() => {
  initStars();
  spawnMeteor();
});

onUnmounted(() => {
  if (meteorTimeout) clearTimeout(meteorTimeout);
  if (bubbleInterval) clearInterval(bubbleInterval);
});
</script>

<style scoped>
.star { position: absolute; background: white; border-radius: 50%; animation: twinkle var(--duration) ease-in-out infinite; animation-delay: var(--delay); }
.shooting-star { position: absolute; height: 2px; background: linear-gradient(90deg, rgba(255,255,255,1), transparent); animation: shoot var(--duration) linear forwards; pointer-events: none; }
.bubble {
  position: absolute; border-radius: 50%;
  background: radial-gradient(circle at 35% 35%, rgba(255, 255, 255, 0.8), rgba(255, 255, 255, 0.2) 40%, rgba(255, 255, 255, 0) 80%);
  border: 1px solid rgba(255,255,255,0.4);
  box-shadow: 0 0 8px rgba(255,255,255,0.3);
  animation: natural-rise var(--duration) linear forwards; pointer-events: none; backdrop-filter: blur(1px);
}
.waves-container { position: absolute; bottom: 0; width: 100%; height: 15vh; min-height: 80px; max-height: 150px; pointer-events: none; z-index: 5; }
.parallax > use { animation: move-forever 25s cubic-bezier(.55,.5,.45,.5) infinite; }
.parallax > use:nth-child(1) { animation-delay: -2s; animation-duration: 7s; }
.parallax > use:nth-child(2) { animation-delay: -3s; animation-duration: 10s; }
.parallax > use:nth-child(3) { animation-delay: -4s; animation-duration: 13s; }
.parallax > use:nth-child(4) { animation-delay: -5s; animation-duration: 20s; }
</style>