import pandas as pd

def resample_1m_to_tf(df_1m: pd.DataFrame, rule: str) -> pd.DataFrame:
    """Remuestrea velas de 1m a otra temporalidad (ej. '5T', '15T', '60T', 'D')."""
    # Agrupacion estandar OHLCV
    ohlc_dict = {
        'open': 'first',
        'high': 'max',
        'low': 'min',
        'close': 'last',
        'volume': 'sum'
    }
    df_resampled = df_1m.resample(rule).agg(ohlc_dict).dropna()
    return df_resampled
    
def generate_mtf_dataframes(df_1m: pd.DataFrame):
    """Genera todos los dataframes requeridos por el Top-Down."""
    
    # Validacion: debe tener indice datetime
    if not isinstance(df_1m.index, pd.DatetimeIndex):
        raise ValueError("df_1m index must be DatetimeIndex")
        
    df_5m = resample_1m_to_tf(df_1m, '5T')
    df_15m = resample_1m_to_tf(df_1m, '15T')
    df_1h = resample_1m_to_tf(df_1m, '60T')
    df_4h = resample_1m_to_tf(df_1m, '240T')
    df_1d = resample_1m_to_tf(df_1m, 'D')
    
    return df_5m, df_15m, df_1h, df_4h, df_1d

def map_macro_trend_to_5m(df_5m: pd.DataFrame, df_1d: pd.DataFrame, df_4h: pd.DataFrame) -> pd.DataFrame:
    """Proyecta las EMA 200 de 1D y EMA 50 de 4H al de 5m."""
    
    # 4H trend
    import core.indicators as ind
    
    df_4h['ema50'] = ind.calculate_ema(df_4h['close'], 50)
    df_4h_mapped = df_4h['ema50'].reindex(df_5m.index, method='ffill')
    df_5m['h4_ema50'] = df_4h_mapped
    
    df_5m['isMacroBullish'] = (df_5m['close'] > df_5m['h4_ema50']) & df_5m['h4_ema50'].notna()
    df_5m['isMacroBearish'] = (df_5m['close'] < df_5m['h4_ema50']) & df_5m['h4_ema50'].notna()
    
    # 1D Equilibrium
    # En Pine Script se usÃ³ high[1] y low[1] del timeframe diario para discount/premium
    df_1d['d_high_prev'] = df_1d['high'].shift(1)
    df_1d['d_low_prev'] = df_1d['low'].shift(1)
    df_1d['d_ema200'] = ind.calculate_ema(df_1d['close'], 200)
    
    df_1d_mapped = df_1d[['d_high_prev', 'd_low_prev', 'd_ema200']].reindex(df_5m.index.normalize(), method='ffill')
    df_1d_mapped.index = df_5m.index.normalize() # ensures alignment if needed, but safer to use map
    
    df_5m['d_high_prev'] = df_5m.index.normalize().map(df_1d['d_high_prev']).fillna(method='ffill')
    df_5m['d_low_prev'] = df_5m.index.normalize().map(df_1d['d_low_prev']).fillna(method='ffill')
    df_5m['d_ema200'] = df_5m.index.normalize().map(df_1d['d_ema200']).fillna(method='ffill')
    
    df_5m['isDiscount'] = df_5m['close'] <= ((df_5m['d_high_prev'] + df_5m['d_low_prev']) / 2.0)
    
    return df_5m
