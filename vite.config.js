import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    host: '0.0.0.0',
    port: 5173,
    allowedHosts: ['anitool.haruyuki.cn'],
    // 开发环境代理配置
    proxy: {
      // 代理 API 请求
      '/search': {
        target: 'http://127.0.0.1:11325',
        changeOrigin: true,
      },
      '/scene': {
        target: 'http://127.0.0.1:11325',
        changeOrigin: true,
      },
      // 代理图片资源
      '/images': {
        target: 'http://127.0.0.1:11325',
        changeOrigin: true,
      },
    }
  },
  build: {
    // 打包输出目录，建议直接放在项目根目录的 dist
    outDir: 'dist',
    assetsDir: 'assets', // 静态资源子目录
    emptyOutDir: true,
  }
})