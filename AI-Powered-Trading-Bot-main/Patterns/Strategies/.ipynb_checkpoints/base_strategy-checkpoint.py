# Patterns/Strategies/base_strategy.py

from abc import ABC, abstractmethod
import pandas as pd
from typing import Optional, Dict, Any

class BaseStrategy(ABC):
    """
    Tüm ticaret stratejileri için soyut temel sınıf (Abstract Base Class).
    Tüm stratejilerin uygulaması gereken arayüzü tanımlar.
    """
    
    def __init__(self, stop_loss: float):
        """
        Tüm stratejilerin kullanacağı ortak parametreleri başlatır.
        
        Args:
            stop_loss (float): İşlem başına maksimum kabul edilebilir kayıp yüzdesi (0.02 = %2).
        """
        self.stop_loss = stop_loss
        self.strategy_name = self.__class__.__name__

    @abstractmethod
    def execute_strategy(self, 
                         row: pd.Series, 
                         df: pd.DataFrame, 
                         position: float, 
                         entry_price: float) -> str:
        """
        Alım/Satım/Bekle kararını veren ana metot.
        Bu metot tüm alt sınıflar tarafından uygulanmalıdır.

        Args:
            row (pd.Series): Güncel (son) mum verisi.
            df (pd.DataFrame): Tüm geçmiş veri ve indikatörleri içeren DataFrame.
            position (float): Mevcut pozisyon büyüklüğü (0 ise pozisyon yok).
            entry_price (float): Pozisyona giriş fiyatı (pozisyon açıksa).

        Returns:
            str: "Buy", "Sell" veya "Hold" aksiyonlarından biri.
        """
        pass
        
    def check_stop_loss(self, current_price: float, entry_price: float) -> bool:
        """
        Stop Loss kuralını kontrol eder.
        """
        if entry_price <= 0:
            return False
            
        # Zarar yüzdesini hesapla
        loss_pct = (entry_price - current_price) / entry_price
        
        # Eğer zarar, tanımlanan stop_loss yüzdesini aşarsa
        if loss_pct >= self.stop_loss:
            return True
        
        return False