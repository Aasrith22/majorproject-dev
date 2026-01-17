"""
Vector Store
Manages vector storage and similarity search using NumPy (no C++ dependencies)
"""

from typing import List, Dict, Any, Optional
from loguru import logger
import os
import json
import numpy as np

from app.config import settings


class VectorStore:
    """Vector store using NumPy for cosine similarity search"""
    
    _vectors: Optional[np.ndarray] = None
    _initialized = False
    _id_to_metadata: Dict[int, Dict[str, Any]] = {}
    _content_id_to_index: Dict[str, int] = {}
    _next_id: int = 0
    _vector_list: List[List[float]] = []
    
    async def initialize(self):
        """Initialize the vector store"""
        if self._initialized:
            return
        
        try:
            # Try to load existing index
            if os.path.exists(settings.vector_index_path):
                try:
                    self._load_index()
                    logger.info(f"Loaded existing vector index from {settings.vector_index_path}")
                except Exception as e:
                    logger.warning(f"Could not load existing index: {e}")
                    self._vectors = None
                    self._vector_list = []
            
            self._initialized = True
            logger.info("Vector store initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize vector store: {e}")
    
    def _load_index(self):
        """Load vectors and metadata from files"""
        # Load vectors
        vectors_path = settings.vector_index_path
        if os.path.exists(vectors_path):
            self._vectors = np.load(vectors_path)
            self._vector_list = self._vectors.tolist()
        
        # Load metadata
        metadata_path = settings.vector_index_path + ".meta.json"
        if os.path.exists(metadata_path):
            try:
                with open(metadata_path, "r") as f:
                    data = json.load(f)
                    self._id_to_metadata = {int(k): v for k, v in data.get("id_to_metadata", {}).items()}
                    self._content_id_to_index = data.get("content_id_to_index", {})
                    self._next_id = data.get("next_id", 0)
            except Exception as e:
                logger.error(f"Failed to load metadata: {e}")
    
    def _save_index(self):
        """Save vectors and metadata to files"""
        try:
            os.makedirs(os.path.dirname(settings.vector_index_path), exist_ok=True)
            
            # Save vectors
            if self._vector_list:
                self._vectors = np.array(self._vector_list, dtype=np.float32)
                np.save(settings.vector_index_path, self._vectors)
            
            # Save metadata
            metadata_path = settings.vector_index_path + ".meta.json"
            with open(metadata_path, "w") as f:
                json.dump({
                    "id_to_metadata": self._id_to_metadata,
                    "content_id_to_index": self._content_id_to_index,
                    "next_id": self._next_id,
                }, f)
        except Exception as e:
            logger.error(f"Failed to save index: {e}")
    
    async def add_vector(
        self,
        vector_id: str,
        vector: List[float],
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Add a vector to the index
        
        Args:
            vector_id: Unique identifier for the vector
            vector: Embedding vector
            metadata: Additional metadata to store
            
        Returns:
            Success status
        """
        if not self._initialized:
            await self.initialize()
        
        try:
            # Check if already exists
            if vector_id in self._content_id_to_index:
                return True
            
            # Add to vector list
            index_id = self._next_id
            self._vector_list.append(vector)
            
            # Store mappings
            self._id_to_metadata[index_id] = metadata or {}
            self._id_to_metadata[index_id]["vector_id"] = vector_id
            self._content_id_to_index[vector_id] = index_id
            
            self._next_id += 1
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to add vector: {e}")
            return False
    
    async def build_index(self):
        """Build the vector index (convert list to numpy array and save)"""
        if not self._vector_list:
            logger.warning("No vectors to build index from")
            return False
        
        try:
            # Convert to numpy array for efficient search
            self._vectors = np.array(self._vector_list, dtype=np.float32)
            
            # Normalize vectors for cosine similarity
            norms = np.linalg.norm(self._vectors, axis=1, keepdims=True)
            norms[norms == 0] = 1  # Avoid division by zero
            self._vectors = self._vectors / norms
            
            # Save index
            self._save_index()
            
            logger.info(f"Built and saved vector index with {self._next_id} vectors")
            return True
            
        except Exception as e:
            logger.error(f"Failed to build index: {e}")
            return False
    
    async def search(
        self,
        query_vector: List[float],
        top_k: int = 10,
        include_distances: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Search for similar vectors using cosine similarity
        
        Args:
            query_vector: Query embedding
            top_k: Number of results to return
            include_distances: Whether to include distance scores
            
        Returns:
            List of results with metadata and scores
        """
        if self._vectors is None or len(self._vectors) == 0:
            return []
        
        try:
            # Convert query to numpy and normalize
            query = np.array(query_vector, dtype=np.float32)
            query_norm = np.linalg.norm(query)
            if query_norm > 0:
                query = query / query_norm
            
            # Compute cosine similarities (dot product of normalized vectors)
            similarities = np.dot(self._vectors, query)
            
            # Get top-k indices
            top_indices = np.argsort(similarities)[::-1][:top_k]
            
            results = []
            for idx in top_indices:
                idx = int(idx)
                metadata = self._id_to_metadata.get(idx, {})
                similarity = float(similarities[idx])
                
                results.append({
                    "index_id": idx,
                    "content_id": metadata.get("content_id"),
                    "score": similarity,
                    "distance": 1 - similarity if include_distances else None,
                    **metadata
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []
    
    async def get_vector(self, vector_id: str) -> Optional[List[float]]:
        """Get a vector by its ID"""
        if self._vectors is None:
            return None
        
        try:
            index_id = self._content_id_to_index.get(vector_id)
            if index_id is None:
                return None
            
            return self._vectors[index_id].tolist()
            
        except Exception as e:
            logger.error(f"Failed to get vector: {e}")
            return None
    
    @property
    def size(self) -> int:
        """Get the number of vectors in the index"""
        return self._next_id
