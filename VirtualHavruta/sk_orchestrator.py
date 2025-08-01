"""
Semantic Kernel-based orchestrator to replace the main VirtualHavruta class.
This module provides SK planner-based workflow orchestration.
"""

import asyncio
from typing import Any, Dict, List, Optional, Tuple, Union
import logging
import json
import yaml
from datetime import datetime

# Import existing modules
from VirtualHavruta.document import ChunkDocument
from VirtualHavruta.util import create_logger, part_res
from VirtualHavruta.sk_plugins import create_semantic_kernel_plugin, run_async
from VirtualHavruta.sk_retrieval import create_sk_retriever, RetrievalResult

# Try to import SK planner components
try:
    from semantic_kernel import Kernel
    from semantic_kernel.planners import ActionPlanner, SequentialPlanner
    from semantic_kernel.skill_definition import sk_function, sk_function_context_parameter
    SEMANTIC_KERNEL_AVAILABLE = True
except ImportError:
    SEMANTIC_KERNEL_AVAILABLE = False


class VirtualHavrutaSemanticKernel:
    """
    Main SK-based Virtual Havruta class that replaces the original LangChain implementation.
    Uses SK planners, plugins, and connectors for all LLM and RAG orchestration.
    """
    
    def __init__(self, prompts_file: str, config_file: str, logger: logging.Logger):
        """
        Initialize the SK-based Virtual Havruta system.
        
        Args:
            prompts_file: Path to prompts YAML file
            config_file: Path to configuration YAML file  
            logger: Logger instance
        """
        # Load configuration and prompts
        with open(prompts_file, 'r') as f:
            self.prompts = yaml.safe_load(f)
        with open(config_file, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.logger = logger
        
        # Initialize SK components
        self.sk_plugin = create_semantic_kernel_plugin(self.config, self.prompts, self.logger)
        self.sk_retriever = create_sk_retriever(self.config, self.logger, self.sk_plugin)
        
        # Initialize planners if SK is available
        self.action_planner = None
        self.sequential_planner = None
        self._initialize_planners()
        
        # Configuration shortcuts
        self.config_emb_db = self.config['database']['embed']
        self.config_kg_db = self.config['database']['kg']
        self.top_k = self.config_emb_db['top_k']
        self.primary_source_filter = self.config['references']['primary_source_filter']
        self.num_primary_citations = self.config['references']['num_primary_citations']
        self.num_secondary_citations = self.config['references']['num_secondary_citations']
        self.neo4j_deeplink = self.config_kg_db['neo4j_deeplink']
        
        self.logger.info("[SK HAVRUTA] Initialized Semantic Kernel-based Virtual Havruta")
    
    def _initialize_planners(self):
        """Initialize SK planners for workflow orchestration."""
        try:
            if SEMANTIC_KERNEL_AVAILABLE:
                kernel = self.sk_plugin.kernel
                self.action_planner = ActionPlanner(kernel)
                self.sequential_planner = SequentialPlanner(kernel)
        except Exception as e:
            self.logger.error(f"[SK HAVRUTA] Failed to initialize planners: {e}")
    
    # Core LLM functions using SK plugins
    
    def anti_attack(self, query: str, msg_id: str = '') -> Tuple[str, str, int]:
        """
        Analyze query for attacks using SK plugin.
        
        Args:
            query: Query to analyze
            msg_id: Message ID for logging
            
        Returns:
            Tuple of (detection, explanation, tokens_used)
        """
        try:
            result = run_async(self.sk_plugin.anti_attack(query, msg_id))
            response_data = json.loads(result)
            detection = response_data.get('detection', 'N')
            explanation = response_data.get('explanation', '')
            tokens_used = 0  # SK doesn't expose token counts in the same way
            
            return detection, explanation, tokens_used
        except Exception as e:
            self.logger.error(f"MsgID={msg_id}. [SK ANTI-ATTACK] Error: {e}")
            return 'N', '', 0
    
    def adaptor(self, query: str, msg_id: str = '') -> Tuple[str, int]:
        """
        Adapt query using SK plugin.
        
        Args:
            query: Query to adapt
            msg_id: Message ID for logging
            
        Returns:
            Tuple of (adapted_text, tokens_used)
        """
        try:
            result = run_async(self.sk_plugin.adaptor(query, msg_id))
            return result, 0
        except Exception as e:
            self.logger.error(f"MsgID={msg_id}. [SK ADAPTOR] Error: {e}")
            return query, 0
    
    def editor(self, query: str, msg_id: str = '') -> Tuple[str, int]:
        """
        Edit query using SK plugin.
        
        Args:
            query: Query to edit
            msg_id: Message ID for logging
            
        Returns:
            Tuple of (edited_text, tokens_used)
        """
        try:
            result = run_async(self.sk_plugin.editor(query, msg_id))
            return result, 0
        except Exception as e:
            self.logger.error(f"MsgID={msg_id}. [SK EDITOR] Error: {e}")
            return query, 0
    
    def optimizer(self, query: str, msg_id: str = '') -> Tuple[str, str, str, str, str, str, int]:
        """
        Optimize query using SK plugin.
        
        Args:
            query: Query to optimize
            msg_id: Message ID for logging
            
        Returns:
            Tuple of (translation, extraction, elaboration, quotation, challenge, proposal, tokens_used)
        """
        try:
            result = run_async(self.sk_plugin.optimizer(query, msg_id))
            response_data = json.loads(result)
            
            return (
                response_data.get('translation', ''),
                response_data.get('extraction', ''),
                response_data.get('elaboration', ''),
                response_data.get('quotation', ''),
                response_data.get('challenge', ''),
                response_data.get('proposal', ''),
                0
            )
        except Exception as e:
            self.logger.error(f"MsgID={msg_id}. [SK OPTIMIZER] Error: {e}")
            return '', '', '', '', '', '', 0
    
    def qa(self, query: str, ref_data: str, msg_id: str = '') -> Tuple[str, int]:
        """
        Perform QA using SK plugin.
        
        Args:
            query: Question to answer
            ref_data: Reference data
            msg_id: Message ID for logging
            
        Returns:
            Tuple of (response, tokens_used)
        """
        try:
            result = run_async(self.sk_plugin.qa(query, ref_data, msg_id))
            return result, 0
        except Exception as e:
            self.logger.error(f"MsgID={msg_id}. [SK QA] Error: {e}")
            return "I apologize, but I encountered an error while processing your question.", 0
    
    # Retrieval functions using SK retriever
    
    def retrieve_docs(self, query: str, msg_id: str = '', filter_mode: str = 'primary') -> List[ChunkDocument]:
        """
        Retrieve documents using SK retrieval.
        
        Args:
            query: Query string
            msg_id: Message ID for logging
            filter_mode: Filter mode ('primary' or 'secondary')
            
        Returns:
            List of documents
        """
        try:
            results = run_async(self.sk_retriever.retrieve_documents_semantic(
                query=query,
                top_k=self.top_k,
                filter_mode=filter_mode,
                msg_id=msg_id
            ))
            return [r.document for r in results]
        except Exception as e:
            self.logger.error(f"MsgID={msg_id}. [SK RETRIEVE DOCS] Error: {e}")
            return []
    
    def retrieve_docs_metadata_filtering(self, query: str, msg_id: str = '', metadata_filter: dict = None) -> List[ChunkDocument]:
        """
        Retrieve documents with metadata filtering (compatibility method).
        
        Args:
            query: Query string
            msg_id: Message ID for logging
            metadata_filter: Metadata filter criteria
            
        Returns:
            List of documents
        """
        # For now, delegate to regular retrieval
        # TODO: Implement metadata filtering in SK retriever
        return self.retrieve_docs(query, msg_id, 'primary')
    
    def graph_traversal_retriever(
        self,
        screen_res: str,
        scripture_query: str,
        enriched_query: str,
        filter_mode_nodes: str = None,
        linker_results: List[dict] = None,
        semantic_search_results: List[Tuple[ChunkDocument, float]] = None,
        msg_id: str = ''
    ) -> Tuple[List[Tuple[ChunkDocument, float]], int]:
        """
        Retrieve documents using graph traversal via SK.
        
        Args:
            screen_res: Screen result query
            scripture_query: Scripture query
            enriched_query: Enriched query
            filter_mode_nodes: Node filter mode
            linker_results: Linker API results
            semantic_search_results: Semantic search results
            msg_id: Message ID for logging
            
        Returns:
            Tuple of (retrieval_results, total_token_count)
        """
        try:
            # Get seed documents from semantic search results or retrieve new ones
            if semantic_search_results:
                seed_documents = [doc for doc, score in semantic_search_results]
            else:
                seed_documents = self.retrieve_docs(enriched_query, msg_id)
            
            # Perform graph traversal using SK retriever
            max_depth = self.config_kg_db.get('max_depth', 2)
            k_seeds = self.config_kg_db.get('k_seeds', 5)
            direction = self.config_kg_db.get('direction', 'both_ways')
            
            graph_results = run_async(self.sk_retriever.retrieve_documents_graph_traversal(
                seed_documents=seed_documents,
                query=enriched_query,
                max_depth=max_depth,
                k_seeds=k_seeds,
                direction=direction,
                msg_id=msg_id
            ))
            
            # Convert to expected format
            retrieval_res_kg = [(r.document, r.score) for r in graph_results]
            
            self.logger.info(f"MsgID={msg_id}. [SK GRAPH TRAVERSAL] Retrieved {len(retrieval_res_kg)} documents")
            return retrieval_res_kg, 0
            
        except Exception as e:
            self.logger.error(f"MsgID={msg_id}. [SK GRAPH TRAVERSAL] Error: {e}")
            return [], 0
    
    # Reference processing functions
    
    def select_reference(self, query: str, retrieval_res: List, msg_id: str = '') -> Tuple[List, int]:
        """
        Select useful references using SK plugin.
        
        Args:
            query: Query string
            retrieval_res: Retrieved documents
            msg_id: Message ID for logging
            
        Returns:
            Tuple of (selected_retrieval_res, tokens_used)
        """
        try:
            # Convert retrieval results to text for SK processing
            ref_text = self._format_references_for_llm(retrieval_res)
            
            result = run_async(self.sk_plugin.selector(query, ref_text, msg_id))
            
            # For simplicity, return original results
            # TODO: Parse SK result and filter accordingly
            return retrieval_res, 0
            
        except Exception as e:
            self.logger.error(f"MsgID={msg_id}. [SK SELECT REFERENCE] Error: {e}")
            return retrieval_res, 0
    
    def sort_reference(
        self,
        scripture_query: str,
        enriched_query: str,
        retrieval_res: List,
        filter_mode: str = 'primary',
        msg_id: str = ''
    ) -> Tuple[dict, dict, dict, int]:
        """
        Sort references using SK-based ranking.
        
        Args:
            scripture_query: Scripture query
            enriched_query: Enriched query
            retrieval_res: Retrieval results
            filter_mode: Filter mode
            msg_id: Message ID for logging
            
        Returns:
            Tuple of (sorted_src_rel_dict, src_data_dict, src_ref_dict, total_tokens)
        """
        try:
            # Convert retrieval_res to RetrievalResult format if needed
            if retrieval_res and isinstance(retrieval_res[0], tuple):
                semantic_results = [
                    RetrievalResult(document=doc, score=score, source="semantic")
                    for doc, score in retrieval_res
                ]
            else:
                semantic_results = [
                    RetrievalResult(document=doc, score=1.0, source="semantic")
                    for doc in retrieval_res
                ]
            
            # Merge and rank using SK retriever
            ranked_docs, ranked_scores = run_async(self.sk_retriever.merge_and_rank_results(
                semantic_results=semantic_results,
                graph_results=[],
                linker_results=[],
                query=enriched_query,
                msg_id=msg_id
            ))
            
            # Convert to expected format
            sorted_src_rel_dict = {}
            src_data_dict = {}
            src_ref_dict = {}
            
            for i, (doc, score) in enumerate(zip(ranked_docs, ranked_scores)):
                doc_url = doc.metadata.get('url', f'doc_{i}')
                sorted_src_rel_dict[doc_url] = score
                src_data_dict[doc_url] = doc.page_content
                src_ref_dict[doc_url] = doc.metadata.get('reference', doc_url)
            
            return sorted_src_rel_dict, src_data_dict, src_ref_dict, 0
            
        except Exception as e:
            self.logger.error(f"MsgID={msg_id}. [SK SORT REFERENCE] Error: {e}")
            return {}, {}, {}, 0
    
    def merge_references_by_url(self, retrieval_res: List[Tuple[ChunkDocument, float]], msg_id: str = '') -> Tuple[dict, dict, dict]:
        """
        Merge references by URL (compatibility method).
        
        Args:
            retrieval_res: List of (document, score) tuples
            msg_id: Message ID for logging
            
        Returns:
            Tuple of (sorted_src_rel_dict, src_data_dict, src_ref_dict)
        """
        try:
            url_groups = {}
            
            # Group by URL
            for doc, score in retrieval_res:
                url = doc.metadata.get('url', 'unknown')
                if url not in url_groups:
                    url_groups[url] = {'docs': [], 'scores': []}
                url_groups[url]['docs'].append(doc)
                url_groups[url]['scores'].append(score)
            
            # Merge content for each URL
            sorted_src_rel_dict = {}
            src_data_dict = {}
            src_ref_dict = {}
            
            for url, group in url_groups.items():
                # Use highest score
                max_score = max(group['scores'])
                sorted_src_rel_dict[url] = max_score
                
                # Merge content
                merged_content = ' '.join([doc.page_content for doc in group['docs']])
                src_data_dict[url] = merged_content
                
                # Use first doc's reference
                src_ref_dict[url] = group['docs'][0].metadata.get('reference', url)
            
            return sorted_src_rel_dict, src_data_dict, src_ref_dict
            
        except Exception as e:
            self.logger.error(f"MsgID={msg_id}. [SK MERGE REFERENCES] Error: {e}")
            return {}, {}, {}
    
    # Utility functions
    
    def _format_references_for_llm(self, retrieval_res: List) -> str:
        """Format retrieval results as text for LLM processing."""
        formatted_refs = []
        
        for i, item in enumerate(retrieval_res):
            if isinstance(item, tuple):
                doc, score = item
                content = doc.page_content
            else:
                doc = item
                content = doc.page_content
            
            formatted_refs.append(f"Reference {i+1}: {content[:500]}...")
        
        return '\n\n'.join(formatted_refs)
    
    def generate_ref_str(
        self,
        sorted_src_rel_dict: dict,
        src_data_dict: dict,
        src_ref_dict: dict,
        msg_id: str = '',
        ref_mode: str = 'primary',
        n_citation_base: int = 0,
        is_linker_search: bool = False
    ) -> Tuple[str, str, List, int]:
        """
        Generate reference strings and citations.
        
        Args:
            sorted_src_rel_dict: Sorted relevance dictionary
            src_data_dict: Source data dictionary
            src_ref_dict: Source reference dictionary
            msg_id: Message ID for logging
            ref_mode: Reference mode
            n_citation_base: Starting citation index
            is_linker_search: Whether this is from linker search
            
        Returns:
            Tuple of (conc_ref_data, citations, deeplinks, n_citation)
        """
        try:
            conc_ref_data = ""
            citations = ""
            deeplinks = []
            n_citation = n_citation_base
            
            # Determine citation limits
            if ref_mode == 'primary':
                max_citations = self.num_primary_citations
            else:
                max_citations = self.num_secondary_citations
            
            # Process references
            citation_count = 0
            for url, relevance in sorted_src_rel_dict.items():
                if max_citations > 0 and citation_count >= max_citations:
                    break
                
                data = src_data_dict.get(url, '')
                ref = src_ref_dict.get(url, url)
                
                n_citation += 1
                citation_count += 1
                
                conc_ref_data += f"\n[{n_citation}] {data}"
                citations += f"[{n_citation}] {ref}\n"
                deeplinks.append(url)
            
            self.logger.info(f"MsgID={msg_id}. [SK GENERATE REF STR] Generated {citation_count} citations")
            return conc_ref_data, citations, deeplinks, n_citation
            
        except Exception as e:
            self.logger.error(f"MsgID={msg_id}. [SK GENERATE REF STR] Error: {e}")
            return "", "", [], n_citation_base
    
    def generate_kg_deeplink(self, deeplinks: List, msg_id: str = '') -> str:
        """
        Generate Knowledge Graph deep link URL.
        
        Args:
            deeplinks: List of deep links
            msg_id: Message ID for logging
            
        Returns:
            Deep link URL
        """
        try:
            if deeplinks and self.neo4j_deeplink:
                # Create a simple deeplink format
                link_params = ','.join(deeplinks[:5])  # Limit to first 5 links
                deeplink_url = f"{self.neo4j_deeplink}?links={link_params}"
                self.logger.info(f"MsgID={msg_id}. [SK KG DEEPLINK] Generated deeplink")
                return deeplink_url
            return ""
        except Exception as e:
            self.logger.error(f"MsgID={msg_id}. [SK KG DEEPLINK] Error: {e}")
            return ""
    
    def retrieve_situational_info(self, msg_id: str = '') -> str:
        """
        Retrieve current date and time.
        
        Args:
            msg_id: Message ID for logging
            
        Returns:
            Formatted date and time string
        """
        try:
            current_time = datetime.now()
            formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
            self.logger.info(f"MsgID={msg_id}. [SK SITUATIONAL INFO] Current time: {formatted_time}")
            return f"Current date and time: {formatted_time}"
        except Exception as e:
            self.logger.error(f"MsgID={msg_id}. [SK SITUATIONAL INFO] Error: {e}")
            return "Unable to retrieve current time"
    
    # Compatibility methods for existing functionality
    
    def query_sefaria_linker(self, text_title="", text_body="", with_text=1, debug=0, max_segments=0, msg_id: str = ''):
        """Compatibility method for Sefaria Linker API (unchanged)."""
        # This method would remain largely the same as it's external API integration
        # For now, return empty result
        self.logger.info(f"MsgID={msg_id}. [SK SEFARIA LINKER] Called with title='{text_title}', body length={len(text_body)}")
        return []
    
    def retrieve_docs_linker(self, screen_res: str, enriched_query: str, msg_id: str = '', filter_mode: str = 'primary'):
        """Compatibility method for linker document retrieval."""
        # This would integrate with Sefaria Linker API
        # For now, return empty list
        self.logger.info(f"MsgID={msg_id}. [SK RETRIEVE DOCS LINKER] Screen res: {screen_res}")
        return []
    
    def topic_ontology(self, extraction: str = '', msgid: str = '', slugs_mode: bool = False):
        """Compatibility method for topic ontology (unchanged)."""
        # This method would remain largely the same as it's external API integration
        if slugs_mode:
            return []
        return {}


def create_sk_havruta(prompts_file: str, config_file: str, logger: logging.Logger) -> VirtualHavrutaSemanticKernel:
    """
    Factory function to create SK-based Virtual Havruta.
    
    Args:
        prompts_file: Path to prompts YAML file
        config_file: Path to configuration YAML file
        logger: Logger instance
        
    Returns:
        SK-based Virtual Havruta instance
    """
    return VirtualHavrutaSemanticKernel(prompts_file, config_file, logger)