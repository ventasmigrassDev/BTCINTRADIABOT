# Plan de Arquitectura y Migración Completa: PRO Intraday Top-Down v1.4.2 (Pine Script -> Python)

Este documento detalla el plan exacto, módulo por módulo, para replicar el 100% de la lógica institucional de TradingView a Python, sin omitir ningún detalle técnico, matemático o de gestión de riesgo.

## 1. Arquitectura del Proyecto (Estructura de Directorios)

```text
BotIntradiaBtcEventura/
â”‚
â”œâ”€â”€ data/                     # Capa de Ingesta y Procesamiento de Datos
â”‚   â”œâ”€â”€ binance_live.py       # ConexiÃ³n WebSockets y REST API Binance (Tiempo real)
â”‚   â”œâ”€â”€ ccxt_history.py       # Descarga y formateo de datos histÃ³ricos usando CCXT
â”‚   â””â”€â”€ mtf_resampler.py      # Motor de remuestreo (convierte 1m a 5m, 15m, 1H, 4H, 1D)
â”‚
â”œâ”€â”€ core/                     # Capa AnalÃ­tica (TraducciÃ³n exacta de Pine Script)
â”‚   â”œâ”€â”€ indicators.py         # ATR, VWAP Diario (reseteable), Medias MÃ³viles
â”‚   â”œâ”€â”€ order_flow.py         # CVD (Cumulative Volume Delta) y VPOC (Volume Profile 40 bins)
â”‚   â”œâ”€â”€ smc_engine.py         # Algoritmos de Order Blocks (Extremos/Decisionales) y FVG en 15m
â”‚   â”œâ”€â”€ liquidity.py          # Rastreo de BSSL / SSSL (Pivots 3,3 en 1H)
â”‚   â””â”€â”€ macro_vetos.py        # ValidaciÃ³n de DXY (yfinance) y Funding Proxy (Spot vs Perp)
â”‚
â”œâ”€â”€ execution/                # Capa de EjecuciÃ³n y GestiÃ³n (Smart Trade)
â”‚   â”œâ”€â”€ risk_manager.py       # TamaÃ±o de posiciÃ³n, SL (ATR * 1.5), TP1, TP2, Riesgo DinÃ¡mico
â”‚   â”œâ”€â”€ trade_manager.py      # MÃ¡quina de estados: Smart Break-Even (MFE), Time Stop (48 barras)
â”‚   â””â”€â”€ signals.py            # EvaluaciÃ³n estricta de las condiciones `m1_Long` y `m1_Short`
â”‚
â”œâ”€â”€ config/                   # ConfiguraciÃ³n Global
â”‚   â””â”€â”€ settings.py           # Variables (Riesgo %, Apalancamiento, Horarios Killzone 7 a 16 UTC)
â”‚
â”œâ”€â”€ main_backtest.py          # PUNTO DE ENTRADA: Simulador Vectorial / Eventos para Backtesting
â”œâ”€â”€ main_live.py              # PUNTO DE ENTRADA: Bot de EjecuciÃ³n en ProducciÃ³n (Binance)
â”œâ”€â”€ requirements.txt          # Dependencias del proyecto
â””â”€â”€ .env                      # Credenciales seguras de Binance
```

---

## 2. Replicación Analítica Exacta (TradingView a Python)

He desglosado el cÃ³digo Pine Script y asÃ­ es como lo pasaremos a Python usando `pandas` y `numpy`:

### A. Multi-Timeframe (MTF)
*   **Problema:** Pine Script usa `request.security`.
*   **SoluciÃ³n Python:** Descargaremos **exclusivamente velas de 1 minuto (1m)**. Usaremos `pandas.DataFrame.resample()` para generar en memoria los dataframes de `5T` (5m - timeframe base), `15T` (SMC), `60T` (1H Liquidez), `240T` (4H Tendencia) y `D` (VWAP y Macro).

### B. Módulo SMC (15 minutos)
*   **Order Blocks Extremos (`f_find_ext_ob`):** Iteraremos sobre las Ãºltimas 40 velas de 15m. Buscaremos el mÃ­nimo/mÃ¡ximo absoluto y, a partir de ahÃ­, en las siguientes 5 velas buscaremos la vela envolvente (cierre por encima de apertura para largos).
*   **Order Blocks Decisionales (`f_find_dec_ob`):** Igual al extremo pero restringido al micro-entorno de las Ãºltimas 5 velas de 15m.
*   **FVG (Fair Value Gaps):** Condiciones de 3 velas: `high[2] < low[0]` para largos y `low[2] > high[0]` para cortos en el marco de 15m.
*   *CondiciÃ³n Final:* `inDemZone` (El precio actual 5m debe estar rebotando dentro de la caja de 15m).

