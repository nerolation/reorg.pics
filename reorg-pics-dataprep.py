#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from datetime import datetime
import pandas as pd
import os


# In[ ]:


def set_google_credentials(CONFIG, GOOGLE_CREDENTIALS):
    try:
        os.environ['GOOGLE_APPLICATION_CREDENTIALS']
    except:
        print(f"setting google credentials as global variable...")
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = CONFIG \
        + GOOGLE_CREDENTIALS or input("No Google API credendials file provided." 
        + "Please specify path now:\n")
        
set_google_credentials("./config/","google-creds.json")


# In[ ]:


def slot_to_time(slot):
    timestamp = 1606824023 + slot * 12
    dt_object = datetime.utcfromtimestamp(timestamp)
    formatted_time = dt_object.strftime("%Y-%m-%d %H:%M:%S")
    return formatted_time

def slot_in_epoch(slot):
    return slot%32
    
def add_link_to_slot(slot):
    return f'[{slot}](https://beaconcha.in/slot/{slot})'


# In[ ]:


query = """
    SELECT
      DISTINCT AA.slot, AA.cl_client, AA.validator_id, BB.validator, BB.builder, BB.relay FROM (
        SELECT
      DISTINCT *
    FROM
      `ethereum-data-nero.ethdata.beaconchain_pace`
    WHERE
      slot IN (
      SELECT
        slot
      FROM
        `ethereum-data-nero.eth.validator_info`
      WHERE
        validator_id= "missed"
        )
    )) AA LEFT JOIN (
      SELECT DISTINCT slot, relay, builder, validator FROM `ethereum-data-nero.eth.mevboost_db` WHERE DATE(date) between DATE_SUB(current_date(), INTERVAL 90 DAY) and current_date()
    ) BB on AA.slot = BB.slot
    ORDER BY slot
"""
df = pd.read_gbq(query)
df["date"] = df["slot"].apply(slot_to_time)
df["slot_in_epoch"] = df["slot"].apply(slot_in_epoch)
df["slot"] = df["slot"].apply(add_link_to_slot)
df


# In[ ]:


df.to_csv("reorg-data.csv", index=None)


# In[ ]:


print("finished")


# In[ ]:




