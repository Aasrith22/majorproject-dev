"""
Knowledge Base Service
Manages educational content storage and retrieval
"""

from typing import List, Optional, Dict, Any
from loguru import logger
import os
import json

from app.config import settings
from app.models.knowledge import KnowledgeChunk, KnowledgeSearchResult
from app.utils.embeddings import EmbeddingService
from app.utils.vector_store import VectorStore


class KnowledgeBaseService:
    """Service for managing the knowledge base"""
    
    _instance = None
    _initialized = False
    
    embedding_service: Optional[EmbeddingService] = None
    vector_store: Optional[VectorStore] = None
    
    @classmethod
    async def initialize(cls):
        """Initialize the knowledge base service"""
        if cls._initialized:
            return
        
        try:
            # Initialize embedding service
            cls.embedding_service = EmbeddingService()
            await cls.embedding_service.initialize()
            
            # Initialize vector store
            cls.vector_store = VectorStore()
            await cls.vector_store.initialize()
            
            # Load any existing knowledge base
            await cls._load_initial_content()
            
            cls._initialized = True
            logger.info("Knowledge base service initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize knowledge base: {e}")
            # Don't raise - allow app to start without knowledge base
    
    @classmethod
    async def _load_initial_content(cls):
        """Load initial content into the knowledge base and rebuild vector index"""
        kb_path = settings.knowledge_base_path
        
        if not os.path.exists(kb_path):
            os.makedirs(kb_path, exist_ok=True)
            logger.info(f"Created knowledge base directory: {kb_path}")
            return
        
        # First, rebuild vector index from existing MongoDB content
        await cls._rebuild_vector_index()
        
        # Then load any new content from JSON files
        content_count = 0
        for filename in os.listdir(kb_path):
            if filename.endswith(".json"):
                filepath = os.path.join(kb_path, filename)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        content_data = json.load(f)
                    
                    if isinstance(content_data, list):
                        for item in content_data:
                            result = await cls.add_content(item)
                            if result:
                                content_count += 1
                    else:
                        result = await cls.add_content(content_data)
                        if result:
                            content_count += 1
                    
                    logger.info(f"Loaded content from {filename}")
                except Exception as e:
                    logger.error(f"Failed to load {filename}: {e}")
        
        # Build the vector index after adding all content
        if cls.vector_store:
            await cls.vector_store.build_index()
            logger.info(f"Built vector index with {cls.vector_store.size} vectors")
    
    @classmethod
    async def _rebuild_vector_index(cls):
        """Rebuild vector index from existing MongoDB content"""
        try:
            # Get all existing content from MongoDB
            chunks = await KnowledgeChunk.find_all().to_list()
            
            if not chunks:
                logger.info("No existing content in MongoDB to rebuild index from")
                return
            
            logger.info(f"Rebuilding vector index from {len(chunks)} existing chunks")
            
            for chunk in chunks:
                # Generate embedding if not present
                if not chunk.embedding_vector and cls.embedding_service:
                    embedding = await cls.embedding_service.embed_text(chunk.content_text)
                    chunk.embedding_vector = embedding
                    await chunk.save()
                
                # Add to vector store
                if chunk.embedding_vector and cls.vector_store:
                    await cls.vector_store.add_vector(
                        vector_id=str(chunk.id),
                        vector=chunk.embedding_vector,
                        metadata={
                            "content_id": chunk.content_id,
                            "topic": chunk.topic,
                            "subject": chunk.subject,
                            "difficulty": chunk.difficulty,
                        }
                    )
            
            logger.info(f"Rebuilt vector index with {len(chunks)} vectors")
            
        except Exception as e:
            logger.error(f"Failed to rebuild vector index: {e}")
    
    @classmethod
    async def add_content(cls, content_data: Dict[str, Any]) -> Optional[str]:
        """
        Add content to the knowledge base
        
        Args:
            content_data: Dictionary with content fields
            
        Returns:
            Content ID if successful
        """
        try:
            # Check if content already exists
            existing = await KnowledgeChunk.find_one(
                KnowledgeChunk.content_id == content_data.get("content_id")
            )
            if existing:
                return str(existing.content_id)
            
            # Generate embedding
            embedding = None
            if cls.embedding_service:
                embedding = await cls.embedding_service.embed_text(
                    content_data.get("content_text", "")
                )
            
            # Create knowledge chunk
            chunk = KnowledgeChunk(
                content_id=content_data.get("content_id", f"chunk_{hash(content_data.get('content_text', ''))}"),
                source_type=content_data.get("source_type", "manual"),
                source_title=content_data.get("source_title", "Unknown"),
                source_url=content_data.get("source_url"),
                content_text=content_data.get("content_text", ""),
                content_summary=content_data.get("content_summary"),
                subject=content_data.get("subject", "general"),
                topic=content_data.get("topic", "general"),
                subtopics=content_data.get("subtopics", []),
                difficulty=content_data.get("difficulty", "medium"),
                keywords=content_data.get("keywords", []),
                concepts=content_data.get("concepts", []),
                embedding_vector=embedding,
            )
            await chunk.insert()
            
            # Add to vector store
            if cls.vector_store and embedding:
                await cls.vector_store.add_vector(
                    vector_id=str(chunk.id),
                    vector=embedding,
                    metadata={"content_id": chunk.content_id}
                )
            
            return chunk.content_id
            
        except Exception as e:
            logger.error(f"Failed to add content: {e}")
            return None
    
    @classmethod
    async def search(
        cls,
        query: str,
        topic: Optional[str] = None,
        difficulty: Optional[str] = None,
        limit: int = 5,
        modality: str = "text"
    ) -> List[KnowledgeSearchResult]:
        """
        Search the knowledge base
        
        Args:
            query: Search query
            topic: Filter by topic
            difficulty: Filter by difficulty
            limit: Maximum results
            modality: Preferred modality
            
        Returns:
            List of search results
        """
        results = []
        
        try:
            # Semantic search using vector store
            if cls.embedding_service and cls.vector_store:
                query_embedding = await cls.embedding_service.embed_text(query)
                
                vector_results = await cls.vector_store.search(
                    query_vector=query_embedding,
                    top_k=limit * 2  # Get more for filtering
                )
                
                # Fetch full documents and filter
                for result in vector_results:
                    chunk = await KnowledgeChunk.find_one(
                        KnowledgeChunk.content_id == result.get("content_id")
                    )
                    
                    if not chunk:
                        continue
                    
                    # Apply filters
                    if topic and chunk.topic.lower() != topic.lower():
                        continue
                    if difficulty and chunk.difficulty != difficulty:
                        continue
                    
                    # Check modality suitability
                    modality_score = 1.0
                    if modality == "voice":
                        modality_score = chunk.voice_suitability
                    elif modality == "diagram":
                        modality_score = chunk.diagram_suitability
                    
                    results.append(KnowledgeSearchResult(
                        content_id=chunk.content_id,
                        content_text=chunk.content_text,
                        content_summary=chunk.content_summary,
                        topic=chunk.topic,
                        difficulty=chunk.difficulty,
                        relevance_score=result.get("score", 0.5) * modality_score,
                        concepts=chunk.concepts,
                    ))
                    
                    # Update retrieval count
                    chunk.times_retrieved += 1
                    await chunk.save()
            
            else:
                # Fallback to keyword search
                results = await cls._keyword_search(query, topic, difficulty, limit)
            
            # Sort by relevance and limit
            results = sorted(results, key=lambda x: x.relevance_score, reverse=True)[:limit]
            
            return results
            
        except Exception as e:
            logger.error(f"Search error: {e}")
            return []
    
    @classmethod
    async def _keyword_search(
        cls,
        query: str,
        topic: Optional[str] = None,
        difficulty: Optional[str] = None,
        limit: int = 5
    ) -> List[KnowledgeSearchResult]:
        """Fallback keyword-based search"""
        
        # Build query
        filter_conditions = []
        
        if topic:
            filter_conditions.append(KnowledgeChunk.topic == topic)
        if difficulty:
            filter_conditions.append(KnowledgeChunk.difficulty == difficulty)
        
        # Search in keywords and content
        chunks = await KnowledgeChunk.find(*filter_conditions).limit(limit * 2).to_list()
        
        results = []
        query_words = set(query.lower().split())
        
        for chunk in chunks:
            # Calculate simple relevance score
            chunk_words = set(chunk.content_text.lower().split())
            keyword_matches = set(k.lower() for k in chunk.keywords) & query_words
            content_matches = chunk_words & query_words
            
            score = (len(keyword_matches) * 2 + len(content_matches)) / (len(query_words) + 1)
            
            if score > 0:
                results.append(KnowledgeSearchResult(
                    content_id=chunk.content_id,
                    content_text=chunk.content_text,
                    content_summary=chunk.content_summary,
                    topic=chunk.topic,
                    difficulty=chunk.difficulty,
                    relevance_score=min(score, 1.0),
                    concepts=chunk.concepts,
                ))
        
        return results
    
    @classmethod
    async def get_by_topic(
        cls,
        topic: str,
        difficulty: Optional[str] = None,
        limit: int = 10
    ) -> List[KnowledgeChunk]:
        """Get content chunks by topic"""
        
        query = KnowledgeChunk.find(KnowledgeChunk.topic == topic)
        
        if difficulty:
            query = query.find(KnowledgeChunk.difficulty == difficulty)
        
        return await query.limit(limit).to_list()
    
    @classmethod
    async def get_by_concepts(
        cls,
        concepts: List[str],
        limit: int = 10
    ) -> List[KnowledgeChunk]:
        """Get content chunks that cover specific concepts"""
        
        # Find chunks that contain any of the concepts
        chunks = await KnowledgeChunk.find(
            {"concepts": {"$in": concepts}}
        ).limit(limit).to_list()
        
        return chunks
