import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Dashboard UniFuturo", page_icon="📊", layout="wide")

@st.cache_data
def load_data():
    df_mat = pd.read_parquet("data/matriculados.parquet")
    df_pc = pd.read_parquet("data/primer_curso.parquet")
    df_prog = pd.read_parquet("data/programas.parquet")
    
    df_mat = df_mat[(df_mat['NIVEL ACADÉMICO'] == 'Pregrado') & (df_mat['AÑO'] == 2024) & 
                    (df_mat['DEPARTAMENTO DE OFERTA DEL PROGRAMA'].isin(['Bogotá, D.C.', 'Cundinamarca']))].copy()
    
    df_pc = df_pc[df_pc['Año'] == 2024].copy()
    df_mat_info = df_mat[['CÓDIGO SNIES DEL PROGRAMA', 'PROGRAMA ACADÉMICO', 'MODALIDAD', 
                           'DEPARTAMENTO DE OFERTA DEL PROGRAMA', 'MUNICIPIO DE OFERTA DEL PROGRAMA',
                           'ÁREA DE CONOCIMIENTO', 'INSTITUCIÓN DE EDUCACIÓN SUPERIOR (IES)']].drop_duplicates()
    df_pc = df_pc.merge(df_mat_info, left_on='Código_SNIES_programa', right_on='CÓDIGO SNIES DEL PROGRAMA', how='left')
    df_pc = df_pc[df_pc['DEPARTAMENTO DE OFERTA DEL PROGRAMA'].isin(['Bogotá, D.C.', 'Cundinamarca'])].copy()
    
    df_prog = df_prog[(df_prog['NIVEL_ACADÉMICO'] == 'Pregrado') & (df_prog['ESTADO_PROGRAMA'] == 'Activo') & 
                      (df_prog['DEPARTAMENTO_OFERTA_PROGRAMA'].isin(['Bogotá, D.C.', 'Cundinamarca']))].copy()
    
    return df_mat, df_pc, df_prog

def calculate_kpis(df_mat, df_pc, df_prog):
    matricula_total = df_mat['MATRICULADOS'].sum()
    primer_curso_total = df_pc['Número de matriculados'].sum()
    df_prog['programa_key'] = (df_prog['NOMBRE_INSTITUCIÓN'] + '|' + df_prog['NOMBRE_DEL_PROGRAMA'] + '|' + 
                                df_prog['MUNICIPIO_OFERTA_PROGRAMA'] + '|' + df_prog['MODALIDAD'])
    programas_activos = df_prog['programa_key'].nunique()
    mat_virtual = df_mat[df_mat['MODALIDAD'] == 'Virtual'].groupby('SEMESTRE')['MATRICULADOS'].sum()
    crecimiento_virtual = ((mat_virtual[2] - mat_virtual[1]) / mat_virtual[1] * 100) if len(mat_virtual) == 2 else 0
    pc_virtual = df_pc[df_pc['MODALIDAD'] == 'Virtual']['Número de matriculados'].sum()
    pct_pc_virtual = (pc_virtual / df_pc['Número de matriculados'].sum() * 100)
    prog_virtual = df_prog[df_prog['MODALIDAD'] == 'Virtual']['programa_key'].nunique()
    pct_prog_virtual = (prog_virtual / df_prog['programa_key'].nunique() * 100)
    brecha_virtual = pct_pc_virtual - pct_prog_virtual
    return {'matricula_total': matricula_total, 'primer_curso_total': primer_curso_total, 
            'programas_activos': programas_activos, 'crecimiento_virtual': crecimiento_virtual, 
            'brecha_virtual': brecha_virtual}

st.title("Dashboard Ejecutivo UniFuturo")
st.markdown("### Analisis de Oportunidades de Nuevos Programas de Pregrado")
st.markdown("**Region:** Bogota y Cundinamarca | **Ano:** 2024")

df_mat, df_pc, df_prog = load_data()

