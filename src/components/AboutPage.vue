<template>
  <div class="w-full max-w-3xl glass-panel rounded-3xl p-8 md:p-12 shadow-2xl border-t border-white/10 relative overflow-hidden animate-fade-in" style="z-index: 50;">
    <div class="absolute -top-20 -right-20 w-64 h-64 bg-purple-500/20 rounded-full blur-3xl pointer-events-none"></div>
    <div class="absolute -bottom-20 -left-20 w-64 h-64 bg-indigo-500/20 rounded-full blur-3xl pointer-events-none"></div>

    <div class="mb-8 flex items-center">
        <button @click="$emit('go-back')" class="group flex items-center gap-2 hover:text-white transition-colors" style="color: var(--text-accent)">
            <i class="ph-bold ph-arrow-left text-xl group-hover:-translate-x-1 transition-transform"></i>
            <span class="font-bold">返回搜索</span>
        </button>
    </div>

    <div class="flex flex-col md:flex-row gap-8 items-center md:items-start z-10 relative">
        <div class="relative shrink-0 group cursor-default">
            <div class="w-32 h-32 rounded-full p-1 bg-gradient-to-br from-purple-400 to-indigo-400 shadow-lg group-hover:scale-105 transition-transform duration-300">
                <img src="https://youke1.picui.cn/s1/2025/11/28/6929314de21cc.jpg" alt="Avatar" class="w-full h-full rounded-full object-cover border-4 border-slate-900 bg-slate-900">
            </div>
            <div class="absolute bottom-1 right-1 bg-green-500 w-6 h-6 rounded-full border-4 border-slate-900 shadow-sm" title="Online"></div>
        </div>

        <div class="flex-1 text-center md:text-left">
            <h2 class="text-3xl font-bold mb-2 tracking-tight" style="color: var(--text-primary)">Everyday <span class="text-sm font-normal px-2 py-0.5 rounded-full ml-2 align-middle border" style="background: var(--bg-glass-hover); border-color: var(--border-glass); color: var(--text-accent)">这是一个彩蛋</span></h2>
            
            <div class="space-y-4 leading-relaxed text-sm md:text-base mt-6" style="color: var(--text-secondary)">
                <p>
                    👋 嗨！这是一个彩蛋！
                </p>
                <p>
                    本来春日酱说弄一个关于页吧，弄好后又不知道写什么，所以干脆就在这里瞎写瞎玩好了（没错就是这么随意）。
                </p>
                <p>
                    如果你对这个笨蛋小网页有什么建议或者意见，欢迎随时通过QQ联系我哦，谢谢你看到这里~ QQ：1633513223
                </p>
            </div>
        </div>
    </div>
  </div>
</template>

<script setup>
defineEmits(['go-back']);
</script>