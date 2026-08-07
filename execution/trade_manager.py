import pandas as pd
import numpy as np

class TradeManager:
    def __init__(self, risk_manager, settings):
        self.rm = risk_manager
        self.settings = settings
        
        self.reset_state()
        
    def reset_state(self):
        self.in_position = 0 # 1 long, -1 short, 0 flat
        self.entry_price = 0.0
        self.qty = 0.0
        self.sl = 0.0
        self.tp1 = 0.0
        self.tp2 = 0.0
        self.tp1_hit = False
        self.entry_bar = 0
        self.pnl = 0.0
        
    def process_bar(self, row, bar_index, is_eod):
        result = None
        
        if self.in_position == 0:
            return result
            
        # Eval EOD
        if is_eod and self.settings.USE_EOD_CLOSE:
            result = self._close_trade(row['close'], "EOD Close")
            return result
            
        # Eval Time Stop
        if self.settings.USE_TIME_STOP and (bar_index - self.entry_bar) >= self.settings.MAX_BARS_TIME and not self.tp1_hit:
            result = self._close_trade(row['close'], "Time Stop")
            return result
            
        # Eval Long Trailing & Exits
        if self.in_position == 1:
            # Smart BE
            if self.settings.USE_SMART_BE and not self.tp1_hit and (row['high'] - self.entry_price >= self.settings.MFE_MULT * row['atr']):
                self.sl = max(self.sl, self.entry_price)
                
            # TP1 Trailing Hit logic
            if self.tp1_hit:
                self.sl = max(self.sl, row['close'] - (row['atr'] * 1.5))
                
            # Exits Check
            if row['low'] <= self.sl:
                result = self._close_trade(self.sl, "Stop Loss")
            elif self.settings.USE_TP1 and not self.tp1_hit and row['high'] >= self.tp1:
                self.tp1_hit = True
                self.qty = self.qty * (1 - self.settings.TP1_SIZE_PCT / 100.0)
                self.sl = max(self.sl, self.entry_price)
                result = {"type": "TP1 Partial", "price": self.tp1}
                # Check if it hit TP2 in the same bar
                if row['high'] >= self.tp2:
                    result = self._close_trade(self.tp2, "TP2 Final")
            elif row['high'] >= self.tp2:
                result = self._close_trade(self.tp2, "TP2 Final" if self.settings.USE_TP1 else "Salida Final")
                
        # Eval Short Trailing & Exits
        elif self.in_position == -1:
            if self.settings.USE_SMART_BE and not self.tp1_hit and (self.entry_price - row['low'] >= self.settings.MFE_MULT * row['atr']):
                self.sl = min(self.sl, self.entry_price)
                
            if self.tp1_hit:
                self.sl = min(self.sl, row['close'] + (row['atr'] * 1.5))
                
            # Exits check
            if row['high'] >= self.sl:
                result = self._close_trade(self.sl, "Stop Loss")
            elif self.settings.USE_TP1 and not self.tp1_hit and row['low'] <= self.tp1:
                self.tp1_hit = True
                self.qty = self.qty * (1 - self.settings.TP1_SIZE_PCT / 100.0)
                self.sl = min(self.sl, self.entry_price)
                result = {"type": "TP1 Partial", "price": self.tp1}
                # Check if it hit TP2 in the same bar
                if row['low'] <= self.tp2:
                    result = self._close_trade(self.tp2, "TP2 Final")
            elif row['low'] <= self.tp2:
                result = self._close_trade(self.tp2, "TP2 Final" if self.settings.USE_TP1 else "Salida Final")
                
        return result
        
    def _close_trade(self, close_price, reason):
        if self.in_position == 1:
            trade_pnl = (close_price - self.entry_price) * self.qty
        else:
            trade_pnl = (self.entry_price - close_price) * self.qty
            
        self.rm.update_streak(trade_pnl)
        
        result = {
            "type": "Close",
            "reason": reason,
            "pnl": trade_pnl,
            "close_price": close_price
        }
        self.reset_state()
        return result
        
    def open_trade(self, is_long: bool, price: float, atr: float, vpoc: float, c_ssl: float, equity: float, bar_index: int):
        self.in_position = 1 if is_long else -1
        self.entry_price = price
        self.entry_bar = bar_index
        
        self.qty = self.rm.calculate_position_size(equity, price, atr)
        self.sl, self.tp1, self.tp2 = self.rm.calculate_sl_tp(is_long, price, atr, vpoc, c_ssl)
        self.tp1_hit = False
