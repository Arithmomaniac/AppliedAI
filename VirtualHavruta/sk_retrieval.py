"""
Semantic Kernel-based retrieval system to replace Neo4j vector operations.
This module provides SK memory connectors and retrieval plugins.
"""

import asyncio
from typing import Any, Dict, List, Optional, Tuple, Union
import logging
import json
import numpy as np
from dataclasses import dataclass

# Import from the existing modules
from VirtualHavruta.document import ChunkDocument
from VirtualHavruta.util import convert_node_to_doc, convert_vector_db_record_to_doc

# Try to import SK memory components
try:
    from semantic_kernel import Kernel
    from semantic_kernel.functions import kernel_function
    from semantic_kernel.memory import SemanticTextMemory
    from semantic_kernel.memory.memory_stores import VolatileMemoryStore
    from semantic_kernel.connectors.memory.azure_cognitive_search import AzureCognitiveSearchMemoryStore
    SEMANTIC_KERNEL_AVAILABLE = True
except ImportError:
    SEMANTIC_KERNEL_AVAILABLE = False


@dataclass
class RetrievalResult:
    """Represents a retrieval result with document and score."""
    document: ChunkDocument
    score: float
    source: str  # 'semantic', 'graph', 'linker'


class SemanticKernelRetriever:
    """
    SK-based retrieval system that replaces Neo4j vector operations with SK memory stores.
    """
    
    def __init__(self, config: Dict[str, Any], logger: logging.Logger, sk_plugin):
        """
        Initialize the SK retrieval system.
        
        Args:
            config: Configuration dictionary
            logger: Logger instance
            sk_plugin: The SK plugin instance for embeddings
        """
        self.config = config
        self.logger = logger
        self.sk_plugin = sk_plugin
        self.memory = None
        self._initialize_memory()
    
    def _initialize_memory(self):
        """Initialize SK memory store."""
        try:
            if SEMANTIC_KERNEL_AVAILABLE:
                # Use in-memory store for now - in production this could be Azure Cognitive Search
                memory_store = VolatileMemoryStore()
                self.memory = SemanticTextMemory(
                    storage=memory_store,
                    embeddings_generator=self.sk_plugin.kernel.get_service("embedding")
                )
            else:
                self.memory = MockMemoryStore()
        except Exception as e:
            self.logger.error(f"[SK RETRIEVER] Failed to initialize memory: {e}")
            self.memory = MockMemoryStore()
    
    async def store_document(self, document: ChunkDocument, collection: str = "default"):
        """
        Store a document in SK memory.
        
        Args:
            document: Document to store
            collection: Memory collection name
        """
        try:
            if SEMANTIC_KERNEL_AVAILABLE and self.memory:
                await self.memory.save_information(
                    collection=collection,
                    text=document.page_content,
                    id=document.metadata.get("url", str(hash(document.page_content))),
                    additional_metadata=json.dumps(document.metadata)
                )
        except Exception as e:
            self.logger.error(f"[SK RETRIEVER] Error storing document: {e}")
    
    async def retrieve_documents_semantic(
        self, 
        query: str, 
        top_k: int = 15, 
        collection: str = "default",
        filter_mode: str = 'primary',
        msg_id: str = ""
    ) -> List[RetrievalResult]:
        """
        Retrieve documents using semantic search via SK memory.
        
        Args:
            query: Search query
            top_k: Number of results to return
            collection: Memory collection to search
            filter_mode: Filter mode ('primary' or 'secondary')
            msg_id: Message ID for logging
            
        Returns:
            List of retrieval results
        """
        try:
            if SEMANTIC_KERNEL_AVAILABLE and self.memory:
                # Use SK memory search
                results = await self.memory.search(
                    collection=collection,
                    query=query,
                    limit=top_k,
                    min_relevance_score=0.0
                )
                
                retrieval_results = []
                for result in results:
                    try:
                        metadata = json.loads(result.additional_metadata) if result.additional_metadata else {}
                        document = ChunkDocument(
                            page_content=result.text,
                            metadata=metadata
                        )
                        
                        # Apply filter mode
                        if self._passes_filter(document, filter_mode):
                            retrieval_results.append(RetrievalResult(
                                document=document,
                                score=result.relevance,
                                source="semantic"
                            ))
                    except Exception as e:
                        self.logger.error(f"[SK RETRIEVER] Error processing result: {e}")
                        continue
                
                self.logger.info(f"MsgID={msg_id}. [SK SEMANTIC RETRIEVAL] Found {len(retrieval_results)} documents for query: {query}")
                return retrieval_results
            else:
                # Fallback to mock results
                return self._create_mock_results(query, top_k, "semantic")
                
        except Exception as e:
            self.logger.error(f"MsgID={msg_id}. [SK SEMANTIC RETRIEVAL] Error: {e}")
            return []
    
    def _passes_filter(self, document: ChunkDocument, filter_mode: str) -> bool:
        """
        Check if document passes the filter criteria.
        
        Args:
            document: Document to check
            filter_mode: Filter mode
            
        Returns:
            True if document passes filter
        """
        if filter_mode == 'primary':
            primary_filters = self.config.get('references', {}).get('primary_source_filter', [])
            doc_category = document.metadata.get('primaryDocCategory', '')
            return not primary_filters or doc_category in primary_filters
        return True
    
    async def retrieve_documents_graph_traversal(
        self,
        seed_documents: List[ChunkDocument],
        query: str,
        max_depth: int = 2,
        k_seeds: int = 5,
        direction: str = "both_ways",
        msg_id: str = ""
    ) -> List[RetrievalResult]:
        """
        Retrieve documents using graph traversal logic adapted for SK.
        
        Since SK doesn't have native graph support, we'll simulate graph traversal
        by finding semantically related documents to the seed documents.
        
        Args:
            seed_documents: Starting documents for traversal
            query: Original query
            max_depth: Maximum traversal depth
            k_seeds: Number of seeds to use
            direction: Traversal direction (maintained for compatibility)
            msg_id: Message ID for logging
            
        Returns:
            List of retrieval results
        """
        try:
            all_results = []
            
            # Use top k_seeds seed documents
            seeds = seed_documents[:k_seeds]
            
            for depth in range(max_depth):
                depth_results = []
                
                for seed_doc in seeds:
                    # Find documents related to this seed
                    related_query = f"{query} {seed_doc.page_content[:200]}"  # Combine query with seed content
                    
                    related_docs = await self.retrieve_documents_semantic(
                        query=related_query,
                        top_k=10,
                        msg_id=msg_id
                    )
                    
                    # Add with decreased score based on depth
                    score_multiplier = 1.0 / (depth + 1)
                    for result in related_docs:
                        result.score *= score_multiplier
                        result.source = f"graph_depth_{depth}"
                        depth_results.append(result)
                
                # Use results from this depth as seeds for next iteration
                seeds = [r.document for r in depth_results[:k_seeds]]
                all_results.extend(depth_results)
            
            # Remove duplicates and sort by score
            unique_results = self._deduplicate_results(all_results)
            unique_results.sort(key=lambda x: x.score, reverse=True)
            
            self.logger.info(f"MsgID={msg_id}. [SK GRAPH TRAVERSAL] Found {len(unique_results)} unique documents")
            return unique_results
            
        except Exception as e:
            self.logger.error(f"MsgID={msg_id}. [SK GRAPH TRAVERSAL] Error: {e}")
            return []
    
    def _deduplicate_results(self, results: List[RetrievalResult]) -> List[RetrievalResult]:
        """Remove duplicate results based on document URL or content hash."""
        seen = set()
        unique_results = []
        
        for result in results:
            doc_id = result.document.metadata.get('url') or hash(result.document.page_content)
            if doc_id not in seen:
                seen.add(doc_id)
                unique_results.append(result)
        
        return unique_results
    
    async def merge_and_rank_results(
        self,
        semantic_results: List[RetrievalResult],
        graph_results: List[RetrievalResult],
        linker_results: List[RetrievalResult],
        query: str,
        msg_id: str = ""
    ) -> Tuple[List[ChunkDocument], List[float]]:
        """
        Merge and rank results from different retrieval methods using SK.
        
        Args:
            semantic_results: Results from semantic search
            graph_results: Results from graph traversal
            linker_results: Results from linker API
            query: Original query
            msg_id: Message ID for logging
            
        Returns:
            Tuple of (ranked_documents, scores)
        """
        try:
            # Combine all results
            all_results = semantic_results + graph_results + linker_results
            
            # Deduplicate
            unique_results = self._deduplicate_results(all_results)
            
            # Re-score using SK embedding similarity
            if unique_results:
                query_embedding = await self.sk_plugin.get_embedding(query)
                
                final_scores = []
                for result in unique_results:
                    doc_embedding = await self.sk_plugin.get_embedding(result.document.page_content)
                    
                    if query_embedding and doc_embedding:
                        # Compute cosine similarity
                        similarity = self._cosine_similarity(query_embedding, doc_embedding)
                        
                        # Combine with original score
                        combined_score = 0.7 * similarity + 0.3 * result.score
                        final_scores.append(combined_score)
                    else:
                        final_scores.append(result.score)
                
                # Sort by combined score
                scored_pairs = list(zip(unique_results, final_scores))
                scored_pairs.sort(key=lambda x: x[1], reverse=True)
                
                ranked_documents = [pair[0].document for pair in scored_pairs]
                ranked_scores = [pair[1] for pair in scored_pairs]
                
                self.logger.info(f"MsgID={msg_id}. [SK MERGE RANK] Ranked {len(ranked_documents)} documents")
                return ranked_documents, ranked_scores
            
            return [], []
            
        except Exception as e:
            self.logger.error(f"MsgID={msg_id}. [SK MERGE RANK] Error: {e}")
            return [], []
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Compute cosine similarity between two vectors."""
        try:
            if not vec1 or not vec2 or len(vec1) != len(vec2):
                return 0.0
            
            vec1_np = np.array(vec1)
            vec2_np = np.array(vec2)
            
            dot_product = np.dot(vec1_np, vec2_np)
            norm1 = np.linalg.norm(vec1_np)
            norm2 = np.linalg.norm(vec2_np)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            return dot_product / (norm1 * norm2)
        except Exception:
            return 0.0
    
    def _create_mock_results(self, query: str, top_k: int, source: str) -> List[RetrievalResult]:
        """Create mock results for testing when SK is not available."""
        results = []
        for i in range(min(top_k, 3)):  # Return fewer mock results
            mock_doc = ChunkDocument(
                page_content=f"Mock document {i+1} for query: {query}",
                metadata={"url": f"mock://doc{i+1}", "source": source}
            )
            results.append(RetrievalResult(
                document=mock_doc,
                score=0.9 - (i * 0.1),
                source=source
            ))
        return results


class MockMemoryStore:
    """Mock memory store for when SK is not available."""
    
    def __init__(self):
        self.documents = {}
    
    async def save_information(self, collection: str, text: str, id: str, additional_metadata: str = ""):
        """Mock save method."""
        if collection not in self.documents:
            self.documents[collection] = {}
        self.documents[collection][id] = {
            "text": text,
            "metadata": additional_metadata
        }
    
    async def search(self, collection: str, query: str, limit: int = 10, min_relevance_score: float = 0.0):
        """Mock search method."""
        # Return empty list for mock
        return []


def create_sk_retriever(config: Dict[str, Any], logger: logging.Logger, sk_plugin) -> SemanticKernelRetriever:
    """
    Factory function to create SK retriever.
    
    Args:
        config: Configuration dictionary
        logger: Logger instance
        sk_plugin: SK plugin instance
        
    Returns:
        SK retriever instance
    """
    return SemanticKernelRetriever(config, logger, sk_plugin)