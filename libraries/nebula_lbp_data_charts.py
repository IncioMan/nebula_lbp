#!/usr/bin/env python
# coding: utf-8

# In[371]:


import pandas as pd
import altair as alt
import warnings
import requests
import datetime
import matplotlib.pyplot as plt
import json
import requests
import numpy as np
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
pd.set_option('display.max_colwidth', None)


# In[372]:


class AstroDataProvider:
    
    def __init__(self, claim):
        daic_url = "https://terra-api.daic.capital/api/tx/GetRichlistByTokenContract?apiKey=vAp6ysmAXH470YcphYxv&contract_address={}"
        self.votes = '4940a215-6e93-4107-bf08-50574b3e431d'
        self.astro_holders_url =daic_url.format("terra1xj49zyqrwpv5k928jwfpfy2ha668nwdgkwlrg3")
        self.xastro_holders_url =daic_url.format("terra14lpnyzc9z4g3ugr4lhm8s4nle0tq8vcltkhzh7")
        self.curr_block = int(requests.get("https://lcd.terra.dev/blocks/latest").json()['block']['header']['height'])
        self.votes_raw = '5de91b84-2450-4b47-b24b-20614e5dc38e'
        self.claim = claim
        
    def get_from_url(self, url):
        json = requests.get(url).json()
        return json
        
    def load(self):
        self.votes_df = self.claim(self.votes)
        self.votes_raw_df = self.claim(self.votes_raw)
        #
        json = self.get_from_url(self.astro_holders_url)['result']['holders']
        self.astro_holders_df = pd.DataFrame(json.values(),json.keys()).reset_index()
        self.astro_holders_df.columns =  ['addr','amount']
        #
        json = self.get_from_url(self.xastro_holders_url)['result']['holders']
        self.xastro_holders_df = pd.DataFrame(json.values(),json.keys()).reset_index()
        self.xastro_holders_df.columns =  ['addr','amount']
        #
       
    def parse_proposal_height(self):
        df = self.votes_raw_df
        df['proposal_end_height'] = self.votes_raw_df.event_attributes.apply(lambda x: x['proposal_end_height'])
        df['proposal_id'] = df.event_attributes.apply(lambda x: x['proposal_id'])
        df = df[['proposal_id','proposal_end_height']]
        df['current_block'] = self.curr_block
        df['Ended'] = df['proposal_end_height'] < df['current_block']
        return df
    
    def parse_proposal_recap(self):
        self.N_PROPOSALS = self.votes_df.proposal_id.nunique()+1
        # 
        votes = self.votes_df.groupby(['proposal_id','vote']).sum().voting_power.reset_index()
        against = votes[votes.vote=='against']
        against.columns = ['proposal_id','against','voting_power_against']
        for_ = votes[votes.vote=='for']
        for_.columns = ['proposal_id','for','voting_power_for']
        votes = against.merge(for_, on='proposal_id')
        votes['delta'] = votes['voting_power_for'] - votes['voting_power_against'] 
        votes['result'] = votes.apply(lambda row: 'Passed' if row.delta > 0 else 'Failed', axis=1)
        votes['result'] = votes.apply(lambda row: 'Passed' if row.delta > 0 else 'Failed', axis=1)
        df = dp.votes_df.groupby('proposal_id').voting_power.sum().reset_index()
        df.columns = ['proposal_id','tot_voting_power']
        votes = votes.merge(df)
        df2 = dp.votes_df.groupby('proposal_id').voter.nunique().reset_index()
        df2.columns = ['proposal_id','n_unique_voters']
        votes = votes.merge(df2)
        votes = votes.merge(self.proposal_height, on='proposal_id')
        votes['result'] = votes.apply(lambda row: row.result if row.Ended else 'Ongoing', axis=1)
        return votes, votes.groupby('result').proposal_id.count().reset_index()
    
    def parse_top_active_voters(self):
        return self.votes_df.groupby('voter').agg({'voting_power':'sum','tx_id':'count'})\
                            .sort_values(by=['tx_id','voting_power'], ascending=False)\
                            .head(20)
    def parse_dist_voting_power_per_proposal(self):
        return self.votes_df[['proposal_id','voting_power']]\
            .pivot(columns='proposal_id',values='voting_power')
    
    def parse_top_voters_per_proposal(self):
        df=[]
        for i in range(1,self.N_PROPOSALS):
            if(len(df)==0):
                df = self.votes_df[self.votes_df.proposal_id==1].sort_values(by='voting_power', ascending=False).head(10)
            else:
                df = df.append(self.votes_df[self.votes_df.proposal_id==i].sort_values(by='voting_power', ascending=False).head(10))
        return df
    
    def parse_votes_over_time(self):
        df_ = []
        for i in range(1,self.N_PROPOSALS):
            df = self.votes_df[self.votes_df.proposal_id==i].groupby(['hr','proposal_id','vote']).voting_power.sum().reset_index()
            df_for = df[df.vote=='for']
            df_for.columns = ['hr','proposal_id','vote_for','voting_power_for']
            df_against = df[df.vote=='against']
            df_against.columns = ['hr','proposal_id','vote_against','voting_power_against']
            df = df_for.merge(df_against, on=['hr','proposal_id'], how='outer')
            df.vote_against = df.vote_against.fillna('against')
            df.vote_for = df.vote_for.fillna('for')
            df.voting_power_against = df.voting_power_against.fillna(0)
            df.voting_power_for = df.voting_power_for.fillna(0)
            df['voting_power_for_cumsum'] = df.sort_values(by=['hr']).voting_power_for.cumsum()
            df['voting_power_against_cumsum'] = df.sort_values(by=['hr']).voting_power_against.cumsum()
            if(len(df_)==0):
                df_ = df
            else:
                df_ = df_.append(df)
        return df_
    
    def parse_voting_power_cumulative(self):
        df_ = []
        top_various_prop = []
        for i in range(1,self.N_PROPOSALS):
            df = self.votes_df
            df = df[df.proposal_id==i]
            df['voting_power_perc'] = df.voting_power/df.voting_power.sum()*100
            df = df.sort_values(by='voting_power_perc', ascending=False)
            df['voting_power_cumsum'] = df.voting_power_perc.fillna(0).cumsum()
            df['n_addresses'] = np.arange(len(df))+1
            df['n_addresses_perc'] = (1-df.n_addresses/df.n_addresses.max())*100
            assert (int(df.voting_power_cumsum.max()) in [100,99]), 'Total % should give 100'
            top_various_prop.append((i,len(df[df.voting_power_cumsum<50])+1))
            if(len(df_)==0):
                    df_ = df
            else:
                df_ = df_.append(df)
        top_various_prop_df = pd.DataFrame(top_various_prop)
        top_various_prop_df.columns = ['proposal_id','n_for_majority']
        return df_, top_various_prop_df
    
    def parse(self):
        df = self.votes_df
        df['block_timestamp'] = df.block_timestamp.astype('datetime64[ms]')
        df.block_timestamp=df.block_timestamp.apply(str).apply(lambda x: x[:-4] if len(x) == 23 else x)
        df.block_timestamp=df.block_timestamp.apply(str).apply(lambda x: x[:-3] if len(x) == 22 else x)
        df.block_timestamp=df.block_timestamp.apply(str).apply(lambda x: x[:-7] if len(x) == 26 else x)
        self.votes_df = df
        #
        self.votes_df['hr'] = self.votes_df.block_timestamp.apply(str).str[:-5] + '00'
        self.votes_df['day'] = self.votes_df.block_timestamp.apply(str).str[:-9]
        self.astro_holders_df.amount = self.astro_holders_df.amount/1000000
        self.proposal_height = self.parse_proposal_height()
        self.proposal_recap, self.proposal_results = self.parse_proposal_recap()
        self.top_active_voters = self.parse_top_active_voters()
        self.dist_voting_power_per_proposal = self.parse_dist_voting_power_per_proposal()
        self.top_voters_per_proposal = self.parse_top_voters_per_proposal()
        self.votes_over_time = self.parse_votes_over_time()
        self.voting_power_cumulative, self.majority_per_vote = self.parse_voting_power_cumulative()
        self.proposal_height = self.parse_proposal_height()
        
    def to_file(self, path='../data'):
        self.votes_df.to_json(f"{path}/votes_df",orient='records')
        self.astro_holders_df.to_json(f"{path}/astro_holders_df",orient='records')
        self.proposal_recap.to_json(f"{path}/proposal_recap", orient='records')
        self.top_active_voters.to_json(f"{path}/top_active_voters",orient='records')
        self.dist_voting_power_per_proposal.to_json(f"{path}/dist_voting_power_per_proposal",orient='records')
        self.top_voters_per_proposal.to_json(f"{path}/top_voters_per_proposal",orient='records')
        self.votes_over_time.to_json(f"{path}/votes_over_time",orient='records')
        self.voting_power_cumulative.to_json(f"{path}/voting_power_cumulative",orient='records')
        self.majority_per_vote.to_json(f"{path}/majority_per_vote",orient='records')
        self.proposal_results.to_json(f"{path}/proposal_results",orient='records')
        
    def read_file(self):
        url = 'https://raw.githubusercontent.com/IncioMan/astroport_governance/master/data/{}'
        self.votes_df =  pd.read_json(url.format('votes_df'))
        self.astro_holders_df =  pd.read_json(url.format('astro_holders_df'))
        self.proposal_recap =  pd.read_json(url.format('proposal_recap'))
        self.top_active_voters =  pd.read_json(url.format('top_active_voters'))
        self.dist_voting_power_per_proposal =  pd.read_json(url.format('dist_voting_power_per_proposal'))
        self.top_voters_per_proposal =  pd.read_json(url.format('top_voters_per_proposal'))
        self.votes_over_time =  pd.read_json(url.format('votes_over_time'))
        self.voting_power_cumulative =  pd.read_json(url.format('voting_power_cumulative'))
        self.majority_per_vote =  pd.read_json(url.format('majority_per_vote'))
        self.proposal_results =  pd.read_json(url.format('proposal_results'))


# In[373]:


def claim(claim_hash):
    df = pd.read_json(
            f"https://api.flipsidecrypto.com/api/v2/queries/{claim_hash}/data/latest",
            convert_dates=["BLOCK_TIMESTAMP"])
    df.columns = [c.lower() for c in df.columns]
    return df


# In[374]:


dp = AstroDataProvider(claim)
dp.load()
dp.parse()
dp.to_file()
#dp.read_file()


# In[375]:


dp.proposal_recap


# In[376]:


dp.votes_df[dp.votes_df.voter.fillna('').str.endswith('6xpdt')]


# In[ ]:




