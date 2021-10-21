import pandas as pd
sheet_id = '1X_3s7widO60dPf4js8e9bRLL_xX8Qnq9OIAWQJgmXI4'
sheet_name = 'restaurantes_edited'
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"

df = pd.read_csv(url)
print(df)