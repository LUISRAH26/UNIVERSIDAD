import numpy as np
import plotly.graph_objects as go
import streamlit as st

# ============================================================
# 1. CONFIGURACION
# ============================================================

st.set_page_config(
    page_title="Diseñador Geométrico 3D",
    layout="wide"
)

FONDO = "#111827"
PANEL = "#1F2937"
TEXTO = "#F9FAFB"

COLORES = {
    "Esfera": "#38BDF8",
    "Elipsoide": "#34D399",
    "Prisma": "#F59E0B"
}


# ============================================================
# 2. PARAMETROS POR FIGURA
#    (etiqueta, clave, minimo, maximo, inicial, paso)
# ============================================================

COMUNES = [
    ("Centro X", "x", -10.0, 10.0, 0.0, 0.1),
    ("Centro Y", "y", -10.0, 10.0, 0.0, 0.1),
    ("Centro Z", "z", -10.0, 10.0, 0.0, 0.1),
]

ROTACIONES = [
    ("Rotación X (°)", "rx", 0, 360, 0, 1),
    ("Rotación Y (°)", "ry", 0, 360, 0, 1),
    ("Rotación Z (°)", "rz", 0, 360, 0, 1),
]


def obtener_parametros(figura):
    if figura == "Esfera":
        return [
            ("Radio de la esfera", "r", 0.2, 10.0, 3.0, 0.1)
        ] + COMUNES

    if figura == "Elipsoide":
        return [
            ("Radio X (semieje A)", "a", 0.2, 10.0, 4.0, 0.1),
            ("Radio Y (semieje B)", "b", 0.2, 10.0, 2.5, 0.1),
            ("Radio Z (semieje C)", "c", 0.2, 10.0, 1.5, 0.1),
        ] + COMUNES + ROTACIONES

    return [
        ("Lados de la base", "n", 3, 20, 6, 1),
        ("Radio de la base", "rp", 0.2, 10.0, 3.0, 0.1),
        ("Altura del prisma", "h", 0.2, 15.0, 5.0, 0.1),
    ] + COMUNES + ROTACIONES


# ============================================================
# 3. ROTACION Y TRANSFORMACION
# ============================================================

def matriz_rotacion(v):
    rx = np.radians(v.get("rx", 0))
    ry = np.radians(v.get("ry", 0))
    rz = np.radians(v.get("rz", 0))

    Rx = np.array([
        [1, 0, 0],
        [0, np.cos(rx), -np.sin(rx)],
        [0, np.sin(rx), np.cos(rx)]
    ])
    Ry = np.array([
        [np.cos(ry), 0, np.sin(ry)],
        [0, 1, 0],
        [-np.sin(ry), 0, np.cos(ry)]
    ])
    Rz = np.array([
        [np.cos(rz), -np.sin(rz), 0],
        [np.sin(rz), np.cos(rz), 0],
        [0, 0, 1]
    ])
    return Rz @ Ry @ Rx


def transformar(X, Y, Z, v):
    puntos = np.stack((X, Y, Z), axis=-1)
    forma = puntos.shape
    puntos = puntos.reshape(-1, 3)

    puntos = puntos @ matriz_rotacion(v).T
    puntos = puntos + np.array([v["x"], v["y"], v["z"]])

    puntos = puntos.reshape(forma)
    return puntos[..., 0], puntos[..., 1], puntos[..., 2]


def superficie(X, Y, Z, color):
    return go.Surface(
        x=X, y=Y, z=Z,
        colorscale=[[0, color], [1, color]],
        showscale=False,
        opacity=0.9,
        lighting=dict(ambient=0.55, diffuse=0.8, specular=0.3)
    )


def marcador_centro(v):
    return go.Scatter3d(
        x=[v["x"]], y=[v["y"]], z=[v["z"]],
        mode="markers",
        marker=dict(size=5, color="red"),
        name="Centro",
        showlegend=False
    )


# ============================================================
# 4. FIGURAS
# ============================================================

