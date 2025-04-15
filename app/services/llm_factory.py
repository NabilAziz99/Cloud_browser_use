from typing import Dict, Any, Type
from abc import ABC, abstractmethod
from langchain_core.language_models.base import BaseLanguageModel

from langchain_openai import ChatOpenAI  # You can replace with any supported LLM


# Abstract Creator
class LLMCreator(ABC):
    """Abstract base class for LLM creators"""
    
    @abstractmethod
    def create_llm(self, **kwargs) -> BaseLanguageModel:
        """Create an LLM instance"""
        pass


# Concrete Creators
class OpenAIChatCreator(LLMCreator):
    """Creator for OpenAI Chat LLMs"""
    
    def create_llm(self, **kwargs) -> BaseLanguageModel:
        return ChatOpenAI(**kwargs)


class LLMFactory:
    """Factory for creating LLM instances from different providers"""
    
    _creators: Dict[str, LLMCreator] = {}
    _cache: Dict[str, BaseLanguageModel] = {}  # Cache for storing instances
    
    @classmethod
    def register_creator(cls, name: str, creator: LLMCreator) -> None:
        """Register a new LLM creator"""
        cls._creators[name.lower()] = creator
    
    @classmethod
    def create_llm(cls, llm_type: str, **kwargs) :
        """
        Create and return an LLM instance based on the specified type
        
        Args:
            llm_type: The type of LLM to create
            **kwargs: Additional arguments to pass to the LLM constructor
            
        Returns:
            An instance of the specified LLM
            
        Raises:
            ValueError: If the specified LLM type is not supported
        """
        llm_type = llm_type.lower()
        
        # Create a cache key from the llm_type and kwargs
        # Sort the kwargs to ensure consistent key generation
        kwargs_str = str(sorted(kwargs.items()))
        cache_key = f"{llm_type}_{kwargs_str}"
        
        # Check if we already have this instance cached
        if cache_key in cls._cache:
            return cls._cache[cache_key]
        
        # Create a new instance if not in cache
        if llm_type in cls._creators:
            creator = cls._creators[llm_type]
            instance = creator.create_llm(**kwargs)
            cls._cache[cache_key] = instance  # Store in cache
            return instance
        else:
            raise ValueError(f"Unsupported LLM type: {llm_type}. Available types: {list(cls._creators.keys())}")
# Register available creators
LLMFactory.register_creator("openai_chat", OpenAIChatCreator())

