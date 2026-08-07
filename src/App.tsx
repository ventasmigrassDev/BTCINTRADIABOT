import { Activity, Clock, Crosshair, Settings2, TrendingDown, TrendingUp, AlertTriangle } from 'lucide-react';
import { useState, useEffect } from 'react';

export default function App() {
  const [time, setTime] = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  return (
    <div className="min-h-screen bg-[#050B14] text-slate-200 p-4 md:p-8 font-sans selection:bg-blue-500/30">
      {/* Background Glow */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden">
        <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-blue-600/10 blur-[120px] rounded-full" />
        <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-emerald-600/10 blur-[120px] rounded-full" />
      </div>

      <div className="max-w-5xl mx-auto relative z-10 space-y-6">
        {/* Header */}
        <header className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-900/40 border border-slate-800/60 backdrop-blur-md p-6 rounded-2xl">
          <div>
            <h1 className="text-2xl font-bold text-white flex items-center gap-2">
              <Crosshair className="text-blue-500" />
              PRO Intraday Top-Down
              <span className="text-xs font-mono bg-blue-500/20 text-blue-400 px-2 py-0.5 rounded border border-blue-500/20 ml-2">v1.4.2</span>
            </h1>
            <p className="text-slate-400 text-sm mt-1">Motor de Ejecución y Análisis Institucional</p>
          </div>
          <div className="flex items-center gap-4 text-sm">
            <div className="flex items-center gap-2 bg-slate-800/50 px-3 py-1.5 rounded-lg border border-slate-700/50">
              <Clock size={16} className="text-slate-400" />
              <span className="font-mono text-slate-300">{time.toLocaleTimeString()}</span>
            </div>
            <div className="flex items-center gap-2 bg-emerald-500/10 px-3 py-1.5 rounded-lg border border-emerald-500/20 text-emerald-400">
              <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
              Sistema Activo
            </div>
          </div>
        </header>

        {/* Dashboard Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          
          {/* Card: Engine Status */}
          <div className="bg-slate-900/40 border border-slate-800/60 backdrop-blur-md p-6 rounded-2xl flex flex-col justify-between">
            <div className="flex items-center gap-3 mb-4">
              <Settings2 className="text-slate-400" />
              <h2 className="text-sm font-medium text-slate-400 uppercase tracking-wider">Modo Motor</h2>
            </div>
            <div>
              <p className="text-2xl font-bold text-emerald-400">Order Flow ON</p>
              <p className="text-xs text-slate-500 mt-1">Lectura de CVD 1m en tiempo real</p>
            </div>
          </div>

          {/* Card: Macro Trend */}
          <div className="bg-slate-900/40 border border-slate-800/60 backdrop-blur-md p-6 rounded-2xl flex flex-col justify-between">
            <div className="flex items-center gap-3 mb-4">
              <TrendingUp className="text-slate-400" />
              <h2 className="text-sm font-medium text-slate-400 uppercase tracking-wider">Tendencia 4H</h2>
            </div>
            <div>
              <div className="inline-flex items-center gap-2 bg-emerald-500/10 text-emerald-400 px-3 py-1 rounded-full border border-emerald-500/20">
                <span className="font-bold tracking-wide">ALCISTA</span>
              </div>
              <p className="text-xs text-slate-500 mt-2">Precio &gt; EMA 50</p>
            </div>
          </div>

          {/* Card: Equilibrium */}
          <div className="bg-slate-900/40 border border-slate-800/60 backdrop-blur-md p-6 rounded-2xl flex flex-col justify-between">
            <div className="flex items-center gap-3 mb-4">
              <Activity className="text-slate-400" />
              <h2 className="text-sm font-medium text-slate-400 uppercase tracking-wider">Equilibrio 1D</h2>
            </div>
            <div>
              <div className="inline-flex items-center gap-2 bg-emerald-500/10 text-emerald-400 px-3 py-1 rounded-full border border-emerald-500/20">
                <span className="font-bold tracking-wide">DISCOUNT (Barato)</span>
              </div>
              <p className="text-xs text-slate-500 mt-2">Zona de compras institucional</p>
            </div>
          </div>

          {/* Card: VWAP */}
          <div className="bg-slate-900/40 border border-slate-800/60 backdrop-blur-md p-6 rounded-2xl flex flex-col justify-between">
            <div className="flex items-center gap-3 mb-4">
              <Activity className="text-slate-400" />
              <h2 className="text-sm font-medium text-slate-400 uppercase tracking-wider">VWAP Diario</h2>
            </div>
            <div>
              <div className="inline-flex items-center gap-2 bg-purple-500/10 text-purple-400 px-3 py-1 rounded-full border border-purple-500/20">
                <span className="font-bold tracking-wide">&gt; SOPORTE</span>
              </div>
              <p className="text-xs text-slate-500 mt-2">Precio sobre el VWAP</p>
            </div>
          </div>

          {/* Card: Order Flow */}
          <div className="bg-slate-900/40 border border-slate-800/60 backdrop-blur-md p-6 rounded-2xl flex flex-col justify-between">
            <div className="flex items-center gap-3 mb-4">
              <TrendingDown className="text-slate-400" />
              <h2 className="text-sm font-medium text-slate-400 uppercase tracking-wider">Flujo 1m (CVD)</h2>
            </div>
            <div>
              <div className="inline-flex items-center gap-2 bg-emerald-500/10 text-emerald-400 px-3 py-1 rounded-full border border-emerald-500/20">
                <TrendingUp size={16} />
                <span className="font-bold tracking-wide">COMPRADOR</span>
              </div>
              <p className="text-xs text-slate-500 mt-2">Delta volumen positivo</p>
            </div>
          </div>

          {/* Card: Trigger Status */}
          <div className="bg-slate-900/40 border border-blue-500/30 backdrop-blur-md p-6 rounded-2xl flex flex-col justify-between relative overflow-hidden">
            <div className="absolute inset-0 bg-blue-500/5 animate-pulse" />
            <div className="relative z-10">
              <div className="flex items-center gap-3 mb-4">
                <AlertTriangle className="text-blue-400" />
                <h2 className="text-sm font-medium text-blue-400 uppercase tracking-wider">Estado Gatillo</h2>
              </div>
              <div>
                <div className="text-xl font-bold text-white bg-slate-800/80 inline-block px-4 py-2 rounded-lg border border-slate-700">
                  Buscando POI...
                </div>
                <p className="text-xs text-slate-400 mt-2">Esperando zona de liquidez</p>
              </div>
            </div>
          </div>

        </div>
      </div>
    </div>
  );
}
