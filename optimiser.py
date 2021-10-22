import pandas as pd
from pyomo.environ import *
from pyomo.opt import *

def create_model(instance,
                 n_acopios=2,  # número de acopios
                 d_max=1000):  # distancia máxima de cobertura

    # Define el modelo
    # Crea el modelo
    model = ConcreteModel(name="cubrimiento")

    # Crea conjuntos
    model.CLIENTES = Set(initialize=instance.CLIENTES, ordered=False)
    model.ACOPIOS = Set(initialize=instance.ACOPIOS, ordered=False)

    # Crea Parámetros
    model.generacion = Param(model.CLIENTES, initialize=instance.generacion)
    model.distancias = Param(model.CLIENTES, model.ACOPIOS, initialize=instance.distancias)
    model.nacopios = Param(initialize=n_acopios)
    model.dmax = Param(initialize=d_max)
    model.abiertos = Param(model.ACOPIOS, initialize=instance.abiertos)

    # Define variables
    model.x = Var(model.CLIENTES, model.ACOPIOS, within=Binary)  # Asignacion
    model.y = Var(model.ACOPIOS,  within=Binary)  # Apertura
    model.w = Var(model.CLIENTES, within=Binary)  # Cobertura

    # Define función objetivo
    def coverage(model):
        return sum(model.w[i]*model.generacion[i] for i in model.CLIENTES) + \
               0.00001*sum(sum(model.x[i,j] for i in model.CLIENTES ) for j in model.ACOPIOS)
    model.coverage = Objective(sense=maximize, rule=coverage)

    # Define restricciones
    # 1. Restricción número de acopios
    def nacopios_rule(model):
        return sum(model.y[j] for j in model.ACOPIOS) == model.nacopios
    model.num_acopios = Constraint(model.ACOPIOS, rule=nacopios_rule)

    # 2. asignación a acopios abiertos
    def consistencia_rule(model, j):
        return sum(model.x[i, j] for i in model.CLIENTES) <= len(model.CLIENTES) * model.y[j]
    model.consistencia = Constraint(model.ACOPIOS, rule=consistencia_rule)

    # 3. Distancia máxima
    def distmax_rule(model, i, j):
        return model.distancias[i, j]*model.x[i, j] <= model.dmax
    model.distmax_rule = Constraint(model.CLIENTES, model.ACOPIOS, rule=distmax_rule)

    # 3. Única cobertura
    def wi_min(model, i):
        return model.w[i]*len(model.ACOPIOS) >= sum(model.x[i, j] for j in model.ACOPIOS)
    model.wi_min = Constraint(model.CLIENTES, rule=wi_min)

    def wi_max(model, i):
        return model.w[i] <= sum(model.x[i, j] for j in model.ACOPIOS)
    model.wi_max = Constraint(model.CLIENTES, rule=wi_max)

    # 4. Acopios de apertura obligatoria
    def obligatorios(model, j):
        if model.abiertos[j] == 1:
            return model.y[j] == 1
        else:
            return Constraint.Skip
    model.obligatorio = Constraint(model.ACOPIOS, rule=obligatorios)

    return model


def solve_model(instance, model, solver_name, solver_path=None):
    if solver_path == None:
        solver = SolverFactory(solver_name)
    else:
        solver = SolverFactory(solver_name, executable=solver_path)
    # set time limit
    solver.options['tmlim'] = 5
    # Resuelve el modelo
    solver.solve(model, options_string="mipgap=0.02")
    # solve the model
    results = solver.solve(model)
    term_cond = results.solver.termination_condition
    if term_cond == TerminationCondition.feasible or term_cond == TerminationCondition.optimal:
        # Obtener función objetivo
        obj_val = model.coverage.expr()
        # dataframe solucion clientes
        df_solclientes = instance.df_clientes
        df_solclientes["cobertura"] = 0
        df_solclientes["list_cob"] = [[] for _ in range(df_solclientes.shape[0])]
        df_solclientes["dist_min"] = -1
        df_solacopios = instance.df_acopios
        df_solacopios["assign"] = 0
        df_solacopios["list_clientes"] = [[] for _ in range(df_solacopios.shape[0])]
        # Obtener coberturas y acopios abiertos
        res = model.x.get_values()
        for key, value in res.items():
            if value > 0:
                df_solclientes.loc[key[0], 'cobertura'] = 1
                df_solacopios.loc[key[1], "assign"] = 1
                df_solclientes.loc[key[0], 'list_cob'].append(key[1])
                df_solacopios.loc[key[1], "list_clientes"].append(key[0])
        # obtener abiertos
        res = model.y.get_values()
        for key, value in res.items():
            if value > 0:
                df_solacopios.loc[key, "assign"] = 1
        # Obtener distancias mínimas
        res = model.y.get_values()
        abiertos = [key for key in res.keys() if res[key] > 0]
        for i in range(len(df_solclientes)):
            dist_min = float('inf')
            for j in abiertos:
                if instance.distancias[(i, j)] <= dist_min:
                    dist_min = instance.distancias[(i, j)]
            df_solclientes.loc[i, "dist_min"]=dist_min
        return df_solclientes, df_solacopios, term_cond

    else:
        return None, None, term_cond



