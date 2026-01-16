"""Storage abstraction interface"""
from abc import ABC, abstractmethod
from typing import Any, Optional


class Storage(ABC):
    """Abstract storage interface following Strategy Pattern"""
    
    @abstractmethod
    def save(self, key: str, data: Any) -> bool:
        """
        Save data to storage
        
        Args:
            key: Data key/identifier
            data: Data to save
            
        Returns:
            bool: True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def load(self, key: str) -> Optional[Any]:
        """
        Load data from storage
        
        Args:
            key: Data key/identifier
            
        Returns:
            Data if found, None otherwise
        """
        pass
    
    @abstractmethod
    def delete(self, key: str) -> bool:
        """
        Delete data from storage
        
        Args:
            key: Data key/identifier
            
        Returns:
            bool: True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if storage is available
        
        Returns:
            bool: True if storage is connected and ready
        """
        pass
