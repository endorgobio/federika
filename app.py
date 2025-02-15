import pandas as pd
import optimiser as opt
from utilities import Instance
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_table
from dash import no_update
from dash.dependencies import Input, Output, State
import plotly.express as px
from plotly import graph_objs as go
import os
import json

# Leer datos de github
#df_clientes= pd.read_csv(r'https://raw.githubusercontent.com/endorgobio/federika/master/data/clientes.csv')
#df_acopios = pd.read_csv(r'https://raw.githubusercontent.com/endorgobio/federika/master/data/acopios.csv')

# Leer datos drive endorgobio
import pandas as pd
book_id = '1X_3s7widO60dPf4js8e9bRLL_xX8Qnq9OIAWQJgmXI4'
sheet_restaurantes = 'restaurantes'
sheet_acopios = 'contenedores'
url_rest = f"https://docs.google.com/spreadsheets/d/{book_id}/gviz/tq?tqx=out:csv&sheet={sheet_restaurantes}"
url_acopios = f"https://docs.google.com/spreadsheets/d/{book_id}/gviz/tq?tqx=out:csv&sheet={sheet_acopios}"
df_clientes= pd.read_csv(url_rest)
df_acopios = pd.read_csv(url_acopios)

df_indicadores = pd.DataFrame(columns=['indicador', 'valor'])
# Crea la instancia
instance = Instance(df_clientes, df_acopios)
min_acopios = max(1, df_acopios['abierto'].sum())
# Preprocesa dataframe
instance.create_elementos()

# Configura optimiser
solvername = 'glpk'
solverpath_exe = 'C:\\glpk-4.65\\w64\\glpsol'
solverpath_exe = 'D:\\glpk-4.65\\w64\\glpsol'

# Define the stylesheets
external_stylesheets = [dbc.themes.BOOTSTRAP,
    #'https://codepen.io/chriddyp/pen/bWLwgP.css'
    'https://fonts.googleapis.com/css2?family=Lato:wght@400;700&display=swap',
    #'https://fonts.googleapis.com/css2?family=Roboto&display=swap" rel="stylesheet'
]

# Crea la app
app = dash.Dash(__name__, external_stylesheets=external_stylesheets,
                external_scripts=['//cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.4/MathJax.js?config=TeX-MML-AM_CHTML',],
                title="Federica Cork",
                suppress_callback_exceptions=True)

# Para correr en heroku
server = app.server

# Narrativas
filepath = os.path.split(os.path.realpath(__file__))[0]
# narrative tab1
#historia_text = open(os.path.join(filepath, "laHistoria.md"), "r").read()
historia_text = html.Div([
    html.P('''Federica Cork es una start-up colombiana que, siguiendo los principios de la 
    economía circular, diseña y produce artículos innovadores usando el corcho recuperado 
    de las botellas de vino'''),
    html.P('''El corcho es un material extraordinario, por lo que usarlo una sola vez y desecharlo 
    al descorchar las botellas es un desperdicio absurdo. Sin embargo, la tarea de recolectarlo no es simple, 
    puesto que la demanda de vino, y por ende la generación de corchos para disponer, esta dispersa en bares,
    restaurantes y cafes.  Ante la imposibilidad de una recolección punto por punto, Federica Cork debe 
    establecer una red de contenedores para que sus establecimientos aliados dispongan allí periódicamente 
    los corchos de las botellas que consumen. 
    '''),
    html.P('''Federica Cork se postuló a proyecto endorgobio con el fin de disponer de una herramienta que 
    le provea información para diseñar la red de contenedores, identificando cuantos y dónde debería localizar 
    para poder ofrecer a sus aliados una propuesta de servicio respecto a la cercanía del sitio donde disponer 
    los corchos de las botellas consumida.. 
    ''')
])

# narrative tab3
#detalles_text = open(os.path.join(filepath, "losDetalles.md"), "r").read()
detalles_text = " "
# narrative tab3
# modelo
f = open('modelo.json', )
# returns JSON object as
# a dictionary
data = json.load(f)

controls_card = dbc.Card(
                    dbc.CardBody(dbc.Row([
                        dbc.Col([
                                dbc.FormGroup([
                                        html.P("Número de acopios"),
                                        dbc.Input(id="n_acopios", type="number", min=min_acopios, max=len(instance.df_acopios),
                                                  step=1, value=int(len(instance.df_acopios)/3)),
                                ]),
                                ],
                            md=4
                        ),
                        dbc.Col(
                            dbc.FormGroup([
                                        html.P("distancia máxima (km)"),
                                        dbc.InputGroup(
                                            [
                                                dbc.Input(id="dmax", type="number", min=0, max=1000, step=0.1, value=1.5,
                                                          placeholder="balance"),
                                                #dbc.InputGroupAddon("%", addon_type="append"),
                                            ],
                                            className="mb-3",
                                        ),
                            ]),
                            md=4
                        ),
                        dbc.Col([
                            dbc.FormGroup(dbc.Button("Resolver", id="resolver", className="mr-2", n_clicks=0)),
                            ],
                            align="end",
                            md=4
                        )
                    ]),)
                )

tab1_content = dbc.Row([
        dbc.Col(historia_text, md=8),
        dbc.Col(html.Div([
            #html.Img(src="/assets/images/banner_blue_text.png", className='banner_subsection'),
            html.Div(
                html.P("Los retos", className="subheader-description"),
                #className="header_subsection1"
            ),
            dbc.Card([
                dbc.CardBody([
                    html.P(
                        "Geolocalizar los estableciemientos aliados y ubicaciones potenciales "
                        "de los contenedores",
                        style={'textAlign': 'justify'},
                        className="card-text",
                    ),
                ])
            ]),
            dbc.Card([
                dbc.CardBody([
                    html.P(
                        "Diseñar una herramienta que permita experimentar con distintas configuraciones "
                        "de la red y niveles de la promesa de servicio",
                        style={'textAlign': 'justify'},
                        className="card-text",
                    ),
                ])
            ]),
            dbc.Card([
                dbc.CardBody([
                    html.P(
                        "Generar indicadores que midan la conveniencia de la configuración "
                        "de la red ",
                        style={'textAlign': 'justify'},
                        className="card-text",
                    ),
                ])
            ]),
        ]),
            md=4),
    ]
)

tab2_content = dbc.Row([
    dbc.Container(controls_card, fluid=True),
    dbc.Container(dbc.Col(dcc.Graph(id="map"), width=12),
                  fluid=True),
    dbc.Container(
        dbc.Row([
            dbc.Col(
                dbc.Card(
                    dbc.CardBody(
                        [  # table of students
                            dash_table.DataTable(
                                id='datatable_indicadores',
                                columns=[
                                    {"name": i, "id": i} for i in ['indicador', 'valor']
                                ],
                                style_table={'overflowX': 'auto'},
                                css=[{'selector': 'table', 'rule': 'table-layout: fixed'}],
                                style_cell={
                                    'textAlign': 'left',
                                    'width': '{}%'.format(len(df_indicadores.columns)),
                                    'textOverflow': 'ellipsis',
                                    'overflow': 'hidden'
                                },
                                style_as_list_view=True,
                            ),
                        ]
                    )
                ),
            md=12
            ),
        ]),
        fluid=True
    )
])

tab3_content = dbc.Row([
    dbc.Col(
        html.Div(id='static', children=[
            html.P("La información que apoya la decisión respecto a la localización de los contenedores para recolectar "
                   "los tapones de corcho esta apoyada por el siguiente modelo matemático:"),
            dbc.Card([
                # dbc.CardImg(src="https://source.unsplash.com/daily", top=True),
                # dbc.CardImg(src="/assets/images/banner_blue.png", top=True),
                dbc.CardBody([
                    dcc.Markdown('''
                        Sea `E` el conjunto de establecimientos, cada uno de ellos con un nivel de generación `g` que
                        determina su importancia. Sea `C` el conjunto de localizaciones potenciales para los contenedores,
                        siendo  `k` el número máximo de contenedores que pueden ubicarse (por ejemplo, por restricciones
                        presupuestales). Sea `d` la distancia entre cada establecimiento y cada ubicación potencial de los
                        contenedores y `dmax` el valor máximo tolerable para dicha distancia.

                        Considere la variable `y` que indica si se situa un contenedor en una determinada localización
                        potencial;   la variable `x` que indica si un establecieminto esta cubierto por un determinado
                        contenedor, es decir, si la distancia entre el estableciemiento y el contenedor es menor a la
                        distancia máxima tolerable; y sea `w` una variable auxiliar que indica si el estableciemiento es
                        cubierto o no, sin eimportar cuantos contenedores lo cubren y evitando asi contar múltiples veces
                        las coberturas.
                    '''),
                    dcc.Markdown(''' La función objetivo maximiza la cobertura total del sistema, '''),
                    data['objetivo'],
                    dcc.Markdown(''' Garantizando el límite máximo de contenedores localizados, '''),
                    data['restriccion1'],
                    dcc.Markdown(''' La asignación solo puede hacerse sobre aquellas localizaciones donde se ubica un
                    contenedor'''),
                    data['restriccion2'],
                    dcc.Markdown(''' Se considera que un contenedor cubre un establecimiento si la distancia entre ellos
                    es menor que el máximo permitido'''),
                    data['restriccion3'],

                    dcc.Markdown(''' Por último se garantiza que solo se contabiliza una vez cada establecimiento
                    cubiert'''),
                    data['restriccion4'],
                    data['restriccion5'],
                ])
            ]),
        ]),
        md=8),
    dbc.Col(
        [
            dbc.Card(
                dbc.CardBody([
                    html.P("Los establecimientos y localizaciones se geoposicionaron usando la API de google Maps")
                ])
            ),
            dbc.Card(
                dbc.CardBody([
                    html.P("Los datos son accesibles y modificables a través de google drive")
                ])
            ),
            dbc.Card(
                dbc.CardBody([
                    html.P("El modelo se implementó en python, haciendo uso de la libreria"
                           "para modelación Pyomo")
                ])
            ),
            dbc.Card(
                dbc.CardBody([
                    html.P("El solver empleado para resolver el modelo fue glpk, cuyo uso  para "
                           "fines no comerciales esta regulado the por el acuerdo 'GNU General Public License'")
                ])
            ),
            dbc.Card(
                dbc.CardBody([
                    html.P("La visualización de los resultados del modelo se implemento haciendo uso del framework "
                           "dash soportado plotly para las gráficas y visualizaciones'")
                ])
            )
        ],
        md=4
    ),
]
)

