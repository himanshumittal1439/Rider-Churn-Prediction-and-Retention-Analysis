"""VoltRelay analysis. Actual data only; no synthetic fallback or cached results."""
from pathlib import Path
import json
import numpy as np
import pandas as pd

FILES = ['swap_events', 'station_hourly_status', 'riders', 'batteries',
         'support_tickets', 'stations', 'city_daily_context', 'fleet_partners']
END = pd.Timestamp('2025-07-01')  # exclusive end of the documented observation period

def load_data(folder):
    data = {}
    for name in FILES:
        candidates = [Path(folder)/(name+ext) for ext in ['.csv', '.csv.gz']]
        path = next((p for p in candidates if p.exists()), None)
        if path is None:
            raise FileNotFoundError(f'Missing {name}.csv or .csv.gz in {folder}. Download the original eight files; do not substitute another dataset.')
        frame = pd.read_csv(path, low_memory=False)
        if len(frame.columns) == 1 and '<' in str(frame.columns[0]):
            raise ValueError(f'{path.name} is an HTML error page, not a CSV dataset. Download quota may be exceeded.')
        # Compress repeated string dimensions after parsing without changing IDs.
        for col in frame.select_dtypes('object'):
            if not col.endswith(('_ts', '_date')) and col != 'hour_start' and frame[col].nunique() < len(frame)*0.3:
                frame[col] = frame[col].astype('category')
        data[name] = frame
    return data

def ratio(a, b):
    return a / b.replace(0, np.nan)

def canonical_city(s):
    mapping = {'bangalore':'Bengaluru','bengaluru':'Bengaluru','blr':'Bengaluru',
               'delhi':'Delhi NCR','delhi ncr':'Delhi NCR','new delhi':'Delhi NCR','ncr':'Delhi NCR',
               'mumbai':'Mumbai','bombay':'Mumbai','mum':'Mumbai','hyderabad':'Hyderabad',
               'hyd':'Hyderabad','jaipur':'Jaipur','jai':'Jaipur','pune':'Pune','pun':'Pune'}
    normalized=s.astype('string').str.strip().str.lower().str.replace(r'[_-]+',' ',regex=True).str.replace(r'\s+',' ',regex=True)
    return normalized.map(mapping).fillna(s.astype('string').str.strip())

