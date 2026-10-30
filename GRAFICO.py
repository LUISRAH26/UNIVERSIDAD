
import streamlit as st
import numpy as np
import plotly.graph_objects as go
import ast
import operator

# =========================================================
# 1. CONFIGURACIÓN DE LA APLICACIÓN
# =========================================================

st.set_page_config(
    page_title="Graficador de Funciones 3D",
    page_icon="📐",
    layout="wide"
)

st.title("📐 GRAFICADOR DE FUNCIONES MATEMÁTICAS 3D")
st.caption("Explora superficies matemáticas modificando sus parámetros.")

# =========================================================
# 2. FUNCIONES PREDEFINIDAS
# =========================================================

funciones_preset = {
    "Paraboloide": "a*x**2 + b*y**2 + c",
    "Silla de montar": "a*x**2 - b*y**2 + c",
    "Ondas / Sombrero": "c*sin(sqrt(a*x**2 + b*y**2))",
    "Seno y coseno": "c*sin(a*x)*cos(b*y)",
    "Plano": "a*x + b*y + c",
    "Paraboloide hiperbólico": "x**2 - y**2",
    "Cono": "sqrt(x**2 + y**2)",
    "Función gaussiana": "a*exp(-(x**2 + y**2)/b) + c",
    "Onda radial": "sin(sqrt(x**2 + y**2))",
    "Personalizada": "a*x**2 + b*y**2 + c"
}

# =========================================================
# 3. EVALUADOR SEGURO DE EXPRESIONES
# =========================================================

OPERADORES = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos
}

FUNCIONES = {
    "sin": np.sin,
    "cos": np.cos,
    "tan": np.tan,
    "sqrt": np.sqrt,
    "exp": np.exp,
    "log": np.log,
    "log10": np.log10,
    "abs": np.abs,
    "sinh": np.sinh,
    "cosh": np.cosh,
    "tanh": np.tanh
}

CONSTANTES = {
    "pi": np.pi,
    "e": np.e
}


def evaluar_nodo(nodo, entorno):

    if isinstance(nodo, ast.Constant):
        if isinstance(nodo.value, (int, float)):
            return nodo.value
        raise ValueError("Solo se permiten números.")

    elif isinstance(nodo, ast.Name):
        if nodo.id in entorno:
            return entorno[nodo.id]
        raise ValueError(f"Variable no reconocida: {nodo.id}")

    elif isinstance(nodo, ast.BinOp):
        tipo = type(nodo.op)

        if tipo not in OPERADORES:
            raise ValueError("Operador no permitido.")

        izquierda = evaluar_nodo(nodo.left, entorno)
        derecha = evaluar_nodo(nodo.right, entorno)

        if isinstance(nodo.op, ast.Pow):
            if np.any(np.abs(derecha) > 20):
                raise ValueError("El exponente máximo permitido es 20.")

        return OPERADORES[tipo](izquierda, derecha)

    elif isinstance(nodo, ast.UnaryOp):
        tipo = type(nodo.op)

        if tipo not in OPERADORES:
            raise ValueError("Operador no permitido.")

        return OPERADORES[tipo](
            evaluar_nodo(nodo.operand, entorno)
        )

    elif isinstance(nodo, ast.Call):
        if not isinstance(nodo.func, ast.Name):
            raise ValueError("Llamada no permitida.")

        nombre = nodo.func.id

        if nombre not in FUNCIONES:
            raise ValueError(f"Función no permitida: {nombre}")

        if nodo.keywords:
            raise ValueError("No se permiten argumentos con nombre.")

        argumentos = [
            evaluar_nodo(arg, entorno)
            for arg in nodo.args
        ]

        return FUNCIONES[nombre](*argumentos)

    else:
        raise ValueError("La expresión contiene elementos no permitidos.")


