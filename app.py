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

# Leer datos
df_clientes= pd.read_csv(r'https://raw.githubusercontent.com/endorgobio/federika/master/data/clientes.csv')
df_acopios = pd.read_csv(r'https://raw.githubusercontent.com/endorgobio/federika/master/data/acopios.csv')
df_indicadores = pd.DataFrame(columns=['indicador', 'valor'])
# Crea la instancia
instance = Instance(df_clientes, df_acopios)
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
                title="Zonificación",
                suppress_callback_exceptions=True)

# Para correr en heroku
server = app.server

# Narrativas
filepath = os.path.split(os.path.realpath(__file__))[0]
# narrative tab1
#historia_text = open(os.path.join(filepath, "laHistoria.md"), "r").read()
historia_text= " "
# narrative tab3
#detalles_text = open(os.path.join(filepath, "losDetalles.md"), "r").read()
detalles_text = " "

controls_card = dbc.Card(
                    dbc.CardBody(dbc.Row([
                        dbc.Col([
                                dbc.FormGroup([
                                        html.P("Número de acopios"),
                                        dbc.Input(id="n_acopios", type="number", min=1, max=len(instance.df_acopios),
                                                  step=1, value=3),
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
        dbc.Col(dcc.Markdown(historia_text, dangerously_allow_html=True), md=8),
        dbc.Col(html.Div([
            #html.Img(src="/assets/images/banner_blue_text.png", className='banner_subsection'),
            html.Div(
                html.P("Los retos", className="subheader-description"),
                #className="header_subsection1"
            ),
            dbc.Card([
                dbc.CardBody([
                    html.P(
                        "Visualizar la asignación de pacientes por zona en un mapa",
                        style={'textAlign': 'justify'},
                        className="card-text",
                    ),
                ])
            ]),
            dbc.Card([
                dbc.CardBody([
                    html.P(
                        "Crear un modelo que asigne zonas a los terapeutas balanceando las"
                        "cargas de trabajo",
                        style={'textAlign': 'justify'},
                        className="card-text",
                    ),
                ])
            ]),
            dbc.Card([
                dbc.CardBody([
                    html.P(
                        "Resolver el modelo con un optimizador no comercial",
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
            html.P("Detras de la zonificación de los pacientes para ser asignados al personal"
                   "asistencial hay un modelo  matemático que genera información que ayuda a "
                   "tomar dicha decisión. Este es el modelo:"),
            dbc.Card([
                # dbc.CardImg(src="https://source.unsplash.com/daily", top=True),
                # dbc.CardImg(src="/assets/images/banner_blue.png", top=True),
                dbc.CardBody([
                    dcc.Markdown('''
                        Sea `P` el conjunto de pacientes, cada uno de ellos con una demanda estimada de
                         tiempo de servicio `t`. Considere la distancia `d` entre cada par de pacientes y `k` 
                         como el número de zonas que deben crearse. La carga de trabajo estimada para cada zona
                         puede calcularse como la suma total de las cargas `t` sobre el número de zonas `k`. Considere
                         ademas &epsilon; como el porcentaje máximo tolerable de diferencia entre la carga de trabajo de
                         una zona y la carga promedio esperada.  
                        Asumiremos que cada una de las zonas se crea entorno a uno de los pacientes. Para ello, 
                        considere la variable `y` que indica si un paciente dado es el centro de una de las `k`
                        zonas; la variable `x` determina a cual de las zonas creadas es asignado cada paciente
                    '''),
                    dcc.Markdown(''' La función busca crear zonas compactas minimizando la suma de  la distancia  de los 
                    pacientes al centro de sus zonas. '''),

                    dcc.Markdown(''' Garantizando que: '''),
                    dcc.Markdown(''' Cada paciente es asignado a una zona. '''),


                    dcc.Markdown(''' Se crean tantas zonas cómo indica el parámetro `k` '''),

                    dcc.Markdown(''' Se identifica la localización de un paciente como el centro de cada zona y los pacientes 
                        se asignan solo a dichas zonas'''),

                    dcc.Markdown(''' La carga de trabajo de cada zona solo puede desviarse un &epsilon; % del valor promedio
                    de la carga '''),
                ])
            ]),
        ]),
        md=8),
    dbc.Col(
        [
            dbc.Card(
                dbc.CardBody([
                    html.P("El modelo se implementó en python, haciendo uso de la libreria "
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
    'color': '#FD6E72',
    'fontWeight': 'bold'
}


# Define the layout
app.layout = dbc.Container([
        #navbar,
        dbc.Row(html.Img(src='assets/images/imagenBanner_Zonificacion1.jpg', style={'width':'100%'})),
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
        dbc.Row(html.Img(src='assets/images/pie-endorgobio.jpg', style={'width':'100%'})),
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