#!/usr/bin/env python3
from __future__ import annotations
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sports_ds.data.mlb_players import load_mlb_player_game_panel
from sports_ds.features.player_form import MLB_STAT_COLS, add_pregame_player_form_features
from sports_ds.validation.splits import season_walk_forward_masks

def mae(y,p):
    return float(mean_absolute_error(y,p))

def main():
    panel = load_mlb_player_game_panel([2023,2024], max_games=2000, workers=8, min_pa=2.0, lineup_only=True)
    feat = add_pregame_player_form_features(panel, stat_cols=list(MLB_STAT_COLS), windows=[3,5,10])
    feat = feat[feat['batting_order_slot'].between(1,9) & (feat['pre_games_played']>=15)].copy()
    feat['opp_k9'] = pd.to_numeric(feat.get('opp_k9'), errors='coerce')
    feat['rest_days'] = pd.to_numeric(feat.get('rest_days'), errors='coerce').fillna(1.0)
    configs = {
      'fantasy': ('fantasy_points', ['is_home','batting_order_slot','rest_days','ewma5_fantasy_points','roll5_fantasy_points','pre_fantasy_points','roll5_ops','pre_ops','roll5_plate_appearances','opp_k9']),
      'total_bases': ('total_bases', ['is_home','batting_order_slot','rest_days','ewma5_total_bases','roll5_total_bases','pre_total_bases','roll5_ops','pre_ops','roll5_plate_appearances','opp_k9']),
      'hits': ('hits', ['is_home','batting_order_slot','rest_days','ewma5_hits','roll5_hits','pre_hits','roll5_ops','pre_ops','roll5_plate_appearances','opp_k9']),
      'pa': ('plate_appearances', ['is_home','batting_order_slot','rest_days','ewma5_plate_appearances','roll5_plate_appearances','pre_plate_appearances','season_week']),
    }
    for name,(target,cols) in configs.items():
        cols=[c for c in cols if c in feat.columns]
        need=[c for c in cols if c!='opp_k9']+[target]
        df=feat.dropna(subset=need).copy()
        print(f'\n=== {name} n={len(df)} ===')
        rows=[]
        for season,tr,te in season_walk_forward_masks(df, min_train_seasons=1):
            train,test=df.loc[tr].copy(),df.loc[te].copy()
            if 'opp_k9' in cols:
                med=float(train['opp_k9'].median()) if train['opp_k9'].notna().any() else 8.0
                train['opp_k9']=train['opp_k9'].fillna(med); test['opp_k9']=test['opp_k9'].fillna(med)
            ytr=train[target].astype(float).to_numpy(); yte=test[target].astype(float).to_numpy()
            const=np.full(len(yte), ytr.mean())
            # shrunk player hist
            mu=train.groupby('player_id')[target].mean(); cnt=train.groupby('player_id')[target].count()
            g=float(ytr.mean()); k=20.0
            shrink=((cnt/(cnt+k))*mu + (k/(cnt+k))*g)
            ph=test['player_id'].map(shrink).astype(float).fillna(g).to_numpy()
            ridge=Pipeline([('s',StandardScaler()),('r',Ridge(alpha=10.0))])
            ridge.fit(train[cols], ytr); rp=np.clip(ridge.predict(test[cols]),0,None)
            gbr=HistGradientBoostingRegressor(max_depth=3, learning_rate=0.05, max_iter=250, min_samples_leaf=80, l2_regularization=2.0)
            gbr.fit(train[cols], ytr); gp=np.clip(gbr.predict(test[cols]),0,None)
            order_cols=[c for c in ['is_home','batting_order_slot'] if c in cols]
            o=Pipeline([('s',StandardScaler()),('r',Ridge(alpha=1.0))])
            o.fit(train[order_cols], ytr); op=np.clip(o.predict(test[order_cols]),0,None)
            blend=np.clip(0.4*ph + 0.6*gp, 0, None)
            row=dict(season=int(season),n=len(yte),const=mae(yte,const),player=mae(yte,ph),ridge=mae(yte,rp),gbr=mae(yte,gp),order=mae(yte,op),blend=mae(yte,blend))
            rows.append(row); print(row)
        m=pd.DataFrame(rows).mean(numeric_only=True)
        best=min([('player',m['player']),('ridge',m['ridge']),('gbr',m['gbr']),('order',m['order']),('blend',m['blend'])], key=lambda x:x[1])
        print('means', m.to_dict()); print('best', best, 'beats', best[1] < m['const'])

if __name__=='__main__':
    main()
