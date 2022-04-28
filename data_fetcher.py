import pandas as pd
from libraries.nebula_lbp_data_charts import NebulaChartProvider, NebulaLBPProvider
def claim(claim_hash):
    df = pd.read_json(
            f"https://api.flipsidecrypto.com/api/v2/queries/{claim_hash}/data/latest",
            convert_dates=["BLOCK_TIMESTAMP"])
    df.columns = [c.lower() for c in df.columns]
    return df

data_provider = NebulaLBPProvider(claim)
data_provider.load()
data_provider.parse()
data_provider.to_csv('./data')