import pandas as pd
import pandas_ta as ta

def calculate_atr(df: pd.DataFrame, length: int = 14) -> pd.Series:
    """Calcula el ATR y lo agrega a la serie"""
    atr = ta.atr(df['high'], df['low'], df['close'], length=length)
    return atr

def calculate_ma_atr(atr_series: pd.Series, length: int = 100) -> pd.Series:
    """Calcula la media movil del ATR"""
    return ta.sma(atr_series, length=length)

def calculate_ema(close_series: pd.Series, length: int) -> pd.Series:
    """Calcula la EMA (Exponential Moving Average)"""
    return ta.ema(close_series, length=length)

def check_volatility_filter(atr: pd.Series, ma_atr: pd.Series, use_vol_filt: bool = True) -> pd.Series:
    """Filtro de volatilidad (atr >= ma_atr * 0.70)"""
    if not use_vol_filt:
        return pd.Series(True, index=atr.index)
    return atr >= (ma_atr * 0.70)