def dibujar_esfera(v):
    r = v["r"]

    u = np.linspace(0, 2 * np.pi, 80)
    w = np.linspace(-np.pi / 2, np.pi / 2, 60)
    U, W = np.meshgrid(u, w)

    X = r * np.cos(W) * np.cos(U)
    Y = r * np.cos(W) * np.sin(U)
    Z = r * np.sin(W)

    X, Y, Z = transformar(X, Y, Z, v)

    trazas = [superficie(X, Y, Z, COLORES["Esfera"]), marcador_centro(v)]

    datos = {
        "Radio": r,
        "Diámetro": 2 * r,
        "Área superficial": 4 * np.pi * r**2,
        "Volumen": (4 / 3) * np.pi * r**3,
        "Fórmula del área": "4 π r²",
        "Fórmula del volumen": "4/3 π r³",
    }
    return trazas, datos, r


def dibujar_elipsoide(v):
    a, b, c = v["a"], v["b"], v["c"]

    u = np.linspace(0, 2 * np.pi, 80)
    w = np.linspace(-np.pi / 2, np.pi / 2, 60)
    U, W = np.meshgrid(u, w)

    X = a * np.cos(W) * np.cos(U)
    Y = b * np.cos(W) * np.sin(U)
    Z = c * np.sin(W)

    X, Y, Z = transformar(X, Y, Z, v)

    trazas = [superficie(X, Y, Z, COLORES["Elipsoide"]), marcador_centro(v)]

    # Aproximación de Knud Thomsen
    p = 1.6075
    area = 4 * np.pi * (
        ((a * b) ** p + (a * c) ** p + (b * c) ** p) / 3
    ) ** (1 / p)

    datos = {
        "Radio X": a,
        "Radio Y": b,
        "Radio Z": c,
        "Área aproximada": area,
        "Volumen": (4 / 3) * np.pi * a * b * c,
        "Fórmula del volumen": "4/3 π abc",
        "Área": "Aproximación de Knud Thomsen",
    }
    return trazas, datos, max(a, b, c)


def dibujar_prisma(v):
    n = int(v["n"])
    radio = v["rp"]
    altura = v["h"]

    ang = np.linspace(0, 2 * np.pi, n, endpoint=False)
    x = radio * np.cos(ang)
    y = radio * np.sin(ang)

    xi, yi, zi = transformar(x, y, np.full(n, -altura / 2), v)
    xs, ys, zs = transformar(x, y, np.full(n, altura / 2), v)

    # Vértices: primero la base inferior (0..n-1), luego la superior (n..2n-1)
    vx = np.concatenate([xi, xs])
    vy = np.concatenate([yi, ys])
    vz = np.concatenate([zi, zs])

    I, J, K = [], [], []

    # Bases (triángulos en abanico)
    for i in range(1, n - 1):
        I += [0, n]
        J += [i, n + i]
        K += [i + 1, n + i + 1]

    # Caras laterales (2 triángulos por cara)
    for i in range(n):
        j = (i + 1) % n
        I += [i, i]
        J += [j, n + j]
        K += [n + j, n + i]

    malla = go.Mesh3d(
        x=vx, y=vy, z=vz,
        i=I, j=J, k=K,
        color=COLORES["Prisma"],
        opacity=0.85,
        flatshading=True
    )

    # Aristas
    ex, ey, ez = [], [], []
    for i in range(n):
        j = (i + 1) % n
        for (p, q) in [(i, j), (n + i, n + j), (i, n + i)]:
            ex += [vx[p], vx[q], None]
            ey += [vy[p], vy[q], None]
            ez += [vz[p], vz[q], None]

    aristas = go.Scatter3d(
        x=ex, y=ey, z=ez,
        mode="lines",
        line=dict(color="#FFF1D6", width=4),
        showlegend=False
    )

    vertices = go.Scatter3d(
        x=vx, y=vy, z=vz,
        mode="markers",
        marker=dict(size=3, color="white"),
        showlegend=False
    )

    # Cálculos del prisma regular
    lado = 2 * radio * np.sin(np.pi / n)
    perimetro = n * lado
    apotema = radio * np.cos(np.pi / n)
    area_base = perimetro * apotema / 2
    area_lateral = perimetro * altura

    datos = {
        "Lados de la base": n,
        "Radio de la base": radio,
        "Altura": altura,
        "Lado del polígono": lado,
        "Apotema": apotema,
        "Perímetro de base": perimetro,
        "Área de una base": area_base,
        "Área lateral": area_lateral,
        "Área total": 2 * area_base + area_lateral,
        "Volumen": area_base * altura,
        "Fórmula del volumen": "Área base × altura",
    }
    return [malla, aristas, vertices, marcador_centro(v)], datos, max(radio, altura / 2)


