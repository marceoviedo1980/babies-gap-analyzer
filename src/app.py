import streamlit as st
import pandas as pd
from supabase import create_client, Client
from babies_calculator import clasificar_caso, calcular_brecha
import plotly.express as px

st.set_page_config(page_title="BABIES Analisis", page_icon="📊", layout="wide")

SUPABASE_URL = "https://ocmjkntwnkyoggjgshah.supabase.co"
SUPABASE_KEY = "sb_publishable_LUI7t1qJUdU86VE_cxYo7w_7xlkCfVi"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@st.cache_data(ttl=5)
def cargar_datos_db():
    response = supabase.table('casos_perinatales').select("*").execute()
    if response.data:
        df = pd.DataFrame(response.data)
        df['clasificacion'] = df.apply(
            lambda row: clasificar_caso(row['peso'], row['tipo_muerte']), axis=1
        )
        return df
    else:
        return pd.DataFrame(columns=['peso', 'tipo_muerte', 'distrito', 'año', 'clasificacion'])

def guardar_caso(peso, tipo_muerte, distrito, año):
    clasificacion = clasificar_caso(peso, tipo_muerte)
    data = {
        'peso': peso,
        'tipo_muerte': tipo_muerte,
        'distrito': distrito,
        'año': año,
        'clasificacion': clasificacion
    }
    supabase.table('casos_perinatales').insert(data).execute()
    st.cache_data.clear()

st.title("📊 Registro y Analisis de Mortalidad Perinatal - Metodo BABIES")
st.caption("Datos guardados de forma segura y permanente en la nube.")

with st.sidebar:
    st.header("📝 Registrar Nuevo Caso")
    with st.form("formulario_caso"):
        peso = st.number_input("Peso al nacer (g)", min_value=0, value=2500, step=100)
        tipo_muerte = st.selectbox("Tipo de muerte", ["Fetal", "Neonatal"])
        distrito = st.text_input("Distrito", value="Independencia")
        año = st.number_input("Año", min_value=2000, max_value=2100, value=2024, step=1)
        submitted = st.form_submit_button("💾 Guardar Caso")
        
        if submitted:
            guardar_caso(peso, tipo_muerte, distrito, año)
            st.success(f"✅ Caso guardado: {peso}g - {tipo_muerte} - {distrito} ({año})")
            st.rerun()

tab_ver, tab_analisis = st.tabs(["📋 Base de Datos", "🎯 Analisis BABIES"])

with tab_ver:
    st.subheader("📂 Casos Registrados en el Sistema")
    df = cargar_datos_db()
    
    if not df.empty:
        st.metric("Total de Casos Registrados", len(df))
        columnas_mostrar = ['peso', 'tipo_muerte', 'distrito', 'año', 'clasificacion', 'fecha_registro']
        if 'fecha_registro' in df.columns:
            df_ordenado = df.sort_values(by='fecha_registro', ascending=False)
        else:
            df_ordenado = df
        st.dataframe(df_ordenado[columnas_mostrar].head(20), use_container_width=True)
        
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="⬇️ Descargar base de datos (CSV)",
            data=csv,
            file_name='casos_perinatales.csv',
            mime='text/csv'
        )
    else:
        st.info("Aun no hay casos registrados. Usa el panel lateral para añadir el primero.")

with tab_analisis:
    st.subheader("🎯 Calcular Brecha de Oportunidad")
    df_analisis = cargar_datos_db()
    
    if df_analisis.empty:
        st.warning("Debes registrar al menos un caso para realizar un analisis.")
        st.stop()
    
    distritos_disponibles = sorted(df_analisis['distrito'].unique())
    
    col_pob1, col_pob2 = st.columns(2)
    with col_pob1:
        pob_analizar = st.selectbox("🔍 Distrito a Analizar:", distritos_disponibles, key='pob_analisis')
    with col_pob2:
        pob_estandar = st.selectbox("✅ Distrito Estandar (Referencia):", distritos_disponibles, key='pob_estandar')
    
    col_nac1, col_nac2 = st.columns(2)
    with col_nac1:
        nacidos_analisis = st.number_input(f"Nacidos vivos totales en **{pob_analizar}**", 
                                           min_value=1, value=1000, step=10, key='nac_analisis')
    with col_nac2:
        nacidos_estandar = st.number_input(f"Nacidos vivos totales en **{pob_estandar}**", 
                                           min_value=1, value=1000, step=10, key='nac_estandar')

    if st.button("🚀 **CALCULAR BRECHA DE OPORTUNIDAD**", type="primary", use_container_width=True):
        df_filtrado_analizar = df_analisis[df_analisis['distrito'] == pob_analizar].copy()
        df_filtrado_estandar = df_analisis[df_analisis['distrito'] == pob_estandar].copy()
        
        brecha = calcular_brecha(df_filtrado_analizar, nacidos_analisis, 
                                 df_filtrado_estandar, nacidos_estandar)
        
        st.success("✅ **Calculo completado**")
        
        col_brecha, col_grafico = st.columns([1, 2])
        
        with col_brecha:
            st.subheader("📈 Exceso de Tasa (por 1000 n.v.)")
            st.dataframe(brecha.rename("Exceso").to_frame().style.highlight_max(color='lightcoral'))
            area_prioritaria = brecha.idxmax()
            st.markdown(f"### 🔥 Area prioritaria de intervencion:")
            st.markdown(f"## **{area_prioritaria}**")
        
        with col_grafico:
            st.subheader("📊 Visualizacion de la Brecha")
            fig = px.bar(brecha, x=brecha.index, y=brecha.values, 
                         title=f"Brecha de Oportunidad: {pob_analizar} vs {pob_estandar}",
                         labels={'x': 'Area BABIES', 'y': 'Exceso de Tasa (x 1000 n.v.)'},
                         color=brecha.values, color_continuous_scale='Reds')
            st.plotly_chart(fig, use_container_width=True)