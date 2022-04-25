from tkinter import N
import streamlit as st
import pandas as pd
import altair as alt
from charts import ChartProvider
import requests
from PIL import Image
import datetime
from data import DataProvider
from libraries.nebula_lbp_data_charts import NebulaChartProvider, NebulaLBPProvider

st.set_page_config(page_title="Nebula LBP - Analytics",\
        page_icon=Image.open(requests.get('https://raw.githubusercontent.com/IncioMan/nebula_lbp/master/images/logo.png',stream=True).raw),\
        layout='wide')

###

@st.cache(ttl=10000, show_spinner=False, allow_output_mutation=True)
def claim(claim_hash):
    df = pd.read_json(
            f"https://api.flipsidecrypto.com/api/v2/queries/{claim_hash}/data/latest",
            convert_dates=["BLOCK_TIMESTAMP"])
    df.columns = [c.lower() for c in df.columns]
    return df

@st.cache(ttl=10000, show_spinner=False, allow_output_mutation=True, persist=True)
def get_url(url, index_col):
    return pd.read_csv(url, index_col=index_col)
    
@st.cache(ttl=10000, show_spinner=False, allow_output_mutation=True, persist=True)
def get_data(dp):
    dp.load()
    dp.parse()
    return dp.hourly_stats_df, dp.ust_traded_prices_df, \
                dp.first_time_parse_df, dp.first_price_parse_df,\
                    dp.n_prices_per_users_df, dp.airdrop_in_lbp, dp.lbp_from_airdrop,\
                        dp.buys_ust_df.sender.nunique(), dp.amount_airdropped_dumped_df, \
                            dp.sender_airdrop_op_df, dp.net_ust_df




data_provider = NebulaLBPProvider(claim)
cp = NebulaChartProvider()

hourly_stats_df, ust_traded_prices_df, \
    first_time_df, first_price_df,\
         n_prices_per_users_df, airdrop_in_lbp, \
             lbp_from_airdrop, n_users, \
                 amount_airdropped_dumped_df, sender_airdrop_op_df,\
                     net_ust_df = get_data(data_provider)


