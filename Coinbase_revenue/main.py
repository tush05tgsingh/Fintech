"""
sec endpoint : https://www.sec.gov/api/xbrl/company_concept/CIK0001679788/us-gaap:Revenues/USD.json
"""

from sec_api import XbrlApi, ExtractorApi
import pandas as pd
from IPython.display import display, HTML
import io

extractorapi = ExtractorApi("2b48b80bbfb42bc4ac67b3812ca3f1a00f3f25440b39e612134d9445f250fa03")

URLS = {
    "url_10k_coinbase_2021": "https://www.sec.gov/ix?doc=/Archives/edgar/data/0001679788/000167978821000010/coin-20210331.htm",
    "url_10k_coinbase_2022": "https://www.sec.gov/Archives/edgar/data/1679788/000162828023005100/a20221231-10k.htm",
    "url_10q_coinbase_q1_2023": "https://www.sec.gov/Archives/edgar/data/1679788/000162828023007068/a20230331-10q.htm",
    "url_10q_coinbase_q2_2023": "https://www.sec.gov/Archives/edgar/data/1679788/000162828023009040/a20230630-10q.htm",
    "url_10q_coinbase_q3_2023": "https://www.sec.gov/Archives/edgar/data/1679788/000162828023011092/a20230930-10q.htm", 
}

# extract text section "Item 1 - Business" from 10-K
item_1_html = extractorapi.get_section(URLS["url_10k_coinbase_2021"], 'part1item2', 'html')
tables = pd.read_html(io.StringIO(item_1_html), header=0)
df = pd.DataFrame(tables[0])
print(df)