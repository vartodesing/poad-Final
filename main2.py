import os
import base64
import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output

external_stylesheets = [
    'https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=Inter:wght@300;400;500;600;700&display=swap'
]
app = Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "Dashboard Aprender 2024 — Desempeño en Matemática"

file_path = os.path.join("data", "aprender2024_matematica.csv")
df = pd.read_csv(file_path)

df_ok = df[df['nivel_desempeno'].isin(['Satisfactorio', 'Avanzado'])].copy()

def get_base64_image(image_filename):
    image_path = os.path.join("graficos", image_filename)
    if os.path.exists(image_path):
        with open(image_path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode("utf-8")
        return f"data:image/png;base64,{encoded}"
    return ""

national_avg = df_ok.groupby(['jurisdiccion', 'tipo_gestion', 'ambito'])['porcentaje'].sum().mean()

mendoza_avg = df_ok[df_ok['jurisdiccion'] == 'Mendoza'].groupby(['tipo_gestion', 'ambito'])['porcentaje'].sum().mean()

prov_series = df_ok.groupby(['jurisdiccion', 'tipo_gestion', 'ambito'])['porcentaje'].sum().groupby('jurisdiccion').mean()
best_prov_name = prov_series.idxmax()
best_prov_pct = prov_series.max()

opciones_gestion = [{'label': 'Todos', 'value': 'Todos'}] + [
    {'label': g, 'value': g} for g in sorted(df['tipo_gestion'].unique())
]

def crear_tarjeta_kpi(titulo, valor, descripcion, color_valor):
    return html.Div(
        className="kpi-card",
        children=[
            html.P(titulo, className="kpi-title"),
            html.H2(valor, className="kpi-value", style={'color': color_valor}),
            html.P(descripcion, className="kpi-desc")
        ]
    )

app.layout = html.Div(
    style={
        'backgroundColor': '#0f172a',
        'color': '#f8fafc',
        'fontFamily': '"Inter", sans-serif',
        'minHeight': '100vh',
        'padding': '30px 40px',
        'margin': '0'
    },
    children=[
        html.Header(
            className="dashboard-header",
            children=[
                html.Div(children=[
                    html.H1(
                        "Desempeño en Matemática — Operativo Aprender 2024",
                        style={
                            'fontFamily': '"Outfit", sans-serif',
                            'fontSize': '28px',
                            'fontWeight': '700',
                            'margin': '0 0 5px 0',
                            'background': 'linear-gradient(to right, #06b6d4, #10b981)',
                            '-webkit-background-clip': 'text',
                            '-webkit-text-fill-color': 'transparent'
                        }
                    ),
                    html.P(
                        "Instituto Superior Manuel Belgrano | Tecnicatura en Ciencia de Datos e IA",
                        style={'fontSize': '14px', 'color': '#94a3b8', 'margin': '0'}
                    )
                ]),
                html.Div(
                    className="materia-badge",
                    children=[
                        html.Span("Materia: ", style={'fontWeight': 'bold', 'color': '#06b6d4'}),
                        "Programación Orientada al Análisis de Datos"
                    ]
                )
            ]
        ),
        
        html.Main(
            children=[
                html.Section(
                    className="grid-kpis",
                    children=[
                        crear_tarjeta_kpi(
                            "PROMEDIO NACIONAL (SATISF. + AVANZ.)",
                            f"{national_avg:.2f}%",
                            "Estudiantes con desempeño óptimo en el país",
                            "#38bdf8"
                        ),
                        crear_tarjeta_kpi(
                            "PROMEDIO MENDOZA (SATISF. + AVANZ.)",
                            f"{mendoza_avg:.2f}%",
                            "Estudiantes con desempeño óptimo en la provincia",
                            "#34d399"
                        ),
                        crear_tarjeta_kpi(
                            "PROVINCIA LÍDER",
                            f"{best_prov_pct:.2f}%",
                            best_prov_name,
                            "#f43f5e"
                        )
                    ]
                ),
                
                html.Section(
                    className="main-panel",
                    children=[
                        html.Div(
                            style={
                                'display': 'flex',
                                'justifyContent': 'space-between',
                                'alignItems': 'center',
                                'flexWrap': 'wrap',
                                'gap': '15px',
                                'marginBottom': '20px'
                            },
                            children=[
                                html.Div(children=[
                                    html.H3("Ranking Nacional por Nivel de Desempeño", style={'fontSize': '18px', 'fontWeight': '600', 'margin': '0 0 5px 0', 'fontFamily': '"Outfit", sans-serif'}),
                                    html.P("Compara el porcentaje de estudiantes en los niveles Satisfactorio y Avanzado.", style={'fontSize': '13px', 'color': '#94a3b8', 'margin': '0'})
                                ]),
                                html.Div(
                                    style={'width': '260px'},
                                    children=[
                                        html.Label("Filtrar por tipo de gestión:", style={'fontSize': '12px', 'fontWeight': '500', 'color': '#94a3b8', 'display': 'block', 'marginBottom': '6px'}),
                                        dcc.Dropdown(
                                            id='filtro-gestion',
                                            options=opciones_gestion,
                                            value='Todos',
                                            clearable=False,
                                            className='dash-dropdown'
                                        )
                                    ]
                                )
                            ]
                        ),
                        
                        dcc.Graph(
                            id='ranking-provincias',
                            config={'displayModeBar': False},
                            style={'height': '650px'}
                        )
                    ]
                ),
                
                html.Section(
                    className="grid-static-plots",
                    children=[
                        html.Div(
                            className="main-panel",
                            style={'marginBottom': '0'},
                            children=[
                                html.H3("Mendoza: Distribución de Desempeño", style={'fontSize': '16px', 'fontWeight': '600', 'margin': '0 0 10px 0', 'fontFamily': '"Outfit", sans-serif'}),
                                html.P("Gráfico estático generado con Matplotlib que muestra el promedio de estudiantes en cada nivel en la provincia de Mendoza.", style={'fontSize': '12px', 'color': '#94a3b8', 'marginBottom': '20px'}),
                                html.Div(
                                    id='matplotlib-container',
                                    style={'display': 'flex', 'justifyContent': 'center'},
                                    children=[
                                        html.Img(
                                            id='matplotlib-img',
                                            style={'maxWidth': '100%', 'borderRadius': '10px', 'boxShadow': '0 4px 15px rgba(0,0,0,0.2)'}
                                        )
                                    ]
                                )
                            ]
                        ),
                        html.Div(
                            className="main-panel",
                            style={'marginBottom': '0'},
                            children=[
                                html.H3("Comparativa por Gestión (Provincia x Sector)", style={'fontSize': '16px', 'fontWeight': '600', 'margin': '0 0 10px 0', 'fontFamily': '"Outfit", sans-serif'}),
                                html.P("Mapa de calor estático generado con Seaborn que compara el porcentaje Satisfactorio + Avanzado según el sector estatal y privado.", style={'fontSize': '12px', 'color': '#94a3b8', 'marginBottom': '20px'}),
                                html.Div(
                                    id='seaborn-container',
                                    style={'display': 'flex', 'justifyContent': 'center'},
                                    children=[
                                        html.Img(
                                            id='seaborn-img',
                                            style={'maxWidth': '100%', 'borderRadius': '10px', 'boxShadow': '0 4px 15px rgba(0,0,0,0.2)'}
                                        )
                                    ]
                                )
                            ]
                        )
                    ]
                )
            ]
        ),
        
        html.Footer(
            className="dashboard-footer",
            children=[
                html.P("Examen Parcial N° 1 — Programación Orientada al Análisis de Datos (POAD)"),
                html.P("Datos oficiales del Operativo Aprender 2024 (datos.gob.ar)", style={'fontSize': '10px', 'marginTop': '5px'})
            ]
        )
    ]
)

@app.callback(
    [
        Output('ranking-provincias', 'figure'),
        Output('matplotlib-img', 'src'),
        Output('seaborn-img', 'src')
    ],
    [Input('filtro-gestion', 'value')]
)
def update_dashboard(gestion):
    if not gestion or gestion == 'Todos':
        df_filtered = df_ok
        title_suffix = " (Gestión Pública y Privada)"
        group_cols = ['jurisdiccion', 'tipo_gestion', 'ambito']
    else:
        df_filtered = df_ok[df_ok['tipo_gestion'] == gestion]
        title_suffix = f" (Gestión: {gestion})"
        group_cols = ['jurisdiccion', 'ambito']
        
    df_rank = (df_filtered.groupby(group_cols)['porcentaje'].sum()
                          .groupby('jurisdiccion').mean()
                          .sort_values()
                          .reset_index(name='porcentaje'))
    
    fig = px.bar(
        df_rank,
        x='porcentaje',
        y='jurisdiccion',
        orientation='h',
        color='porcentaje',
        color_continuous_scale='RdYlGn',
        range_color=[0, 45],
        labels={'porcentaje': '% Estudiantes (Satisf. + Avanz.)', 'jurisdiccion': 'Provincia'},
        title=f"Ranking de Provincias — % Nivel Satisfactorio + Avanzado{title_suffix}"
    )
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_family='"Inter", sans-serif',
        font_color='#cbd5e1',
        title_font_family='"Outfit", sans-serif',
        title_font_size=15,
        title_font_color='#f8fafc',
        margin=dict(l=10, r=10, t=40, b=10),
        xaxis=dict(
            gridcolor='rgba(255,255,255,0.05)',
            zerolinecolor='rgba(255,255,255,0.1)',
            ticksuffix='%',
            range=[0, 45]
        ),
        yaxis=dict(
            gridcolor='rgba(255,255,255,0.05)',
            categoryorder='total ascending'
        ),
        coloraxis_colorbar=dict(
            title='% Desempeño',
            thicknessmode="pixels", thickness=15,
            lenmode="pixels", len=300,
            yanchor="middle", y=0.5
        )
    )
    
    fig.update_traces(
        hovertemplate="<b>%{y}</b><br>%{x:.2f}% de los estudiantes<extra></extra>"
    )
    
    matplotlib_src = get_base64_image("barras_desempeno_mendoza.png")
    seaborn_src = get_base64_image("heatmap_gestion_provincia.png")
    
    return fig, matplotlib_src, seaborn_src

if __name__ == '__main__':
    app.run(debug=True, port=8050)
