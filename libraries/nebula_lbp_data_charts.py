#!/usr/bin/env python
# coding: utf-8

# In[392]:


import pandas as pd
import altair as alt
import warnings
import requests
import datetime
alt.renderers.set_embed_options(theme='dark')
pd.set_option('display.max_colwidth', None)


# In[393]:


class NebulaLBPProvider:
    
    def __init__(self, claim):
        self.first_tx = '4f066998-97c3-4851-b0d6-bf11508d46a0'
        self.n_tx_users = '81e1f1ff-f27d-4727-8bbf-3cb7e00dfde3'
        self.hourly_stats = '7a8ea41c-8c5e-4ca7-b466-6844b37b1adc'
        self.ust_traded_prices = '75cb6f4e-a94a-4efa-bc39-187bb7d6c54d'
        self.buys_ust = 'ffb18f2a-061f-44b9-9acf-44d509ec4681'
        self.first_price = '5364bf88-617f-40ec-b95f-b3c003fd29f7'
        self.vote = 'd1cb394d-cda8-41a8-8f0d-030ee74c9d93'
        self.airdrop = 'd140dd89-7157-4166-95ef-f7813fec7910'
        self.stake = '90d2caca-80d6-4996-8fe0-ba9a86edd485'
        self.buys_sells = 'f6317ba0-be76-4e85-9339-7aa172a5afc0'
        self.buys_sells_ust = '9934570e-542b-4e3c-bdd2-b9070c22b9a0'
        self.claim = claim
        
    def load(self):
        self.first_tx_df = self.claim(self.first_tx)
        self.n_tx_users_df = self.claim(self.n_tx_users)
        self.hourly_stats_df = self.claim(self.hourly_stats)
        self.ust_traded_prices_df = self.claim(self.ust_traded_prices)
        self.buys_ust_df = self.claim(self.buys_ust)
        self.first_price_df = self.claim(self.first_price)
        self.vote_df = self.claim(self.vote)
        self.stake_df = self.claim(self.stake)
        self.airdrop_df = self.claim(self.airdrop)
        self.buys_sells_df = self.claim(self.buys_sells)
        self.buys_sells_ust_df = self.claim(self.buys_sells_ust)
        
    def get_first_price(self):
        df = self.first_price_df.copy()
        cols = ['Price','Number of Users']
        df.columns = cols
        df.Price = df.Price.apply(lambda x: round(x,2))
        return df
    
    def get_first_time(self):
        df = self.first_tx_df.copy()
        cols = ['Time','Number of Users']
        df.columns = cols
        n_data = 20
        if df.Time.nunique() < n_data:
            extra_data = []
            for i in range(n_data-df.Time.nunique()):
                extra_data.append([(pd.to_datetime(df.Time.max())+datetime.timedelta(hours=i)).strftime("%Y-%m-%d %H:%M"),0])
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
    
    def get_n_prices_per_users(self):
        df = self.buys_ust_df.copy()
        df.belief_price = df.belief_price.apply(lambda x: round(x,2))
        df = df.groupby('sender').belief_price.count().reset_index()
        df = df.groupby('belief_price').sender.count().reset_index()
        cols = ['Number of Different Prices','Number of Users']
        df.columns = cols
        return df
    
    def addr_participation(self):
        dep_addr = set(self.buys_sells_df.sender)
        airdrop_addr = set(self.airdrop_df.sender)
        inters_addr = dep_addr.intersection(airdrop_addr)
        cols = ['Number of Users','Participated in LBP?']
        airdrop_in_lbp = pd.DataFrame([[len(airdrop_addr) - len(inters_addr), 'No'],
                     [len(inters_addr), 'Yes']], columns=cols)
        cols = ['Number of Users','Received The Airdrop?']
        lbp_from_airdrop = pd.DataFrame([[len(dep_addr) - len(inters_addr), 'No'],
                     [len(inters_addr), 'Yes']], columns=cols)
        return airdrop_in_lbp, lbp_from_airdrop
    
    def sender_airdrop_op(self):
        sod = {}
        so = self.buys_sells_df[['sender','type']].drop_duplicates(ignore_index=True)
        for s, row in so.iterrows():
            if not row.sender in sod:
                sod[row.sender] = set()
            sod[row.sender].add(row.type)
        data = []
        for s, ops in sod.items():
            if('sell' in ops):
                d = [s, 'Sold']
            if('buy' in ops):
                d = [s, 'Bought']
            if('sell' in ops and 'buy' in ops):
                d = [s, 'Bought and Sold']
            data.append(d) 
        sender_op = pd.DataFrame(data, columns=['sender','operation'])
        sender_airdrop_op = self.airdrop_df.merge(sender_op,on='sender')[['sender','operation']]\
                              .groupby('operation').sender.count().reset_index()
        sender_airdrop_op.columns = ['Actions performed','Number of users']
        return sender_airdrop_op
    
    def amount_airdropped_dumped(self):
        sold = self.airdrop_df[['sender','tx_id']].merge(self.buys_sells_df[self.buys_sells_df.type=='buy'],on='sender').amount.sum()
        df = pd.DataFrame([['Sold',sold],
                     ['Kept', 10000000-sold]], columns=['Type','Amount'])
        df['Amount'] = df['Amount'].apply(lambda x: round(x,2))
        return df
    
    def get_net_ust(self):
        self.buys_sells_ust_df['amount_signed'] = self.buys_sells_ust_df\
                                                    .apply(lambda row: row.amount if row.type=='buy' \
                                                                           else -row.amount, axis=1)
        return self.buys_sells_ust_df.amount_signed.sum()
        
    def parse(self):
        self.ust_traded_prices_df =  self.get_ust_traded_prices()
        self.first_price_parse_df =  self.get_first_price()
        self.first_time_parse_df = self.get_first_time()
        self.n_prices_per_users_df = self.get_n_prices_per_users()
        self.airdrop_in_lbp, self.lbp_from_airdrop = self.addr_participation()
        self.sender_airdrop_op_df = self.sender_airdrop_op()
        self.amount_airdropped_dumped_df = self.amount_airdropped_dumped()
        self.net_ust_df = self.get_net_ust()
        self.n_users_df = self.buys_sells_df.sender.nunique()
        
    def to_csv(self, path='../data'):
        self.ust_traded_prices_df.to_csv(f"{path}/ust_traded_prices_df.csv")
        self.first_price_parse_df.to_csv(f"{path}/first_price_parse_df.csv")
        self.hourly_stats_df.to_csv(f"{path}/hourly_stats_df.csv")
        self.first_time_parse_df.to_csv(f"{path}/first_time_parse_df.csv")
        self.n_prices_per_users_df.to_csv(f"{path}/n_prices_per_users_df.csv")
        self.airdrop_in_lbp.to_csv(f"{path}/airdrop_in_lbp.csv")
        self.lbp_from_airdrop.to_csv(f"{path}/lbp_from_airdrop.csv")
        self.sender_airdrop_op_df.to_csv(f"{path}/sender_airdrop_op_df.csv")
        self.amount_airdropped_dumped_df.to_csv(f"{path}/amount_airdropped_dumped_df.csv")
        
    def read_csv(self):
        url = 'https://raw.githubusercontent.com/IncioMan/nebula_lbp/master/data/{}.csv'
        self.ust_traded_prices_df =  pd.read_csv(url.format('ust_traded_prices_df'), index_col=0)
        self.first_price_parse_df =  pd.read_csv(url.format('first_price_parse_df'), index_col=0)
        self.hourly_stats_df =  pd.read_csv(url.format('hourly_stats_df'), index_col=0)
        self.first_time_parse_df = pd.read_csv(url.format('first_time_parse_df'), index_col=0)
        self.n_prices_per_users_df = pd.read_csv(url.format('n_prices_per_users_df'), index_col=0)
        self.airdrop_in_lbp = pd.read_csv(url.format('airdrop_in_lbp'), index_col=0)
        self.lbp_from_airdrop = pd.read_csv(url.format('lbp_from_airdrop'), index_col=0)
        self.sender_airdrop_op_df = pd.read_csv(url.format('sender_airdrop_op_df'), index_col=0)
        self.amount_airdropped_dumped_df = pd.read_csv(url.format('amount_airdropped_dumped_df'), index_col=0)


