import googlemaps
import pandas as pd

# Set Google MAPS API_Key
g_API = "AIzaSyCZ7uHDJNPNFNpH1-b6rsZUM7h5oQcFV0U"
gmaps_key = googlemaps.Client(key=g_API)

# Get addresses
restaurantes = pd.read_csv('../data/restaurantes_located.csv')

restaurantes["latitud"] = None
restaurantes["longitud"] = None

for i in range(len(restaurantes)):
    address = restaurantes.loc[i, 'nombre'] + ', ' + restaurantes.loc[i, 'Ciudad'] + ', ' \
              + restaurantes.loc[i, 'Departamento'] + ', ' + restaurantes.loc[i, 'Pais']
    geocode_obj = gmaps_key.geocode(address)
    try:
        restaurantes.loc[i, 'latitud'] = geocode_obj[0]['geometry']['location']['lat']
        restaurantes.loc[i, 'longitud'] = geocode_obj[0]['geometry']['location']['lng']
    except:
        restaurantes.loc[i, 'latitud'] = None
        restaurantes.loc[i, 'longitud'] = None

restaurantes.to_csv('restaurantes_located.csv')