st.sidebar.header("Filtros")
modalidad = st.sidebar.selectbox("Modalidad", ['Todas'] + sorted(df_mat['MODALIDAD'].unique().tolist()))
area = st.sidebar.selectbox("Area de Conocimiento", ['Todas'] + sorted(df_mat['ÁREA DE CONOCIMIENTO'].dropna().unique().tolist()))

df_mat_f = df_mat.copy()
df_pc_f = df_pc.copy()
if modalidad != 'Todas':
    df_mat_f = df_mat_f[df_mat_f['MODALIDAD'] == modalidad]
    df_pc_f = df_pc_f[df_pc_f['MODALIDAD'] == modalidad]
if area != 'Todas':
    df_mat_f = df_mat_f[df_mat_f['ÁREA DE CONOCIMIENTO'] == area]
    df_pc_f = df_pc_f[df_pc_f['ÁREA DE CONOCIMIENTO'] == area]

kpis = calculate_kpis(df_mat, df_pc, df_prog)

st.markdown("---")
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Matricula Total", f"{kpis['matricula_total']:,}")
col2.metric("Primer Curso", f"{kpis['primer_curso_total']:,}")
col3.metric("Programas Activos", f"{kpis['programas_activos']:,}")
col4.metric("Crecimiento Virtual", f"{kpis['crecimiento_virtual']:.1f}%")
col5.metric("Brecha Virtual", f"{kpis['brecha_virtual']:.1f} pp")

st.markdown("---")

tab1, tab2, tab3, tab4 = st.tabs(["Modalidades", "Programas", "Competidores", "Proyecciones"])

with tab1:
    col1, col2 = st.columns(2)
    with col1:
        mat_by_mod = df_mat_f.groupby('MODALIDAD')['MATRICULADOS'].sum().reset_index()
        fig1 = px.pie(mat_by_mod, values='MATRICULADOS', names='MODALIDAD', hole=0.4, title='Distribucion de matricula por modalidad')
        st.plotly_chart(fig1, use_container_width=True)
    with col2:
        mat_trend = df_mat_f.groupby(['SEMESTRE', 'MODALIDAD'])['MATRICULADOS'].sum().reset_index()
        mat_trend['SEMESTRE'] = mat_trend['SEMESTRE'].map({1: '2024-I', 2: '2024-II'})
        fig2 = px.line(mat_trend, x='SEMESTRE', y='MATRICULADOS', color='MODALIDAD', markers=True, title='Tendencia de matricula')
        st.plotly_chart(fig2, use_container_width=True)
    
    col3, col4 = st.columns(2)
    with col3:
        pc_by_mod = df_pc_f.groupby('MODALIDAD')['Número de matriculados'].sum().reset_index()
        pc_by_mod['Porcentaje'] = (pc_by_mod['Número de matriculados'] / pc_by_mod['Número de matriculados'].sum() * 100).round(1)
        fig3 = px.bar(pc_by_mod, x='MODALIDAD', y='Número de matriculados', text='Porcentaje', title='Demanda nueva por modalidad')
        fig3.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        st.plotly_chart(fig3, use_container_width=True)
    with col4:
        df_prog['programa_key'] = (df_prog['NOMBRE_INSTITUCIÓN'] + '|' + df_prog['NOMBRE_DEL_PROGRAMA'] + '|' + 
                                  df_prog['MUNICIPIO_OFERTA_PROGRAMA'] + '|' + df_prog['MODALIDAD'])
        prog_by_mod = df_prog.groupby('MODALIDAD')['programa_key'].nunique().reset_index()
        prog_by_mod.columns = ['MODALIDAD', 'Programas']
        demand_supply = pc_by_mod[['MODALIDAD', 'Número de matriculados']].merge(prog_by_mod, on='MODALIDAD', how='outer').fillna(0)
        total_demand = demand_supply['Número de matriculados'].sum()
        total_supply = demand_supply['Programas'].sum()
        demand_supply['Pct_Demanda'] = (demand_supply['Número de matriculados'] / total_demand * 100) if total_demand > 0 else 0
        demand_supply['Pct_Oferta'] = (demand_supply['Programas'] / total_supply * 100) if total_supply > 0 else 0
        demand_supply['Indice_Oportunidad'] = demand_supply['Pct_Demanda'] - demand_supply['Pct_Oferta']
        demand_supply = demand_supply.sort_values('Indice_Oportunidad')
        fig4 = px.bar(demand_supply, y='MODALIDAD', x='Indice_Oportunidad', orientation='h', title='Indice de oportunidad')
        fig4.add_vline(x=0, line_dash='dash', line_color='gray')
        st.plotly_chart(fig4, use_container_width=True)

