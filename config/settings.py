# config/settings.py

# =========================================================================================
# CONFIGURACION GLOBAL DEL BOT INTRADIA
# =========================================================================================

# Motor de Ejecucion y Backtesting
DEEP_BACKTEST = True # Modo Backtesting Profundo (Apaga 1m CVD si es True)

# Gestion de Riesgo Intradia
INITIAL_CAPITAL = 1000.0
RISK_PCT_PER_TRADE = 1.0 # Riesgo por Operacion (%)
MAX_LEVERAGE = 10.0 # Apalancamiento Maximo
USE_DYN_RISK = True # Drawdown Mgmt (Mitad riesgo tras 3 perdidas)

# Killzones ETF (Londres & NY)
USE_SESSION_FILT = True # Activar Filtro de Sesion (Killzones)
SESSION_START = 7 # Hora UTC Inicio (Apertura Londres)
SESSION_END = 16 # Hora UTC Fin (Cierre NY)
USE_EOD_CLOSE = False # Cierre Fin de Sesion (EOD)

# Salidas Anti-Barridos y Trailing
SL_MULT = 1.5 # Multiplicador SL (Holgura Anti-Barrido)
TP_MULT = 3.0 # Multiplicador TP2 (Liquidez Final)
USE_TP1 = True # Activar TP1 Parcial
TP1_MULT = 1.5 # TP1 Base xATR
TP1_SIZE_PCT = 50.0 # TP1 - % a cerrar
USE_SMART_BE = True # Smart Break-Even por MFE
MFE_MULT = 1.2 # Multiplicador MFE xATR a BE
USE_TIME_STOP = True # Cierre por Lateralizacion
MAX_BARS_TIME = 48 # Max Barras en Op (48 en 5m = 4 horas)

# Modulos Institucionales
USE_VOL_FILT = True # Filtro Volatilidad Anti-Choppy
USE_SMT = True # Filtro Trampa SMT (1H)
SYM_ETH = "ETH/USDT" # Simbolo SMT
USE_LIQ_POOLS = True # Imanes Liquidez (1H BSSL/SSSL)
USE_F0 = True # Activar Vetos Macro (DXY/Funding)
SYM_DXY = "DX-Y.NYB" # Simbolo DXY (Yahoo Finance)
SYM_PERP = "BTC/USDT:USDT" # Perpetuo
SYM_SPOT = "BTC/USDT" # Spot BTC
