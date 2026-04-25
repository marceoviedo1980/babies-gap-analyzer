import pandas as pd

def clasificar_caso(peso, tipo_muerte):
    if peso >= 2500:
        if tipo_muerte == 'Fetal':
            return 'A'
        else:
            return 'B'
    else:
        if tipo_muerte == 'Fetal':
            return 'C'
        else:
            return 'D'

def calcular_tasas(df, total_nacidos):
    if total_nacidos == 0:
        return pd.Series({'A': 0, 'B': 0, 'C': 0, 'D': 0})
    conteo = df['clasificacion'].value_counts()
    tasas = (conteo / total_nacidos) * 1000
    return tasas.reindex(['A', 'B', 'C', 'D'], fill_value=0)

def calcular_brecha(df_analisis, nacidos_analisis, df_estandar, nacidos_estandar):
    tasas_analisis = calcular_tasas(df_analisis, nacidos_analisis)
    tasas_estandar = calcular_tasas(df_estandar, nacidos_estandar)
    
    exceso = tasas_analisis - tasas_estandar
    exceso = exceso.round(2)

    mapeo_nombres = {
        'A': 'Salud Materna',
        'B': 'Cuidado Recien Nacido',
        'C': 'Cuidado durante el Embarazo',
        'D': 'Cuidado durante el Parto'
    }
    exceso.index = exceso.index.map(mapeo_nombres)
    return exceso.sort_values(ascending=False)