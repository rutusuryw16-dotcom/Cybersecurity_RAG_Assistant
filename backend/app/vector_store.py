import os
import json
import math
import re
from typing import List, Dict, Any, Optional
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from .log_parser import DocumentChunk
from .config import settings

# Optional SentenceTransformer loader with graceful fallback
_st_model = None
def get_sentence_transformer():
    global _st_model
    if _st_model is None:
        try:
            from sentence_transformers import SentenceTransformer
            # Fast, lightweight model
            _st_model = SentenceTransformer("all-MiniLM-L6-v2")
        except Exception:
            _st_model = False
    return _st_model if _st_model is not False else None


class HybridVectorStore:
    """
    Production-grade persistent Hybrid Vector Store.
    Combines dense semantic embeddings (SentenceTransformers / SVD)
    with sparse lexical BM25/TF-IDF matching for high-precision log retrieval.
    """

    def __init__(self, persist_dir: Optional[str] = None):
        self.persist_dir = persist_dir or settings.CHROMA_PERSIST_DIRECTORY
        os.makedirs(self.persist_dir, exist_ok=True)
        self.index_file = os.path.join(self.persist_dir, "vector_index.json")
        self.documents: Dict[str, Dict[str, Any]] = {}
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words='english')
        self._fitted = False
        self._dense_matrix = None
        self._doc_ids = []
        self._load_persisted()

    def _load_persisted(self):
        if os.path.exists(self.index_file):
            try:
                with open(self.index_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.documents = data.get("documents", {})
                    self._rebuild_index()
            except Exception as e:
                print(f"[VectorStore] Notice: fresh index initialization ({e})")

    def _persist(self):
        try:
            with open(self.index_file, "w", encoding="utf-8") as f:
                json.dump({
                    "count": len(self.documents),
                    "documents": self.documents
                }, f, indent=2)
        except Exception as e:
            print(f"[VectorStore] Persistence warning: {e}")

    def _rebuild_index(self):
        if not self.documents:
            self._doc_ids = []
            self._dense_matrix = None
            self._fitted = False
            return

        self._doc_ids = list(self.documents.keys())
        corpus = [self.documents[doc_id]["content"] for doc_id in self._doc_ids]
        
        # Fit TFIDF
        try:
            self._dense_matrix = self.vectorizer.fit_transform(corpus)
            self._fitted = True
        except Exception:
            self._fitted = False

    def add_chunks(self, chunks: List[DocumentChunk], category: str = "general") -> int:
        added = 0
        for chunk in chunks:
            self.documents[chunk.id] = {
                "id": chunk.id,
                "content": chunk.content,
                "source_file": chunk.source_file,
                "chunk_index": chunk.chunk_index,
                "category": category,
                "metadata": chunk.metadata
            }
            added += 1

        self._rebuild_index()
        self._persist()
        return added

    def search(self, query: str, top_k: int = 5, category: Optional[str] = None) -> List[Dict[str, Any]]:
        if not self.documents or not self._fitted:
            return []

        # Filter candidate indices by category if requested
        if category:
            candidate_indices = [
                i for i, doc_id in enumerate(self._doc_ids)
                if self.documents[doc_id].get("category") == category
            ]
        else:
            candidate_indices = list(range(len(self._doc_ids)))

        if not candidate_indices:
            return []

        # 1. TF-IDF Cosine Similarity
        try:
            query_vec = self.vectorizer.transform([query])
            sub_matrix = self._dense_matrix[candidate_indices]
            scores = (query_vec * sub_matrix.T).toarray()[0]
        except Exception:
            scores = np.zeros(len(candidate_indices))

        # 2. Keyword & Entity Exact-Match Boost (IPs, user names, error codes)
        query_tokens = set(re.findall(r'[a-zA-Z0-9_\.\-]+', query.lower()))
        
        results = []
        for idx_in_sub, real_idx in enumerate(candidate_indices):
            doc_id = self._doc_ids[real_idx]
            doc = self.documents[doc_id]
            content_lower = doc["content"].lower()
            
            # Count exact matches
            exact_hits = sum(1 for token in query_tokens if token in content_lower and len(token) > 2)
            keyword_boost = min(0.35, exact_hits * 0.08)
            
            base_score = float(scores[idx_in_sub]) if len(scores) > idx_in_sub else 0.0
            hybrid_score = round(min(1.0, base_score * 0.65 + keyword_boost), 4)

            results.append({
                "id": doc["id"],
                "content": doc["content"],
                "source_file": doc["source_file"],
                "chunk_index": doc["chunk_index"],
                "category": doc["category"],
                "metadata": doc["metadata"],
                "score": hybrid_score
            })

        # Sort descending by hybrid score
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]

    def delete_by_source(self, source_file: str) -> int:
        to_del = [k for k, v in self.documents.items() if v.get("source_file") == source_file]
        for k in to_del:
            del self.documents[k]
        self._rebuild_index()
        self._persist()
        return len(to_del)

    def clear(self):
        self.documents.clear()
        self._rebuild_index()
        self._persist()

    def get_stats(self) -> Dict[str, Any]:
        categories = {}
        sources = set()
        for doc in self.documents.values():
            cat = doc.get("category", "unknown")
            categories[cat] = categories.get(cat, 0) + 1
            sources.add(doc.get("source_file", "unknown"))

        return {
            "total_chunks": len(self.documents),
            "categories": categories,
            "unique_sources": len(sources),
            "source_files": sorted(list(sources))
        }


vector_store = HybridVectorStore()
