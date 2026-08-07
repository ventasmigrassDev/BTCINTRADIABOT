import pandas as pd
import numpy as np

def calculate_smc_15m(df_15m: pd.DataFrame) -> pd.DataFrame:
    """Calcula Cajas de Order Blocks y FVG en la temporalidad de 15m."""
    # Para ser eficientes sin usar bucles for en cada fila, crearemos columnas shifted.
    
    highs = df_15m['high'].values
    lows = df_15m['low'].values
    opens = df_15m['open'].values
    closes = df_15m['close'].values
    n = len(df_15m)
    
    eBT, eBB = np.full(n, np.nan), np.full(n, np.nan)
    eRT, eRB = np.full(n, np.nan), np.full(n, np.nan)
    dBT, dBB = np.full(n, np.nan), np.full(n, np.nan)
    dRT, dRB = np.full(n, np.nan), np.full(n, np.nan)
    fDT, fDB = np.full(n, np.nan), np.full(n, np.nan)
    fST, fSB = np.full(n, np.nan), np.full(n, np.nan)

    # Nota: Esta es una implementacion simplificada del loop de 40 barras del Pine Script.
    # Para backtesting vectorizado exacto usaremos un rolling apply, pero para mantener 
    # la legibilidad lo haremos fila por fila para un histÃ³rico rÃ¡pido (numba/cython es mejor, pero usamos np).
    
    # FVG es mÃ¡s facil (3 barras)
    for i in range(2, n):
        # FVG Bullish (Demanda): high[2] < low[0] (en Python: i-2 y i)
        if highs[i-2] < lows[i]:
            fDT[i] = lows[i]
            fDB[i] = highs[i-2]
        else:
            fDT[i] = fDT[i-1]
            fDB[i] = fDB[i-1]
            
        # FVG Bearish (Oferta): low[2] > high[0]
        if lows[i-2] > highs[i]:
            fST[i] = lows[i-2]
            fSB[i] = highs[i]
        else:
            fST[i] = fST[i-1]
            fSB[i] = fSB[i-1]

    # Para Order Blocks (Extreme y Decisional) se necesita lÃ³gica lookback. 
    # Mantenemos las variables activas hasta que se rompen.
    for i in range(40, n):
        # Extreme Bullish OB
        lookback_lows = lows[i-40:i]
        ext_idx = np.argmin(lookback_lows) + (i - 40)
        
        o_top, o_bot = np.nan, np.nan
        for j in range(ext_idx, min(ext_idx + 6, i+1)):
            if closes[j] > opens[j]: # Vela alcista envolvente
                o_top = max(opens[j], closes[j])
                o_bot = lows[j]
                break
        eBT[i] = o_top
        eBB[i] = o_bot

        # Extreme Bearish OB
        lookback_highs = highs[i-40:i]
        ext_h_idx = np.argmax(lookback_highs) + (i - 40)
        
        o_top_r, o_bot_r = np.nan, np.nan
        for j in range(ext_h_idx, min(ext_h_idx + 6, i+1)):
            if closes[j] < opens[j]: # Vela bajista envolvente
                o_top_r = highs[j]
                o_bot_r = min(opens[j], closes[j])
                break
        eRT[i] = o_top_r
        eRB[i] = o_bot_r

        # Decisional Bullish (5 barras)
        d_top, d_bot = np.nan, np.nan
        for j in range(i-5, i):
            if closes[j] > opens[j]:
                d_top = max(opens[j], closes[j])
                d_bot = lows[j]
                break
        dBT[i] = d_top
        dBB[i] = d_bot
        
        # Decisional Bearish
        d_top_r, d_bot_r = np.nan, np.nan
        for j in range(i-5, i):
            if closes[j] < opens[j]:
                d_top_r = highs[j]
                d_bot_r = min(opens[j], closes[j])
                break
        dRT[i] = d_top_r
        dRB[i] = d_bot_r

    df_15m['eBullT'] = eBT
    df_15m['eBullB'] = eBB
    df_15m['eBearT'] = eRT
    df_15m['eBearB'] = eRB
    
    df_15m['dBullT'] = dBT
    df_15m['dBullB'] = dBB
    df_15m['dBearT'] = dRT
    df_15m['dBearB'] = dRB
    
    df_15m['fvgDT'] = fDT
    df_15m['fvgDB'] = fDB
    df_15m['fvgST'] = fST
    df_15m['fvgSB'] = fSB

    return df_15m

def map_smc_to_5m(df_15m: pd.DataFrame, df_5m: pd.DataFrame) -> pd.DataFrame:
    """Proyecta los niveles de SMC de 15m al dataframe de 5m."""
    cols = ['eBullT', 'eBullB', 'eBearT', 'eBearB', 'dBullT', 'dBullB', 'dBearT', 'dBearB', 'fvgDT', 'fvgDB', 'fvgST', 'fvgSB']
    # forward fill from 15m to 5m
    df_mapped = df_15m[cols].reindex(df_5m.index, method='ffill')
    for c in cols:
        df_5m[c] = df_mapped[c]
        
    # Evaluar si esta dentro de las zonas
    # inExtDem = not na(eBullT) and low <= eBullT and close >= eBullB
    df_5m['inExtDem'] = (df_5m['low'] <= df_5m['eBullT']) & (df_5m['close'] >= df_5m['eBullB']) & df_5m['eBullT'].notna()
    df_5m['inDecDem'] = (df_5m['low'] <= df_5m['dBullT']) & (df_5m['close'] >= df_5m['dBullB']) & df_5m['dBullT'].notna()
    df_5m['inFvgDem'] = (df_5m['low'] <= df_5m['fvgDT']) & (df_5m['close'] >= df_5m['fvgDB']) & df_5m['fvgDT'].notna()
    df_5m['inDemZone'] = df_5m['inExtDem'] | df_5m['inDecDem'] | df_5m['inFvgDem']
    
    df_5m['inExtSup'] = (df_5m['high'] >= df_5m['eBearB']) & (df_5m['close'] <= df_5m['eBearT']) & df_5m['eBearT'].notna()
    df_5m['inDecSup'] = (df_5m['high'] >= df_5m['dBearB']) & (df_5m['close'] <= df_5m['dBearT']) & df_5m['dBearT'].notna()
    df_5m['inFvgSup'] = (df_5m['high'] >= df_5m['fvgSB']) & (df_5m['close'] <= df_5m['fvgST']) & df_5m['fvgST'].notna()
    df_5m['inSupZone'] = df_5m['inExtSup'] | df_5m['inDecSup'] | df_5m['inFvgSup']
    
    return df_5m
