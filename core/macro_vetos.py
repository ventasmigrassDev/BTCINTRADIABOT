import pandas as pd
import numpy as np

def apply_macro_vetos(df_5m: pd.DataFrame, df_1d: pd.DataFrame, dxy_data: pd.DataFrame, funding_proxy: pd.Series, use_f0: bool = True) -> pd.DataFrame:
    """Aplica vetos macro de DXY y Funding Proxy al marco de 5m."""
    if not use_f0:
        df_5m['vetoLong'] = False
        df_5m['vetoShort'] = False
        return df_5m

    # DXY Veto
    # dxyClose3 > 0 and ((dxyClose - dxyClose3)/dxyClose3 * 100.0) > 0.8
    if dxy_data is not None and not dxy_data.empty:
        dxy_data['dxy_pct'] = dxy_data['close'].pct_change(3) * 100
        dxy_data['dxyVeto'] = dxy_data['dxy_pct'] > 0.8
        
        # Mapear 1D a 5m
        df_dxy_mapped = dxy_data['dxyVeto'].reindex(df_5m.index.normalize(), method='ffill')
        # df_5m index is datetime, matching normalize()
        df_5m['dxyVeto'] = df_5m.index.normalize().map(df_dxy_mapped).fillna(False)
    else:
        df_5m['dxyVeto'] = False
        
    # Funding Veto
    if funding_proxy is not None and not funding_proxy.empty:
        # Assuming funding_proxy is a series with 60m resolution, map to 5m
        fp_mapped = funding_proxy.reindex(df_5m.index, method='ffill').fillna(0.0)
        df_5m['fundVetoLong'] = fp_mapped > 0.05
        df_5m['fundVetoShort'] = fp_mapped < -0.05
    else:
        df_5m['fundVetoLong'] = False
        df_5m['fundVetoShort'] = False
        
    df_5m['vetoLong'] = df_5m['dxyVeto'] | df_5m['fundVetoLong']
    df_5m['vetoShort'] = df_5m['fundVetoShort']
    
    return df_5m
