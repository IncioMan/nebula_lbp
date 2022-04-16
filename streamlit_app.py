import streamlit as st
import pandas as pd
import altair as alt
from charts import ChartProvider
import requests
from PIL import Image
from data import DataProvider
from libraries.nebula_lbp_data_charts import NebulaChartProvider, NebulaLBPProvider

st.set_page_config(page_title="Nebula LBP - Analytics",\
        page_icon=Image.open(requests.get('https://raw.githubusercontent.com/IncioMan/mars_lockdrop/master/images/mars_logo_hd.png',stream=True).raw),\
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
    return dp.hourly_stats_df, dp.ust_traded_prices_df


data_provider = NebulaLBPProvider(claim)
chart_provider = NebulaChartProvider()

hourly_stats_df, ust_traded_prices_df = get_data(data_provider)

###
###
st.markdown(f"""
<div class="date-banner" style=\"font-size: 13px; width: 165px; position: absolute; top: 10px;\">Last update: </div>
<div class="banner" style=\"max-width: 50px;float: left;z-index: 1\">
    <a href="https://marsprotocol.io/">
        <img src="images/nebula.svg" style=\"margin-left: 5px;\" width=\"100px\">
        <img src="https://raw.githubusercontent.com/IncioMan/mars_lockdrop/master/images/M.png" width=\"100px\">
        <img src="https://raw.githubusercontent.com/IncioMan/mars_lockdrop/master/images/A.png" width=\"100px\">
        <img src="https://raw.githubusercontent.com/IncioMan/mars_lockdrop/master/images/R.png" style=\"margin-left: 6px;\" width=\"100px\">
        <img src="https://raw.githubusercontent.com/IncioMan/mars_lockdrop/master/images/S.png" width=\"100px\">
    </a>
    <div style=\"width: 100px;margin-top: 5px;margin-bottom: 10px;\"><span class="terminated"></span>Terminated</div>
    <div style=\"border-top: 3px solid #ffffff;width: 100px;margin-top: 15px;padding-bottom: 20px;\"></div>
    <div style=\"width: 100px; margin-left: 10px;\">
        <a href="https://flipsidecrypto.xyz"><img src="https://raw.githubusercontent.com/IncioMan/mars_lockdrop/master//images/fc.png" width=\"30px\"></a>
        <a href="https://twitter.com/IncioMan"><img src="https://raw.githubusercontent.com/IncioMan/mars_lockdrop/master//images/twitter.png" width=\"50px\"></a>
    </div>
</div>
""", unsafe_allow_html=True)
  

col1, col2,col3 = st.columns([2,8,1])
with col2:
    st.subheader('Amount of UST locked')
    st.markdown("""Distribution of UST locked for different durations.""")
    st.markdown("""Have users preferred shorter or longer durations? Has one duration the largest share?""")
    st.altair_chart(chart_provider.price_chart(hourly_stats_df), use_container_width=True)

col1, col2,col3 = st.columns([2,8,1])
with col2:
    st.subheader('Amount of UST locked')
    st.markdown("""Distribution of UST locked for different durations.""")
    st.markdown("""Have users preferred shorter or longer durations? Has one duration the largest share?""")
    st.altair_chart(chart_provider.ust_traded_prices_chart(ust_traded_prices_df), use_container_width=True)



###
#st.markdown("""This dashboard was built with love for the 🌖 community by [IncioMan](https://twitter.com/IncioMan) and [sem1d5](https://twitter.com/sem1d5)""")
st.markdown("""
<style>
    @media (min-width:640px) {
        .block-container {
            padding-left: 7rem;
            padding-right: 7rem;
        }
    }
    @media (min-width:800px) {
        .block-container {
            padding-left: 7rem;
            padding-right: 7rem;
        }
    }
    .block-container
    {
        padding-bottom: 1rem;
        padding-top: 5rem;
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
        border: 1px solid #FFFFFF;
        background-color: #FFFFFF;
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

    @media (min-width:800px) {
        .css-yksnv9 {
            margin-top: 30px;
        }
        [data-testid="metric-container"]{
            padding-bottom: 20px;
        }
        .banner {
            position: fixed;
        }
        .date-banner{
            right: 115px;
        }
    }
    </style>
    """, unsafe_allow_html=True)
