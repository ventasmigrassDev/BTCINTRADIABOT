import sys
import os
import time

# Configuracion de paths para imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data.binance_live import BinanceLiveManager

def run_live():
    print("========================================")
    print("Iniciando Motor de Trading en Vivo")
    print("PRO Intraday Top-Down v1.4.2 (Python)")
    print("========================================")
    print("ADVERTENCIA: ESTE ES EL ENTORNO DE PRODUCCION.")
    
    # 1. Instanciar el gestor de WebSockets
    # ws_manager = BinanceLiveManager(symbol="BTCUSDT")
    
    # 2. Bucle principal de ejecucion
    # Aqui se conectaria el WS con el motor logico
    # ws_manager.run()
    
    print("Servicio Live detenido. Para implementar ejecucion real configure sus API Keys en .env y active el modulo binance_live.")

if __name__ == "__main__":
    run_live()
