import sys
import os
import time
import datetime

# Configuracion de paths para imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data.binance_live import BinanceLiveManager

def run_live():
    print("========================================")
    print("Iniciando Motor de Trading en Vivo")
    print("PRO Intraday Top-Down v1.4.2 (Python)")
    print("========================================")
    print("ADVERTENCIA: ESTE ES EL ENTORNO DE PRODUCCION.")
    
    # 1. Instanciar el gestor de WebSockets (para leer CVD en 1m)
    # ws_manager = BinanceLiveManager(symbol="BTCUSDT")
    # ws_manager.run() # Esto deberia correr en un hilo separado
    
    print("[INFO] Motor iniciado. Esperando cierres de vela de 5 minutos...")
    
    # Bucle principal de ejecucion
    try:
        while True:
            current_time = datetime.datetime.now()
            
            # Chequear si estamos en el cierre de una vela de 5 minutos
            # (ej: 10:00, 10:05, 10:10)
            if current_time.minute % 5 == 0 and current_time.second == 0:
                print(f"[{current_time.strftime('%Y-%m-%d %H:%M:%S')}] Cierre de vela de 5m detectado. Ejecutando analisis Top-Down...")
                
                # AQUI VA LA LOGICA DEL BOT CADA 5 MINUTOS:
                # 1. Obtener datos historicos recientes (1m, 5m, 15m, 1H, 4H, 1D)
                # 2. Calcular indicadores (SMC, BSSL/SSSL, VWAP, CVD)
                # 3. Validar reglas de la estrategia
                # 4. Generar senales
                # 5. Ejecutar ordenes en Binance si hay trigger
                
                print("[INFO] Analisis completado. Buscando POI...")
                
                # Dormir 1 minuto para evitar multiples ejecuciones en el mismo minuto 00
                time.sleep(60)
            else:
                # Dormir 1 segundo y volver a chequear
                time.sleep(1)
                
    except KeyboardInterrupt:
        print("\n[INFO] Apagando Motor de Trading en Vivo. Hasta luego!")

if __name__ == "__main__":
    run_live()
