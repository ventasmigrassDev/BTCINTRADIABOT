import pandas as pd

def generate_signals(df: pd.DataFrame, use_session_filt: bool, session_start: int, session_end: int) -> pd.DataFrame:
    """Combina todas las logicas y genera las seÃ±ales M1 y Ejecucion."""
    
    # VP Wall Block
    # bool vpWallBlockLong  = (vpoc > close) and (vpoc - close < atr * 0.1) 
    # bool vpWallBlockShort = (vpoc < close) and (close - vpoc < atr * 0.1)
    df['vpWallBlockLong'] = (df['vpoc'] > df['close']) & ((df['vpoc'] - df['close']) < (df['atr'] * 0.1))
    df['vpWallBlockShort'] = (df['vpoc'] < df['close']) & ((df['close'] - df['vpoc']) < (df['atr'] * 0.1))
    
    # Session Filter
    if use_session_filt:
        df['sessionOK'] = (df.index.hour >= session_start) & (df.index.hour < session_end)
    else:
        df['sessionOK'] = True
        
    # Pre-alerts
    df['preAlertLong'] = df['inDemZone'] & df['cvdRising'] & df['volLongOK']
    df['preAlertShort'] = df['inSupZone'] & df['cvdFalling'] & df['volShortOK']
    
    # M1 Strict Conditions
    df['m1_Long'] = df['isMacroBullish'] & df['volLongOK'] & df['cvdRising'] & df['inExtDem'] & df['vwapBullish'] & ~df['vetoLong']
    df['m1_Short'] = df['isMacroBearish'] & df['volShortOK'] & df['cvdFalling'] & df['inExtSup'] & df['vwapBearish'] & ~df['vetoShort']
    
    # Triggers
    df['triLong'] = df['m1_Long'] & ~df['vpWallBlockLong'] & df['volIsOK'] & df['sessionOK']
    df['triShort'] = df['m1_Short'] & ~df['vpWallBlockShort'] & df['volIsOK'] & df['sessionOK']
    
    return df
