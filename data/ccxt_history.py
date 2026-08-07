import ccxt
import pandas as pd
import time

def fetch_historical_data_1m(symbol: str, since: str, limit: int = 1000) -> pd.DataFrame:
    """Descarga datos historicos de Binance usando CCXT."""
    exchange = ccxt.binance({
        'enableRateLimit': True,
    })
    
    since_timestamp = exchange.parse8601(since)
    all_ohlcv = []
    
    print(f"Descargando historico para {symbol} desde {since}...")
    
    while True:
        try:
            ohlcv = exchange.fetch_ohlcv(symbol, '1m', since_timestamp, limit)
            if not ohlcv:
                break
                
            all_ohlcv.extend(ohlcv)
            since_timestamp = ohlcv[-1][0] + 60000 # avanzamos 1 minuto
            
            # Si trajimos menos del limite, significa que ya llegamos al presente
            if len(ohlcv) < limit:
                break
                
        except Exception as e:
            print(f"Error fetching data: {e}. Retrying in 5s...")
            time.sleep(5)
            
    df = pd.DataFrame(all_ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)
    
    # Drop duplicates just in case
    df = df[~df.index.duplicated(keep='first')]
    
    print(f"Descargadas {len(df)} velas de 1m.")
    return df
