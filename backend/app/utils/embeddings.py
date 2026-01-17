"""
Embedding Service
Handles text embedding generation using sentence-transformers or OpenAI fallback
"""

from typing import List, Optional
from loguru import logger
import hashlib

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
    np = None

from app.config import settings


class EmbeddingService:
    """Service for generating text embeddings"""
    
    _model = None
    _openai_client = None
    _initialized = False
    _use_openai_fallback = False
    
    async def initialize(self):
        """Initialize the embedding model"""
        if self._initialized:
            return
        
        # Try sentence-transformers first
        try:
            from sentence_transformers import SentenceTransformer
            
            self._model = SentenceTransformer(settings.embedding_model)
            self._initialized = True
            logger.info(f"Embedding model loaded: {settings.embedding_model}")
            return
            
        except ImportError:
            logger.warning("sentence-transformers not installed.")
        except Exception as e:
            logger.warning(f"Failed to load sentence-transformers: {e}")
        
        # Fallback to OpenAI embeddings
        if settings.openai_api_key:
            try:
                from openai import OpenAI
                self._openai_client = OpenAI(api_key=settings.openai_api_key)
                self._use_openai_fallback = True
                self._initialized = True
                logger.info("Using OpenAI embeddings as fallback")
                return
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI embeddings: {e}")
        
        # Final fallback: simple hash-based embeddings (for testing only)
        logger.warning("Using simple hash-based embeddings (not recommended for production)")
        self._initialized = True
    
    def _simple_hash_embedding(self, text: str) -> List[float]:
        """Generate a simple deterministic embedding based on text hash (fallback only)"""
        # Create a deterministic embedding from text hash
        import random
        hash_bytes = hashlib.sha256(text.encode()).digest()
        seed = int.from_bytes(hash_bytes[:4], 'big')
        random.seed(seed)
        return [random.uniform(-1, 1) for _ in range(settings.vector_dimensions)]
    
    async def embed_text(self, text: str) -> Optional[List[float]]:
        """
        Generate embedding for a single text
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector as list of floats
        """
        if not self._initialized:
            await self.initialize()
        
        try:
            # Use sentence-transformers if available
            if self._model:
                embedding = self._model.encode(text, convert_to_numpy=True)
                return embedding.tolist()
            
            # Use OpenAI embeddings as fallback
            if self._use_openai_fallback and self._openai_client:
                try:
                    response = self._openai_client.embeddings.create(
                        model="text-embedding-3-small",
                        input=text,
                        dimensions=settings.vector_dimensions
                    )
                    return response.data[0].embedding
                except Exception as openai_error:
                    # On OpenAI error (quota, etc.), disable OpenAI and use hash fallback
                    logger.warning(f"OpenAI embedding failed, switching to hash fallback: {openai_error}")
                    self._use_openai_fallback = False
                    self._openai_client = None
            
            # Final fallback: simple hash embedding
            return self._simple_hash_embedding(text)
            
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            return self._simple_hash_embedding(text)
    
    async def embed_texts(self, texts: List[str]) -> Optional[List[List[float]]]:
        """
        Generate embeddings for multiple texts
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        if not self._initialized:
            await self.initialize()
        
        try:
            # Use sentence-transformers if available
            if self._model:
                embeddings = self._model.encode(texts, convert_to_numpy=True)
                return embeddings.tolist()
            
            # Use OpenAI embeddings as fallback
            if self._use_openai_fallback and self._openai_client:
                try:
                    response = self._openai_client.embeddings.create(
                        model="text-embedding-3-small",
                        input=texts,
                        dimensions=settings.vector_dimensions
                    )
                    return [item.embedding for item in response.data]
                except Exception as openai_error:
                    # On OpenAI error (quota, etc.), disable OpenAI and use hash fallback
                    logger.warning(f"OpenAI batch embedding failed, switching to hash fallback: {openai_error}")
                    self._use_openai_fallback = False
                    self._openai_client = None
            
            # Final fallback: simple hash embeddings
            return [self._simple_hash_embedding(text) for text in texts]
            
        except Exception as e:
            logger.error(f"Batch embedding generation failed: {e}")
            return [self._simple_hash_embedding(text) for text in texts]
    
    def cosine_similarity(
        self,
        embedding1: List[float],
        embedding2: List[float]
    ) -> float:
        """
        Calculate cosine similarity between two embeddings
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Cosine similarity score (0-1)
        """
        if not HAS_NUMPY:
            logger.warning("numpy not installed, cosine similarity unavailable")
            return 0.0
        
        try:
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)
            
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            return float(dot_product / (norm1 * norm2))
            
        except Exception as e:
            logger.error(f"Similarity calculation failed: {e}")
            return 0.0
    
    @property
    def embedding_dimension(self) -> int:
        """Get the dimension of embeddings produced by the model"""
        return settings.vector_dimensions
