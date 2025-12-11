#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Unified Qwen Backend with Vite Integration
功能: 
1. 台词检索 (Text Search) - 匹配模式 & 对答模式 (支持多 Scope)
2. 画面检索 (Scene Search) - 小说场景提取 & 文本搜图
3. 静态资源托管 - 托管 Vite 打包后的 dist 目录及图片资源

【目录结构说明 (推荐)】
backend/
  ├── data/
  │   ├── indexes/
  │   │   ├── scope1/  (凉宫索引: match.index, ...)
  │   │   ├── scope2/  (京阿尼索引: match.index, ...)
  │   │   └── scene/   (画面索引: images.index, ...)
  │   └── images/      (图片根目录: IMAGE_ROOT)
  │       ├── haruhi/
  │       ├── kyoani/
  │       └── illustrations/
"""

from __future__ import annotations
import os
import json
import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
import datetime
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

import numpy as np
import faiss
from openai import OpenAI

from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import requests

# ===================== 配置 =====================

@dataclass
class AppConfig:
    # 1. API 配置
    api_key: str = os.getenv("DASHSCOPE_API_KEY", "")
    base_url: str = os.getenv("DASHSCOPE_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
    
    # 2. 索引路径配置 (优先读取环境变量，否则使用默认值)
    # Scope 1: 凉宫春日
    index_dir_scope1: Path = Path(os.getenv("INDEX_DIR_SCOPE_1", "./data/indexes/scope1"))
    # Scope 2: 京阿尼全家桶
    index_dir_scope2: Path = Path(os.getenv("INDEX_DIR_SCOPE_2", "./data/indexes/scope2"))
    # Scene: 画面检索
    index_dir_scene: Path = Path(os.getenv("INDEX_DIR_SCENE", "./data/indexes/scene"))
    
    # 3. 静态资源配置
    # 图片根目录：所有图片(台词截图、插画)都应该放在这个目录下或其子目录中
    # 对应 URL 前缀: /images/
    image_root: Path = Path(os.getenv("IMAGE_ROOT", "./data/images"))

# ===================== 日志模块 =====================

class UsageLogger:
    def __init__(self, log_dir: Optional[Path] = None):
        if log_dir is None:
            log_dir = Path(os.getenv("USAGE_LOG_DIR", "./usage_logs"))
        self.log_dir = log_dir
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.match_log_path = self.log_dir / "match_log.jsonl"
        self.reply_log_path = self.log_dir / "reply_log.jsonl"
        self.scene_log_path = self.log_dir / "scene_log.jsonl"
        self._lock = threading.Lock()

    def _append(self, path: Path, record: Dict[str, Any]) -> None:
        line = json.dumps(record, ensure_ascii=False)
        with self._lock:
            with path.open("a", encoding="utf-8") as f:
                f.write(line + "\n")

    def log_match(self, **kwargs): self._append(self.match_log_path, {"ts": datetime.datetime.utcnow().isoformat() + "Z", "type": "match", **kwargs})
    def log_reply(self, **kwargs): self._append(self.reply_log_path, {"ts": datetime.datetime.utcnow().isoformat() + "Z", "type": "reply", **kwargs})
    def log_scene(self, **kwargs): self._append(self.scene_log_path, {"ts": datetime.datetime.utcnow().isoformat() + "Z", "type": "scene", **kwargs})

# ===================== Qwen Embedding =====================

class QwenEmbedder:
    def __init__(self, api_key: str, base_url: str):
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = os.getenv("EMBEDDING_MODEL", "text-embedding-v4")
        self.dimensions = int(os.getenv("EMBEDDING_DIM", "1024"))
        self.batch_size = 10
        self.parallelism = 4

    def _embed_raw(self, texts: List[str]) -> np.ndarray:
        if not texts: return np.zeros((0, self.dimensions), dtype="float32")
        try:
            resp = self.client.embeddings.create(model=self.model, input=texts, dimensions=self.dimensions)
            embeddings = [item.embedding for item in resp.data]
            return np.asarray(embeddings, dtype="float32")
        except Exception as e:
            print(f"[Error] Embed failed: {e}")
            raise e

    def encode_queries(self, texts: List[str]) -> np.ndarray:
        return self._embed_batched(texts)

    def _embed_batched(self, texts: List[str]) -> np.ndarray:
        if not texts: return np.zeros((0, self.dimensions), dtype="float32")
        batches = [(i, texts[i: i + self.batch_size]) for i in range(0, len(texts), self.batch_size)]
        
        results = [None] * len(batches)
        def worker(idx, chunk): return idx, self._embed_raw(chunk)

        with ThreadPoolExecutor(max_workers=self.parallelism) as ex:
            futures = [ex.submit(worker, b[0], b[1]) for b in batches]
            for fut in as_completed(futures):
                idx, arr = fut.result()
                results[idx // self.batch_size] = arr 
        
        return np.vstack([r for r in results if r is not None])

# ===================== Qwen Rerank =====================

class QwenReranker:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.model = os.getenv("RERANK_MODEL", "qwen3-rerank")
        self.base_url = os.getenv("RERANK_BASE_URL", "https://dashscope.aliyuncs.com/api/v1/services/rerank/text-rerank/text-rerank")

    def rerank(self, query: str, documents: List[str], top_n: int = 10) -> List[Tuple[int, float]]:
        if not documents: return []
        payload = {
            "model": self.model,
            "input": {"query": query, "documents": documents},
            "parameters": {"return_documents": False, "top_n": top_n}
        }
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        try:
            resp = requests.post(self.base_url, headers=headers, json=payload, timeout=15)
            if resp.status_code != 200:
                print(f"[w] Rerank error {resp.status_code}: {resp.text}")
                return []
            data = resp.json()
            results = data.get("output", {}).get("results", [])
            return [(item["index"], item["relevance_score"]) for item in results]
        except Exception as e:
            print(f"[w] Rerank failed: {e}")
            return []

# ===================== Qwen Chat (LLM for Scene Extraction) =====================

class QwenChat:
    def __init__(self, api_key: str, base_url: str):
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = "qwen-plus" 

    def extract_scenes(self, article_text: str) -> List[str]:
        system_prompt = """
        你是一个专业的文学编辑，你的任务是从给定的的小说或文章中，提取出最具有画面感、最适合用图片来表现的句子或段落。
        你要遵循以下规则：
        1. 只选择那些包含具体动作、场景描写、人物外貌或强烈情绪氛围的片段。
        2. 忽略那些纯粹的对话、心理活动或抽象的论述。
        3. 每个提取的片段不宜过长，最好是一到三句话。
        4. 你的输出必须是一个严格的JSON格式的字符串列表。例如：["片段1", "片段2", "片段3"]
           - 不要加入任何解释或额外文字。
        """
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": "请处理以下文章：\n\n" + article_text},
                ],
                temperature=0.2,
            )
            content = completion.choices[0].message.content
            start = content.find('[')
            end = content.rfind(']') + 1
            if start != -1 and end != -1:
                json_str = content[start:end]
                return json.loads(json_str)
            return []
        except Exception as e:
            print(f"[Error] Scene extraction failed: {e}")
            return []

# ===================== 索引类 (FAISS Wrappers) =====================

class BaseIndex:
    def __init__(self, index_path: Path, meta_path: Path):
        self.index = faiss.read_index(str(index_path))
        self.meta = []
        with open(meta_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip(): 
                    try:
                        self.meta.append(json.loads(line))
                    except:
                        pass
        print(f"[i] Loaded index from {index_path}, size={self.index.ntotal}")

    def search(self, query_vec: np.ndarray, top_k: int) -> List[Dict[str, Any]]:
        faiss.normalize_L2(query_vec)
        scores, idxs = self.index.search(query_vec, top_k)
        results = []
        for score, i in zip(scores[0], idxs[0]):
            if i >= 0 and i < len(self.meta):
                item = dict(self.meta[i])
                item["score"] = float(score)
                results.append(item)
        return results

class ImageIndex(BaseIndex):
    """用于画面检索的索引"""
    pass

# ===================== FastAPI Models =====================

class SearchRequest(BaseModel):
    query: str
    top_k: int = 10
    scope: int = 1 # 1=Haruhi, 2=KyoAni

class SceneAnalyzeRequest(BaseModel):
    text: str

class SceneSearchRequest(BaseModel):
    query: str
    top_k: int = 20

# ===================== App Initialization =====================

app = FastAPI(title="Unified Anime Search Backend")

# Globals
_embedder: Optional[QwenEmbedder] = None
_reranker: Optional[QwenReranker] = None
_chat: Optional[QwenChat] = None
_usage_logger: Optional[UsageLogger] = None

# Indexes
_match_indexes: Dict[int, BaseIndex] = {}
_reply_indexes: Dict[int, BaseIndex] = {}
_image_index: Optional[ImageIndex] = None

def load_resources(cfg: AppConfig):
    global _embedder, _reranker, _chat, _usage_logger, _image_index
    
    _embedder = QwenEmbedder(cfg.api_key, cfg.base_url)
    _chat = QwenChat(cfg.api_key, cfg.base_url)
    _usage_logger = UsageLogger()
    
    try:
        _reranker = QwenReranker(cfg.api_key)
    except Exception as e:
        print(f"[w] Reranker init failed: {e}")

    # ============ 加载 Scope 1 & 2 索引 ============
    # 定义 Scope -> 路径的映射
    scope_paths = {
        1: cfg.index_dir_scope1,
        2: cfg.index_dir_scope2
    }
    
    for scope, path in scope_paths.items():
        if not path.exists():
            print(f"[w] Scope {scope} index dir not found: {path}")
            continue

        # 尝试加载 Match 索引
        if (path / "match.index").exists():
            try:
                _match_indexes[scope] = BaseIndex(path / "match.index", path / "match_meta.jsonl")
            except Exception as e:
                print(f"[!] Failed to load match index for scope {scope}: {e}")
        
        # 尝试加载 Reply 索引
        if (path / "reply_answer.index").exists():
            try:
                _reply_indexes[scope] = BaseIndex(path / "reply_answer.index", path / "reply_meta.jsonl")
            except Exception as e:
                print(f"[!] Failed to load reply index for scope {scope}: {e}")

    # ============ 加载 Scene 画面索引 ============
    if cfg.index_dir_scene.exists() and (cfg.index_dir_scene / "images.index").exists():
        try:
            _image_index = ImageIndex(cfg.index_dir_scene / "images.index", cfg.index_dir_scene / "images_meta.jsonl")
        except Exception as e:
            print(f"[!] Failed to load image index: {e}")
    else:
        print(f"[w] Scene index not found at {cfg.index_dir_scene}")

# ===================== API Endpoints & Vite Integration =====================

# 1. CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Startup Event
@app.on_event("startup")
def startup_event():
    cfg = AppConfig()
    if not cfg.api_key:
        print("[!] Warning: DASHSCOPE_API_KEY not found.")
    print(f"[i] IMAGE_ROOT: {cfg.image_root.resolve()}")
    load_resources(cfg)

# 3. Mount Image Resources
# 统一挂载：要求所有图片（scope1, scope2, scene）都在这个根目录下
# 如果物理文件夹分散，请使用软链接 (Symlinks) 链接到这个目录下
APP_CFG = AppConfig() # 实例化以获取路径
if APP_CFG.image_root.exists():
    app.mount("/images", StaticFiles(directory=str(APP_CFG.image_root)), name="images")
else:
    print(f"[!] Warning: Image root {APP_CFG.image_root} does not exist. Images will not display.")

# ===================== 路径处理辅助函数 =====================
def _resolve_web_path(local_path_str: str) -> str:
    """
    将数据库中的图片路径转换为 Web URL 路径 (/images/...)
    假设 IMAGE_ROOT 挂载在 /images
    """
    if not local_path_str: 
        return ""
    if local_path_str.startswith("http"): 
        return local_path_str
    
    # 移除可能存在的路径前缀干扰
    # 策略：如果路径包含 'dataset/images' 或 'my_images' 等已知前缀，尝试剥离
    # 最通用的方法：清洗掉 ./ 或 / 开头，直接拼接到 /images/
    
    clean_path = local_path_str.strip("/\\")
    
    # 特殊处理：如果数据库里存的是绝对路径，或者包含了 IMAGE_ROOT 的一部分，需要截断
    # 这里简单处理：假设数据库存的是相对于 IMAGE_ROOT 的路径
    # 例如：Scope1 存的是 "haruhi/ep01/01.jpg" -> "/images/haruhi/ep01/01.jpg"
    
    return f"/images/{clean_path}"

# 4. API Endpoints

# --- Match Search ---
@app.post("/search/match")
def search_match(req: SearchRequest, request: Request):
    if not _embedder: raise HTTPException(500, "Embedder not initialized")
    idx = _match_indexes.get(req.scope, _match_indexes.get(1))
    if not idx: return {"results": []}
    
    q_vec = _embedder.encode_queries([req.query])
    candidates = idx.search(q_vec, top_k=req.top_k * 5)
    results = _apply_rerank(req.query, candidates, "text", req.top_k)
    
    if _usage_logger:
        _usage_logger.log_match(query=req.query, scope=req.scope, ip=request.client.host, top_result=results[0] if results else None)
    return {"results": _format_subtitle_results(results)}

# --- Reply Search ---
@app.post("/search/reply")
def search_reply(req: SearchRequest, request: Request):
    if not _embedder: raise HTTPException(500, "Embedder not initialized")
    idx = _reply_indexes.get(req.scope, _reply_indexes.get(1))
    if not idx: return {"results": []}

    q_vec = _embedder.encode_queries([req.query])
    candidates = idx.search(q_vec, top_k=req.top_k * 5)
    results = _apply_rerank(req.query, candidates, "question_text", req.top_k)
    
    if _usage_logger:
        _usage_logger.log_reply(query=req.query, scope=req.scope, ip=request.client.host, top_result=results[0] if results else None)
    return {"results": _format_reply_results(results)}

# --- Scene Analyze ---
@app.post("/scene/analyze")
def scene_analyze(req: SceneAnalyzeRequest):
    if not _chat: raise HTTPException(500, "Chat model not initialized")
    scenes = _chat.extract_scenes(req.text)
    return {"scenes": scenes}

# --- Scene Search ---
@app.post("/scene/search")
def scene_search(req: SceneSearchRequest, request: Request):
    if not _image_index: raise HTTPException(500, "Image index not loaded")
    if not _embedder: raise HTTPException(500, "Embedder not initialized")
    
    q_vec = _embedder.encode_queries([req.query])
    candidates = _image_index.search(q_vec, top_k=req.top_k * 2)
    
    # 画面检索的 candidates 里，text 字段是图片的描述
    results = _apply_rerank(req.query, candidates, "text", req.top_k)
    
    formatted = []
    for r in results:
        # 画面检索的图片路径处理
        raw_path = r.get("image_path", "")
        formatted.append({
            "image": _resolve_web_path(raw_path),
            "text": r.get("text"), 
            "score": r.get("_rerank_score", r.get("score")),
            "raw_path": raw_path
        })

    if _usage_logger:
        _usage_logger.log_scene(query=req.query, ip=request.client.host, top_result=formatted[0] if formatted else None)
    return {"results": formatted}

# 5. Vite Static Files & SPA Fallback
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST_DIR = os.path.join(BASE_DIR, "dist")
ASSETS_DIR = os.path.join(DIST_DIR, "assets")

if os.path.exists(DIST_DIR):
    print(f"[i] Serving Vite app from {DIST_DIR}")
    if os.path.exists(ASSETS_DIR):
        app.mount("/assets", StaticFiles(directory=ASSETS_DIR), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        if full_path.startswith("search/") or full_path.startswith("scene/"):
            raise HTTPException(404, "API endpoint not found")
        file_path = os.path.join(DIST_DIR, full_path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        index_file = os.path.join(DIST_DIR, "index.html")
        return FileResponse(index_file)
else:
    print(f"[Warning] Dist directory not found at {DIST_DIR}. SPA serving disabled.")


# ===================== Helpers =====================

def _apply_rerank(query, candidates, text_field, top_k):
    if not candidates: return []
    if not _reranker: return candidates[:top_k]
    
    docs = [c.get(text_field, "") for c in candidates]
    ranked_indices = _reranker.rerank(query, docs, top_n=top_k)
    
    final_results = []
    if not ranked_indices:
        candidates.sort(key=lambda x: x.get("score", 0), reverse=True)
        return candidates[:top_k]

    for idx, score in ranked_indices:
        if idx < len(candidates):
            item = candidates[idx].copy()
            item["_rerank_score"] = score
            final_results.append(item)
    return final_results

def _format_subtitle_results(items):
    out = []
    for r in items:
        ep_num = r.get("episode_number") or r.get("episode_index")
        img_p = r.get("image_path", r.get("image", ""))
        
        out.append({
            "text": r.get("text"),
            "work_name": r.get("work_name"),
            "episode_index": ep_num,
            "episode_title": r.get("episode_title"),
            "time_s": r.get("time_s"),
            "image_path": _resolve_web_path(img_p),
            "coarse_score": (r.get("score", 0) + 1) / 2, 
            "rerank_score": r.get("_rerank_score")
        })
    return out

def _format_reply_results(items):
    out = []
    for r in items:
        ep_num = r.get("episode_number")
        if ep_num is None:
             ep_num = r.get("raw_answer_record", {}).get("episode_number")

        img_p = r.get("answer_image_path", "")

        out.append({
            "question_text": r.get("question_text"),
            "answer_text": r.get("answer_text"),
            "work_name": r.get("work_name"),
            "episode_index": ep_num,
            "episode_title": r.get("episode_title"),
            "answer_time_s": r.get("answer_time_s"),
            "answer_image_path": _resolve_web_path(img_p),
            "coarse_score": (r.get("score", 0) + 1) / 2,
            "rerank_score": r.get("_rerank_score")
        })
    return out

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=11325)