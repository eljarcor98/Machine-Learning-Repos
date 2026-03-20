import streamlit as st
import numpy as np
import plotly.graph_objects as go

# Configuración de la página
st.set_page_config(page_title="Simulación Intervalos de Confianza", layout="wide")

# Estilo personalizado (Premium Dark)
st.markdown("""
<style>
    .main {
        background-color: #0f172a;
    }
    .stMetric {
        background-color: rgba(30, 41, 59, 0.7);
        padding: 15px;
        border-radius: 10px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    h1 {
        background: linear-gradient(to right, #818cf8, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
    }
</style>
""", unsafe_allow_html=True)

st.title("📊 Simulación de Intervalos de Confianza al 95%")
st.markdown("Visualiza cómo varía la precisión y la cobertura al cambiar el tamaño de la muestra ($n$) con desviación estándar conocida ($\sigma$).")

# Barra lateral para parámetros
st.sidebar.header("⚙️ Parámetros de la Simulación")
n = st.sidebar.slider("Tamaño de Muestra (n)", min_value=5, max_value=500, value=30, step=5)
sigma = st.sidebar.slider("Desviación Estándar (σ)", min_value=1, max_value=50, value=10)
num_intervals = st.sidebar.slider("Cantidad de Intervalos", min_value=10, max_value=100, value=50)

# Constantes de la población
MU = 100
Z_CRITICAL = 1.96  # Para 95% de confianza

# Simulación
np.random.seed(42)  # Para reproducibilidad inicial, se puede quitar para más aleatoriedad
means = []
lowers = []
uppers = []
captures = []

# Margen de error (fijo para desviación conocida)
margin_of_error = Z_CRITICAL * (sigma / np.sqrt(n))

for i in range(num_intervals):
    sample = np.random.normal(MU, sigma, n)
    sample_mean = np.mean(sample)
    
    lower = sample_mean - margin_of_error
    upper = sample_mean + margin_of_error
    
    is_capture = lower <= MU <= upper
    
    means.append(sample_mean)
    lowers.append(lower)
    uppers.append(upper)
    captures.append(is_capture)

# Métricas
capture_rate = sum(captures) / num_intervals
col1, col2, col3 = st.columns(3)
col1.metric("Tasa de Captura", f"{capture_rate:.1%}", delta=f"{capture_rate-0.95:.1%}", delta_color="normal")
col2.metric("Margen de Error (ME)", f"{margin_of_error:.2f}")
col3.metric("n (Tamaño Muestra)", n)

# Visualización con Plotly
fig = go.Figure()

# Línea de la media poblacional (μ)
fig.add_shape(
    type="line", line=dict(color="red", width=2, dash="dash"),
    x0=MU, x1=MU, y0=-1, y1=num_intervals,
    name="Media Real (μ)"
)

# Intervalos
for i in range(num_intervals):
    color = "#818cf8" if captures[i] else "#ef4444"
    # Línea del intervalo
    fig.add_trace(go.Scatter(
        x=[lowers[i], uppers[i]],
        y=[i, i],
        mode='lines',
        line=dict(color=color, width=2),
        showlegend=False,
        hoverinfo='skip'
    ))
    # Punto de la media muestral
    fig.add_trace(go.Scatter(
        x=[means[i]],
        y=[i],
        mode='markers',
        marker=dict(color=color, size=6),
        name="Captura" if captures[i] else "Fallo",
        showlegend=False,
        hovertemplate=f"Media: %{{x:.2f}}<br>Intervalo: [{lowers[i]:.2f}, {uppers[i]:.2f}]<extra></extra>"
    ))

fig.update_layout(
    title=f"Distribución de {num_intervals} Intervalos de Confianza",
    xaxis_title="Valor de la Variable",
    yaxis_title="Índice de Simulación",
    height=600,
    showlegend=False,
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    font=dict(color="#94a3b8"),
    xaxis=dict(gridcolor='rgba(255,255,255,0.05)'),
    yaxis=dict(showticklabels=False)
)

st.plotly_chart(fig, use_container_width=True)

# Explicación
with st.expander("📖 Conceptos Estadísticos"):
    st.markdown(f"""
    ### ¿Qué estamos viendo?
    1. **Intervalo de Confianza (95%)**: Si repitiéramos este experimento muchas veces, esperaríamos que el 95% de los intervalos calculados contengan la verdadera media poblacional ($\mu = {MU}$).
    2. **Impacto de $n$**: Al **aumentar $n$**, el error estándar ($\sigma/\sqrt{{n}}$) disminuye, haciendo que los intervalos sean **más estrechos** (mayor precisión).
    3. **Impacto de $\sigma$**: Si la variabilidad de la población ($\sigma$) es mayor, los intervalos se vuelven **más anchos**.
    
    La fórmula utilizada para el intervalo es:
    $$\\bar{{x}} \pm z_{{1-\\alpha/2}} \\frac{{\sigma}}{{\sqrt{{n}}}}$$
    Donde $z_{{0.975}} = {Z_CRITICAL}$.
    """)
