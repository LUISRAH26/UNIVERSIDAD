
import streamlit as st
import numpy as np
import plotly.graph_objects as go

# ============================================================
# 1. CONFIGURACIÓN GENERAL
# ============================================================

st.set_page_config(
    page_title="GEOMETRY 3D",
    page_icon="📐",
    layout="wide"
)

st.title("📐 GEOMETRY 3D")
st.caption("EDITOR MATEMÁTICO | Visualización interactiva de superficies 3D")

# ============================================================
# 2. DEFINICIÓN DE FIGURAS Y PARÁMETROS
# ============================================================

FIGURAS = {
    "Elipsoide": [
        ("Semieje X (a)", 5.0),
        ("Semieje Y (b)", 3.0),
        ("Semieje Z (c)", 4.0),
        ("Centro X (h)", 0.0),
        ("Centro Y (k)", 0.0),
        ("Centro Z (l)", 0.0)
    ],

    "Esfera": [
        ("Radio (r)", 5.0),
        ("Centro X (h)", 0.0),
        ("Centro Y (k)", 0.0),
        ("Centro Z (l)", 0.0)
    ],

    "Paraboloide": [
        ("Escala X (a)", 2.0),
        ("Escala Y (b)", 2.0),
        ("Altura (c)", 5.0)
    ],

    "Hiperboloide de 1 hoja": [
        ("Semieje X (a)", 3.0),
        ("Semieje Y (b)", 3.0),
        ("Semieje Z (c)", 2.0)
    ],

    "Hiperboloide de 2 hojas": [
        ("Semieje X (a)", 3.0),
        ("Semieje Y (b)", 3.0),
        ("Semieje Z (c)", 2.0)
    ],

    "Cono": [
        ("Radio X (a)", 4.0),
        ("Radio Y (b)", 4.0),
        ("Altura (c)", 5.0)
    ],

    "Cilindro": [
        ("Radio (r)", 3.0),
        ("Altura (h)", 6.0)
    ]
}

# ============================================================
# 3. PANEL LATERAL
# ============================================================

st.sidebar.title("⚙️ CONFIGURACIÓN")

figura = st.sidebar.selectbox(
    "Seleccionar figura geométrica",
    list(FIGURAS.keys())
)

st.sidebar.divider()
st.sidebar.subheader("Parámetros dimensionales")

parametros = {}

for nombre, valor_default in FIGURAS[figura]:

    es_centro = nombre.startswith("Centro")

    parametros[nombre] = st.sidebar.number_input(
        nombre,
        value=float(valor_default),
        step=0.5,
        format="%.2f"
    )

    # Validación de dimensiones
    if not es_centro and parametros[nombre] <= 0:
        st.sidebar.error(f"{nombre} debe ser mayor que cero.")

# ============================================================
# 4. CONFIGURACIÓN VISUAL
# ============================================================

st.sidebar.divider()
st.sidebar.subheader("Apariencia del gráfico")

colores = {
    "Viridis": "Viridis",
    "Plasma": "Plasma",
    "Cool": "Ice",
    "Turbo": "Turbo",
    "Inferno": "Inferno",
    "Magma": "Magma",
    "Cividis": "Cividis",
    "Blues": "Blues"
}

color_nombre = st.sidebar.selectbox(
    "Color de superficie",
    list(colores.keys())
)

opacidad = st.sidebar.slider(
    "Opacidad",
    min_value=0.1,
    max_value=1.0,
    value=0.85,
    step=0.05
)

resolucion = st.sidebar.slider(
    "Resolución de la superficie",
    min_value=30,
    max_value=150,
    value=100,
    step=10
)

mostrar_centro = st.sidebar.checkbox(
    "Mostrar centro de referencia",
    value=True
)

mostrar_ejes = st.sidebar.checkbox(
    "Mostrar ejes coordenados",
    value=True
)

# ============================================================
# 5. FUNCIONES AUXILIARES
# ============================================================

def obtener(nombre):
    return parametros[nombre]


def crear_malla(res):
    u = np.linspace(0, 2*np.pi, res)
    v = np.linspace(-1, 1, res)
    U, V = np.meshgrid(u, v)
    return U, V


def agregar_superficie(fig, X, Y, Z, nombre, color, opacidad):

    fig.add_trace(go.Surface(
        x=X,
        y=Y,
        z=Z,
        colorscale=color,
        opacity=opacidad,
        showscale=False,
        name=nombre,
        hovertemplate=(
            "X: %{x:.2f}<br>"
            "Y: %{y:.2f}<br>"
            "Z: %{z:.2f}"
            "<extra>" + nombre + "</extra>"
        )
    ))


