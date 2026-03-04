from abc import ABC, abstractmethod


class Subject(ABC):
    """
    Subject Interface
    Observer'ları yöneten ve bilgilendiren sınıflar için interface
    """
    
    @abstractmethod
    def register_observer(self, observer):
        """Observer ekle"""
        pass

    @abstractmethod
    def remove_observer(self, observer):
        """Observer çıkar"""
        pass

    @abstractmethod
    def notify_observers(self, message: str):
        """Tüm observer'ları bilgilendir"""
        pass

    @abstractmethod
    def set_change(self):
        """Observer'lara bildirim geçilmeden önce değişiklik durumunu işaretle"""
        pass