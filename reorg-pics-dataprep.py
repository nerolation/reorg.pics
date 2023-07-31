#!/usr/bin/env python
# coding: utf-8

# In[1]:


from datetime import datetime
import pandas as pd
import os


# In[2]:


def set_google_credentials(CONFIG, GOOGLE_CREDENTIALS):
    try:
        os.environ['GOOGLE_APPLICATION_CREDENTIALS']
    except:
        print(f"setting google credentials as global variable...")
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = CONFIG \
        + GOOGLE_CREDENTIALS or input("No Google API credendials file provided." 
        + "Please specify path now:\n")
        
set_google_credentials("./config/","google-creds.json")


# In[3]:


def slot_to_time(slot):
    timestamp = 1606824023 + slot * 12
    dt_object = datetime.utcfromtimestamp(timestamp)
    formatted_time = dt_object.strftime("%Y-%m-%d %H:%M:%S")
    return formatted_time

def slot_in_epoch(slot):
    return slot%32
    
def add_link_to_slot(slot):
    return f'[{slot}](https://beaconcha.in/slot/{slot})'


# In[4]:


query = """
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
"""
df = pd.read_gbq(query)
df["date"] = df["slot"].apply(slot_to_time)
df["slot_in_epoch"] = df["slot"].apply(slot_in_epoch)
df["slot"] = df["slot"].apply(add_link_to_slot)
df


# In[5]:


df.to_csv("reorg-data.csv", index=None)


# In[6]:


print("finished")