def clean_data(data):
    """Return cleaned copies and an auditable count of every exclusion."""
    d={k:v.copy() for k,v in data.items()}
    audit={f'raw_{k}':len(v) for k,v in d.items()}
    keys={'stations':['station_id'],'riders':['rider_id'],'batteries':['battery_id'],
          'fleet_partners':['partner_id'],'support_tickets':['ticket_id'],
          'city_daily_context':['city','date'],'station_hourly_status':['station_id','hour_start']}
    for name, cols in keys.items():
        if d[name][cols].isna().any().any() or d[name].duplicated(cols).any():
            raise ValueError(f'{name}: missing or duplicate primary keys; resolve explicitly before joining.')
    for name,col in [('stations','city'),('riders','home_city'),('city_daily_context','city')]:
        d[name][col]=canonical_city(d[name][col])
    if d['city_daily_context'].duplicated(['city','date']).any():
        raise ValueError('City normalization produced duplicate city-date keys.')
    for name in d:
        for col in d[name].columns:
            if col.endswith(('_ts','_date')) or col in ['hour_start','date','competitor_within_1_5km_since']:
                d[name][col]=pd.to_datetime(d[name][col],errors='coerce')
    s=d['swap_events']
    if s['event_id'].isna().any():raise ValueError('Missing event_id')
    duplicate_ids=s.duplicated('event_id',keep=False)
    if duplicate_ids.any():
        conflicting=s[duplicate_ids].drop_duplicates().duplicated('event_id').any()
        if conflicting:raise ValueError('Conflicting rows share event_id; manual resolution required.')
    audit['exact_duplicate_rows']=int(s.duplicated().sum())
    s=s.drop_duplicates().copy()
    corrected=s.event_ts+pd.Timedelta(hours=5,minutes=30)
    bug=s.station_firmware.eq('v3.2.0') & corrected.ge('2025-03-10') & corrected.lt('2025-04-15')
    audit['timestamps_corrected']=int(bug.sum());s.loc[bug,'event_ts']=corrected[bug]
    outside=s.event_ts.isna() | s.event_ts.lt('2024-01-01') | s.event_ts.ge(END)
    audit['invalid_or_outside_period_events']=int(outside.sum());s=s.loc[~outside].copy()
    test=s.station_id.astype('string').str.startswith('STN-TST')
    audit['test_station_events_excluded']=int(test.sum());s=s.loc[~test].copy()
    # Strict retry signature. Do not collapse genuine failed attempts with no battery identity.
    signature=['rider_id','station_id','battery_in_id','battery_out_id','event_type',
               'amount_charged_inr','soc_in_pct','soc_out_pct','queue_wait_sec']
    s=s.sort_values('event_ts').reset_index(drop=True)
    hashed=pd.util.hash_pandas_object(s[signature],index=False)
    s['_signature']=hashed
    previous=s.groupby('_signature',observed=True).event_ts.shift()
    previous_offline=s.sync_mode.eq('offline_batch').groupby(hashed).shift().fillna(False)
    retry=(s.event_ts-previous).dt.total_seconds().between(0,120) & (s.sync_mode.eq('offline_batch')|previous_offline)
    retry &= s.battery_in_id.notna() | s.battery_out_id.notna()
    audit['strict_near_duplicate_candidates_excluded']=int(retry.sum())
    audit['strict_retry_revenue_removed_inr']=float(s.loc[retry,'amount_charged_inr'].sum())
    s=s.loc[~retry].drop(columns='_signature').copy()
    for col in ['soc_in_pct','soc_out_pct','soh_in_pct','soh_out_pct']:
        invalid=s[col].notna() & ~s[col].between(0,100)
        audit[f'invalid_{col}']=int(invalid.sum());s.loc[invalid,col]=np.nan
    invalid_distance=s.km_since_last_swap.notna() & ~s.km_since_last_swap.between(0,500)
    audit['distance_outside_0_500_km']=int(invalid_distance.sum())
    s.loc[invalid_distance,'km_since_last_swap']=np.nan
    audit['negative_queue_waits']=int(s.queue_wait_sec.lt(0).sum())
    s.loc[s.queue_wait_sec.lt(0),'queue_wait_sec']=np.nan
    for col in ['amount_charged_inr','energy_to_recharge_kwh']:
        audit[f'negative_{col}']=int(s[col].lt(0).sum());s.loc[s[col].lt(0),col]=np.nan
    for child,col,parent,key,nullable in [
        (s,'rider_id',d['riders'],'rider_id',False),(s,'station_id',d['stations'],'station_id',False),
        (s,'battery_in_id',d['batteries'],'battery_id',True),(s,'battery_out_id',d['batteries'],'battery_id',True),
        (d['riders'],'partner_id',d['fleet_partners'],'partner_id',True),
        (d['support_tickets'],'rider_id',d['riders'],'rider_id',False),
        (d['support_tickets'],'station_id',d['stations'],'station_id',True),
        (d['support_tickets'],'battery_id',d['batteries'],'battery_id',True),
        (d['station_hourly_status'],'station_id',d['stations'],'station_id',False)]:
        unknown=~child[col].isin(parent[key])
        if nullable:unknown &= child[col].notna()
        if unknown.any():raise ValueError(f'{col}: {int(unknown.sum())} orphan or missing references')
    d['stations']=d['stations'][~d['stations'].station_id.astype('string').str.startswith('STN-TST')].copy()
    h=d['station_hourly_status'];h=h[h.station_id.isin(d['stations'].station_id)].copy()
    h=h[h.hour_start.ge('2024-01-01') & h.hour_start.lt(END)].copy()
    audit['clean_attempts']=len(s);audit['clean_stations']=len(d['stations'])
    d['swap_events']=s;d['station_hourly_status']=h
    return d,audit