# In[394]:


def claim(claim_hash):
    df = pd.read_json(
            f"https://api.flipsidecrypto.com/api/v2/queries/{claim_hash}/data/latest",
            convert_dates=["BLOCK_TIMESTAMP"])
    df.columns = [c.lower() for c in df.columns]
    return df


# In[395]:


class NebulaChartProvider:
    
    def ust_traded_prices_chart(self, ust_traded_prices):
        chart = alt.Chart(ust_traded_prices).mark_point().encode(
        x=alt.X('Price:Q', sort=alt.EncodingSortField(order='ascending')),
        y="Amount UST (M):Q",
        color=alt.Color('Action:N', scale=alt.Scale(domain=['Sold NEB','Bought NEB'],
                                                      range=['#F24A72','#21bcd7'])),
        tooltip=['Action','Amount UST (M):N','Price:Q']
        ).configure_mark(
            color='#21bcd7'
        ).properties(width=700).configure_axisX(
            labelAngle=0
        ).configure_view(strokeOpacity=0).configure_axis(grid=False)
        return chart
    
    def first_price_chart(self,df):
        cols = ['Number of Users','Price']
        chart = alt.Chart(df).mark_line(point=True).encode(
            y=alt.Y(cols[0]+":Q"),
            x=alt.X(cols[1]+":Q",axis=alt.Axis(tickCount=20, labelAngle=0, tickBand = 'center')),
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
    
    def n_prices_per_users_df_chart(self,df):
        cols = ['Number of Users','Number of Different Prices']
        chart = alt.Chart(df).mark_bar().encode(
            y=alt.Y(cols[0]+":Q"),
            x=alt.X(cols[1]+":N",axis=alt.Axis(tickCount=10, labelAngle=30, tickBand = 'center')),
            tooltip=[cols[1], cols[0]]
        ).configure_mark(
            color='#21bcd7'
        ).properties(height=300).configure_axisX(
            labelAngle=0
        ).configure_view(strokeOpacity=0).configure_axis(grid=False)
        return chart
    
    def user_distr_pie(self, df, cols):
        chart = alt.Chart(df).mark_arc(innerRadius=60).encode(
            theta=alt.Theta(field=cols[0], type="quantitative"),
            color=alt.Color(field=cols[1], type="nominal",
                    #sort=['MARS & UST','MARS','UST'],
                    scale=alt.Scale(domain=df[cols[1]].unique(), range=['#F24A72','#21bcd7']),
                    legend=alt.Legend(
                    orient='none',
                    padding=10,
                    legendY=-10,
                    direction='vertical')),
            tooltip=[cols[1]+':N',cols[0]+':N']
        ).configure_view(strokeOpacity=0)
        return chart
    
    def sender_airdrop_op_charts(self, df, cols):
        df.columns = cols
        chart = alt.Chart(df).mark_arc(innerRadius=60).encode(
                    theta=alt.Theta(field=cols[1], type="quantitative"),
                    color=alt.Color(field=cols[0], type="nominal",
                            #sort=['MARS & UST','MARS','UST'],
                            scale=alt.Scale(domain=df[cols[0]].unique(), range=['#ffffff','#21bcd7','#F24A72']),
                            legend=alt.Legend(
                            orient='none',
                            padding=10,
                            legendY=-10,
                            direction='vertical')),
                    tooltip=[cols[1]+':N',cols[0]+':N']
                ).configure_view(strokeOpacity=0)
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