def evaluar_funcion(expresion, entorno):

    try:
        arbol = ast.parse(expresion, mode="eval")
        resultado = evaluar_nodo(arbol.body, entorno)

        resultado = np.asarray(resultado)

        if resultado.ndim == 0:
            resultado = np.full_like(entorno["x"], resultado.item(), dtype=float)

        if resultado.shape != entorno["x"].shape:
            raise ValueError("La función debe devolver una matriz compatible con X e Y.")

        resultado = np.asarray(resultado, dtype=float)
        resultado[~np.isfinite(resultado)] = np.nan

        return resultado

    except Exception as error:
        raise ValueError(str(error))


# =========================================================
# 4. PANEL LATERAL
# =========================================================

st.sidebar.header("⚙️ Configuración")

st.sidebar.subheader("Función matemática")

seleccion = st.sidebar.selectbox(
    "Seleccionar función:",
    list(funciones_preset.keys())
)

formula_default = funciones_preset[seleccion]

if "formula_anterior" not in st.session_state:
    st.session_state.formula_anterior = seleccion
    st.session_state.formula = formula_default

if st.session_state.formula_anterior != seleccion:
    st.session_state.formula = formula_default
    st.session_state.formula_anterior = seleccion

st.sidebar.markdown("**Fórmula z = f(x,y,a,b,c)**")

formula = st.sidebar.text_input(
    "Escribe tu fórmula:",
    key="formula"
)

st.sidebar.caption(
    "Ejemplo: a*x**2 + b*y**2 + c"
)

st.sidebar.divider()

# =========================================================
# 5. PARÁMETROS DINÁMICOS
# =========================================================

st.sidebar.subheader("Parámetros dinámicos")

a = st.sidebar.slider(
    "Parámetro a",
    min_value=-5.0,
    max_value=5.0,
    value=1.0,
    step=0.1
)

b = st.sidebar.slider(
    "Parámetro b",
    min_value=-5.0,
    max_value=5.0,
    value=1.0,
    step=0.1
)

c = st.sidebar.slider(
    "Parámetro c",
    min_value=-5.0,
    max_value=5.0,
    value=0.0,
    step=0.1
)

st.sidebar.divider()

# =========================================================
# 6. CONFIGURACIÓN DEL DOMINIO
# =========================================================

st.sidebar.subheader("Dominio y resolución")

limite = st.sidebar.slider(
    "Rango del dominio [-L, L]",
    min_value=1.0,
    max_value=20.0,
    value=5.0,
    step=0.5
)

resolucion = st.sidebar.slider(
    "Resolución de la malla",
    min_value=20,
    max_value=150,
    value=60,
    step=10
)

st.sidebar.divider()

# =========================================================
# 7. CONFIGURACIÓN VISUAL
# =========================================================

st.sidebar.subheader("Visualización")

colores = {
    "Viridis": "Viridis",
    "Plasma": "Plasma",
    "Inferno": "Inferno",
    "Magma": "Magma",
    "Turbo": "Turbo",
    "Cividis": "Cividis",
    "Blues": "Blues",
    "RdBu": "RdBu"
}

color = st.sidebar.selectbox(
    "Paleta de colores:",
    list(colores.keys())
)

opacidad = st.sidebar.slider(
    "Transparencia de superficie",
    min_value=0.1,
    max_value=1.0,
    value=0.9,
    step=0.1
)

mostrar_malla = st.sidebar.checkbox(
    "Mostrar líneas de malla",
    value=False
)

# =========================================================
# 8. GENERACIÓN DE LA MALLA
# =========================================================

x = np.linspace(-limite, limite, resolucion)
y = np.linspace(-limite, limite, resolucion)

X, Y = np.meshgrid(x, y)

entorno = {
    "x": X,
    "y": Y,
    "X": X,
    "Y": Y,
    "a": a,
    "b": b,
    "c": c,
    **CONSTANTES
}

# =========================================================
# 9. EVALUACIÓN DE LA FUNCIÓN
# =========================================================

