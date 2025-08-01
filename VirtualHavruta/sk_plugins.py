"""
Semantic Kernel plugins to replace LangChain chains.
This module contains SK function implementations for all the LLM operations.
"""

import asyncio
from typing import Any, Dict, List, Optional, Tuple, Union
import logging
import json
import yaml

# Import Semantic Kernel dependencies 
# Note: We'll implement a compatibility layer if SK is not available
try:
    from semantic_kernel import Kernel
    from semantic_kernel.functions import kernel_function
    from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
    from semantic_kernel.connectors.ai.open_ai import OpenAITextEmbedding
    from semantic_kernel.prompt_template import PromptTemplateConfig
    from semantic_kernel.memory import SemanticTextMemory
    from semantic_kernel.memory.memory_stores import VolatileMemoryStore
    SEMANTIC_KERNEL_AVAILABLE = True
except ImportError:
    # Fallback implementations for development/testing
    SEMANTIC_KERNEL_AVAILABLE = False
    
    class MockKernel:
        def __init__(self):
            self.services = {}
            self.plugins = {}
            
        def add_service(self, service_type, service):
            self.services[service_type] = service
            
        def add_plugin(self, plugin, plugin_name=None):
            self.plugins[plugin_name or plugin.__class__.__name__] = plugin
            
        async def invoke(self, function_name, **kwargs):
            # Mock implementation
            return f"Mock response for {function_name}"
    
    def kernel_function(name=None, description=None):
        def decorator(func):
            func._sk_function_name = name or func.__name__
            func._sk_function_description = description
            return func
        return decorator
    
    Kernel = MockKernel


