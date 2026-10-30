
import tkinter as tk
from tkinter import ttk
import numpy as np

import matplotlib
matplotlib.use("TkAgg")

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg,
    NavigationToolbar2Tk
)
from mpl_toolkits.mplot3d.art3d import Poly3DCollection


# ============================================================
# 1. CONFIGURACION VISUAL
# ============================================================

FONDO = "#111827"
PANEL = "#1F2937"
PANEL_INTERIOR = "#273449"
TEXTO = "#F9FAFB"
SECUNDARIO = "#CBD5E1"
AZUL = "#38BDF8"

COLORES = {
    "Esfera": "#38BDF8",
    "Elipsoide": "#34D399",
    "Prisma": "#F59E0B"
}


# ============================================================
# 2. APLICACION PRINCIPAL
# ============================================================

class Geometria3D:

    def __init__(self, root):

        self.root = root
        self.root.title("Diseñador Geometrico 3D")
        self.root.geometry("1550x900")
        self.root.minsize(1150, 700)
        self.root.configure(bg=FONDO)

        self.figura = tk.StringVar(value="Esfera")
        self.valores = {}
        self.sliders = {}

        self.actualizacion_pendiente = None

        self.crear_interfaz()
        self.cambiar_figura("Esfera")


    # ========================================================
    # 3. ESTRUCTURA GENERAL DE LA VENTANA
    # ========================================================

    def crear_interfaz(self):

        encabezado = tk.Frame(
            self.root,
            bg=FONDO,
            height=65
        )
        encabezado.pack(fill="x", padx=15, pady=10)

        tk.Label(
            encabezado,
            text="DISEÑADOR GEOMÉTRICO 3D",
            bg=FONDO,
            fg=TEXTO,
            font=("Arial", 19, "bold")
        ).pack(side="left")

        tk.Label(
            encabezado,
            text="Visualización y análisis de sólidos geométricos",
            bg=FONDO,
            fg=SECUNDARIO,
            font=("Arial", 10)
        ).pack(side="right", padx=10)

        # Tres paneles independientes
        contenido = tk.Frame(self.root, bg=FONDO)
        contenido.pack(fill="both", expand=True, padx=12, pady=5)

        contenido.columnconfigure(0, weight=0, minsize=285)
        contenido.columnconfigure(1, weight=1)
        contenido.columnconfigure(2, weight=0, minsize=275)
        contenido.rowconfigure(0, weight=1)

        self.panel_controles = tk.Frame(
            contenido,
            bg=PANEL,
            width=285
        )
        self.panel_controles.grid(
            row=0, column=0, sticky="nsew", padx=5
        )
        self.panel_controles.grid_propagate(False)

        self.panel_grafica = tk.Frame(
            contenido,
            bg=PANEL
        )
        self.panel_grafica.grid(
            row=0, column=1, sticky="nsew", padx=5
        )

        self.panel_resultados = tk.Frame(
            contenido,
            bg=PANEL,
            width=275
        )
        self.panel_resultados.grid(
            row=0, column=2, sticky="nsew", padx=5
        )
        self.panel_resultados.grid_propagate(False)

        self.crear_panel_controles()
        self.crear_panel_grafica()
        self.crear_panel_resultados()


    # ========================================================
    # 4. PANEL IZQUIERDO: CONTROLES
    # ========================================================

    def crear_panel_controles(self):

        tk.Label(
            self.panel_controles,
            text="PARÁMETROS",
            bg=PANEL,
            fg=TEXTO,
            font=("Arial", 13, "bold")
        ).pack(pady=(15, 5))

        tk.Label(
            self.panel_controles,
            text="Selecciona una figura geométrica",
            bg=PANEL,
            fg=SECUNDARIO,
            font=("Arial", 9)
        ).pack(pady=5)

        selector = ttk.Combobox(
            self.panel_controles,
            textvariable=self.figura,
            values=["Esfera", "Elipsoide", "Prisma"],
            state="readonly",
            font=("Arial", 10)
        )
        selector.pack(fill="x", padx=15, pady=8)
        selector.bind(
            "<<ComboboxSelected>>",
            lambda event: self.cambiar_figura(self.figura.get())
        )

        # Area desplazable para los deslizadores
        self.canvas_controles = tk.Canvas(
            self.panel_controles,
            bg=PANEL,
            highlightthickness=0
        )
        self.canvas_controles.pack(
            fill="both", expand=True, padx=5, pady=5
        )

        barra = ttk.Scrollbar(
            self.panel_controles,
            orient="vertical",
            command=self.canvas_controles.yview
        )
        barra.place(relx=0.965, rely=0.20, relheight=0.72)

        self.canvas_controles.configure(
            yscrollcommand=barra.set
        )

        self.contenedor_sliders = tk.Frame(
            self.canvas_controles,
            bg=PANEL
        )

        self.ventana_sliders = self.canvas_controles.create_window(
            (0, 0),
            window=self.contenedor_sliders,
            anchor="nw"
        )

        self.contenedor_sliders.bind(
            "<Configure>",
            lambda event: self.canvas_controles.configure(
                scrollregion=self.canvas_controles.bbox("all")
            )
        )

        self.canvas_controles.bind(
            "<Configure>",
            lambda event: self.canvas_controles.itemconfigure(
                self.ventana_sliders,
                width=event.width
            )
        )

        # Botones inferiores
        botones = tk.Frame(
            self.panel_controles,
            bg=PANEL
        )
        botones.pack(fill="x", padx=10, pady=12)

        tk.Button(
            botones,
            text="RESTABLECER",
            bg="#334155",
            fg="white",
            activebackground="#475569",
            activeforeground="white",
            relief="flat",
            command=self.restablecer
        ).pack(fill="x", pady=3)

        tk.Button(
            botones,
            text="ACTUALIZAR GRÁFICA",
            bg="#0369A1",
            fg="white",
            activebackground="#0284C7",
            activeforeground="white",
            relief="flat",
            command=self.actualizar
        ).pack(fill="x", pady=3)


    # ========================================================
    # 5. PANEL CENTRAL: GRAFICA 3D
    # ========================================================

    def crear_panel_grafica(self):

        tk.Label(
            self.panel_grafica,
            text="VISUALIZACIÓN TRIDIMENSIONAL",
            bg=PANEL,
            fg=TEXTO,
            font=("Arial", 13, "bold")
        ).pack(pady=12)

        self.fig = Figure(
            figsize=(8, 7),
            dpi=100,
            facecolor=FONDO
        )

        self.ax = self.fig.add_subplot(
            111,
            projection="3d"
        )

        self.canvas_grafica = FigureCanvasTkAgg(
            self.fig,
            master=self.panel_grafica
        )

        self.canvas_grafica.get_tk_widget().pack(
            fill="both",
            expand=True,
            padx=8,
            pady=5
        )

        # Barra de herramientas para rotar y acercar
        self.toolbar_frame = tk.Frame(
            self.panel_grafica,
            bg=PANEL
        )
        self.toolbar_frame.pack(fill="x")

        self.toolbar = NavigationToolbar2Tk(
            self.canvas_grafica,
            self.toolbar_frame,
            pack_toolbar=False
        )
        self.toolbar.update()
        self.toolbar.pack(side="left", padx=5, pady=5)


    # ========================================================
    # 6. PANEL DERECHO: RESULTADOS
    # ========================================================

    def crear_panel_resultados(self):

        tk.Label(
            self.panel_resultados,
            text="RESULTADOS GEOMÉTRICOS",
            bg=PANEL,
            fg=TEXTO,
            font=("Arial", 12, "bold")
        ).pack(pady=15)

        self.nombre_resultado = tk.Label(
            self.panel_resultados,
            text="Esfera",
            bg=PANEL,
            fg=AZUL,
            font=("Arial", 14, "bold")
        )
        self.nombre_resultado.pack(pady=5)

        self.texto_resultados = tk.Text(
            self.panel_resultados,
            bg=PANEL_INTERIOR,
            fg=TEXTO,
            font=("Consolas", 10),
            relief="flat",
            wrap="word",
            padx=12,
            pady=12,
            spacing1=5,
            spacing3=8
        )
        self.texto_resultados.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )

        self.texto_resultados.configure(state="disabled")

        tk.Label(
            self.panel_resultados,
            text="Las áreas y volúmenes se expresan en unidades geométricas.",
            bg=PANEL,
            fg=SECUNDARIO,
            font=("Arial", 8),
            wraplength=235,
            justify="left"
        ).pack(padx=12, pady=12)


    # ========================================================
    # 7. DEFINICION DE PARAMETROS POR FIGURA
    # ========================================================

    def obtener_parametros(self, figura):

        comunes = [
            ("Centro X", "x", -10, 10, 0, 0.1),
            ("Centro Y", "y", -10, 10, 0, 0.1),
            ("Centro Z", "z", -10, 10, 0, 0.1)
        ]

        rotaciones = [
            ("Rotación X (°)", "rx", 0, 360, 0, 1),
            ("Rotación Y (°)", "ry", 0, 360, 0, 1),
            ("Rotación Z (°)", "rz", 0, 360, 0, 1)
        ]

        if figura == "Esfera":

            return [
                ("Radio de la esfera", "r", 0.2, 10, 3, 0.1)
            ] + comunes

        elif figura == "Elipsoide":

            return [
                ("Radio X (semieje A)", "a", 0.2, 10, 4, 0.1),
                ("Radio Y (semieje B)", "b", 0.2, 10, 2.5, 0.1),
                ("Radio Z (semieje C)", "c", 0.2, 10, 1.5, 0.1)
            ] + comunes + rotaciones

        elif figura == "Prisma":

            return [
                ("Lados de la base", "n", 3, 20, 6, 1),
                ("Radio de la base", "rp", 0.2, 10, 3, 0.1),
                ("Altura del prisma", "h", 0.2, 15, 5, 0.1)
            ] + comunes + rotaciones


    # ========================================================
    # 8. CREAR DESLIZADORES DINAMICOS
    # ========================================================

    def cambiar_figura(self, figura):

        self.figura.set(figura)

        # Limpiar controles anteriores
        for widget in self.contenedor_sliders.winfo_children():
            widget.destroy()

        self.sliders.clear()
        self.valores.clear()

        self.nombre_resultado.configure(text=figura)

        tk.Label(
            self.contenedor_sliders,
            text="DIMENSIONES Y POSICIÓN",
            bg=PANEL,
            fg=AZUL,
            font=("Arial", 10, "bold")
        ).pack(fill="x", padx=10, pady=(10, 8))

        parametros = self.obtener_parametros(figura)

        for etiqueta, clave, minimo, maximo, inicial, paso in parametros:

            self.valores[clave] = inicial

            grupo = tk.Frame(
                self.contenedor_sliders,
                bg=PANEL_INTERIOR,
                padx=8,
                pady=5
            )
            grupo.pack(fill="x", padx=8, pady=5)

            fila = tk.Frame(grupo, bg=PANEL_INTERIOR)
            fila.pack(fill="x")

            tk.Label(
                fila,
                text=etiqueta,
                bg=PANEL_INTERIOR,
                fg=TEXTO,
                font=("Arial", 9)
            ).pack(side="left")

            valor_label = tk.Label(
                fila,
                text=str(inicial),
                bg=PANEL_INTERIOR,
                fg=AZUL,
                font=("Arial", 9, "bold")
            )
            valor_label.pack(side="right")

            def cambiar_valor(valor, k=clave, etiqueta_valor=valor_label):

                numero = float(valor)

                if k == "n":
                    numero = int(round(numero))

                self.valores[k] = numero
                etiqueta_valor.configure(text=str(numero))

                self.programar_actualizacion()

            slider = tk.Scale(
                grupo,
                from_=minimo,
                to=maximo,
                resolution=paso,
                orient="horizontal",
                showvalue=False,
                bg=PANEL_INTERIOR,
                fg=TEXTO,
                troughcolor="#475569",
                activebackground=AZUL,
                highlightthickness=0,
                bd=0,
                command=cambiar_valor
            )

            slider.set(inicial)
            slider.pack(fill="x", pady=(3, 0))

            self.sliders[clave] = slider

        self.canvas_controles.yview_moveto(0)
        self.actualizar()


    # ========================================================
    # 9. PROGRAMAR ACTUALIZACION
    # ========================================================

    def programar_actualizacion(self):

        # Evita acumular muchas actualizaciones mientras
        # se mueve rapidamente un deslizador.

        if self.actualizacion_pendiente is not None:
            self.root.after_cancel(self.actualizacion_pendiente)

        self.actualizacion_pendiente = self.root.after(
            40,
            self.actualizar
        )


    # ========================================================
    # 10. MATRICES DE ROTACION
    # ========================================================

    def matriz_rotacion(self):

        rx = np.radians(self.valores.get("rx", 0))
        ry = np.radians(self.valores.get("ry", 0))
        rz = np.radians(self.valores.get("rz", 0))

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


    def transformar(self, X, Y, Z):

        puntos = np.stack((X, Y, Z), axis=-1)

        forma = puntos.shape
        puntos = puntos.reshape(-1, 3)

        puntos = puntos @ self.matriz_rotacion().T

        centro = np.array([
            self.valores.get("x", 0),
            self.valores.get("y", 0),
            self.valores.get("z", 0)
        ])

        puntos += centro

        puntos = puntos.reshape(forma)

        return (
            puntos[..., 0],
            puntos[..., 1],
            puntos[..., 2]
        )


    # ========================================================
    # 11. CONSTRUIR ESFERA
    # ========================================================

    def dibujar_esfera(self):

        r = self.valores["r"]

        u = np.linspace(0, 2 * np.pi, 80)
        v = np.linspace(-np.pi / 2, np.pi / 2, 60)

        U, V = np.meshgrid(u, v)

        X = r * np.cos(V) * np.cos(U)
        Y = r * np.cos(V) * np.sin(U)
        Z = r * np.sin(V)

        centro = [
            self.valores["x"],
            self.valores["y"],
            self.valores["z"]
        ]

        X = X + centro[0]
        Y = Y + centro[1]
        Z = Z + centro[2]

        self.ax.plot_surface(
            X, Y, Z,
            color=COLORES["Esfera"],
            edgecolor="#D9F3FF",
            linewidth=0.25,
            alpha=0.88,
            rstride=3,
            cstride=3
        )

        self.ax.scatter(*centro, color="red", s=35)

        area = 4 * np.pi * r**2
        volumen = (4 / 3) * np.pi * r**3

        return {
            "Radio": r,
            "Diámetro": 2 * r,
            "Área superficial": area,
            "Volumen": volumen,
            "Fórmula del área": "4 π r²",
            "Fórmula del volumen": "4/3 π r³"
        }, r


    # ========================================================
    # 12. CONSTRUIR ELIPSOIDE
    # ========================================================

    def dibujar_elipsoide(self):

        a = self.valores["a"]
        b = self.valores["b"]
        c = self.valores["c"]

        u = np.linspace(0, 2 * np.pi, 80)
        v = np.linspace(-np.pi / 2, np.pi / 2, 60)

        U, V = np.meshgrid(u, v)

        # Ecuaciones parametricas del elipsoide
        X = a * np.cos(V) * np.cos(U)
        Y = b * np.cos(V) * np.sin(U)
        Z = c * np.sin(V)

        X, Y, Z = self.transformar(X, Y, Z)

        self.ax.plot_surface(
            X, Y, Z,
            color=COLORES["Elipsoide"],
            edgecolor="#D9FFF0",
            linewidth=0.25,
            alpha=0.88,
            rstride=3,
            cstride=3
        )

        centro = [
            self.valores["x"],
            self.valores["y"],
            self.valores["z"]
        ]

        self.ax.scatter(*centro, color="red", s=35)

        # Aproximacion de Knud Thomsen
        p = 1.6075

        area = 4 * np.pi * (
            (
                (a*b)**p +
                (a*c)**p +
                (b*c)**p
            ) / 3
        )**(1/p)

        volumen = (4 / 3) * np.pi * a * b * c

        return {
            "Radio X": a,
            "Radio Y": b,
            "Radio Z": c,
            "Área aproximada": area,
            "Volumen": volumen,
            "Fórmula del volumen": "4/3 π abc",
            "Área": "Aproximación de Knud Thomsen"
        }, max(a, b, c)


    # ========================================================
    # 13. CONSTRUIR PRISMA REGULAR
    # ========================================================

    def dibujar_prisma(self):

        n = int(self.valores["n"])
        radio = self.valores["rp"]
        altura = self.valores["h"]

        angulos = np.linspace(
            0, 2 * np.pi, n, endpoint=False
        )

        # Coordenadas de los vertices de las bases
        x = radio * np.cos(angulos)
        y = radio * np.sin(angulos)

        z_inferior = np.full(n, -altura / 2)
        z_superior = np.full(n, altura / 2)

        xi, yi, zi = self.transformar(
            x, y, z_inferior
        )

        xs, ys, zs = self.transformar(
            x, y, z_superior
        )

        base_inferior = np.column_stack((xi, yi, zi))
        base_superior = np.column_stack((xs, ys, zs))

        caras = [
            base_inferior.tolist(),
            base_superior.tolist()
        ]

        # Construir cada cara lateral
        for i in range(n):

            j = (i + 1) % n

            cara = [
                base_inferior[i],
                base_inferior[j],
                base_superior[j],
                base_superior[i]
            ]

            caras.append(cara)

        coleccion = Poly3DCollection(
            caras,
            facecolors=COLORES["Prisma"],
            edgecolors="#FFF1D6",
            linewidths=1.2,
            alpha=0.85
        )

        self.ax.add_collection3d(coleccion)

        # Mostrar vertices
        vertices = np.vstack((
            base_inferior,
            base_superior
        ))

        self.ax.scatter(
            vertices[:, 0],
            vertices[:, 1],
            vertices[:, 2],
            color="white",
            s=18
        )

        # Calculos geometricos del prisma regular
        lado = 2 * radio * np.sin(np.pi / n)

        perimetro = n * lado

        apotema = radio * np.cos(np.pi / n)

        area_base = (
            perimetro * apotema / 2
        )

        area_lateral = perimetro * altura

        area_total = (
            2 * area_base + area_lateral
        )

        volumen = area_base * altura

        return {
            "Lados de la base": n,
            "Radio de la base": radio,
            "Altura": altura,
            "Lado del polígono": lado,
            "Apotema": apotema,
            "Perímetro de base": perimetro,
            "Área de una base": area_base,
            "Área lateral": area_lateral,
            "Área total": area_total,
            "Volumen": volumen,
            "Fórmula del volumen": "Área base × altura"
        }, max(radio, altura / 2)


    # ========================================================
    # 14. CONFIGURACION DE EJES
    # ========================================================

    def configurar_ejes(self, centro, extension):

        extension = max(extension * 1.5, 1.5)

        self.ax.set_xlim(
            centro[0] - extension,
            centro[0] + extension
        )

        self.ax.set_ylim(
            centro[1] - extension,
            centro[1] + extension
        )

        self.ax.set_zlim(
            centro[2] - extension,
            centro[2] + extension
        )

        self.ax.set_box_aspect((1, 1, 1))

        self.ax.set_xlabel("X", color=TEXTO, labelpad=8)
        self.ax.set_ylabel("Y", color=TEXTO, labelpad=8)
        self.ax.set_zlabel("Z", color=TEXTO, labelpad=8)

        self.ax.tick_params(
            colors=SECUNDARIO,
            labelsize=8
        )

        self.ax.set_facecolor(FONDO)

        self.ax.xaxis.pane.set_facecolor(PANEL)
        self.ax.yaxis.pane.set_facecolor(PANEL)
        self.ax.zaxis.pane.set_facecolor(PANEL)

        self.ax.grid(True, alpha=0.20)

        self.ax.view_init(
            elev=25,
            azim=40
        )


    # ========================================================
    # 15. MOSTRAR RESULTADOS
    # ========================================================

    def mostrar_resultados(self, datos):

        self.texto_resultados.configure(state="normal")
        self.texto_resultados.delete("1.0", tk.END)

        for nombre, valor in datos.items():

            if isinstance(valor, (int, float, np.number)):

                linea = f"{nombre}\n{valor:,.3f}\n\n"

            else:

                linea = f"{nombre}\n{valor}\n\n"

            self.texto_resultados.insert(
                tk.END,
                linea
            )

        self.texto_resultados.configure(state="disabled")


    # ========================================================
    # 16. ACTUALIZAR TODO EL PROGRAMA
    # ========================================================

    def actualizar(self):

        self.actualizacion_pendiente = None

        self.ax.clear()

        figura = self.figura.get()

        centro = (
            self.valores.get("x", 0),
            self.valores.get("y", 0),
            self.valores.get("z", 0)
        )

        if figura == "Esfera":

            datos, extension = self.dibujar_esfera()

        elif figura == "Elipsoide":

            datos, extension = self.dibujar_elipsoide()

        else:

            datos, extension = self.dibujar_prisma()

        self.ax.set_title(
            figura.upper(),
            color=TEXTO,
            fontsize=15,
            pad=18,
            fontweight="bold"
        )

        self.configurar_ejes(centro, extension)

        self.mostrar_resultados(datos)

        self.canvas_grafica.draw_idle()


    # ========================================================
    # 17. RESTABLECER PARAMETROS
    # ========================================================

    def restablecer(self):

        parametros = self.obtener_parametros(
            self.figura.get()
        )

        for etiqueta, clave, minimo, maximo, inicial, paso in parametros:

            self.sliders[clave].set(inicial)


# ============================================================
# 18. EJECUTAR APLICACION
# ============================================================

if __name__ == "__main__":

    ventana = tk.Tk()

    aplicacion = Geometria3D(ventana)

    ventana.mainloop()
