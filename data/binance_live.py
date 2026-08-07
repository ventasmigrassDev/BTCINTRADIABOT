import json
import asyncio
import websockets
import pandas as pd
from datetime import datetime

class BinanceLiveManager:
    def __init__(self, symbol="BTCUSDT"):
        self.symbol = symbol.lower()
        self.ws_url = f"wss://stream.binance.com:9443/ws/{self.symbol}@kline_1m"
        self.current_1m_kline = {}
        
    async def _handle_messages(self):
        async with websockets.connect(self.ws_url) as ws:
            print(f"Conectado a Binance WS para {self.symbol.upper()}")
            while True:
                try:
                    msg = await ws.recv()
                    data = json.loads(msg)
                    kline = data['k']
                    
                    self.current_1m_kline = {
                        'timestamp': pd.to_datetime(kline['t'], unit='ms'),
                        'open': float(kline['o']),
                        'high': float(kline['h']),
                        'low': float(kline['l']),
                        'close': float(kline['c']),
                        'volume': float(kline['v']),
                        'is_closed': kline['x']
                    }
                    
                    # Aca se emitiria un evento al motor principal para actualizar el tick
                    
                except Exception as e:
                    print(f"Error en websocket: {e}")
                    await asyncio.sleep(5)
                    break
                    
    def run(self):
        # Para ejecucion concurrente o hilo principal
        asyncio.run(self._handle_messages())