# ============================================================
# 5. CONFIGURACION DE LA GRAFICA
# ============================================================

def crear_figura(trazas, titulo, centro, extension):
    ext = max(extension * 1.5, 1.5)

    eje = dict(
        backgroundcolor=PANEL,
        gridcolor="rgba(255,255,255,0.2)",
        color=TEXTO,
        showbackground=True
    )

    fig = go.Figure(data=trazas)
    fig.update_layout(
        title=dict(text=titulo.upper(), font=dict(color=TEXTO, size=20), x=0.5),
        paper_bgcolor=FONDO,
        margin=dict(l=0, r=0, t=50, b=0),
        height=650,
        scene=dict(
            xaxis=dict(range=[centro[0] - ext, centro[0] + ext], title="X", **eje),
            yaxis=dict(range=[centro[1] - ext, centro[1] + ext], title="Y", **eje),
            zaxis=dict(range=[centro[2] - ext, centro[2] + ext], title="Z", **eje),
            aspectmode="cube",
            camera=dict(eye=dict(x=1.5, y=1.5, z=1.0)),
        ),
    )
    return fig


# ============================================================
# 6. INTERFAZ
# ============================================================

st.title("DISEÑADOR GEOMÉTRICO 3D")
st.caption("Visualización y análisis de sólidos geométricos")

# --- Panel izquierdo: controles (sidebar) ---
st.sidebar.header("PARÁMETROS")

figura = st.sidebar.selectbox(
    "Selecciona una figura geométrica",
    ["Esfera", "Elipsoide", "Prisma"]
)

parametros = obtener_parametros(figura)


def restablecer():
    for _, clave, _, _, inicial, _ in parametros:
        st.session_state[f"{figura}_{clave}"] = inicial


st.sidebar.subheader("DIMENSIONES Y POSICIÓN")

valores = {}
for etiqueta, clave, minimo, maximo, inicial, paso in parametros:
    valores[clave] = st.sidebar.slider(
        etiqueta,
        min_value=minimo,
        max_value=maximo,
        value=inicial,
        step=paso,
        key=f"{figura}_{clave}"
    )

st.sidebar.button(
    "RESTABLECER",
    on_click=restablecer,
    use_container_width=True
)

# --- Cálculo ---
if figura == "Esfera":
    trazas, datos, extension = dibujar_esfera(valores)
elif figura == "Elipsoide":
    trazas, datos, extension = dibujar_elipsoide(valores)
else:
    trazas, datos, extension = dibujar_prisma(valores)

centro = (valores["x"], valores["y"], valores["z"])

# --- Panel central y derecho ---
col_grafica, col_resultados = st.columns([3, 1])

with col_grafica:
    st.subheader("VISUALIZACIÓN TRIDIMENSIONAL")
    st.plotly_chart(
        crear_figura(trazas, figura, centro, extension),
        use_container_width=True
    )
    st.caption("Arrastra con el mouse para rotar y usa la rueda para acercar.")

with col_resultados:
    st.subheader("RESULTADOS GEOMÉTRICOS")
    st.markdown(f"### {figura}")

    for nombre, valor in datos.items():
        if isinstance(valor, (int, float, np.number)):
            st.metric(nombre, f"{valor:,.3f}")
        else:
            st.markdown(f"**{nombre}**  \n{valor}")

    st.caption("Las áreas y volúmenes se expresan en unidades geométricas.")

    aplicacion = Geometria3D(ventana)

    ventana.mainloop()