def prepare_events(d):
    station_cols=['station_id','city','zone','charger_generation','expansion_wave','location_type','host_type','grid_tariff_inr_kwh']
    rider_cols=['rider_id','partner_id','vehicle_class','plan_type','signup_date']
    e=d['swap_events'].merge(d['stations'][station_cols],on='station_id',validate='many_to_one')
    e=e.merge(d['riders'][rider_cols],on='rider_id',validate='many_to_one')
    e['month']=e.event_ts.dt.to_period('M').astype(str);e['date']=e.event_ts.dt.normalize();e['hour']=e.event_ts.dt.hour
    e['season']=e.event_ts.dt.month.map({1:'Winter',2:'Winter',3:'Pre-summer',4:'Summer',5:'Summer',6:'Summer',7:'Monsoon',8:'Monsoon',9:'Monsoon',10:'Post-monsoon',11:'Post-monsoon',12:'Winter'})
    e['completed']=e.event_type.eq('swap_completed');e['no_battery']=e.event_type.eq('failed_no_charged_battery')
    e['failed']=e.event_type.isin(['failed_no_charged_battery','failed_system_error']);e['abandoned']=e.event_type.eq('abandoned_queue')
    e['revenue']=e.amount_charged_inr.where(e.completed)
    e['energy_cost']=(e.energy_to_recharge_kwh*e.grid_tariff_inr_kwh).where(e.completed)
    e['known_pair']=e.completed & e.revenue.notna() & e.energy_cost.notna()
    e['energy_contribution']=(e.revenue-e.energy_cost).where(e.known_pair)
    return e

def service_table(e, groups):
    t=e.groupby(groups,observed=True,dropna=False).agg(attempts=('event_id','size'),completed=('completed','sum'),
        failures=('failed','sum'),no_battery=('no_battery','sum'),abandoned=('abandoned','sum'),
        queue_count=('queue_wait_sec','count'),queue_sum=('queue_wait_sec','sum'),queue_p90_sec=('queue_wait_sec',lambda x:x.quantile(.9)))
    for col in ['failures','no_battery','abandoned']:t[col+'_pct']=100*ratio(t[col],t.attempts)
    t['queue_mean_sec']=ratio(t.queue_sum,t.queue_count)
    return t.reset_index()

def network_economics(e,stations):
    t=e.groupby('month',observed=True).agg(attempts=('event_id','size'),completed=('completed','sum'),
        no_battery=('no_battery','sum'),abandoned=('abandoned','sum'),
        revenue=('revenue',lambda x:x.sum(min_count=1)),energy_cost=('energy_cost',lambda x:x.sum(min_count=1)),
        energy_contribution=('energy_contribution',lambda x:x.sum(min_count=1)),known_pairs=('known_pair','sum'))
    t['no_battery_pct']=100*ratio(t.no_battery,t.attempts)
    t['contribution_per_known_swap']=ratio(t.energy_contribution,t.known_pairs)
    t['cost_coverage_pct']=100*ratio(t.known_pairs,t.completed)
    costs={}
    for month in t.index:
        start=pd.Timestamp(month+'-01');end=start+pd.offsets.MonthBegin(1)
        left=stations.commissioned_date.clip(lower=start)
        right=stations.decommissioned_date.fillna(end).clip(upper=end)
        days=(right-left).dt.total_seconds().div(86400).clip(lower=0)
        costs[month]=float(((stations.monthly_rent_inr+stations.monthly_maintenance_inr)*days/(end-start).days).sum())
    t['site_cost_prorated']=pd.Series(costs)
    t['after_site_before_wear']=t.energy_contribution-t.site_cost_prorated
    # Deliberately not called net profit: battery wear, staff and other costs are absent.
    return t.reset_index()