with tab2:
    col1, col2 = st.columns(2)
    with col1:
        top_prog = df_pc.groupby('PROGRAMA ACADÉMICO')['Número de matriculados'].sum().nlargest(10).reset_index().sort_values('Número de matriculados')
        fig5 = px.bar(top_prog, y='PROGRAMA ACADÉMICO', x='Número de matriculados', orientation='h', title='Top 10 programas')
        st.plotly_chart(fig5, use_container_width=True)
    with col2:
        top_ies = df_mat.groupby('INSTITUCIÓN DE EDUCACIÓN SUPERIOR (IES)')['MATRICULADOS'].sum().nlargest(10).reset_index().sort_values('MATRICULADOS')
        fig6 = px.bar(top_ies, y='INSTITUCIÓN DE EDUCACIÓN SUPERIOR (IES)', x='MATRICULADOS', orientation='h', title='Principales competidores')
        st.plotly_chart(fig6, use_container_width=True)

with tab3:
    st.subheader("Top 5 Competidores Virtuales")
    df_mat_virtual = df_mat[df_mat['MODALIDAD'] == 'Virtual'].copy()
    top5_comp = df_mat_virtual.groupby('INSTITUCIÓN DE EDUCACIÓN SUPERIOR (IES)')['MATRICULADOS'].sum().nlargest(5).reset_index()
    top5_comp.columns = ['Institucion', 'Matricula Virtual']
    st.dataframe(top5_comp, use_container_width=True)
    st.markdown("""
    ### Recomendacion Estrategica: PRIORIZAR OFERTA VIRTUAL
    
    **Razones clave:**
    - Brecha de mercado de **33.4 puntos porcentuales** entre demanda y oferta
    - Crecimiento sostenido del **14.1%** semestral
    - **1,245** estudiantes por programa virtual vs **162** en presencial
    - Mercado presencial saturado (-48.6 pp de indice de oportunidad)
    """)

with tab4:
    st.subheader("Proyecciones de Matricula - Programas Recomendados")
    st.markdown("""
    ### Escenario Moderado (5% de captura de mercado)
    
    **1. Administracion de Empresas**
    - Ano 1: 2,778 estudiantes | Ano 3: 4,126 estudiantes
    
    **2. Ingenieria de Sistemas**
    - Ano 1: 2,678 estudiantes | Ano 3: 3,977 estudiantes
    
    **3. Licenciatura en Pedagogia Infantil**
    - Ano 1: 2,058 estudiantes | Ano 3: 3,056 estudiantes
    
    **Total proyectado:** Ano 1: **7,513** estudiantes | Ano 3: **11,160** estudiantes
    """)
    projection_data = pd.DataFrame({
        'Ano': ['Ano 1', 'Ano 2', 'Ano 3'] * 3,
        'Escenario': ['Conservador']*3 + ['Moderado']*3 + ['Optimista']*3,
        'Estudiantes': [4507, 5868, 6696, 7513, 9781, 11160, 12020, 15649, 17856]
    })
    fig7 = px.line(projection_data, x='Ano', y='Estudiantes', color='Escenario', markers=True, title='Proyeccion de Matricula Total')
    st.plotly_chart(fig7, use_container_width=True)
