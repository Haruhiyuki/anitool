// config.js

// ✅ 不再写死 127.0.0.1，统一使用相对路径，让 Vite 代理 / 反向代理去转发
export const API_BASE_URL = "";  // 留空字符串即可

// 接口端点（直接就是相对路径）
export const ENDPOINTS = {
  MATCH: "/search/match", // 匹配模式
  REPLY: "/search/reply", // 对答模式
};

// 图片基础路径：也是相对路径，交给 Vite 代理 + 后端静态服务
export const IMAGE_BASE_URL = "";
