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

df_alder = hentdata(payload_alder_køn)
df_herkomst = hentdata(payload_herkomst)
df_uddannelse = hentdata(payload_uddannelse)
df_postnr = hentdata(payload_postnr) # Tager ikke højde for, at postnumre ikke følger kommunegrænser


pass