class VirtualHavrutaSemanticKernelPlugin:
    """
    Main plugin class that contains all the SK functions replacing LangChain chains.
    """
    
    def __init__(self, config: Dict[str, Any], prompts: Dict[str, Any], logger: logging.Logger):
        """
        Initialize the SK plugin with configuration and prompts.
        
        Args:
            config: Configuration dictionary from config.yaml
            prompts: Prompts dictionary from prompts.yaml  
            logger: Logger instance
        """
        self.config = config
        self.prompts = prompts
        self.logger = logger
        self.kernel = None
        self._initialize_kernel()
    
    def _initialize_kernel(self):
        """Initialize the Semantic Kernel with OpenAI services."""
        self.kernel = Kernel()
        
        if SEMANTIC_KERNEL_AVAILABLE:
            # Add OpenAI chat completion service
            api_key = self.config.get("openai_model_api", {}).get("api_key")
            main_model = self.config.get("openai_model_api", {}).get("main_model", "gpt-3.5-turbo")
            support_model = self.config.get("openai_model_api", {}).get("support_model", "gpt-3.5-turbo")
            embedding_model = self.config.get("openai_model_api", {}).get("embedding_model", "text-embedding-ada-002")
            
            # Add chat completion services
            self.kernel.add_service(
                OpenAIChatCompletion(
                    service_id="main_chat",
                    ai_model_id=main_model,
                    api_key=api_key
                )
            )
            
            self.kernel.add_service(
                OpenAIChatCompletion(
                    service_id="support_chat", 
                    ai_model_id=support_model,
                    api_key=api_key
                )
            )
            
            # Add embedding service
            self.kernel.add_service(
                OpenAITextEmbedding(
                    service_id="embedding",
                    ai_model_id=embedding_model,
                    api_key=api_key
                )
            )
        
        # Register this plugin with the kernel
        self.kernel.add_plugin(self, "VirtualHavruta")
    
    @kernel_function(
        description="Analyzes a query for potential attacks or harmful content",
        name="anti_attack"
    )
    async def anti_attack(self, query: str, msg_id: str = "") -> str:
        """
        Analyzes a query for potential attacks using SK function.
        
        Args:
            query: The input query to analyze
            msg_id: Message ID for logging
            
        Returns:
            JSON string with detection result and explanation
        """
        system_prompt = self.prompts.get("system", {}).get("anti_attack", "Analyze this query for potential attacks.")
        
        prompt = f"""
        {system_prompt}
        
        Query: {query}
        
        Please respond with a JSON object containing:
        - detection: "Y" or "N" for whether an attack was detected
        - explanation: Brief explanation of the analysis
        """
        
        try:
            if SEMANTIC_KERNEL_AVAILABLE:
                result = await self.kernel.invoke(
                    "main_chat",
                    user_message=prompt
                )
                response = str(result)
            else:
                # Mock response for development
                response = '{"detection": "N", "explanation": "No attack detected in mock mode"}'
            
            self.logger.info(f"MsgID={msg_id}. [SK ANTI-ATTACK] Query={query}. Result={response}")
            return response
            
        except Exception as e:
            self.logger.error(f"MsgID={msg_id}. [SK ANTI-ATTACK] Error: {e}")
            return '{"detection": "N", "explanation": "Error in analysis"}'
    
    @kernel_function(
        description="Adapts and enriches a query for better processing", 
        name="adaptor"
    )
    async def adaptor(self, query: str, msg_id: str = "") -> str:
        """
        Adapts a query using SK function.
        
        Args:
            query: The input query to adapt
            msg_id: Message ID for logging
            
        Returns:
            Adapted query text
        """
        system_prompt = self.prompts.get("system", {}).get("adaptor", "Adapt and improve this query.")
        
        prompt = f"""
        {system_prompt}
        
        Query: {query}
        
        Please provide an adapted version of this query that is more suitable for retrieval and processing.
        """
        
        try:
            if SEMANTIC_KERNEL_AVAILABLE:
                result = await self.kernel.invoke(
                    "support_chat",
                    user_message=prompt
                )
                response = str(result)
            else:
                response = f"Adapted: {query}"
            
            self.logger.info(f"MsgID={msg_id}. [SK ADAPTOR] Query={query}. Result={response}")
            return response
            
        except Exception as e:
            self.logger.error(f"MsgID={msg_id}. [SK ADAPTOR] Error: {e}")
            return query  # Return original query on error
    
    @kernel_function(
        description="Edits and improves query text",
        name="editor"
    )
    async def editor(self, query: str, msg_id: str = "") -> str:
        """
        Edits a query using SK function.
        
        Args:
            query: The input query to edit
            msg_id: Message ID for logging
            
        Returns:
            Edited query text
        """
        system_prompt = self.prompts.get("system", {}).get("editor", "Edit and improve this query.")
        
        prompt = f"""
        {system_prompt}
        
        Query: {query}
        
        Please provide an edited version of this query with improved clarity and structure.
        """
        
        try:
            if SEMANTIC_KERNEL_AVAILABLE:
                result = await self.kernel.invoke(
                    "support_chat",
                    user_message=prompt
                )
                response = str(result)
            else:
                response = f"Edited: {query}"
            
            self.logger.info(f"MsgID={msg_id}. [SK EDITOR] Query={query}. Result={response}")
            return response
            
        except Exception as e:
            self.logger.error(f"MsgID={msg_id}. [SK EDITOR] Error: {e}")
            return query
    
    @kernel_function(
        description="Optimizes query with translation, extraction, elaboration, etc.",
        name="optimizer"
    )
    async def optimizer(self, query: str, msg_id: str = "") -> str:
        """
        Optimizes a query using SK function.
        
        Args:
            query: The input query to optimize
            msg_id: Message ID for logging
            
        Returns:
            JSON string with optimization components
        """
        system_prompt = self.prompts.get("system", {}).get("optimization", "Optimize this query with various components.")
        
        prompt = f"""
        {system_prompt}
        
        Query: {query}
        
        Please respond with a JSON object containing:
        - translation: Any translation needed
        - extraction: Key topics/concepts extracted
        - elaboration: Expanded explanation  
        - quotation: Relevant quotations if any
        - challenge: Potential challenges/questions
        - proposal: Proposed improvements
        """
        
        try:
            if SEMANTIC_KERNEL_AVAILABLE:
                result = await self.kernel.invoke(
                    "main_chat",
                    user_message=prompt
                )
                response = str(result)
            else:
                response = json.dumps({
                    "translation": "",
                    "extraction": f"Key topics from: {query}",
                    "elaboration": f"Elaborated: {query}",
                    "quotation": "",
                    "challenge": "",
                    "proposal": ""
                })
            
            self.logger.info(f"MsgID={msg_id}. [SK OPTIMIZER] Query={query}. Result={response}")
            return response
            
        except Exception as e:
            self.logger.error(f"MsgID={msg_id}. [SK OPTIMIZER] Error: {e}")
            return json.dumps({"translation": "", "extraction": "", "elaboration": "", "quotation": "", "challenge": "", "proposal": ""})
    
    @kernel_function(
        description="Performs question-answering with reference data",
        name="qa"
    )
    async def qa(self, query: str, ref_data: str, msg_id: str = "") -> str:
        """
        Performs question-answering using SK function.
        
        Args:
            query: The question to answer
            ref_data: Reference data/context
            msg_id: Message ID for logging
            
        Returns:
            Answer text
        """
        system_prompt = self.prompts.get("system", {}).get("qa", "Answer the question based on the provided reference data.")
        
        prompt = f"""
        {system_prompt}
        
        Question: {query}
        
        Reference Data: {ref_data}
        
        Please provide a comprehensive answer based on the reference data provided.
        """
        
        try:
            if SEMANTIC_KERNEL_AVAILABLE:
                result = await self.kernel.invoke(
                    "main_chat",
                    user_message=prompt
                )
                response = str(result)
            else:
                response = f"Answer to '{query}' based on provided references."
            
            self.logger.info(f"MsgID={msg_id}. [SK QA] Query={query}. RefData length={len(ref_data)}. Result={response}")
            return response
            
        except Exception as e:
            self.logger.error(f"MsgID={msg_id}. [SK QA] Error: {e}")
            return "I apologize, but I encountered an error while processing your question."
    
    @kernel_function(
        description="Selects relevant references from retrieval results",
        name="selector"
    )
    async def selector(self, query: str, ref_data: str, msg_id: str = "") -> str:
        """
        Selects useful references using SK function.
        
        Args:
            query: The original query
            ref_data: Retrieved reference data
            msg_id: Message ID for logging
            
        Returns:
            Selected references
        """
        system_prompt = self.prompts.get("system", {}).get("selector", "Select the most relevant references for the query.")
        
        prompt = f"""
        {system_prompt}
        
        Query: {query}
        
        Available References: {ref_data}
        
        Please select and return the most relevant references for answering the query.
        """
        
        try:
            if SEMANTIC_KERNEL_AVAILABLE:
                result = await self.kernel.invoke(
                    "support_chat",
                    user_message=prompt
                )
                response = str(result)
            else:
                response = ref_data  # Return all refs in mock mode
            
            self.logger.info(f"MsgID={msg_id}. [SK SELECTOR] Query={query}. Selected refs length={len(response)}")
            return response
            
        except Exception as e:
            self.logger.error(f"MsgID={msg_id}. [SK SELECTOR] Error: {e}")
            return ref_data  # Return original refs on error
    
    @kernel_function(
        description="Classifies references by type and relevance",
        name="classification"
    )
    async def classification(self, query: str, ref_data: str, msg_id: str = "") -> str:
        """
        Classifies references using SK function.
        
        Args:
            query: The original query
            ref_data: Reference data to classify
            msg_id: Message ID for logging
            
        Returns:
            Classification results
        """
        system_prompt = self.prompts.get("system", {}).get("classification", "Classify these references by type and relevance.")
        
        prompt = f"""
        {system_prompt}
        
        Query: {query}
        
        References to Classify: {ref_data}
        
        Please classify these references by type and relevance to the query.
        """
        
        try:
            if SEMANTIC_KERNEL_AVAILABLE:
                result = await self.kernel.invoke(
                    "support_chat", 
                    user_message=prompt
                )
                response = str(result)
            else:
                response = "Primary reference classification"
            
            self.logger.info(f"MsgID={msg_id}. [SK CLASSIFICATION] Query={query}. Classification={response}")
            return response
            
        except Exception as e:
            self.logger.error(f"MsgID={msg_id}. [SK CLASSIFICATION] Error: {e}")
            return "primary"  # Default classification
    
    async def get_embedding(self, text: str) -> List[float]:
        """
        Get embeddings for text using SK embedding service.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
        """
        try:
            if SEMANTIC_KERNEL_AVAILABLE:
                embedding_service = self.kernel.get_service("embedding")
                embeddings = await embedding_service.generate_embeddings([text])
                return embeddings[0] if embeddings else []
            else:
                # Return mock embedding
                import random
                return [random.random() for _ in range(1536)]
                
        except Exception as e:
            self.logger.error(f"[SK EMBEDDING] Error: {e}")
            return []


def create_semantic_kernel_plugin(config: Dict[str, Any], prompts: Dict[str, Any], logger: logging.Logger) -> VirtualHavrutaSemanticKernelPlugin:
    """
    Factory function to create the Semantic Kernel plugin.
    
    Args:
        config: Configuration dictionary
        prompts: Prompts dictionary
        logger: Logger instance
        
    Returns:
        Initialized SK plugin
    """
    return VirtualHavrutaSemanticKernelPlugin(config, prompts, logger)


# Utility function to run async functions in sync context
def run_async(coroutine):
    """Run an async function in a sync context."""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(coroutine)