tabs_styles = {
    'height': '44px',
    'align-items': 'center'
}

tab_label_style = {
    'color' : 'black'
}

activetab_label_style = {
    'color': '#0d594c',
    'fontWeight': 'bold'
}


# Define the layout
app.layout = dbc.Container([
        #navbar,
        dbc.Row(html.Img(src='assets/images/federica_header.png', style={'width':'100%'})),
        dbc.Tabs(
            children=[
                dbc.Tab(label="La historia", tab_id="historia", label_style=tab_label_style, active_label_style=activetab_label_style),
                dbc.Tab(label="La solución", tab_id="solucion", label_style=tab_label_style, active_label_style=activetab_label_style),
                dbc.Tab(label="Los detalles", tab_id="detalles",  label_style=tab_label_style, active_label_style=activetab_label_style),
            ],
            id="tabs",
            active_tab="historia",
            style=tabs_styles
        ),
        # Loading allows the spinner showing something is running
        dcc.Loading(
            id="loading",
            # dcc.Store inside the app that stores the intermediate value
            children=[dcc.Store(id='data_solver_clientes'),
                      dcc.Store(id='data_solver_acopios')]
        ),
        dbc.Container(id="tab-content", className="p-4", fluid=True),
        dbc.Row(html.Img(src='assets/images/footnote_federica.png', style={'width':'100%'})),
    ],
    fluid=True,
)


# Render the tabs depending on the selection
@app.callback(
    Output("tab-content", "children"),
    Input("tabs", "active_tab"),
)
def render_tab_content(active_tab):
    """
    This callback takes the 'active_tab' property as input, as well as the
    stored graphs, and renders the tab content depending on what the value of
    'active_tab' is.
    """
    if active_tab == "historia":
        return tab1_content
    elif active_tab == "solucion":
        return tab2_content
    elif active_tab == "detalles":
        return tab3_content

# Actualiza tabla de indicadores
@app.callback(
    Output('datatable_indicadores', 'data'),
    Input('data_solver_clientes', 'data'),
    Input('data_solver_acopios', 'data'))
def update_table_indicators(data_solver_clientes, data_solver_acopios):
    df_solclientes = pd.read_json(data_solver_clientes, orient='split')
    df_solacopios = pd.read_json(data_solver_acopios, orient='split')
    df_ind = pd.DataFrame(columns=['indicador', 'valor'])
    # clientes cubiertos con dmax
    new_row = {'indicador': 'número clientes cubiertos',
               'valor':  df_solclientes['cobertura'].sum()}
    df_ind = df_ind.append(new_row, ignore_index=True)
    # % clientes cubiertos con dmax
    txt = "{valor:.1f}%"
    perc = 100*df_solclientes["cobertura"].sum()/len(df_solclientes)
    new_row = {'indicador': 'porcentaje clientes cubiertos',
               'valor': txt.format(valor=perc)}
    df_ind = df_ind.append(new_row, ignore_index=True)
    # Distancia a acopio
    txt = "{valor:.1f} km"
    valor = df_solclientes['dist_min'].mean()/1000
    new_row = {'indicador': 'distancia promedio a acopio',
               'valor': txt.format(valor=valor)}
    df_ind = df_ind.append(new_row, ignore_index=True)


    return df_ind.to_dict('records')


@app.callback(Output('data_solver_clientes', 'data'),
              Output('data_solver_acopios', 'data'),
              Input('resolver', 'n_clicks'),
              State('n_acopios', 'value'),
              State('dmax', 'value')
              )
def solve_model(clic_resolver, n_acopios, dmax):
    # create model
    model = opt.create_model(instance, n_acopios, dmax*1000)
    #df_solclientes, df_solacopios, opt_term_cond = opt.solve_model(instance, model, solvername, solverpath_exe)
    df_solclientes, df_solacopios, opt_term_cond = opt.solve_model(instance, model, solvername)
    if opt_term_cond == 'infeasible':
        return no_update, no_update
    else:
        data_clientes= df_solclientes.to_json(date_format='iso', orient='split')
        data_acopios = df_solacopios.to_json(date_format='iso', orient='split')
        return data_clientes, data_acopios

# Update map
@app.callback(Output('map', 'figure'),
              Input('data_solver_clientes', 'data'),
              Input('data_solver_acopios', 'data')
              )
def update_graph(jsonified_solclientes, jsonified_solacopios, ):
    df_solclientes = pd.read_json(jsonified_solclientes, orient='split')
    df_solacopios= pd.read_json(jsonified_solacopios, orient='split')

    # Crea mapa
    map = go.Figure()
    # adiciona trace para clientes cubiertos
    df_solclientes_cub = df_solclientes[df_solclientes['cobertura'] == 1]
    map.add_trace(go.Scattermapbox(
        lat=df_solclientes_cub.latitud,
        lon=df_solclientes_cub.longitud,
        mode='markers',
        marker=go.scattermapbox.Marker(
            size=10,
            color='green',
            opacity=0.7
        ),
        text=df_solclientes_cub.cliente,
        hoverinfo='text',
        name="cubiertos"
    ))

    # adiciona trace para clientes no cubiertos
    df_solclientes_nocub = df_solclientes[df_solclientes['cobertura'] == 0]
    map.add_trace(go.Scattermapbox(
        lat=df_solclientes_nocub.latitud,
        lon=df_solclientes_nocub.longitud,
        mode='markers',
        marker=go.scattermapbox.Marker(
            size=10,
            color='red',
            opacity=0.3
        ),
        text=df_solclientes_nocub.cliente,
        hoverinfo='text',
        name="no cubiertos"
    ))

    # adiciona trace para acopios abiertos
    df_solacopios_si = df_solacopios[df_solacopios['assign'] == 1]
    map.add_trace(go.Scattermapbox(
        lat=df_solacopios_si.latitud,
        lon=df_solacopios_si.longitud,
        mode='markers',
        marker=go.scattermapbox.Marker(
            size=12,
            color='black',
            opacity=0.9
        ),
        text=df_solacopios_si.acopio,
        hoverinfo='text',
        name="contenedores"
    ))

    # adiciona trace para acopios no cubiertos
    df_solacopios_no = df_solacopios[df_solacopios['assign'] == 0]
    map.add_trace(go.Scattermapbox(
        lat=df_solacopios_no.latitud,
        lon=df_solacopios_no.longitud,
        mode='markers',
        marker=go.scattermapbox.Marker(
            size=12,
            color='black',
            opacity=0.2
        ),
        text=df_solacopios_no.acopio,
        hoverinfo='text',
        name="potenciales"
    ))

    map.update_layout(
        mapbox_style="open-street-map",
        autosize=True,
        hovermode='closest',
        showlegend=True,
        height=600
    )
    map.update_mapboxes(
        center=go.layout.mapbox.Center(
            lat=df_solclientes.loc[0, 'latitud'],
            lon=df_solclientes.loc[0, 'longitud'],
        ),
        zoom=12
    )

    return map

# add callback for toggling the collapse on small screens
@app.callback(
    Output("navbar-collapse", "is_open"),
    [Input("navbar-toggler", "n_clicks")],
    [State("navbar-collapse", "is_open")],
)
def toggle_navbar_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

# main to run the app
if __name__ == "__main__":
    app.run_server(debug=True)