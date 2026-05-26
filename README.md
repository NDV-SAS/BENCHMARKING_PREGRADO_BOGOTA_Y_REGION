# Dashboard UniFuturo - Analisis de Oportunidades

Dashboard ejecutivo para analizar oportunidades de nuevos programas de pregrado en Bogota y Cundinamarca.

## Deployment en Streamlit Cloud

### Opcion 1: Streamlit Cloud (Recomendado)

1. Sube este repositorio a GitHub
2. Ve a https://share.streamlit.io
3. Conecta tu cuenta de GitHub
4. Selecciona este repositorio
5. Especifica `app.py` como el archivo principal
6. Click en "Deploy"

### Opcion 2: Local

```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar la aplicacion
streamlit run app.py
```

## Caracteristicas

- **5 KPIs principales**: Matricula total, primer curso, programas activos, crecimiento virtual, brecha virtual
- **Analisis de modalidades**: Distribucion, tendencias, demanda vs oferta
- **Programas y competidores**: Top 10 programas, principales competidores
- **Analisis competitivo**: Posicionamiento de top 5 competidores virtuales
- **Proyecciones**: Estimaciones de matricula para 3 programas recomendados

## Estructura del Proyecto

```
.
├── app.py                  # Aplicacion principal de Streamlit
├── requirements.txt        # Dependencias de Python
├── README.md              # Este archivo
├── .gitignore             # Archivos a ignorar en Git
└── data/                  # Datos (archivos .parquet)
    ├── matriculados.parquet
    ├── primer_curso.parquet
    └── programas.parquet
```

## Datos

Los datos incluyen:
- **matriculados.parquet**: 1,656,729 estudiantes matriculados en pregrado 2024
- **primer_curso.parquet**: 1,239,357 estudiantes de primer curso 2024
- **programas.parquet**: 2,584 programas activos de pregrado

**Region**: Bogota y Cundinamarca  
**Ano**: 2024  
**Nivel**: Pregrado

## Hallazgos Clave

- **Brecha virtual**: 33.4 puntos porcentuales entre demanda (54.3%) y oferta (20.9%)
- **Crecimiento virtual**: 14.1% semestral
- **Programas recomendados**: Administracion de Empresas, Ingenieria de Sistemas, Licenciatura en Pedagogia Infantil
- **Proyeccion moderada**: 7,513 estudiantes en Ano 1 -> 11,160 en Ano 3

## Licencia

Este proyecto es de uso educativo y analitico.