###
###
st.markdown(f"""
<div class="banner" style=\"max-width: 200px;float: left;z-index: 1;\">
    <a href="https://app.neb.money/">
        <img src="https://raw.githubusercontent.com/IncioMan/nebula_lbp/master/images/nebula.svg" style=\"margin-left: 5px;\" width=\"200px\">
    </a>
    <div class='banner-desc-container'>
        <div>
        Nebula is a protocol built on Terra that enables users to invest in narratives and strategies expressed through decentralized basket instruments called clusters.
        </div>
        <div>
        Liquidity Bootstrapping Pool, it is a mechanism for launching tokens that is designed to defer bot activity by starting the token price high and allowing it to float down to price discovery over a pre-set period of time, in this case 5 days. 
        </div>
    </div>
    <div style=\"width: 100px;margin-top: 5px;margin-bottom: 10px;\"><span class="blink_me"></span>Active</div>
    <div style=\"border-top: 3px solid #ffffff;width: 100px;margin-top: 15px;\"></div>
    <div style=\"width: 100px; margin-left: 10px;\">
        <a href="https://flipsidecrypto.xyz"><img src="https://raw.githubusercontent.com/IncioMan/mars_lockdrop/master//images/fc.png" width=\"30px\"></a>
        <a href="https://twitter.com/IncioMan"><img src="https://raw.githubusercontent.com/IncioMan/mars_lockdrop/master//images/twitter.png" width=\"50px\"></a>
    </div>
</div>
""", unsafe_allow_html=True)
###
hr_left = round((datetime.datetime(2022, 5, 2, 0, 0, 0, 0) - datetime.datetime.now()).seconds/60,0)
st.markdown(f"""
<div class="metrics-banner" style=\"max-width: 200px;float: right;z-index: 1;\">
    <div class='metrics-container'>
        <div class='metric-container-row'>
            <div class='metric-container' style=\"border-right: solid #21bcd7; border-bottom: solid #21bcd7;\">
                <div class='metric-name'>
                    Price
                </div>
                <div class='metric-value'>
                    0.34$
                </div>
            </div>
            <div class='metric-container' style=\"border-bottom: solid #21bcd7;\">
                <div class='metric-name'>
                    Users
                </div>
                <div class='metric-value'>
                    {n_users}
                </div>
            </div>
        </div>
        <div class='metric-container-row'>
            <div class='metric-container' style=\"border-right: solid #21bcd7;\">
                <div class='metric-name'>
                    Net UST
                </div>
                <div class='metric-value'>
                    {round(net_ust_df/1000000,1)}M
                </div>
            </div>
            <div class='metric-container'>
                <div class='metric-name'>
                    Hours Left
                </div>
                <div class='metric-value'>
                    {int(hr_left)}
                </div>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)
  

col1, col2,col3 = st.columns([3,8,1.5])
with col2:
    st.subheader('Price of NEB')
    st.markdown("""Observe the average buy price over the course of the event.  
    Has the price been increasing or decreasing over time? After how much time has the price had its first spike?""")
    st.altair_chart(cp.price_chart(hourly_stats_df), use_container_width=True)

col1, col2,col3 = st.columns([3,8,1.5])
with col2:
    st.subheader('UST Exchanged at each price')
    st.markdown("""UST can either be used to buy NEB or obtained by selling NEB previously bought.  
    Has the amount of UST used to buy NEB always been greater than the one obtained by selling NEB?""")
    st.altair_chart(cp.ust_traded_prices_chart(ust_traded_prices_df), use_container_width=True)

col1, col2,col3 = st.columns([3,8,1.5])
with col2:
    st.subheader('Users\' First Swap (Time)')
    st.markdown("""
    In LBPs being fast might not be the best decision.  
    What hour did see the highest number of users make their first swap?
    """)
    st.altair_chart(cp.first_time_chart(first_time_df), use_container_width=True)
col1, col2,col3 = st.columns([3,8,1.5])
with col2:
    st.subheader('Users\' First Swap (Price)')
    st.markdown("""
    In LBPs the price decreases over time if nobody buys or sells from the pool.  
    At what price did the highest number of users buy the NEB token?
    """)
    st.altair_chart(cp.first_price_chart(first_price_df), use_container_width=True)
col1, col2,col3 = st.columns([3,8,1.5])
with col2:
    st.subheader('Different Prices Users Bought At')
    st.markdown("""
    Users might DCA or simply buy at several different prices.  
    At how many different prices have most of the user bought? What is the max n° of different prices per user?
    """)
    st.altair_chart(cp.n_prices_per_users_df_chart(n_prices_per_users_df), use_container_width=True)

col1, col21,col2,col3 = st.columns([3,4,4,1.5])
with col21:
    st.subheader('Airdrop Receivers in LBP')
    st.markdown("""
    Luna stakers have been airdropped some NEB tokens. How many of them are participating 
    in the LBP?
    """)
    st.altair_chart(cp.user_distr_pie(airdrop_in_lbp, airdrop_in_lbp.columns), use_container_width=True)
with col2:
    st.subheader('LBP Participants Airdrop')
    st.markdown("""
    Out of all the LBP participants so far, how many of these have received the Nebula Airdrop?""")
    st.altair_chart(cp.user_distr_pie(lbp_from_airdrop, lbp_from_airdrop.columns), use_container_width=True)
col1, col21,col2,col3 = st.columns([3,4,4,1.5])
with col21:
    st.subheader('What Airdrop receivers do?')
    st.markdown("""
    How many of the users who claimed their airdrop have sold their NEB? How many have bought more?
    """)
    st.altair_chart(cp.sender_airdrop_op_charts(sender_airdrop_op_df, sender_airdrop_op_df.columns), use_container_width=True)
with col2:
    st.subheader('Airdrop Retained')
    st.markdown("""
    How many of the total NEB airdropped (1M) have been sold by those who received it?""")
    st.altair_chart(cp.sender_airdrop_op_charts(amount_airdropped_dumped_df, amount_airdropped_dumped_df.columns), use_container_width=True)



###
#st.markdown("""This dashboard was built with love for the 🌖 community by [IncioMan](https://twitter.com/IncioMan) and [sem1d5](https://twitter.com/sem1d5)""")
st.markdown("""
<style>
    @media (min-width:640px) {
        .block-container {
            padding-left: 1rem;
            padding-right: 7rem;
        }
    }
    @media (min-width:800px) {
        .block-container {
            padding-left: 5rem;
            padding-right: 7rem;
        }
    }
    .block-container
    {
        padding-bottom: 1rem;
        padding-top: 2rem;
    }
    .st-bx{
        background-color: transparent;
    }
    .st-bu{
        background-color: transparent;
    }
    .st-bv{
        background-color: transparent;
    }
    .css-k7dvn8{
        background-color: transparent;
    }
</style>
""", unsafe_allow_html=True)
hide_streamlit_style = """
                        <style>
                        #MainMenu {visibility: hidden;}
                        #footer {visibility: hidden;}
                        </style>
                        """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)
st.markdown("""
    <style>
    [data-testid="stHeader"]{
        display: none;
    }
    .terminated {
        margin-right: 10px;
        width: 10px;
        height: 10px;
        display: inline-block;
        border: 1px solid red;
        background-color: red;
        border-radius: 100%;
        opacity: 0.8;
    }

    .idle {
        margin-right: 10px;
        width: 10px;
        height: 10px;
        display: inline-block;
        border: 1px solid grey;
        background-color: grey;
        border-radius: 100%;
        opacity: 0.8;
    }

    .blink_me {
        margin-left: 15px;
        margin-right: 15px;
        animation: blinker 2s linear infinite;
        width: 10px;
        height: 10px;
        display: inline-block;
        border: 1px solid #21bcd7;
        background-color: #21bcd7;
        border-radius: 100%;
        }
        @keyframes blinker {
        50% {
            opacity: 0;
        }
    }

    .date-banner{
        right: 15px;
    }

    .metrics-container{
        min-height: 150px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        align-items: center;
    }

    .metric-container-row{
        display: flex;
        width: 160px;
    }
    .metric-container{
        display: flex;
        flex-direction: column;
        font-family: sans-serif;
        padding: 12px;
        width: 50%;
    }
    .metric-name{
        font-size: 12px;
        border-bottom: solid;
        border-color: #21bcd7;
    }
    .metric-value{
        font-size: 20px;
        
    }

    @media (min-width:1000px) {
        .css-yksnv9 {
            margin-top: 30px;
        }
        [data-testid="metric-container"]{
            padding-bottom: 20px;
        }
        .banner {
            position: fixed;
            top: 70px;
        }
        .metrics-banner{
            width: 180px;
            float: right;
            z-index: 1;
            position: fixed;
            right: 5em;
            top: 74px;
            overflow: auto;
        }
        .date-banner{
            right: 115px;
        }
        .banner-desc-container{
            display: flex;
            flex-direction: column;
            justify-content: space-evenly;
            min-height: 450px;
        }
    }
    </style>
    """, unsafe_allow_html=True)
