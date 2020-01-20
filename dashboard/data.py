import numpy as np
import pandas as pd

df_total = None
conteos_mensuales = None
conteos_activos = None
meses = None
origenes = None

def create_basic_data():
    global meses
    global origenes

    meses = ["Ene 17", "Feb 17", "Mar 17", "Abr 17",
            "May 17", "Jun 17", "Jul 17", "Ago 17",
            "Sep 17", "Oct 17", "Nov 17", "Dic 17",
            "Ene 18"]

    origenes = ["Internet", "Teléfono", "Oficina", "Otros"]

def create_random_dataset():
    global df_total

    np.random.seed(42)

    df_total = pd.DataFrame(columns=["saldo", "mes", "activo", "origen"])

    for i, j in enumerate(meses):
        n_filas = np.random.randint(2_000, 5_000)
        probabilidad_finalizado = np.random.uniform(0,1)
        dict_columnas = dict()
        dict_columnas["saldo"] = np.random.normal(np.random.randint(500, 3000), 
                                                np.random.randint(200, 1000),
                                                n_filas)
        dict_columnas["mes"] = [j] * n_filas
        dict_columnas["activo"] = np.random.choice([0,1], 
                                                size=n_filas, 
                                                p=[1-probabilidad_finalizado, probabilidad_finalizado])
        
        dist_proba_origen = np.random.uniform(0, 10, len(origenes))
        dict_columnas["origen"] = np.random.choice(origenes,
                                                size=n_filas,
                                                p=dist_proba_origen/dist_proba_origen.sum())
        df_total = pd.concat([df_total, pd.DataFrame(dict_columnas)])
        
        
    df_total["saldo"] = df_total["saldo"].apply(lambda x: 0 if x < 0 else x)

def create_conteos_mensuales():
    global conteos_mensuales

    conteos_mensuales = df_total.groupby("mes").size().loc[meses].reset_index()
    conteos_mensuales.columns=["mes", "nuevos"]

def create_conteos_activos():
    global conteos_activos

    conteos_activos = df_total.groupby("mes")[["activo"]].sum().loc[meses].reset_index()
    conteos_activos.columns=["mes", "activos"]
