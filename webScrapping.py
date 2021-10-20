import pandas as pd
from bs4 import BeautifulSoup
from urllib.request import urlopen



soup = BeautifulSoup(open(r'data/RestaurantesRionegroGuru.html', encoding="utf8"), "html.parser")
df_rest = pd.DataFrame(columns=['nombre', 'descripcion'])
new_row = {'nombre': 'a', 'descripcion': 'descripcion'}
df_rest.append(new_row, ignore_index = True)
headers = soup.find_all("div", class_="info_header")

for head in headers:
    nombre = head.find("a").get("title")
    descripcion = head.span
    df_rest = df_rest.append({'nombre': nombre, 'descripcion': descripcion},
                             ignore_index=True)
df_rest = df_rest[df_rest['descripcion'].notnull()]
df_rest.to_csv('data/restaurantes_located.csv')


