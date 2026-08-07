import pandas as pd
import numpy as np

class RiskManager:
    def __init__(self, settings):
        self.settings = settings
        self.consec_losses = 0
        self.current_risk_pct = self.settings.RISK_PCT_PER_TRADE
        
    def update_streak(self, last_trade_pnl: float):
        if last_trade_pnl < 0:
            self.consec_losses += 1
        else:
            self.consec_losses = 0
            
        if self.settings.USE_DYN_RISK and self.consec_losses >= 3:
            self.current_risk_pct = self.settings.RISK_PCT_PER_TRADE / 2.0
        else:
            self.current_risk_pct = self.settings.RISK_PCT_PER_TRADE
            
    def calculate_position_size(self, current_equity: float, current_price: float, atr: float):
        dist_sl = self.settings.SL_MULT * atr
        dist_sl = max(dist_sl, 1.0) # Prevent div zero
        
        # Risk amount based on equity
        risk_amount = current_equity * (self.current_risk_pct / 100.0)
        
        # Max pos allowed by max leverage
        max_pos_value = current_equity * self.settings.MAX_LEVERAGE
        
        qty_by_risk = risk_amount / dist_sl
        qty_by_lev = max_pos_value / current_price
        
        return min(qty_by_risk, qty_by_lev)
        
    def calculate_sl_tp(self, is_long: bool, current_price: float, atr: float, vpoc: float, c_ssl: float):
        dist_sl = self.settings.SL_MULT * atr
        
        if is_long:
            trade_sl = current_price - dist_sl
            trade_tp1 = vpoc if vpoc > current_price + atr else current_price + self.settings.TP1_MULT * atr
            trade_tp2 = c_ssl if (self.settings.USE_LIQ_POOLS and not np.isnan(c_ssl)) else current_price + self.settings.TP_MULT * atr
        else:
            trade_sl = current_price + dist_sl
            trade_tp1 = vpoc if vpoc < current_price - atr else current_price - self.settings.TP1_MULT * atr
            trade_tp2 = c_ssl if (self.settings.USE_LIQ_POOLS and not np.isnan(c_ssl)) else current_price - self.settings.TP_MULT * atr
            
        return trade_sl, trade_tp1, trade_tp2
