#!/usr/bin/env python
# coding: utf-8

# In[2]:


import pandas as pd
import altair as alt
import warnings
import requests
import datetime
alt.renderers.set_embed_options(theme='dark')


# In[13]:


class NebulaLBPProvider:
    
    def __init__(self, claim):
        self.first_tx = '4f066998-97c3-4851-b0d6-bf11508d46a0'
        self.n_tx_users = '81e1f1ff-f27d-4727-8bbf-3cb7e00dfde3'
        self.hourly_stats = '7a8ea41c-8c5e-4ca7-b466-6844b37b1adc'
        self.ust_traded_prices = '75cb6f4e-a94a-4efa-bc39-187bb7d6c54d'
        self.n_users = 'bf67c3a8-530d-4520-b7af-5da5094a255c'
        self.buys_ust = 'ffb18f2a-061f-44b9-9acf-44d509ec4681'
        self.claim = claim
        
    def load(self):
        self.first_tx_df = self.claim(self.first_tx)
        self.n_tx_users_df = self.claim(self.n_tx_users)
        self.hourly_stats_df = self.claim(self.hourly_stats)
        self.ust_traded_prices_df = self.claim(self.ust_traded_prices)
        self.n_users_df = self.claim(self.n_users)
        self.buys_ust_df = self.claim(self.buys_ust)
        
    def get_ust_traded_prices(self):
        b = self.ust_traded_prices_df[['belief_price','buy']]
        b.columns = ['Price','Amount']
        b['Action'] = 'Buy'
        s = self.ust_traded_prices_df[['belief_price','sell']]
        s.columns = ['Price','Amount']
        s['Action'] = 'Sell'
        ust_traded_prices = b.append(s)
        ust_traded_prices['Amount (M)'] = ust_traded_prices['Amount']
        ust_traded_prices['Amount'] = ust_traded_prices['Amount (M)'].apply(lambda x: str(round(x,2))+'M')
        return ust_traded_prices
        
    def parse(self):
        self.ust_traded_prices_df =  self.get_ust_traded_prices()


# In[14]:


def claim(claim_hash):
    df = pd.read_json(
            f"https://api.flipsidecrypto.com/api/v2/queries/{claim_hash}/data/latest",
            convert_dates=["BLOCK_TIMESTAMP"])
    df.columns = [c.lower() for c in df.columns]
    return df


# In[19]:


class NebulaChartProvider:
    
    def ust_traded_prices_chart(self, ust_traded_prices):
        chart = alt.Chart(ust_traded_prices).mark_line(point=True).encode(
        x=alt.X('Price:Q', sort=alt.EncodingSortField(order='ascending')),
        y="Amount (M):Q",
        color=alt.Color('Action:N', scale=alt.Scale(domain=['Sell','Buy'],
                                                      range=['#F24A72','#21bcd7'])),
        tooltip=['Amount (M):N','Price:Q',"Amount:Q"]
        ).configure_mark(
            color='#21bcd7'
        ).properties(width=700).configure_axisX(
            labelAngle=0
        ).configure_view(strokeOpacity=0).configure_axis(grid=False)
        return chart
    
    def price_chart(self,hourly_stats_df):
        #272231 background
        df=hourly_stats_df[['avg_belief_price','time']]
        df.columns=['Price','Hour']
        n_data = 100
        if df.Hour.nunique() < n_data:
            extra_data = []
            for i in range(n_data-df.Hour.nunique()):
                extra_data.append([None,(pd.to_datetime(df.Hour.max())+datetime.timedelta(hours=i)).strftime("%Y-%m-%d %H:%M")])
            df2 = df.append(pd.DataFrame(extra_data, columns=df.columns))
        else:
            df2 = df
        chart = alt.Chart(df2).mark_line(point=True).encode(
            x=alt.X('Hour:T', sort=alt.EncodingSortField(order='ascending')),
            y="Price:Q",
            tooltip=['Hour:T',"Price:Q"]
        ).configure_mark(
            color='#21bcd7'
        ).properties(width=700).configure_axisX(
            labelAngle=0
        ).configure_view(strokeOpacity=0).configure_axis(grid=False)
        return chart



# In[21]:





# In[ ]:




