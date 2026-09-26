import sys,unittest,tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pandas as pd
import numpy as np
from analysis import canonical_city,ratio,service_table,network_economics,retention_tables,load_data

class AnalysisTests(unittest.TestCase):
    def test_city_normalisation(self):
        self.assertEqual(canonical_city(pd.Series([' BLR ','delhi_ncr','Bombay'])).tolist(),['Bengaluru','Delhi NCR','Mumbai'])
    def test_zero_denominator(self):
        self.assertTrue(np.isnan(ratio(pd.Series([2]),pd.Series([0])).iloc[0]))
    def test_weighted_queue_and_outcome_denominator(self):
        e=pd.DataFrame({'event_id':['a','b','c'],'city':['A']*3,'completed':[1,1,0],'failed':[0,0,1],'no_battery':[0,0,1],'abandoned':[0,0,0],'queue_wait_sec':[10,10,100]})
        t=service_table(e,['city']).iloc[0]
        self.assertEqual(t.queue_mean_sec,40);self.assertAlmostEqual(t.no_battery_pct,100/3)
    def test_missing_queue_is_not_zero(self):
        e=pd.DataFrame({'event_id':['a','b'],'city':['A']*2,'completed':[1,1],'failed':[0,0],'no_battery':[0,0],'abandoned':[0,0],'queue_wait_sec':[10,np.nan]})
        self.assertEqual(service_table(e,['city']).iloc[0].queue_mean_sec,10)
    def test_retention_eligibility_and_ticket_denominator(self):
        riders=pd.DataFrame({'rider_id':['a','b','new'],'signup_date':pd.to_datetime(['2024-01-01','2024-01-01','2025-06-20']),'home_city':['A']*3,'vehicle_class':['2W']*3,'plan_type':['pay']*3})
        e=pd.DataFrame({'rider_id':['a','b','b','new'],'event_ts':pd.to_datetime(['2024-01-02','2024-01-02','2024-02-10','2025-06-21']),'event_id':['1','2','3','4'],'completed':[True]*4,'failed':[False]*4,'no_battery':[False]*4,'abandoned':[False]*4,'queue_wait_sec':[10]*4})
        e=e.merge(riders[['rider_id','signup_date']],on='rider_id')
        tickets=pd.DataFrame({'rider_id':['a','a','b','a'],'category':['billing']*4,'created_ts':pd.to_datetime(['2024-01-03','2024-01-04','2024-01-03','2024-03-10'])})
        c,s,t,r=retention_tables(e,riders,tickets)
        self.assertEqual(int(r.eligible_60d.sum()),2)
        self.assertEqual(t.iloc[0].unique_riders,2);self.assertEqual(t.iloc[0].not_returned_pct,50)
        self.assertEqual(c.iloc[0].return_pct_among_activated,50)
    def test_site_cost_includes_idle_stations(self):
        e=pd.DataFrame({'month':['2024-01'],'event_id':['1'],'completed':[True],'no_battery':[False],'abandoned':[False],'revenue':[100.],'energy_cost':[20.],'energy_contribution':[80.],'known_pair':[True]})
        stations=pd.DataFrame({'commissioned_date':pd.to_datetime(['2024-01-01','2024-01-01']),'decommissioned_date':pd.to_datetime([None,None]),'monthly_rent_inr':[310,310],'monthly_maintenance_inr':[0,0]})
        t=network_economics(e,stations).iloc[0]
        self.assertEqual(t.site_cost_prorated,620);self.assertEqual(t.after_site_before_wear,-540)
    def test_missing_source_fails_clearly(self):
        with tempfile.TemporaryDirectory() as p:
            with self.assertRaises(FileNotFoundError):load_data(p)
    def test_html_download_rejected(self):
        with tempfile.TemporaryDirectory() as p:
            Path(p,'swap_events.csv').write_text('<html>Quota exceeded</html>')
            with self.assertRaises(ValueError):load_data(p)

if __name__=='__main__':unittest.main()
