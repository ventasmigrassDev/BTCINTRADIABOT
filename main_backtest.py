import sys
import os
import pandas as pd
import yfinance as yf

# Configuracion de paths para imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import config.settings as settings
from data.ccxt_history import fetch_historical_data_1m
from data.mtf_resampler import generate_mtf_dataframes, map_macro_trend_to_5m
import core.indicators as ind
import core.order_flow as flow
import core.smc_engine as smc
import core.liquidity as liq
import core.macro_vetos as macro
from execution.signals import generate_signals
from execution.risk_manager import RiskManager
from execution.trade_manager import TradeManager

def run_backtest():
    print("========================================")
    print("Iniciando Motor de Backtesting Profundo")
    print("PRO Intraday Top-Down v1.4.2 (Python)")
    print("========================================")
    
    # 1. Descarga de Datos (Usaremos un historico corto para pruebas rÃ¡pidas)
    symbol = "BTC/USDT"
    since = "2024-01-01T00:00:00Z" # Enero 2024
    
    try:
        # Intenta cargar de disco si existe
        df_1m = pd.read_csv('btc_1m_data.csv', index_col='timestamp', parse_dates=True)
        print("Cargados datos 1m desde disco local.")
    except FileNotFoundError:
        df_1m = fetch_historical_data_1m(symbol, since, limit=40000) # Aproximadamente 1 mes de 1m
        df_1m.to_csv('btc_1m_data.csv')
        
    if df_1m.empty:
        print("No hay datos para backtest.")
        return

    # 2. Resampling MTF
    print("Procesando Multi-Timeframe (MTF)...")
    df_5m, df_15m, df_1h, df_4h, df_1d = generate_mtf_dataframes(df_1m)
    
    # 3. Calculos Core - 1D y 4H
    df_5m = map_macro_trend_to_5m(df_5m, df_1d, df_4h)
    
    # 4. Calculos Core - 15m (SMC)
    print("Calculando zonas institucionales (SMC 15m)...")
    df_15m = smc.calculate_smc_15m(df_15m)
    df_5m = smc.map_smc_to_5m(df_15m, df_5m)
    
    # 5. Calculos Core - 1H (Liquidez)
    print("Calculando Pool de Liquidez (BSSL/SSSL 1H)...")
    df_1h = liq.calculate_liquidity_1h(df_1h)
    df_5m = liq.map_liquidity_to_5m(df_1h, df_5m)
    
    # 6. Order Flow y VWAP (5m)
    print("Calculando Order Flow, CVD y VWAP Diario...")
    df_1m = flow.calculate_cvd_1m(df_1m)
    df_5m = flow.map_cvd_to_5m(df_1m, df_5m, settings.DEEP_BACKTEST)
    df_5m = flow.calculate_daily_vwap_and_vpoc(df_5m)
    
    # 7. Filtro Volatilidad
    df_5m['atr'] = ind.calculate_atr(df_5m, 14)
    df_5m['ma_atr'] = ind.calculate_ma_atr(df_5m['atr'], 100)
    df_5m['volIsOK'] = ind.check_volatility_filter(df_5m['atr'], df_5m['ma_atr'], settings.USE_VOL_FILT)
    
    # 8. Macro Vetos (DXY y Funding)
    print("Obteniendo Vetos Macro (DXY)...")
    # Para backtest, descargaremos el dxy de yahoo finance en diario
    try:
        dxy = yf.download(settings.SYM_DXY, start="2023-12-25", progress=False)
        dxy_data = pd.DataFrame({'close': dxy['Close'].squeeze()})
        dxy_data.index = pd.to_datetime(dxy_data.index).tz_localize('UTC')
    except Exception as e:
        print(f"No se pudo descargar DXY: {e}. Desactivando veto DXY.")
        dxy_data = None
        
    df_5m = macro.apply_macro_vetos(df_5m, df_1d, dxy_data, funding_proxy=None, use_f0=settings.USE_F0)
    
    # 9. Generacion de SeÃ±ales
    print("Generando SeÃ±ales de Entrada...")
    df_5m = generate_signals(df_5m, settings.USE_SESSION_FILT, settings.SESSION_START, settings.SESSION_END)
    
    # 10. Simulacion de Trades (Bucle Vectorial / Bucle Row-by-Row)
    print("Iniciando Simulador de Operaciones...")
    rm = RiskManager(settings)
    tm = TradeManager(rm, settings)
    
    equity = settings.INITIAL_CAPITAL
    equity_curve = [equity]
    trades_log = []
    
    # Limpiamos na de seÃ±ales (arranque)
    df_sim = df_5m.dropna(subset=['atr', 'triLong', 'triShort']).copy()
    
    for i, (index, row) in enumerate(df_sim.iterrows()):
        is_eod = (index.hour == settings.SESSION_END and index.minute == 0)
        
        # Procesar posiciones abiertas
        result = tm.process_bar(row, i, is_eod)
        if result:
            if result['type'] == 'Close':
                equity += result['pnl']
                trades_log.append({
                    'time': index,
                    'action': 'CLOSE',
                    'reason': result['reason'],
                    'price': result['close_price'],
                    'pnl': result['pnl'],
                    'equity': equity
                })
            elif result['type'] == 'TP1 Partial':
                trades_log.append({
                    'time': index,
                    'action': 'TP1_PARTIAL',
                    'price': result['price']
                })
                
        # Evaluar entradas
        if tm.in_position == 0:
            if row['triLong']:
                tm.open_trade(True, row['close'], row['atr'], row['vpoc'], row['c_sssl'], equity, i)
                trades_log.append({
                    'time': index,
                    'action': 'ENTRY_LONG',
                    'price': row['close'],
                    'sl': tm.sl,
                    'tp1': tm.tp1,
                    'tp2': tm.tp2
                })
            elif row['triShort']:
                tm.open_trade(False, row['close'], row['atr'], row['vpoc'], row['c_bssl'], equity, i)
                trades_log.append({
                    'time': index,
                    'action': 'ENTRY_SHORT',
                    'price': row['close'],
                    'sl': tm.sl,
                    'tp1': tm.tp1,
                    'tp2': tm.tp2
                })
                
        equity_curve.append(equity)
        
    print("========================================")
    print("RESULTADOS DEL BACKTEST")
    print(f"Capital Inicial: ${settings.INITIAL_CAPITAL:.2f}")
    print(f"Capital Final:   ${equity:.2f}")
    pnl_pct = ((equity - settings.INITIAL_CAPITAL) / settings.INITIAL_CAPITAL) * 100
    print(f"Retorno Neto:    {pnl_pct:.2f}%")
    
    closed_trades = [t for t in trades_log if t['action'] == 'CLOSE']
    print(f"Total Trades:    {len(closed_trades)}")
    
    if len(closed_trades) > 0:
        win_trades = [t for t in closed_trades if t['pnl'] > 0]
        loss_trades = [t for t in closed_trades if t['pnl'] <= 0]
        print(f"Win Rate:        {(len(win_trades)/len(closed_trades))*100:.2f}%")
    
    print("========================================")
    
if __name__ == "__main__":
    run_backtest()
