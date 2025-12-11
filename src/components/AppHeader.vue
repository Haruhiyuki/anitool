<template>
  <header class="w-full px-4 sm:px-8 py-4 sm:py-6 flex justify-between items-center z-50 sticky top-0 glass-panel border-b-0 border-b-white/5 shadow-sm transition-all duration-500">
    
    <!-- Left: Logo -->
    <div class="flex items-center gap-2 sm:gap-3 cursor-pointer group shrink-0 z-10" @click="$emit('navigate', 'home')">
      <i class="ph-fill ph-film-strip text-2xl sm:text-3xl transition-colors" style="color: var(--text-accent)"></i>
      <!-- 移动端隐藏文字，防止与中间导航栏重叠 -->
      <span class="text-xl font-bold tracking-wide drop-shadow-sm transition-colors hidden sm:block" style="color: var(--text-primary)">Animetool</span>
    </div>
    
    <!-- Center: Navigation (全端常驻显示) -->
    <nav class="flex items-center gap-1 bg-black/5 p-1 rounded-full border border-white/5 absolute left-1/2 -translate-x-1/2 shadow-sm backdrop-blur-md z-0 sm:z-auto">
        <button 
            @click="$emit('navigate', 'home')"
            class="px-4 sm:px-5 py-1.5 rounded-full text-xs sm:text-sm font-bold transition-all duration-300 flex items-center gap-1.5 sm:gap-2 whitespace-nowrap"
            :class="currentView === 'home' ? 'bg-white/10 text-white shadow-sm border border-white/10' : 'text-slate-400 hover:text-slate-200 hover:bg-white/5'"
        >
            <i class="ph-bold ph-chat-text text-base sm:text-lg"></i>
            <span>台词匹配</span>
        </button>
        <button 
            @click="$emit('navigate', 'scene')"
            class="px-4 sm:px-5 py-1.5 rounded-full text-xs sm:text-sm font-bold transition-all duration-300 flex items-center gap-1.5 sm:gap-2 whitespace-nowrap"
            :class="currentView === 'scene' ? 'bg-white/10 text-white shadow-sm border border-white/10' : 'text-slate-400 hover:text-slate-200 hover:bg-white/5'"
        >
            <i class="ph-bold ph-image text-base sm:text-lg"></i>
            <span>画面搜索</span>
        </button>
    </nav>
    
    <!-- Right: Menu -->
    <div class="relative shrink-0 z-10" ref="menuRef">
      <button 
        @click="toggleMenu"
        class="w-9 h-9 sm:w-10 sm:h-10 rounded-full hover:bg-black/5 transition flex items-center justify-center border border-transparent active:scale-95"
        style="color: var(--text-secondary)"
      >
        <i class="ph ph-gear text-lg sm:text-xl transition-transform duration-300" :class="{ 'rotate-90': isMenuOpen }"></i>
      </button>

      <transition
        enter-active-class="transition ease-out duration-200"
        enter-from-class="opacity-0 translate-y-2 scale-95"
        enter-to-class="opacity-100 translate-y-0 scale-100"
        leave-active-class="transition ease-in duration-150"
        leave-from-class="opacity-100 translate-y-0 scale-100"
        leave-to-class="opacity-0 translate-y-2 scale-95"
      >
        <div v-if="isMenuOpen" class="absolute right-0 top-12 w-48 glass-panel rounded-xl shadow-2xl overflow-hidden py-1 z-50 origin-top-right border border-white/5">
            <button @click="handleAction('about')" class="w-full px-4 py-3 text-left text-sm hover:bg-black/5 flex items-center gap-3 transition-colors group" style="color: var(--text-primary)">
                <i class="ph ph-info text-lg group-hover:opacity-80" style="color: var(--text-accent)"></i>
                关于我们
            </button>
            
            <div class="w-full px-4 py-2 text-left text-xs cursor-default flex justify-between items-center" style="color: var(--text-secondary)">
                <span>Version</span>
                <span class="font-mono">1.3.1</span>
            </div>
        </div>
      </transition>
    </div>
  </header>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';

// 接收 currentView 以显示当前激活状态
defineProps({
    currentView: {
        type: String,
        default: 'home'
    }
});

const emit = defineEmits(['navigate']);
const isMenuOpen = ref(false);
const menuRef = ref(null);

const toggleMenu = () => {
    isMenuOpen.value = !isMenuOpen.value;
};

const handleAction = (action) => {
    isMenuOpen.value = false;
    emit('navigate', action);
};

const handleClickOutside = (event) => {
    if (menuRef.value && !menuRef.value.contains(event.target)) {
        isMenuOpen.value = false;
    }
};

onMounted(() => document.addEventListener('click', handleClickOutside));
onUnmounted(() => document.removeEventListener('click', handleClickOutside));
</script>