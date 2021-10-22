import pandas as pd
from geopy.distance import distance
import requests
import json

class Instance:

    def __init__(self, df_clientes, df_acopios):
        self.df_clientes = df_clientes
        self.df_acopios = df_acopios
        self.CLIENTES = set()
        self.ACOPIOS = set()
        self.distancias = {}
        self.generacion = {}  # cantidad generada en cada cliente
        self.abiertos = {} # 1 indica que el acopio debe estar abierto

    def create_elementos(self):
        # Adiciona consecutivos para nombrar las variables
        self.df_clientes["var_id"] = self.df_clientes.index
        self.df_acopios["var_id"] = self.df_acopios.index
        # Conjunto de estudiantes
        self.CLIENTES = set(self.df_clientes["var_id"].to_list())
        # Conjunto de cursos
        self.ACOPIOS = set(self.df_acopios["var_id"].to_list())

        # Parámetros
        self.generacion = dict(zip(self.df_clientes.var_id, self.df_clientes.generacion))
        self.abiertos = dict(zip(self.df_acopios.var_id, self.df_acopios.abierto))


        # TODO: precalcular
        # calcula distancas
        for i in range(len(self.df_clientes)):
            for j in range(len(self.df_acopios)):
                cliente = (self.df_clientes.loc[i, "latitud"], self.df_clientes.loc[i, "longitud"])
                acopio = (self.df_acopios.loc[j, "latitud"], self.df_acopios.loc[j, "longitud"])
                # d =
                key = (self.df_clientes.loc[i, "var_id"], self.df_acopios.loc[j, "var_id"])
                # Usando OSM
                #d = road_dis_OSM(cliente, acopio)
                # Usando Geopy
                d = distance(cliente, acopio).m
                self.distancias[key] = d

def road_dis_OSM(point1, point2):
    # Nota que deben entrase las coordenadas en el orden longitud latitud
    r = requests.get(
        f"""http://router.project-osrm.org/route/v1/car/{point1[1]},{point1[0]};{point2[1]},{point2[0]}?overview=false""")
    routes = json.loads(r.content)
    route_1 = routes.get("routes")[0]
    distance = route_1["distance"]
    return distance







