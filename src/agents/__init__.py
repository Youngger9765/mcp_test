# src/agents/__init__.py
from abc import ABC, abstractmethod
from typing import List, Dict, Any

class Agent(ABC):
    def __init__(self, 
                 id: str, 
                 name: str, 
                 description: str, 
                 parameters: List[Dict[str, Any]],
                 category: str = "",
                 tags: List[str] = None,
                 example_queries: List[str] = None,
                 request_example: Dict[str, Any] = None,
                 response_example: Dict[str, Any] = None,
                 icon: str = "",
                 author: str = "",
                 version: str = ""):
        self.id = id
        self.name = name
        self.description = description
        self.parameters = parameters
        self.category = category
        self.tags = tags if tags is not None else []
        self.example_queries = example_queries if example_queries is not None else []
        self.request_example = request_example
        self.response_example = response_example
        self.icon = icon
        self.author = author
        self.version = version

    @abstractmethod
    def respond(self, **kwargs) -> Dict[str, Any]:
        '''
        Process the request and return a response.
        Subclasses must implement this method.
        '''
        raise NotImplementedError("Subclasses must implement the respond method.")

    def get_metadata(self) -> Dict[str, Any]:
        """Returns the agent's metadata as a dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters,
            "category": self.category,
            "tags": self.tags,
            "example_queries": self.example_queries,
            "request_example": self.request_example,
            "response_example": self.response_example,
            "icon": self.icon,
            "author": self.author,
            "version": self.version,
        }
