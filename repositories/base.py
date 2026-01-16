"""Base repository interface"""
from abc import ABC, abstractmethod
from typing import Any, Optional, Dict


class Repository(ABC):
    """Abstract base class for all repositories"""
    
    @abstractmethod
    def save(self, key: str, data: Any) -> bool:
        """Save data"""
        pass
    
    @abstractmethod
    def load(self, key: str) -> Optional[Any]:
        """Load data"""
        pass
    
    @abstractmethod
    def delete(self, key: str) -> bool:
        """Delete data"""
        pass
    
    @abstractmethod
    def load_all(self) -> Dict[str, Any]:
        """Load all data"""
        pass
