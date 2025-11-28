import requests
import pandas as pd
from io import StringIO

kommune = 350 # Kommunenummeret for Lejre

# API-endpoint
url = "https://api.statbank.dk/v1/data"

########################
# Alder

# Parametre / payload
payload_alder_køn = {
   "table": "FOLK1AM",
   "format": "CSV",
   "variables": [
      {
         "code": "KØN",
         "values": [
            "*"
         ]
      },
      {
         "code": "ALDER",
         "values": [
            "*"
         ]
      },
      {
         "code": "OMRÅDE",
         "values": [
            str(kommune)
         ]
      }
   ]
}

payload_herkomst = {
   "table": "FOLK1E",
   "format": "CSV",
   "variables": [
      {
         "code": "KØN",
         "values": [
            "TOT"
         ]
      },
      {
         "code": "ALDER",
         "values": [
            "IALT"
         ]
      },
      {
         "code": "OMRÅDE",
         "values": [
            "350"
         ]
      },
      {
         "code": "HERKOMST",
         "values": [
            "*"
         ]
      }
   ]
}

payload_uddannelse = {
   "table": "HFUDD11",
   "format": "CSV",
   "variables": [
      {
         "code": "KØN",
         "values": [
            "TOT"
         ]
      },
      {
         "code": "ALDER",
         "values": [
            "TOT"
         ]
      },
      {
         "code": "BOPOMR",
         "values": [
            "350"
         ]
      },
      {
         "code": "HERKOMST",
         "values": [
            "TOT"
         ]
      },
      {
         "code": "HFUDD",
         "values": [
            "*"
         ]
      }
   ]
}

payload_postnr = {
   "table": "POSTNR1",
   "format": "CSV",
   "variables": [
      {
         "code": "PNR20",
         "values": [
            "*"
         ]
      },
      {
         "code": "KØN",
         "values": [
            "TOT"
         ]
      },
      {
         "code": "ALDER",
         "values": [
            "IALT"
         ]
      }
   ]
}

def hentdata(payload):
    # POST request til API
    response = requests.post(url, json=payload)

    # Tjek om requesten lykkedes
    if response.status_code == 200:
        # Læs CSV-data direkte ind i en Pandas DataFrame
        df = pd.read_csv(StringIO(response.text), sep=";")
        print(df.head())
    else:
        print(f"Fejl ved hentning: {response.status_code}")
        print(response.text)
    return df

# Rå indhentning fra Statistikbanken
df_alder = hentdata(payload_alder_køn)
df_herkomst = hentdata(payload_herkomst)
df_uddannelse = hentdata(payload_uddannelse)
df_postnr = hentdata(payload_postnr) # Tager ikke højde for, at postnumre ikke følger kommunegrænser

# Bearbejdning

# Kønsfordeling
df_køn = df_alder[(df_alder['ALDER']=='Alder i alt')&(df_alder['KØN']!='I alt')][['KØN','INDHOLD']]
df_køn['Brøkdel']=df_køn['INDHOLD']/df_køn['INDHOLD'].sum()
df_køn['Køn']=df_køn['KØN'].map({'Mænd':'Mand','Kvinder':'Kvinde'})
df_køn = df_køn[['Køn','Brøkdel']]

# Aldersfordeling
aldersgruppering = [18,25,30,40,50,60,70,80,200]
group_labels = ['18-24', '25-29', '30-39', '40-49', '50-59', '60-69', '70-79','80+']

df_alder = df_alder[df_alder['KØN']!='I alt'][['ALDER','INDHOLD']]
df_alder = df_alder[df_alder['ALDER']!='Alder i alt']
df_alder['Alder']=df_alder['ALDER'].str.slice(stop=-2).astype(int)
df_alder['Aldersgruppe']=df_alder['Alder']
df_alder['aldersgruppe'] = pd.cut(df_alder['Alder'], bins=aldersgruppering, right=False, labels=group_labels)
print(df_alder[['Alder','INDHOLD']])

pass