try:

    Z = evaluar_funcion(formula, entorno)

    if not np.any(np.isfinite(Z)):
        raise ValueError("La función no produce valores reales finitos.")

    # Limitar valores extremos para proteger la visualización
    Z_plot = np.where(
        np.abs(Z) <= 1e6,
        Z,
        np.nan
    )

    if not np.any(np.isfinite(Z_plot)):
        raise ValueError("Los valores de la función son demasiado grandes.")

    z_min = float(np.nanmin(Z_plot))
    z_max = float(np.nanmax(Z_plot))
    z_media = float(np.nanmean(Z_plot))

    # =====================================================
    # 10. CONSTRUCCIÓN DEL GRÁFICO 3D
    # =====================================================

    fig = go.Figure()

    fig.add_trace(
        go.Surface(
            x=X,
            y=Y,
            z=Z_plot,
            colorscale=colores[color],
            opacity=opacidad,
            showscale=True,
            colorbar=dict(
                title="Valor Z",
                thickness=15
            ),
            contours=dict(
                z=dict(
                    show=mostrar_malla,
                    usecolormap=True,
                    highlightcolor="white",
                    project_z=True
                )
            ),
            name="Superficie"
        )
    )

    # =====================================================
    # 11. DISEÑO DE LA ESCENA 3D
    # =====================================================

    fig.update_layout(
        height=720,
        margin=dict(
            l=0,
            r=0,
            t=50,
            b=0
        ),
        title=dict(
            text=f"z = {formula}",
            x=0.5,
            xanchor="center"
        ),
        scene=dict(
            xaxis=dict(
                title="Eje X",
                showbackground=True,
                backgroundcolor="rgb(245,245,245)",
                gridcolor="white",
                zerolinecolor="black"
            ),
            yaxis=dict(
                title="Eje Y",
                showbackground=True,
                backgroundcolor="rgb(245,245,245)",
                gridcolor="white",
                zerolinecolor="black"
            ),
            zaxis=dict(
                title="Eje Z",
                showbackground=True,
                backgroundcolor="rgb(245,245,245)",
                gridcolor="white",
                zerolinecolor="black"
            ),
            aspectmode="data",
            camera=dict(
                eye=dict(x=1.6, y=1.6, z=1.3)
            )
        ),
        uirevision="mantener_vista"
    )

    # =====================================================
    # 12. DISTRIBUCIÓN PRINCIPAL
    # =====================================================

    st.subheader("Visualización de la superficie")

    col_grafica, col_datos = st.columns(
        [2.8, 1]
    )

    with col_grafica:

        st.plotly_chart(
            fig,
            use_container_width=True,
            config={
                "displayModeBar": True,
                "scrollZoom": True,
                "displaylogo": False
            }
        )

    with col_datos:

        st.subheader("📊 Datos matemáticos")

        st.metric(
            "Valor mínimo Z",
            f"{z_min:.4f}"
        )

        st.metric(
            "Valor máximo Z",
            f"{z_max:.4f}"
        )

        st.metric(
            "Valor medio Z",
            f"{z_media:.4f}"
        )

        st.divider()

        st.markdown("**Parámetros utilizados**")

        st.write(f"a = {a}")
        st.write(f"b = {b}")
        st.write(f"c = {c}")

        st.divider()

        st.markdown("**Dominio**")

        st.write(f"X: [{-limite}, {limite}]")
        st.write(f"Y: [{-limite}, {limite}]")

        st.write(f"Resolución: {resolucion} × {resolucion}")

    # =====================================================
    # 13. INFORMACIÓN MATEMÁTICA
    # =====================================================

    with st.expander("📘 Información de la función"):

        st.write("**Función utilizada:**")
        st.latex(r"z=f(x,y,a,b,c)")

        st.code(formula)

        st.write("**Parámetros actuales:**")
        st.latex(
            rf"a={a},\quad b={b},\quad c={c}"
        )

        st.write(
            "La superficie se genera mediante una malla "
            "de coordenadas X e Y, evaluando la función "
            "para obtener los valores de Z."
        )

except Exception as error:

    st.error(f"Error en la función matemática: {error}")

    st.info(
        "Revisa la fórmula. Utiliza operadores como ** "
        "para potencias y funciones como sin(), cos(), "
        "sqrt(), exp() y log()."
    )

# =========================================================
# 14. PIE DE PÁGINA
# =========================================================

st.divider()

st.caption(
    "Graficador Matemático 3D | "
    "Python + Streamlit + NumPy + Plotly"
)