def retention_tables(e,riders,tickets,end=END):
    r=riders.copy();r['cohort']=r.signup_date.dt.to_period('M').astype(str)
    r['eligible_60d']=r.signup_date.notna() & r.signup_date.ge('2024-01-01') & (r.signup_date+pd.Timedelta(days=60)).le(end)
    completed=e[e.completed].copy();completed['age_days']=(completed.event_ts-completed.signup_date).dt.total_seconds()/86400
    first=completed[completed.age_days.between(0,30,inclusive='left')].groupby('rider_id',observed=True).size()
    next30=completed[completed.age_days.between(30,60,inclusive='left')].groupby('rider_id',observed=True).size()
    r['swaps_days_0_29']=r.rider_id.map(first).fillna(0).astype(int)
    r['swaps_days_30_59']=r.rider_id.map(next30).fillna(0).astype(int)
    r['activated_30d']=r.swaps_days_0_29.gt(0)
    r['retained_30_60']=r.swaps_days_30_59.gt(0)
    r['not_returned_30_60']=~r.retained_30_60
    early=e[(e.event_ts-e.signup_date).dt.total_seconds().div(86400).between(0,30,inclusive='left')]
    stats=service_table(early,['rider_id'])[['rider_id','attempts','no_battery_pct','queue_mean_sec']]
    r=r.merge(stats,on='rider_id',how='left',validate='one_to_one')
    r['early_failure_band']=pd.cut(r.no_battery_pct,[-.001,0,5,100],labels=['0%','>0–5%','>5%']).astype('string').fillna('No attempts')
    eligible=r[r.eligible_60d].copy();active=eligible[eligible.activated_30d].copy()
    cohort=eligible.groupby('cohort',observed=True).agg(eligible_riders=('rider_id','size'),activated=('activated_30d','sum'),returned=('retained_30_60','sum'))
    cohort['activation_pct']=100*ratio(cohort.activated,cohort.eligible_riders)
    cohort['return_pct_all_eligible']=100*ratio(cohort.returned,cohort.eligible_riders)
    conditional=active.groupby('cohort').retained_30_60.mean()*100
    cohort['return_pct_among_activated']=conditional
    segments=[]
    for key in ['home_city','vehicle_class','plan_type','early_failure_band']:
        t=active.groupby(['cohort',key],observed=True,dropna=False).agg(riders=('rider_id','size'),not_returned=('not_returned_30_60','sum'))
        t['not_returned_pct']=100*ratio(t.not_returned,t.riders)
        t=t.reset_index().rename(columns={key:'segment'});t['dimension']=key;segments.append(t)
    tk=tickets.merge(riders[['rider_id','signup_date']],on='rider_id',validate='many_to_one')
    age=(tk.created_ts-tk.signup_date).dt.total_seconds()/86400
    tk=tk[age.between(0,30,inclusive='left')][['rider_id','category']].drop_duplicates()
    tk=tk.merge(active[['rider_id','not_returned_30_60']],on='rider_id',validate='many_to_one')
    support=tk.groupby('category',observed=True).agg(unique_riders=('rider_id','size'),not_returned=('not_returned_30_60','sum'))
    support['not_returned_pct']=100*ratio(support.not_returned,support.unique_riders)
    return cohort.reset_index(),pd.concat(segments,ignore_index=True),support.reset_index(),r

