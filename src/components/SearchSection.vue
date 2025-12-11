<template>
  <div class="w-full max-w-3xl glass-panel rounded-3xl transition-all duration-300 flex flex-col overflow-hidden group shadow-lg">
    
    <!-- 输入区 -->
    <div class="w-full p-2">
      <textarea 
        :value="modelValue"
        @input="$emit('update:modelValue', $event.target.value)"
        @keydown.enter.prevent="$emit('search')"
        rows="2"
        :placeholder="placeholderText" 
        class="w-full bg-transparent border-none outline-none text-xl px-6 py-4 resize-none font-medium transition-colors"
        style="color: var(--text-primary); caret-color: var(--text-accent);"
      ></textarea>
    </div>

    <!-- 底部工具栏 -->
    <div class="w-full px-6 py-3 border-t flex flex-col md:flex-row items-center justify-between gap-4 transition-colors"
         style="background-color: var(--bg-glass-hover); border-color: var(--border-glass)">
      
      <div class="flex flex-wrap items-center gap-3 w-full md:w-auto justify-center md:justify-start">
        
        <!-- 1. 模式切换 -->
        <div class="rounded-full p-1 flex border shrink-0" style="background-color: var(--input-bg); border-color: var(--border-glass)">
          <button 
            @click="$emit('update:mode', 1)" 
            class="px-4 py-2 rounded-full text-xs sm:text-sm font-bold transition-all duration-300 flex items-center gap-2 whitespace-nowrap" 
            :class="mode === 1 ? 'text-white shadow-md' : 'hover:bg-black/5'"
            :style="mode === 1 ? { background: 'var(--text-accent)' } : { color: 'var(--text-secondary)' }"
          >
            <i class="ph-bold ph-magnifying-glass"></i> <span>匹配</span>
          </button>
          <button 
            @click="$emit('update:mode', 2)" 
            class="px-4 py-2 rounded-full text-xs sm:text-sm font-bold transition-all duration-300 flex items-center gap-2 whitespace-nowrap" 
            :class="mode === 2 ? 'text-white shadow-md' : 'hover:bg-black/5'"
            :style="mode === 2 ? { background: 'var(--text-accent)', filter: 'brightness(0.9)' } : { color: 'var(--text-secondary)' }"
          >
            <i class="ph-bold ph-magic-wand"></i> <span>对答</span>
          </button>
        </div>

        <!-- 2. 范围切换 -->
        <div class="rounded-full p-1 flex border shrink-0" style="background-color: var(--input-bg); border-color: var(--border-glass)">
          <button 
            @click="$emit('update:scope', 1)" 
            class="px-3 py-2 rounded-full text-xs sm:text-sm font-bold transition-all duration-300 flex items-center gap-2 whitespace-nowrap" 
            :class="scope === 1 ? 'text-white shadow-md' : 'hover:bg-black/5'"
            :style="scope === 1 ? { background: '#9333ea' } : { color: 'var(--text-secondary)' }"
          >
            <i class="ph-bold ph-star"></i> <span>凉宫春日</span>
          </button>
          <button 
            @click="$emit('update:scope', 2)" 
            class="px-3 py-2 rounded-full text-xs sm:text-sm font-bold transition-all duration-300 flex items-center gap-2 whitespace-nowrap" 
            :class="scope === 2 ? 'text-white shadow-md' : 'hover:bg-black/5'"
            :style="scope === 2 ? { background: '#0ea5e9' } : { color: 'var(--text-secondary)' }"
          >
            <i class="ph-bold ph-buildings"></i> <span>全京阿尼</span>
          </button>
        </div>

        <!-- 3. 数量选择 -->
        <div class="rounded-full p-1 flex items-center border shrink-0 select-none" style="background-color: var(--input-bg); border-color: var(--border-glass)">
          <button 
            @click="updateK(-1)"
            class="w-8 h-8 flex items-center justify-center rounded-full hover:bg-black/5 transition-colors disabled:opacity-30"
            :disabled="topK <= 1"
            style="color: var(--text-secondary)"
          >
            <i class="ph-bold ph-minus"></i>
          </button>
          
          <div class="flex items-center justify-center px-1 cursor-text" @click="$refs.kInput.focus()">
            <input 
              ref="kInput"
              type="number"
              :value="topK"
              @change="handleInputK"
              class="w-6 bg-transparent text-center font-bold outline-none font-mono appearance-none m-0 p-0 no-spinners"
              min="1"
              max="10"
              style="color: var(--text-primary)"
            />
          </div>

          <button 
            @click="updateK(1)"
            class="w-8 h-8 flex items-center justify-center rounded-full hover:bg-black/5 transition-colors disabled:opacity-30"
            :disabled="topK >= 10"
            style="color: var(--text-secondary)"
          >
            <i class="ph-bold ph-plus"></i>
          </button>
        </div>
      </div>

      <!-- 搜索按钮 -->
      <button 
        @click="$emit('search')" 
        :disabled="isLoading || !modelValue" 
        class="h-11 w-full md:w-auto px-6 rounded-full text-white font-bold shadow-lg transition-all duration-200 flex items-center justify-center gap-2 active:scale-95 group-focus-within:animate-pulse shrink-0 whitespace-nowrap"
        style="background: var(--btn-gradient);"
      >
        <i v-if="isLoading" class="ph ph-spinner animate-spin text-xl"></i>
        <i v-else class="ph-bold ph-paper-plane-right text-xl"></i>
        <span class="text-sm" v-if="!isLoading">开始探索</span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue';

const props = defineProps({
  modelValue: String,
  mode: Number,
  topK: {
    type: Number,
    default: 3
  },
  scope: {
    type: Number,
    default: 1
  },
  isLoading: Boolean
});

const emit = defineEmits(['update:modelValue', 'update:mode', 'update:topK', 'update:scope', 'search']);

const placeholderText = computed(() => {
  const scopeText = props.scope === 1 ? "凉宫春日系列" : "京阿尼主要作品";
  return props.mode === 1 
      ? `输入文本，在${scopeText}中寻找语义接近的台词...` 
      : `输入前文，在${scopeText}中寻找后文...`;
});

const updateK = (delta) => {
  let newValue = props.topK + delta;
  if (newValue < 1) newValue = 1;
  if (newValue > 10) newValue = 10;
  emit('update:topK', newValue);
};

const handleInputK = (event) => {
  let val = parseInt(event.target.value);
  if (isNaN(val)) val = 1;
  if (val < 1) val = 1;
  if (val > 10) val = 10;
  event.target.value = val;
  emit('update:topK', val);
};
</script>