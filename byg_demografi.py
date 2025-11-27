import requests
import pandas as pd
from io import StringIO

kommune = 350 # Kommunenummeret for Lejre

# API-endpoint
url = "https://api.statbank.dk/v1/data"

########################
# Alder

# Parametre / payload
payload = {
   "table": "FOLK1AM",
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
pass