def agregar_centro(fig, x, y, z):

    fig.add_trace(go.Scatter3d(
        x=[x],
        y=[y],
        z=[z],
        mode="markers",
        marker=dict(
            color="black",
            size=5
        ),
        name="Centro"
    ))


# ============================================================
# 6. GENERACIÓN DE FIGURAS GEOMÉTRICAS
# ============================================================

def generar_figura():

    fig = go.Figure()

    U, V = crear_malla(resolucion)

    a = b = c = 1.0

    # --------------------------------------------------------
    # ELIPSOIDE
    # --------------------------------------------------------

    if figura == "Elipsoide":

        a = obtener("Semieje X (a)")
        b = obtener("Semieje Y (b)")
        c = obtener("Semieje Z (c)")

        h = obtener("Centro X (h)")
        k = obtener("Centro Y (k)")
        l = obtener("Centro Z (l)")

        X = h + a*np.cos(U)*np.sqrt(1-V**2)
        Y = k + b*np.sin(U)*np.sqrt(1-V**2)
        Z = l + c*V

        agregar_superficie(
            fig, X, Y, Z,
            "Elipsoide", colores[color_nombre], opacidad
        )

        if mostrar_centro:
            agregar_centro(fig, h, k, l)

    # --------------------------------------------------------
    # ESFERA
    # --------------------------------------------------------

    elif figura == "Esfera":

        r = obtener("Radio (r)")

        h = obtener("Centro X (h)")
        k = obtener("Centro Y (k)")
        l = obtener("Centro Z (l)")

        a = b = c = r

        X = h + r*np.cos(U)*np.sqrt(1-V**2)
        Y = k + r*np.sin(U)*np.sqrt(1-V**2)
        Z = l + r*V

        agregar_superficie(
            fig, X, Y, Z,
            "Esfera", colores[color_nombre], opacidad
        )

        if mostrar_centro:
            agregar_centro(fig, h, k, l)

    # --------------------------------------------------------
    # PARABOLOIDE ELÍPTICO
    # --------------------------------------------------------

    elif figura == "Paraboloide":

        a = obtener("Escala X (a)")
        b = obtener("Escala Y (b)")
        c = obtener("Altura (c)")

        R = (V+1)/2

        X = a*R*np.cos(U)
        Y = b*R*np.sin(U)
        Z = c*R**2

        agregar_superficie(
            fig, X, Y, Z,
            "Paraboloide", colores[color_nombre], opacidad
        )

    # --------------------------------------------------------
    # HIPERBOLOIDE DE UNA HOJA
    # --------------------------------------------------------

    elif figura == "Hiperboloide de 1 hoja":

        a = obtener("Semieje X (a)")
        b = obtener("Semieje Y (b)")
        c = obtener("Semieje Z (c)")

        W = np.linspace(-1.5, 1.5, resolucion)

        U2, W2 = np.meshgrid(
            np.linspace(0, 2*np.pi, resolucion),
            W
        )

        X = a*np.cosh(W2)*np.cos(U2)
        Y = b*np.cosh(W2)*np.sin(U2)
        Z = c*np.sinh(W2)

        agregar_superficie(
            fig, X, Y, Z,
            "Hiperboloide de una hoja",
            colores[color_nombre], opacidad
        )

    # --------------------------------------------------------
    # HIPERBOLOIDE DE DOS HOJAS
    # --------------------------------------------------------

    elif figura == "Hiperboloide de 2 hojas":

        a = obtener("Semieje X (a)")
        b = obtener("Semieje Y (b)")
        c = obtener("Semieje Z (c)")

        W = np.linspace(0, 1.5, resolucion)

        U2, W2 = np.meshgrid(
            np.linspace(0, 2*np.pi, resolucion),
            W
        )

        X = a*np.sinh(W2)*np.cos(U2)
        Y = b*np.sinh(W2)*np.sin(U2)
        Z = c*np.cosh(W2)

        agregar_superficie(
            fig, X, Y, Z,
            "Hiperboloide superior",
            colores[color_nombre], opacidad
        )

        agregar_superficie(
            fig, X, Y, -Z,
            "Hiperboloide inferior",
            colores[color_nombre], opacidad
        )

    # --------------------------------------------------------
    # CONO
    # --------------------------------------------------------

    elif figura == "Cono":

        a = obtener("Radio X (a)")
        b = obtener("Radio Y (b)")
        c = obtener("Altura (c)")

        R = (V+1)/2

        X = a*R*np.cos(U)
        Y = b*R*np.sin(U)
        Z = c*V

        agregar_superficie(
            fig, X, Y, Z,
            "Cono", colores[color_nombre], opacidad
        )

    # --------------------------------------------------------
    # CILINDRO
    # --------------------------------------------------------

    elif figura == "Cilindro":

        r = obtener("Radio (r)")
        h = obtener("Altura (h)")

        a = b = r
        c = h/2

        X = r*np.cos(U)
        Y = r*np.sin(U)
        Z = h*V/2

        agregar_superficie(
            fig, X, Y, Z,
            "Cilindro", colores[color_nombre], opacidad
        )

        # Tapa superior e inferior
        theta = np.linspace(0, 2*np.pi, resolucion)

        radio = np.linspace(0, r, resolucion)

        R, T = np.meshgrid(radio, theta)

        X_tapa = R*np.cos(T)
        Y_tapa = R*np.sin(T)

        for altura in [-h/2, h/2]:

            Z_tapa = np.full_like(X_tapa, altura)

            agregar_superficie(
                fig, X_tapa, Y_tapa, Z_tapa,
                "Tapa del cilindro",
                colores[color_nombre], opacidad
            )

    # --------------------------------------------------------
    # DISEÑO GENERAL
    # --------------------------------------------------------

    fig.update_layout(
        height=750,
        margin=dict(l=0, r=0, t=50, b=0),
        title=dict(
            text=f"Visualización 3D: {figura}",
            x=0.5
        ),
        scene=dict(
            xaxis=dict(
                title="Eje X",
                visible=mostrar_ejes,
                showbackground=True,
                backgroundcolor="rgb(245,247,250)",
                gridcolor="white"
            ),
            yaxis=dict(
                title="Eje Y",
                visible=mostrar_ejes,
                showbackground=True,
                backgroundcolor="rgb(245,247,250)",
                gridcolor="white"
            ),
            zaxis=dict(
                title="Eje Z",
                visible=mostrar_ejes,
                showbackground=True,
                backgroundcolor="rgb(245,247,250)",
                gridcolor="white"
            ),
            aspectmode="data",
            camera=dict(
                eye=dict(x=1.6, y=1.6, z=1.3)
            )
        ),
        uirevision="geometry_3d"
    )

    return fig, a, b, c


