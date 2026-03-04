from abc import ABC, abstractmethod
from sklearn.ensemble import RandomForestClassifier
import pandas as pd
from typing import final


class TradingStrategyTemplate(ABC):
    """
    TEMPLATE METHOD PATTERN:
    Ana algoritma iskeletini tanımlar, alt sınıflar sadece belirli adımları override eder.
    """
    
    def __init__(self, stop_loss: float):
        """
        Initialize the trading strategy with stop_loss and model.
        
        Args:
            stop_loss (float): Stop loss percentage (örn: 0.02 = %2)
        """
        self.stop_loss = stop_loss
        self.model = RandomForestClassifier(
            class_weight='balanced',
            n_estimators=100,
            random_state=42
        )
        self.is_trained = False
    
    @final
    def execute_strategy(self, row: pd.Series, df: pd.DataFrame) -> str:
        """
        TEMPLATE METHOD: Ana algoritma - değiştirilemez.
        
        İş akışı:
        1. Veriyi etiketle
        2. Modeli eğit (eğer eğitilmemişse)
        3. Özellikleri çıkar
        4. Karar ver
        
        Args:
            row (pd.Series): Mevcut satır (tahmin için)
            df (pd.DataFrame): Tüm veri (eğitim için)
            
        Returns:
            str: "Buy", "Sell" veya "Hold"
        """
        # Step 1: Label data
        if not self.is_trained:
            df_labeled = self.label_data(df.copy())
            
            # Step 2: Train the model
            self.train_model(df_labeled)
            self.is_trained = True

        # Step 3: Extract features for prediction
        features = self._get_features(row)

        # Step 4: Decide action
        action = self.decide_action(features)
        return action

    @abstractmethod
    def label_logic(self, row: pd.Series) -> str:
        """
        Abstract method: Alt sınıflar kendi etiketleme mantığını sağlamalı.
        
        Args:
            row (pd.Series): Veri satırı
            
        Returns:
            str: "Buy", "Sell" veya "Hold"
        """
        pass

    @abstractmethod
    def feature_columns(self) -> list:
        """
        Abstract method: Alt sınıflar kullanacakları feature'ları tanımlamalı.
        
        Returns:
            list: Feature sütun isimleri
        """
        pass

    def decide_action(self, features: pd.DataFrame) -> str:
        """
        Ortak karar verme mantığı - model tahminini kullanır.
        
        Args:
            features (pd.DataFrame): Tahmin için özellikler
            
        Returns:
            str: Tahmin edilen aksiyon
        """
        if not self.is_trained:
            return "Hold"
        
        prediction = self.model.predict(features)[0]
        print(f"📊 Predicted action: {prediction}")
        return prediction

    def label_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Tüm veri setine etiket uygula.
        
        Args:
            df (pd.DataFrame): Etiketlenecek veri
            
        Returns:
            pd.DataFrame: Etiketlenmiş veri
        """
        labels = [self.label_logic(row) for _, row in df.iterrows()]
        df['Action'] = labels
        return df

    def train_model(self, df: pd.DataFrame) -> None:
        """
        Modeli eğit.
        
        Args:
            df (pd.DataFrame): Eğitim verisi (Action sütunu içermeli)
        """
        features_list = self.feature_columns()
        
        # Ensure all required columns exist
        missing_cols = set(features_list) - set(df.columns)
        if missing_cols:
            raise ValueError(f"❌ Missing columns: {missing_cols}")
        
        X = df[features_list]
        y = df['Action']
        
        # Remove any NaN values
        mask = ~(X.isna().any(axis=1) | y.isna())
        X = X[mask]
        y = y[mask]
        
        if len(X) == 0:
            raise ValueError("❌ No valid training data after removing NaN values")
        
        self.model.fit(X, y)
        print(f"✅ Model trained with {len(X)} samples using {self.__class__.__name__}")

    def _get_features(self, row: pd.Series) -> pd.DataFrame:
        """
        Tahmin için özellikleri DataFrame olarak çıkar.
        
        Args:
            row (pd.Series): Veri satırı
            
        Returns:
            pd.DataFrame: Feature DataFrame (1 satır)
        """
        features_list = self.feature_columns()
        return pd.DataFrame([row[features_list]], columns=features_list)

    def get_strategy_name(self) -> str:
        """Strategy adını döndür"""
        return self.__class__.__name__