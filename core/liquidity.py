import pandas as pd
import numpy as np
from scipy.signal import argrelextrema

def calculate_liquidity_1h(df_1h: pd.DataFrame) -> pd.DataFrame:
    """Calcula Pivot Highs (BSSL) y Pivot Lows (SSSL) en 1H."""
    # Pivot High de orden 3 a ambos lados
    highs = df_1h['high'].values
    lows = df_1h['low'].values
    
    # Encontramos indices locales
    ph_indices = argrelextrema(highs, np.greater, order=3)[0]
    pl_indices = argrelextrema(lows, np.less, order=3)[0]
    
    ph_series = pd.Series(np.nan, index=df_1h.index)
    ph_series.iloc[ph_indices] = highs[ph_indices]
    
    pl_series = pd.Series(np.nan, index=df_1h.index)
    pl_series.iloc[pl_indices] = lows[pl_indices]
    
    df_1h['ph_btc'] = ph_series
    df_1h['pl_btc'] = pl_series
    
    return df_1h

def map_liquidity_to_5m(df_1h: pd.DataFrame, df_5m: pd.DataFrame) -> pd.DataFrame:
    """Proyecta y gestiona las lineas de liquidez (BSSL/SSSL)."""
    df_mapped = df_1h[['ph_btc', 'pl_btc']].reindex(df_5m.index, method='ffill')
    df_5m['ph_btc'] = df_mapped['ph_btc']
    df_5m['pl_btc'] = df_mapped['pl_btc']
    
    # La gestion dinamica de arreglos en pandas para backtest es compleja.
    # Simularemos c_bssl y c_sssl tomando el Ãºltimo pivot vÃ¡lido no mitigado.
    
    c_bssl = np.full(len(df_5m), np.nan)
    c_sssl = np.full(len(df_5m), np.nan)
    
    active_bssl = []
    active_sssl = []
    
    closes = df_5m['close'].values
    phs = df_5m['ph_btc'].values
    pls = df_5m['pl_btc'].values
    
    for i in range(len(df_5m)):
        # Agregar nuevos pivots
        if not np.isnan(phs[i]) and (len(active_bssl) == 0 or active_bssl[-1] != phs[i]):
            active_bssl.append(phs[i])
        if not np.isnan(pls[i]) and (len(active_sssl) == 0 or active_sssl[-1] != pls[i]):
            active_sssl.append(pls[i])
            
        # Remover mitigados
        active_bssl = [x for x in active_bssl if closes[i] <= x]
        active_sssl = [x for x in active_sssl if closes[i] >= x]
        
        # Encontrar el mas cercano
        if len(active_bssl) > 0:
            c_bssl[i] = min(active_bssl, key=lambda x: x - closes[i])
            
        if len(active_sssl) > 0:
            c_sssl[i] = min(active_sssl, key=lambda x: closes[i] - x)
            
    df_5m['c_bssl'] = c_bssl
    df_5m['c_sssl'] = c_sssl
    
    return df_5m
