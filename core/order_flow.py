import pandas as pd
import numpy as np

def calculate_cvd_1m(df_1m: pd.DataFrame) -> pd.DataFrame:
    """Calcula el delta de volumen barra a barra en 1 minuto."""
    delta = np.where(df_1m['close'] >= df_1m['open'], df_1m['volume'], -df_1m['volume'])
    df_1m['bar_delta'] = delta
    df_1m['cvd'] = df_1m['bar_delta'].cumsum()
    return df_1m

def map_cvd_to_5m(df_1m: pd.DataFrame, df_5m: pd.DataFrame, deep_backtest: bool) -> pd.DataFrame:
    """Agrega CVD a datos de 5m. En backtest profundo simulamos esto con True o 0."""
    if deep_backtest:
        df_5m['bar_delta'] = 0.0
        df_5m['cvd'] = 0.0
        df_5m['cvdRising'] = True
        df_5m['cvdFalling'] = True
        df_5m['volLongOK'] = True
        df_5m['volShortOK'] = True
        return df_5m

    # Agrupamos bar_delta por 5m
    df_1m_resampled = df_1m['bar_delta'].resample('5T').sum().reindex(df_5m.index, method='ffill').fillna(0)
    df_5m['bar_delta'] = df_1m_resampled
    df_5m['cvd'] = df_5m['bar_delta'].cumsum()
    
    # CVD Rising/Falling - comparamos cvd actual vs hace 3 periodos de 5m
    df_5m['cvdRising'] = df_5m['cvd'].diff(3) >= 0
    df_5m['cvdFalling'] = df_5m['cvd'].diff(3) <= 0
    df_5m['volLongOK'] = df_5m['bar_delta'] >= 0
    df_5m['volShortOK'] = df_5m['bar_delta'] < 0
    
    return df_5m

def calculate_daily_vwap_and_vpoc(df_5m: pd.DataFrame) -> pd.DataFrame:
    """Calcula VWAP diario y un aproximado de VPOC (SesiÃ³n) en pandas."""
    df_5m['date'] = df_5m.index.date
    df_5m['hlc3'] = (df_5m['high'] + df_5m['low'] + df_5m['close']) / 3
    df_5m['hlc3_vol'] = df_5m['hlc3'] * df_5m['volume']
    
    # VWAP Diario
    df_5m['cum_vol'] = df_5m.groupby('date')['volume'].cumsum()
    df_5m['cum_hlc3_vol'] = df_5m.groupby('date')['hlc3_vol'].cumsum()
    df_5m['dailyVWAP'] = df_5m['cum_hlc3_vol'] / df_5m['cum_vol']
    
    # VWAP Bullish/Bearish
    df_5m['vwapBullish'] = df_5m['close'] > df_5m['dailyVWAP']
    df_5m['vwapBearish'] = df_5m['close'] < df_5m['dailyVWAP']

    # Aproximacion de VPOC por sesion (dÃ­a) - esto iterara para armar perfil
    # En Python es mas sencillo tomar un rolling de ultimas 300 barras o agrupar por dia.
    # Para ser fieles al script: calcula el VPOC basado en las barras de la sesion actual.
    
    vpoc_list = []
    
    # Group by date to compute rolling or expanding VPOC
    # Para simplificar y mantener velocidad, usamos un VPOC expandido del dÃ­a
    for date, group in df_5m.groupby('date'):
        prices = group['hlc3'].values
        vols = group['volume'].values
        
        # expanding VPOC array
        expanding_vpoc = np.zeros(len(group))
        for i in range(len(group)):
            lookback = max(10, min(i+1, 300))
            start_idx = max(0, i - lookback + 1)
            p_slice = prices[start_idx:i+1]
            v_slice = vols[start_idx:i+1]
            
            vp_hh = np.max(group['high'].values[start_idx:i+1])
            vp_ll = np.min(group['low'].values[start_idx:i+1])
            
            if vp_hh == vp_ll:
                expanding_vpoc[i] = p_slice[-1]
                continue
                
            bins = 40
            bin_size = max((vp_hh - vp_ll) / bins, 0.0001)
            
            # asginar a bins
            bin_indices = np.floor((p_slice - vp_ll) / bin_size).astype(int)
            bin_indices = np.clip(bin_indices, 0, bins - 1)
            
            a_vol = np.zeros(bins)
            for b_idx, vol in zip(bin_indices, v_slice):
                a_vol[b_idx] += vol
                
            best_bin = np.argmax(a_vol)
            vpoc_price = vp_ll + (best_bin * bin_size) + (bin_size / 2)
            expanding_vpoc[i] = vpoc_price
            
        vpoc_list.extend(expanding_vpoc)
        
    df_5m['vpoc'] = vpoc_list
    
    # vpWallBlock
    # atr is needed for this, assuming it will be merged later
    
    return df_5m
