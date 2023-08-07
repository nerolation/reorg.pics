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
    ) AA LEFT JOIN (
      SELECT DISTINCT slot, relay, builder, validator FROM `ethereum-data-nero.eth.mevboost_db` WHERE DATE(date) between DATE_SUB(current_date(), INTERVAL 90 DAY) and DATE_Add(current_date(), INTERVAL 1 DAY)
    ) BB on AA.slot = BB.slot
    ORDER BY slot
"""
df = pd.read_gbq(query)
df["date"] = df["slot"].apply(slot_to_time)
df["slot_in_epoch"] = df["slot"].apply(slot_in_epoch)
df["slot"] = df["slot"].apply(add_link_to_slot)
df



# In[ ]:


#def max_slot(slot):
#    return int(slot.split("[")[1].split("]")[0])
##df["slot"] = df["slot"].apply(max_slot)
#df[~df["relay"].isna()].sort_values("slot", ascending=False).head(2000).to_csv("missed-slot-data.csv", index=False)


# In[ ]:


#df = df.sort_values("slot", ascending=False)#.head(1000)


# In[ ]:


#pd.read_csv("missed-slot-data.csv")


# In[ ]:





# In[ ]:


query = """
  SELECT
  DISTINCT AA.slot,
  AA.validator_id,
  BB.validator,
  BB.builder,
  BB.relay,
  BB.cl_client
FROM (
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
      validator_id= "missed" ) ) AA
LEFT JOIN (
  SELECT
    DD.*,
    CC.cl_client
  FROM (
    SELECT
      DISTINCT slot,
      relay,
      builder,
      validator
    FROM
      `ethereum-data-nero.eth.mevboost_db`
    WHERE
      DATE(date) BETWEEN DATE_SUB(CURRENT_DATE(), INTERVAL 90 DAY)
      AND CURRENT_DATE()) DD
  LEFT JOIN (
    SELECT
      slot,
      cl_client
    FROM
      `ethereum-data-nero.ethdata.beaconchain_pace`)CC
  ON
    DD.slot = CC.slot ) BB
ON
  AA.slot+1 = BB.slot
ORDER BY
  slot
    """
df_reorg = pd.read_gbq(query)
df_reorg["date"] = df_reorg["slot"].apply(slot_to_time)
df_reorg["slot_in_epoch"] = df_reorg["slot"].apply(slot_in_epoch)
df_reorg["slot"] = df_reorg["slot"].apply(add_link_to_slot)
df_reorg

df_reorg.to_csv("reorgers-data.csv", index=None)


# In[ ]:


df.to_csv("reorg-data.csv", index=None)
df_reorg.to_csv("reorgers-data.csv", index=None)

df2 = pd.read_gbq('SELECT DISTINCT validator, count(Distinct slot) slots FROM `ethereum-data-nero.eth.mevboost_db` WHERE validator is not null and DATE(date) between DATE_SUB(current_date(), INTERVAL 90 DAY) and current_date() group by validator order by slots desc limit 10')
df3 = pd.read_gbq('SELECT DISTINCT relay, count(Distinct slot) slots FROM `ethereum-data-nero.eth.mevboost_db` WHERE relay is not null and DATE(date) between DATE_SUB(current_date(), INTERVAL 90 DAY) and current_date() group by relay order by slots desc limit 10')
df4 = pd.read_gbq('SELECT DISTINCT builder, count(Distinct slot) slots FROM `ethereum-data-nero.eth.mevboost_db` WHERE builder is not null and DATE(date) between DATE_SUB(current_date(), INTERVAL 90 DAY) and current_date() group by builder order by slots desc limit 10')
df2.to_csv("validator_slots.csv", index=None)
df3.to_csv("relay_slots.csv", index=None)
df4.to_csv("builder_slots.csv", index=None)
df5 = pd.read_gbq('''SELECT DISTINCT cl_client, count(cl_client) slots FROM 
(SELECT cl_client, slot FROM `ethereum-data-nero.ethdata.beaconchain_pace` order by slot desc limit 216000)
group by cl_client
order by slots desc
''')
df5.to_csv("clclient_slots.csv", index=None)


# In[ ]:


print("finished")


# In[ ]:




