
import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class Geometry3D:

    def __init__(self, root):
        self.root = root
        self.root.title("GEOMETRY 3D")
        self.root.geometry("1200x780")
        self.root.configure(bg="#edf1f5")

        self.entries = {}

        # Parámetros específicos de cada figura
        self.figuras = {
            "Elipsoide": [
                ("Semieje X (a)", "5"),
                ("Semieje Y (b)", "3"),
                ("Semieje Z (c)", "4"),
                ("Centro X (h)", "0"),
                ("Centro Y (k)", "0"),
                ("Centro Z (l)", "0")
            ],

            "Esfera": [
                ("Radio (r)", "5"),
                ("Centro X (h)", "0"),
                ("Centro Y (k)", "0"),
                ("Centro Z (l)", "0")
            ],

            "Paraboloide": [
                ("Escala X (a)", "2"),
                ("Escala Y (b)", "2"),
                ("Altura (c)", "5")
            ],

            "Hiperboloide de 1 hoja": [
                ("Semieje X (a)", "3"),
                ("Semieje Y (b)", "3"),
                ("Semieje Z (c)", "2")
            ],

            "Hiperboloide de 2 hojas": [
                ("Semieje X (a)", "3"),
                ("Semieje Y (b)", "3"),
                ("Semieje Z (c)", "2")
            ],

            "Cono": [
                ("Radio X (a)", "4"),
                ("Radio Y (b)", "4"),
                ("Altura (c)", "5")
            ],

            "Cilindro": [
                ("Radio (r)", "3"),
                ("Altura (h)", "6")
            ]
        }

        # Encabezado
        header = tk.Frame(root, bg="#172b4d")
        header.pack(fill="x")

        tk.Label(
            header,
            text="GEOMETRY 3D - EDITOR MATEMÁTICO",
            font=("Arial", 20, "bold"),
            bg="#172b4d",
            fg="white"
        ).pack(pady=18)

        main = tk.Frame(root, bg="#edf1f5")
        main.pack(fill="both", expand=True, padx=15, pady=15)

        # Panel izquierdo
        panel = tk.Frame(main, bg="white", width=300)
        panel.pack(side="left", fill="y", padx=(0, 15))
        panel.pack_propagate(False)

        tk.Label(
            panel,
            text="SELECCIONAR FIGURA",
            font=("Arial", 12, "bold"),
            bg="white"
        ).pack(pady=15)

        self.shape = tk.StringVar(value="Elipsoide")

        selector = ttk.Combobox(
            panel,
            textvariable=self.shape,
            values=list(self.figuras.keys()),
            state="readonly"
        )
        selector.pack(fill="x", padx=20)

        selector.bind(
            "<<ComboboxSelected>>",
            lambda event: self.crear_campos()
        )

        tk.Label(
            panel,
            text="PARÁMETROS EDITABLES",
            font=("Arial", 12, "bold"),
            bg="white"
        ).pack(pady=15)

        # Contenedor de parámetros dinámicos
        self.campos_frame = tk.Frame(panel, bg="white")
        self.campos_frame.pack(fill="x")

        self.crear_campos()

        # Color
        tk.Label(
            panel,
            text="Color de superficie",
            bg="white"
        ).pack(pady=(20, 5))

        self.color = tk.StringVar(value="viridis")

        ttk.Combobox(
            panel,
            textvariable=self.color,
            values=["viridis", "plasma", "cool", "turbo"],
            state="readonly"
        ).pack(fill="x", padx=20)

        ttk.Button(
            panel,
            text="GRAFICAR",
            command=self.graficar
        ).pack(fill="x", padx=20, pady=20)

        # Área gráfica
        graph = tk.Frame(main, bg="white")
        graph.pack(side="right", fill="both", expand=True)

        self.fig = Figure(figsize=(8, 7), dpi=100)
        self.ax = self.fig.add_subplot(111, projection="3d")

        self.canvas = FigureCanvasTkAgg(
            self.fig,
            master=graph
        )

        self.canvas.get_tk_widget().pack(
            fill="both", expand=True
        )

        self.graficar()

    def crear_campos(self):

        # Eliminar campos anteriores
        for widget in self.campos_frame.winfo_children():
            widget.destroy()

        self.entries = {}

        # Crear los nuevos campos
        parametros = self.figuras[self.shape.get()]

        for nombre, valor in parametros:

            tk.Label(
                self.campos_frame,
                text=nombre,
                bg="white",
                anchor="w"
            ).pack(fill="x", padx=20, pady=(7, 2))

            entrada = ttk.Entry(self.campos_frame)
            entrada.insert(0, valor)
            entrada.pack(fill="x", padx=20, pady=3)

            self.entries[nombre] = entrada

    def obtener(self, nombre):

        return float(self.entries[nombre].get())

    def graficar(self):

        try:

            figura = self.shape.get()

            p = {
                nombre: self.obtener(nombre)
                for nombre in self.entries
            }

            if any(valor <= 0 for nombre, valor in p.items()
                   if not nombre.startswith("Centro")):
                raise ValueError("Las dimensiones deben ser positivas.")

            u = np.linspace(0, 2*np.pi, 100)
            v = np.linspace(-1, 1, 100)
            U, V = np.meshgrid(u, v)

            self.ax.clear()

            if figura == "Elipsoide":

                a = p["Semieje X (a)"]
                b = p["Semieje Y (b)"]
                c = p["Semieje Z (c)"]

                X = a*np.cos(U)*np.sqrt(1-V**2)
                Y = b*np.sin(U)*np.sqrt(1-V**2)
                Z = c*V

                X += p["Centro X (h)"]
                Y += p["Centro Y (k)"]
                Z += p["Centro Z (l)"]

            elif figura == "Esfera":

                r = p["Radio (r)"]

                X = r*np.cos(U)*np.sqrt(1-V**2)
                Y = r*np.sin(U)*np.sqrt(1-V**2)
                Z = r*V

                X += p["Centro X (h)"]
                Y += p["Centro Y (k)"]
                Z += p["Centro Z (l)"]

                a = b = c = r

            elif figura == "Paraboloide":

                a = p["Escala X (a)"]
                b = p["Escala Y (b)"]
                c = p["Altura (c)"]

                R = (V+1)/2

                X = a*R*np.cos(U)
                Y = b*R*np.sin(U)
                Z = c*R**2

            elif figura == "Hiperboloide de 1 hoja":

                a = p["Semieje X (a)"]
                b = p["Semieje Y (b)"]
                c = p["Semieje Z (c)"]

                W = np.linspace(-1.5, 1.5, 100)
                U, W = np.meshgrid(u, W)

                X = a*np.cosh(W)*np.cos(U)
                Y = b*np.cosh(W)*np.sin(U)
                Z = c*np.sinh(W)

            elif figura == "Hiperboloide de 2 hojas":

                a = p["Semieje X (a)"]
                b = p["Semieje Y (b)"]
                c = p["Semieje Z (c)"]

                W = np.linspace(0, 1.5, 100)
                U, W = np.meshgrid(u, W)

                X = a*np.sinh(W)*np.cos(U)
                Y = b*np.sinh(W)*np.sin(U)
                Z = c*np.cosh(W)

                self.ax.plot_surface(
                    X, Y, Z, cmap=self.color.get()
                )
                self.ax.plot_surface(
                    X, Y, -Z, cmap=self.color.get()
                )

                self.terminar(a, b, c)
                return

            elif figura == "Cono":

                a = p["Radio X (a)"]
                b = p["Radio Y (b)"]
                c = p["Altura (c)"]

                R = (V+1)/2

                X = a*R*np.cos(U)
                Y = b*R*np.sin(U)
                Z = c*V

            elif figura == "Cilindro":

                r = p["Radio (r)"]
                h = p["Altura (h)"]

                X = r*np.cos(U)
                Y = r*np.sin(U)
                Z = h*V/2

                a = b = r
                c = h/2

            self.ax.plot_surface(
                X, Y, Z,
                cmap=self.color.get(),
                alpha=0.85,
                edgecolor="none"
            )

            self.terminar(a, b, c)

        except ValueError as error:
            messagebox.showerror("Error de parámetros", str(error))

    def terminar(self, a, b, c):

        self.ax.set_title(self.shape.get())
        self.ax.set_xlabel("Eje X")
        self.ax.set_ylabel("Eje Y")
        self.ax.set_zlabel("Eje Z")

        self.ax.set_box_aspect((a, b, c))
        self.canvas.draw()


if __name__ == "__main__":

    root = tk.Tk()
    app = Geometry3D(root)
    root.mainloop()
