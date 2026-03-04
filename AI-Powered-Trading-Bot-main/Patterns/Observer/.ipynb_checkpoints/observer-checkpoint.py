from abc import ABC, abstractmethod


class Observer(ABC):
    """
    Observer Interface
    Subject'ten gelen güncellemeleri alan sınıflar için interface
    """
    
    @abstractmethod
    def update(self, message: str):
        """
        Subject'ten gelen mesajları işle
        
        Args:
            message (str): Subject'ten gelen bildirim mesajı
        """
        pass