def run_analysis(data):
    d,audit=clean_data(data);e=prepare_events(d);tables={}
    tables['monthly_network']=network_economics(e,d['stations'])
    for key in ['city','station_id','hour','season','vehicle_class','charger_generation','expansion_wave','location_type']:
        tables['service_by_'+key]=service_table(e,[key])
    tables['service_city_month_generation']=service_table(e,['city','month','charger_generation'])
    h=d['station_hourly_status'].merge(d['stations'][['station_id','city']],on='station_id',validate='many_to_one')
    h['month']=h.hour_start.dt.to_period('M').astype(str)
    h['low_2w']=h.charged_2w_min.le(2).where(h.charged_2w_min.notna())
    h['low_3w']=h.charged_3w_min.le(2).where(h.charged_3w_min.notna())
    tables['station_telemetry']=h.groupby(['station_id','city','month'],observed=True).agg(
        rows=('hour_start','size'),observed_2w_hours=('charged_2w_min','count'),low_2w_share=('low_2w','mean'),
        observed_3w_hours=('charged_3w_min','count'),low_3w_share=('low_3w','mean'),charge_minutes=('avg_charge_minutes','mean'),
        grid_kwh=('grid_kwh',lambda x:x.sum(min_count=1)),quarantined=('packs_quarantined','mean')).reset_index()
    b=e[e.completed].merge(d['batteries'][['battery_id','supplier','manufacturing_lot','rated_capacity_kwh','purchase_cost_inr']],left_on='battery_in_id',right_on='battery_id',how='left',validate='many_to_one')
    b['observed_return_number']=b.sort_values('event_ts').groupby('battery_in_id',observed=True).cumcount()+1
    b['soh_band']=pd.cut(b.soh_in_pct,[0,70,80,90,100],include_lowest=True)
    tables['battery_supplier']=b.groupby(['supplier','vehicle_class'],observed=True,dropna=False).agg(swaps=('event_id','size'),packs=('battery_in_id','nunique'),valid_distance=('km_since_last_swap','count'),median_km=('km_since_last_swap','median'),mean_soh=('soh_in_pct','mean')).reset_index()
    tables['battery_lot']=b.groupby(['supplier','manufacturing_lot','month','vehicle_class'],observed=True,dropna=False).agg(swaps=('event_id','size'),median_km=('km_since_last_swap','median'),mean_soh=('soh_in_pct','mean')).reset_index()
    tables['battery_range_by_soh']=b.groupby(['vehicle_class','soh_band'],observed=True).agg(swaps=('event_id','size'),valid_distance=('km_since_last_swap','count'),median_km=('km_since_last_swap','median')).reset_index()
    lifecycle=d['batteries'].copy();lifecycle['soh_loss']=lifecycle.initial_soh_pct-lifecycle.current_soh_pct
    tables['battery_lifecycle']=lifecycle.groupby(['supplier','pack_type'],observed=True).agg(packs=('battery_id','size'),retired=('retired_date','count'),mean_soh_loss=('soh_loss','mean')).reset_index()
    tables['pricing']=e[e.completed].groupby(['city','month','hour','tariff_code','vehicle_class','plan_type'],observed=True,dropna=False).agg(swaps=('event_id','size'),mean_list_price=('list_price_inr','mean'),mean_paid=('revenue','mean'),energy_contribution=('energy_contribution','sum')).reset_index()
    pe=e[e.completed].merge(d['fleet_partners'][['partner_id','partner_name','amendment_date','peak_surcharge_billable']],on='partner_id',how='left',validate='many_to_one')
    tables['partner_economics']=pe.groupby(['partner_name','month'],observed=True,dropna=False).agg(swaps=('event_id','size'),revenue=('revenue','sum'),energy_contribution=('energy_contribution','sum'),known_pairs=('known_pair','sum')).reset_index()
    amended=pe[pe.amendment_date.notna()].copy();amended['days_from_amendment']=(amended.event_ts-amended.amendment_date).dt.total_seconds()/86400
    amended=amended[amended.days_from_amendment.between(-30,30,inclusive='left')]
    amended['period']=np.where(amended.days_from_amendment.lt(0),'30 days before','30 days after')
    tables['contract_amendment']=amended.groupby(['partner_name','period','vehicle_class'],observed=True).agg(swaps=('event_id','size'),mean_paid=('revenue','mean'),mean_energy_contribution=('energy_contribution','mean')).reset_index()
    cohort,seg,support,r=retention_tables(e,d['riders'],d['support_tickets'])
    tables.update(retention_cohort=cohort,retention_segments=seg,retention_support=support)
    # Descriptive daily context join, rather than claiming correlation establishes causality.
    daily=service_table(e,['city','date']).merge(d['city_daily_context'],on=['city','date'],how='left',validate='one_to_one')
    tables['weather_correlations']=daily[['no_battery_pct','max_temp_c','grid_outage_hours','rainfall_mm']].corr().reset_index()
    audit['weather_matched_city_days']=int(daily.max_temp_c.notna().sum())
    audit['eligible_retention_riders']=int(r.eligible_60d.sum())
    audit['retention_right_censored_riders']=int((~r.eligible_60d).sum())
    # Model scores from the old notebook are deliberately not reused.
    return tables,audit

def export_results(tables,audit,folder):
    out=Path(folder);out.mkdir(parents=True,exist_ok=True)
    for name,table in tables.items():table.to_csv(out/(name+'.csv'),index=False)
    (out/'quality_audit.json').write_text(json.dumps(audit,indent=2),encoding='utf-8')
    import matplotlib.pyplot as plt
    m=tables['monthly_network'];fig,axes=plt.subplots(2,2,figsize=(12,8))
    for ax,col,title in zip(axes.flat,['completed','revenue','no_battery_pct','contribution_per_known_swap'],['Completed swaps','Revenue INR','No-battery failures %','Energy-only contribution per known swap INR']):
        ax.plot(m.month,m[col],marker='o');ax.set_title(title);ax.tick_params(axis='x',rotation=65)
    fig.tight_layout();fig.savefig(out/'network_trends.png',dpi=180);plt.close(fig)
    c=tables['retention_cohort'];fig,ax=plt.subplots(figsize=(10,4))
    ax.plot(c.cohort,c.return_pct_among_activated,marker='o');ax.set_ylabel('Return rate in days 30–59 (%)');ax.set_title('Equal-follow-up retention among riders activated in the first 30 days');ax.tick_params(axis='x',rotation=65)
    fig.tight_layout();fig.savefig(out/'retention_cohorts.png',dpi=180);plt.close(fig)

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--data-dir',default='data');p.add_argument('--output-dir',default='results');args=p.parse_args()
    tables,audit=run_analysis(load_data(args.data_dir));export_results(tables,audit,args.output_dir)
    print(json.dumps(audit,indent=2))