### C. Módulo de Liquidez (BSSL / SSSL en 1 Hora)
*   Pine Script usa `ta.pivothigh(high, 3, 3)`. En Python usaremos `scipy.signal.argrelextrema` sobre la serie temporal de 1H con una ventana (window) de 3 para ubicar los picos.
*   Mantendremos un array dinÃ¡mico (`bssl_array`, `sssl_array`) y los eliminaremos una vez que el precio de 5m cruce por encima/debajo de ellos, asegurando que apuntamos a la liquidez sin mitigar mÃ¡s cercana (`f_get_closest`).

### D. Flujo de Órdenes y Volumen (CVD y VWAP)
*   **CVD (1m Delta):** Sobre los datos de 1 minuto, si `close >= open` sumamos volumen, si es menor restamos. Usaremos una media mÃ³vil de 3 perÃ­odos para detectar la direcciÃ³n (`cvdRising`, `cvdFalling`).
*   **VWAP Diario y VPOC:** Reiniciaremos los acumuladores a las 00:00 UTC. Para el **Session Volume Profile (VPOC)**, replicaremos la matriz de 40 bins (`bins = 40`) iterando las velas de la sesiÃ³n y calculando la zona de mayor concentraciÃ³n de volumen.

### E. Filtros y Vetos Macro
*   **Horarios:** Killzones de Londres/NY activas sÃ³lo entre las 7:00 UTC y las 16:00 UTC.
*   **Volatilidad:** `atr(14) >= sma(atr(14), 100) * 0.70`.
*   **Veto Macro (DXY y Funding):** Obtendremos el DXY con `yfinance`. Veto alcista si el DXY sube > 0.8% en 3 dÃ­as. Veto por funding rate si la diferencia entre Perpetuo y Spot de Binance supera el 0.05% o baja de -0.05%.

---

## 3. Motor de Ejecución y Gestión de Riesgo (Risk Management)

La parte crÃ­tica donde el bot gana su dinero, replicada paso a paso:

1.  **CÃ¡lculo del Riesgo (DinÃ¡mico):** Por defecto `1.0%` del capital por trade. Si el historial de trades cerrados (`consecLosses`) detecta 3 pÃ©rdidas consecutivas, el riesgo bÃ¡sico se divide a la mitad (`0.5%`).
2.  **FÃ³rmula de TamaÃ±o de PosiciÃ³n (Leverage):** LÃ­mite matemÃ¡tico de `min(riesgo_equidad / distSL, equidad * maxLeverage / close)`.
3.  **Take Profit 1 (TP1) y Cierre Parcial:**
    *   UbicaciÃ³n: El VPOC si estÃ¡ lo suficientemente lejos, si no `precio_entrada + 1.5 * ATR`.
    *   EjecuciÃ³n: Se vende el **50%** del tamaÃ±o de la posiciÃ³n original al tocar el TP1.
4.  **Take Profit 2 (TP2 - Cierre Final):** Apunta al BSSL/SSSL mÃ¡s cercano de 1H, de lo contrario a `precio_entrada + 3.0 * ATR`.
5.  **Smart Break-Even (MFE):** Si el precio se mueve a nuestro favor `1.2 * ATR` (Multiplicador MFE) antes de tocar TP1, el Stop Loss se mueve automÃ¡ticamente al precio de entrada (`trade_sl := math.max(trade_sl, e_price)`).
6.  **Time Stop (Anti-LateralizaciÃ³n):** Si despuÃ©s de 48 velas de 5m (4 horas exactas) la operaciÃ³n sigue abierta y no ha tocado ni siquiera TP1, se cierra la operaciÃ³n a precio de mercado.

---

## 4. Ejecución del Plan en Python (Siguientes Pasos Reales)

**Fase 1: Preparación de Datos (El Motor Base)**
- CreaciÃ³n de los scripts en `data/` usando **CCXT** para descargar el aÃ±o completo 2024 de BTC/USDT en 1 minuto.
- ImplementaciÃ³n del remuestreador (Resampler) para construir el Top-Down.

**Fase 2: Motor Lógico (Core)**
- Programar los detectores matemÃ¡ticos de Extremos/Decisionales (SMC).
- Programar el Delta Acumulado (CVD) usando el timeframe 1m cruzado con 5m.

**Fase 3: Backtesting (Validación Visual y Métrica)**
- Construir `main_backtest.py` iterando los datos y evaluando la lÃ³gica de salidas paso a paso.
- Generar reporte (Drawdown, Racha, PnL, Winrate).

**Fase 4: Live Trading (Binance)**
- `main_live.py`: IntegraciÃ³n de **WebSockets de Binance** para leer el Order Flow (CVD) milisegundo a milisegundo.
- Uso de Ã³rdenes LIMIT y STOP MARKET reales a travÃ©s de la API.

> *Nota sobre GitHub: He inicializado el repositorio local en este entorno y lo he enlazado a tu GitHub (`https://github.com/ventasmigrassDev/BotIntradiaBtcEventura.git`). Una vez generemos el cÃ³digo base, podrÃ¡s pushearlo o lo prepararemos para exportar.*