# ============================================================
# 7. VALIDACIÓN Y GENERACIÓN
# ============================================================

dimensiones_validas = all(
    valor > 0
    for nombre, valor in parametros.items()
    if not nombre.startswith("Centro")
)

if dimensiones_validas:

    fig, a, b, c = generar_figura()

    # ========================================================
    # 8. DISTRIBUCIÓN DE LA INTERFAZ
    # ========================================================

    columna_grafica, columna_info = st.columns(
        [2.7, 1]
    )

    with columna_grafica:

        st.subheader("📊 Gráfica tridimensional")

        st.plotly_chart(
            fig,
            use_container_width=True,
            config={
                "displayModeBar": True,
                "scrollZoom": True,
                "displaylogo": False
            }
        )

    with columna_info:

        st.subheader("📐 Dimensiones")

        for nombre, valor in parametros.items():

            st.metric(
                nombre,
                f"{valor:.2f}"
            )

        st.divider()

        st.markdown("**Proporción de referencia**")

        st.write(f"X: {a:.2f}")
        st.write(f"Y: {b:.2f}")
        st.write(f"Z: {c:.2f}")

else:

    st.error(
        "Las dimensiones deben ser mayores que cero. "
        "Corrige los parámetros en el panel lateral."
    )

# ============================================================
# 9. INFORMACIÓN FINAL
# ============================================================

with st.expander("Información del programa"):

    st.write("""
    **GEOMETRY 3D - EDITOR MATEMÁTICO**

    Aplicación para visualizar superficies geométricas
    tridimensionales a partir de sus parámetros matemáticos.

    Funcionalidades:
    - Selección dinámica de figuras.
    - Parámetros independientes.
    - Representación tridimensional interactiva.
    - Cambio de colores y opacidad.
    - Visualización de coordenadas centrales.
    - Ajuste de resolución de las superficies.
    """)

st.divider()

st.caption(
    "GEOMETRY 3D | Python + Streamlit + NumPy + Plotly"
)

