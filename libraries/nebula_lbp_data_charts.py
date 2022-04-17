#!/usr/bin/env python
# coding: utf-8

# In[54]:


import pandas as pd
import altair as alt
import warnings
import requests
import datetime
alt.renderers.set_embed_options(theme='dark')


# In[135]:


class NebulaLBPProvider:
    
    def __init__(self, claim):
        self.first_tx = '4f066998-97c3-4851-b0d6-bf11508d46a0'
        self.n_tx_users = '81e1f1ff-f27d-4727-8bbf-3cb7e00dfde3'
        self.hourly_stats = '7a8ea41c-8c5e-4ca7-b466-6844b37b1adc'
        self.ust_traded_prices = '75cb6f4e-a94a-4efa-bc39-187bb7d6c54d'
        self.n_users = 'bf67c3a8-530d-4520-b7af-5da5094a255c'
        self.buys_ust = 'ffb18f2a-061f-44b9-9acf-44d509ec4681'
        self.first_price = '5364bf88-617f-40ec-b95f-b3c003fd29f7'
        self.claim = claim
        
    def load(self):
        self.first_tx_df = self.claim(self.first_tx)
        self.n_tx_users_df = self.claim(self.n_tx_users)
        self.hourly_stats_df = self.claim(self.hourly_stats)
        self.ust_traded_prices_df = self.claim(self.ust_traded_prices)
        self.n_users_df = self.claim(self.n_users)
        self.buys_ust_df = self.claim(self.buys_ust)
        self.first_price_df = self.claim(self.first_price)
        
    def get_first_price(self):
        df = self.first_price_df.copy()
        cols = ['Number of Users','Price']
        df.columns = cols
        df.Price = df.Price.apply(lambda x: round(x,2))
        return df
    
    def get_first_time(self):
        df = dp.first_tx_df.copy()
        cols = ['Number of Users','Time']
        df.columns = cols
        n_data = 20
        if df.Time.nunique() < n_data:
            extra_data = []
            for i in range(n_data-df.Time.nunique()):
                extra_data.append([None,0,(pd.to_datetime(df.Time.max())+datetime.timedelta(hours=i)).strftime("%Y-%m-%d %H:%M")])
            df2 = df.append(pd.DataFrame(extra_data, columns=df.columns))
        else:
            df2 = df
        return df2
    
    def get_ust_traded_prices(self):
        b = self.ust_traded_prices_df[['belief_price','buy']].copy()
        b.columns = ['Price','Amount']
        b['Action'] = 'Bought NEB'
        s = self.ust_traded_prices_df[['belief_price','sell']].copy()
        s.columns = ['Price','Amount']
        s['Action'] = 'Sold NEB'
        ust_traded_prices = b.append(s)
        ust_traded_prices['Amount UST (M)'] = ust_traded_prices['Amount']
        ust_traded_prices['Amount'] = ust_traded_prices['Amount UST (M)'].apply(lambda x: str(round(x,2))+'M')
        return ust_traded_prices
        
    def parse(self):
        self.ust_traded_prices_df =  self.get_ust_traded_prices()
        self.first_price_parse_df =  self.get_first_price()
        self.first_time_parse_df = self.get_first_time()


# In[136]:


def claim(claim_hash):
    df = pd.read_json(
            f"https://api.flipsidecrypto.com/api/v2/queries/{claim_hash}/data/latest",
            convert_dates=["BLOCK_TIMESTAMP"])
    df.columns = [c.lower() for c in df.columns]
    return df


# In[137]:


class NebulaChartProvider:
    
    def ust_traded_prices_chart(self, ust_traded_prices):
        chart = alt.Chart(ust_traded_prices).mark_line(point=True).encode(
        x=alt.X('Price:Q', sort=alt.EncodingSortField(order='ascending')),
        y="Amount UST (M):Q",
        color=alt.Color('Action:N', scale=alt.Scale(domain=['Sold NEB','Bought NEB'],
                                                      range=['#F24A72','#21bcd7'])),
        tooltip=['Amount UST (M):N','Price:Q',"Amount:Q"]
        ).configure_mark(
            color='#21bcd7'
        ).properties(width=700).configure_axisX(
            labelAngle=0
        ).configure_view(strokeOpacity=0).configure_axis(grid=False)
        return chart
    
    def first_price_chart(self,df):
        cols = ['Number of Users','Price']
        chart = alt.Chart(df).mark_bar().encode(
            y=alt.Y(cols[0]+":Q"),
            x=alt.X(cols[1]+":Q",axis=alt.Axis(tickCount=20, labelAngle=90, tickBand = 'center')),
            tooltip=[cols[0],cols[1]]
        ).configure_mark(
            color='#21bcd7'
        ).properties(height=300).configure_view(strokeOpacity=0).configure_axis(grid=False)
        return chart
    
    def first_time_chart(self,df):
        cols = ['Number of Users','Time'] 
        chart = alt.Chart(df).mark_bar().encode(
            y=alt.Y(cols[0]+":Q"),
            x=alt.X(cols[1]+":T"),
            tooltip=[alt.Tooltip(cols[1]+':T', format='%Y-%m-%d %H:%M'), alt.Tooltip(cols[0]+":Q")]
        ).configure_mark(
            color='#21bcd7'
        ).properties(height=300).configure_axisX(
            labelAngle=0
        ).configure_view(strokeOpacity=0).configure_axis(grid=False)
        return chart
    
    def price_chart(self,hourly_stats_df):
        #272231 background
        df=hourly_stats_df[['avg_belief_price','time']]
        df.columns=['Price','Hour']
        n_data = 20
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

