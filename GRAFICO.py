import math
import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import numpy as np


class AppGraficador3D:

    def __init__(self, root):
        self.root = root
        self.root.title("Graficador 3D Interactiva con Parámetros")
        self.root.geometry("1100x750")

        # --- Panel Principal (Izquierda: Controles / Derecha: Gráfica) ---
        frame_izquierdo = ttk.Frame(self.root, padding=10)
        frame_izquierdo.pack(side=tk.LEFT, fill=tk.Y)

        frame_derecho = ttk.Frame(self.root)
        frame_derecho.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # -------------------------------------------------------------
        # SECCIÓN 1: Selección de Función y Campo de Entrada
        # -------------------------------------------------------------
        lbl_frame_fun = ttk.LabelFrame(
            frame_izquierdo, text=" Configuración de la Función ", padding=10
        )
        lbl_frame_fun.pack(fill=tk.X, pady=5)

        ttk.Label(lbl_frame_fun, text="Elegir Preset:").pack(
            anchor=tk.W, pady=2
        )

        self.funciones_preset = {
            "Paraboloide: a*x^2 + b*y^2 + c": "a*x**2 + b*y**2 + c",
            "Silla de Montar: a*x^2 - b*y^2": "a*x**2 - b*y**2",
            "Ondas / Sombrero: c * sin(sqrt(a*x^2 + b*y^2))": "c * np.sin(np.sqrt(a*x**2 + b*y**2))",
            "Seno/Coseno: c * sin(a*x) * cos(b*y)": "c * np.sin(a*x) * np.cos(b*y)",
            "Plano: a*x + b*y + c": "a*x + b*y + c",
            "Personalizada (usar a, b, c)": "custom",
        }

        self.combo_opciones = ttk.Combobox(
            lbl_frame_fun,
            values=list(self.funciones_preset.keys()),
            state="readonly",
            width=35,
        )
        self.combo_opciones.current(0)
        self.combo_opciones.pack(fill=tk.X, pady=5)
        self.combo_opciones.bind("<<ComboboxSelected>>", self.actualizar_campo)

        ttk.Label(
            lbl_frame_fun, text="Fórmula z = f(x, y, a, b, c):"
        ).pack(anchor=tk.W, pady=2)
        self.entry_funcion = ttk.Entry(lbl_frame_fun, width=37)
        self.entry_funcion.insert(0, "a*x**2 + b*y**2 + c")
        self.entry_funcion.pack(fill=tk.X, pady=5)

        # -------------------------------------------------------------
        # SECCIÓN 2: Deslizadores de Parámetros (a, b, c)
        # -------------------------------------------------------------
        lbl_frame_params = ttk.LabelFrame(
            frame_izquierdo, text=" Parámetros Dinámicos ", padding=10
        )
        lbl_frame_params.pack(fill=tk.X, pady=10)

        # Parámetro a
        self.val_a = tk.DoubleVar(value=1.0)
        self.crear_slider(lbl_frame_params, "Parámetro a:", self.val_a, -5.0, 5.0)

        # Parámetro b
        self.val_b = tk.DoubleVar(value=1.0)
        self.crear_slider(lbl_frame_params, "Parámetro b:", self.val_b, -5.0, 5.0)

        # Parámetro c
        self.val_c = tk.DoubleVar(value=0.0)
        self.crear_slider(lbl_frame_params, "Parámetro c:", self.val_c, -5.0, 5.0)

        # -------------------------------------------------------------
        # SECCIÓN 3: Configuración del Dominio (Rango x, y) y Resolución
        # -------------------------------------------------------------
        lbl_frame_rango = ttk.LabelFrame(
            frame_izquierdo, text=" Dominio y Resolución ", padding=10
        )
        lbl_frame_rango.pack(fill=tk.X, pady=5)

        self.val_rango = tk.DoubleVar(value=5.0)
        self.crear_slider(
            lbl_frame_rango, "Rango [-L, L]:", self.val_rango, 1.0, 20.0, es_int=False
        )

        self.val_res = tk.IntVar(value=60)
        self.crear_slider(
            lbl_frame_rango, "Resolución (malla):", self.val_res, 20, 120, es_int=True
        )

        # Botón para actualizar manualmente
        btn_graficar = ttk.Button(
            frame_izquierdo, text="Re-Graficar", command=self.graficar
        )
        btn_graficar.pack(fill=tk.X, pady=10)

        # -------------------------------------------------------------
        # SECCIÓN 4: Área de la Gráfica 3D (Matplotlib)
        # -------------------------------------------------------------
        self.fig = plt.Figure(figsize=(6, 5), dpi=100)
        self.ax = self.fig.add_subplot(111, projection="3d")

        self.canvas = FigureCanvasTkAgg(self.fig, master=frame_derecho)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        toolbar = NavigationToolbar2Tk(self.canvas, frame_derecho)
        toolbar.update()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Graficar por primera vez
        self.graficar()

    def crear_slider(self, parent, label_text, variable, min_v, max_v, es_int=False):
        """Crea un slider con etiqueta descriptiva y valor numérico."""
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=3)

        ttk.Label(frame, text=label_text).pack(side=tk.LEFT)
        val_label = ttk.Label(
            frame, text=f"{variable.get():.2f}" if not es_int else f"{variable.get()}"
        )
        val_label.pack(side=tk.RIGHT)

        def al_cambiar(v):
            val = float(v)
            if es_int:
                variable.set(int(val))
                val_label.config(text=f"{int(val)}")
            else:
                variable.set(round(val, 2))
                val_label.config(text=f"{val:.2f}")
            self.graficar()

        slider = ttk.Scale(
            parent,
            from_=min_v,
            to=max_v,
            value=variable.get(),
            command=al_cambiar,
        )
        slider.pack(fill=tk.X, pady=(0, 5))

    def actualizar_campo(self, event):
        seleccion = self.combo_opciones.get()
        expr = self.funciones_preset[seleccion]

        if expr != "custom":
            self.entry_funcion.delete(0, tk.END)
            self.entry_funcion.insert(0, expr)
            self.graficar()

    def graficar(self):
        expr_str = self.entry_funcion.get()

        # Obtener valores actuales de parámetros y dominio
        a = self.val_a.get()
        b = self.val_b.get()
        c = self.val_c.get()
        limite = self.val_rango.get()
        num_puntos = self.val_res.get()

        # Generar malla 3D (X, Y)
        x = np.linspace(-limite, limite, num_puntos)
        y = np.linspace(-limite, limite, num_puntos)
        X, Y = np.meshgrid(x, y)

        # Entorno de variables para evaluar
        entorno_evaluacion = {
            "x": X,
            "y": Y,
            "X": X,
            "Y": Y,
            "a": a,
            "b": b,
            "c": c,
            "np": np,
            "sin": np.sin,
            "cos": np.cos,
            "tan": np.tan,
            "sqrt": np.sqrt,
            "exp": np.exp,
            "pi": np.pi,
            "abs": np.abs,
        }

        try:
            # Evaluar la función en la malla
            Z = eval(expr_str, {"__builtins__": None}, entorno_evaluacion)

            # Preservar el ángulo de visión actual de la cámara al redibujar
            elev = self.ax.elev
            azim = self.ax.azim

            # Limpiar la escena 3D anterior
            self.ax.clear()

            # Dibujar la superficie
            surf = self.ax.plot_surface(
                X, Y, Z, cmap="viridis", edgecolor="none", alpha=0.88
            )

            # Restaurar ángulo de cámara
            if elev is not None and azim is not None:
                self.ax.view_init(elev=elev, azim=azim)

            # Ajustar títulos y etiquetas
            self.ax.set_title(f"z = {expr_str}", fontsize=11)
            self.ax.set_xlabel("Eje X")
            self.ax.set_ylabel("Eje Y")
            self.ax.set_zlabel("Eje Z")

            # Redibujar canvas
            self.canvas.draw_idle()

        except Exception:
            # Ignorar errores mientras el usuario edita la fórmula activa
            pass


if __name__ == "__main__":
    root = tk.Tk()
    app = AppGraficador3D(root)
    root.mainloop()