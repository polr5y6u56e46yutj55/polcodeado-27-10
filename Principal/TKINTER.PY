# app_farmacia_tkinter.py

import tkinter as tk
from tkinter import ttk, messagebox
import sys
from io import StringIO
from CODE import FarmaciaManager # Importamos la clase principal
from datetime import datetime # Necesario para simular datos de entrada

# --- CLASE PRINCIPAL DE LA INTERFAZ GRÁFICA ---

class FarmaciaApp(tk.Tk):
    """Interfaz gráfica para gestionar las funcionalidades de FarmaciaManager."""

    def __init__(self):
        super().__init__()
        self.title("Sistema de Gestión Farmacia - Tkinter")
        self.geometry("800x600")
        
        # Inicializa el Manager (que conecta con la BD y estructuras de datos)
        try:
            self.manager = FarmaciaManager()
            self.manager_status = True
        except Exception as e:
            messagebox.showerror("Error de Conexión", 
                                 f"No se pudo conectar a la base de datos 'farmacy'. Verifique las credenciales y el servidor. Detalle: {e}")
            self.manager_status = False
            self.destroy() # Cierra la app si la conexión falla

        if self.manager_status:
            self._crear_widgets()
    
    def _crear_widgets(self):
        """Configura el layout de la interfaz con pestañas."""
        
        # Notebook (Pestañas)
        notebook = ttk.Notebook(self)
        notebook.pack(pady=10, padx=10, fill="both", expand=True)

        # --- Pestaña 1: Búsqueda y Venta ---
        frame_venta = ttk.Frame(notebook)
        notebook.add(frame_venta, text="💊 Venta y Stock")
        self._crear_frame_venta(frame_venta)

        # --- Pestaña 2: Pedidos y Reportes ---
        frame_reportes = ttk.Frame(notebook)
        notebook.add(frame_reportes, text="📈 Reportes y Gestión")
        self._crear_frame_reportes(frame_reportes)

    # -----------------------------------------------
    # PESTAÑA 1: VENTA Y STOCK
    # -----------------------------------------------
    def _crear_frame_venta(self, parent_frame):
        """Crea el panel de búsqueda y registro de ventas."""
        
        # --- SECCIÓN 1: BÚSQUEDA (Tabla Hash) ---
        
        # Etiquetas y Campos de Búsqueda
        lbl_buscar = ttk.Label(parent_frame, text="1. Búsqueda Rápida (Código de Barras):", font=("Arial", 10, "bold"))
        lbl_buscar.grid(row=0, column=0, columnspan=2, pady=(10, 5), padx=10, sticky="w")
        
        self.entry_codigo_buscar = ttk.Entry(parent_frame, width=30)
        self.entry_codigo_buscar.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        
        btn_buscar = ttk.Button(parent_frame, text="Buscar (O(1))", command=self._ejecutar_busqueda)
        btn_buscar.grid(row=1, column=1, padx=10, pady=5, sticky="w")
        
        # Área de Resultados de Búsqueda
        self.txt_resultado_busqueda = tk.Text(parent_frame, height=5, width=75, state='disabled')
        self.txt_resultado_busqueda.grid(row=2, column=0, columnspan=2, padx=10, pady=5)
        
        # Separador
        ttk.Separator(parent_frame, orient='horizontal').grid(row=3, column=0, columnspan=2, sticky='ew', pady=10)

        # --- SECCIÓN 2: REGISTRO DE VENTA (Transacción + Grafo) ---
        
        lbl_venta = ttk.Label(parent_frame, text="2. Registrar Venta:", font=("Arial", 10, "bold"))
        lbl_venta.grid(row=4, column=0, columnspan=2, pady=(10, 5), padx=10, sticky="w")

        # Campos de Entrada para la Venta
        labels = ["Código de Barras:", "ID Cliente (Ej. 1):", "ID Empleado (Ej. 1):", "Cantidad Vendida:"]
        self.entries_venta = {}
        for i, text in enumerate(labels):
            ttk.Label(parent_frame, text=text).grid(row=5 + i, column=0, padx=10, pady=2, sticky="w")
            entry = ttk.Entry(parent_frame, width=20)
            entry.grid(row=5 + i, column=1, padx=10, pady=2, sticky="w")
            self.entries_venta[text.split('(')[0].strip()] = entry
            
        btn_venta = ttk.Button(parent_frame, text="Registrar Venta", command=self._ejecutar_venta)
        btn_venta.grid(row=9, column=0, columnspan=2, pady=15)
        
    def _ejecutar_busqueda(self):
        """Llama al método buscar_medicamento del Manager."""
        codigo = self.entry_codigo_buscar.get().strip()
        
        self.txt_resultado_busqueda.config(state='normal')
        self.txt_resultado_busqueda.delete(1.0, tk.END)
        
        # Redirigir la salida de print() temporalmente para capturar la info
        original_stdout = sys.stdout
        sys.stdout = capture_output = StringIO()
        
        self.manager.buscar_medicamento(codigo)
        
        sys.stdout = original_stdout # Restaurar stdout
        
        # Limpiar y mostrar el resultado
        resultado_texto = capture_output.getvalue().strip()
        self.txt_resultado_busqueda.insert(tk.END, resultado_texto)
        self.txt_resultado_busqueda.config(state='disabled')
        
        if "Encontrado por Hash" not in resultado_texto:
             messagebox.showwarning("Advertencia", "Medicamento no encontrado.")

    def _ejecutar_venta(self):
        """Recoge datos y llama al método registrar_venta del Manager."""
        
        try:
            codigo = self.entries_venta["Código de Barras:"].get().strip()
            id_cliente = int(self.entries_venta["ID Cliente"].get().strip())
            id_empleado = int(self.entries_venta["ID Empleado"].get().strip())
            cantidad = int(self.entries_venta["Cantidad Vendida:"].get().strip())
            
            if not codigo or cantidad <= 0:
                raise ValueError("Verifique los campos de entrada.")

            # Redirigir la salida de print() temporalmente
            original_stdout = sys.stdout
            sys.stdout = capture_output = StringIO()
            
            self.manager.registrar_venta(codigo, id_cliente, id_empleado, cantidad)
            
            sys.stdout = original_stdout # Restaurar stdout
            
            resultado_texto = capture_output.getvalue().strip()
            
            # Mostrar el resultado de la venta (incluyendo alertas de Grafo o Stock)
            if "❌ Error" in resultado_texto:
                messagebox.showerror("Error de Venta", resultado_texto)
            else:
                messagebox.showinfo("Venta Exitosa", resultado_texto)

            # Opcional: limpiar los campos después de una venta exitosa
            for entry in self.entries_venta.values():
                 entry.delete(0, tk.END)
                 
        except ValueError as e:
            messagebox.showerror("Error de Datos", f"Datos inválidos: {e}. Asegúrese de que ID y Cantidad sean números enteros.")
        except Exception as e:
            messagebox.showerror("Error de Ejecución", f"Ocurrió un error inesperado: {e}")


    # -----------------------------------------------
    # PESTAÑA 2: REPORTES Y GESTIÓN
    # -----------------------------------------------

    def _crear_frame_reportes(self, parent_frame):
        """Crea el panel de reportes y gestión de pedidos."""
        
        # Configuración de pesos para centrar
        parent_frame.columnconfigure(0, weight=1)
        parent_frame.columnconfigure(1, weight=1)

        # --- SECCIÓN 1: BOTONES DE ACCIÓN ---
        frame_acciones = ttk.Frame(parent_frame)
        frame_acciones.grid(row=0, column=0, columnspan=2, pady=10, padx=10, sticky="n")

        btn_urgentes = ttk.Button(frame_acciones, text="Atender Pedido Urgente (Cola Prioritaria)", 
                                  command=lambda: self._ejecutar_reporte(self.manager.gestionar_pedidos_urgentes))
        btn_urgentes.pack(side=tk.LEFT, padx=10)

        btn_reporte_ventas = ttk.Button(frame_acciones, text="Reporte: Ventas por Empleado", 
                                  command=lambda: self._ejecutar_reporte(self.manager.ventas_por_empleado))
        btn_reporte_ventas.pack(side=tk.LEFT, padx=10)

        btn_reporte_vencimiento = ttk.Button(frame_acciones, text="Reporte: Stock Crítico / Vencimiento", 
                                  command=lambda: self._ejecutar_reporte(self.manager.medicamentos_proximos_a_vencer))
        btn_reporte_vencimiento.pack(side=tk.LEFT, padx=10)

        # Botón nuevo: Stock por categoría
        btn_stock_cat = ttk.Button(frame_acciones, text="📊 Stock por Categoría (NUEVO)", 
                                    command=lambda: self._ejecutar_reporte(self.manager.reporte_stock_por_categoria))
        btn_stock_cat.pack(side=tk.LEFT, padx=10)

        # --- SECCIÓN 2: VISUALIZACIÓN DE RESULTADOS ---
        lbl_resultado_reporte = ttk.Label(parent_frame, text="Resultados de la Operación/Reporte:", font=("Arial", 10, "bold"))
        lbl_resultado_reporte.grid(row=1, column=0, columnspan=2, pady=(20, 5), padx=10, sticky="w")

        self.txt_resultado_reporte = tk.Text(parent_frame, height=20, width=95, state='disabled')
        self.txt_resultado_reporte.grid(row=2, column=0, columnspan=2, padx=10, pady=5)

        
    def _ejecutar_reporte(self, funcion_manager):
        """Ejecuta una función del manager y muestra el resultado en el Text widget."""
        
        self.txt_resultado_reporte.config(state='normal')
        self.txt_resultado_reporte.delete(1.0, tk.END)
        
        # Redirigir la salida de print() temporalmente
        original_stdout = sys.stdout
        sys.stdout = capture_output = StringIO()
        
        # Ejecutar la función (puede ser un reporte o atender pedidos)
        resultado = funcion_manager()
        
        sys.stdout = original_stdout # Restaurar stdout
        
        # Si la función retornó algo (como gestionar_pedidos_urgentes), úselo.
        # Si es un reporte (ventas_por_empleado), el resultado está en stdout (capture_output).
        
        if isinstance(resultado, str):
            resultado_texto = resultado + "\n" + capture_output.getvalue().strip()
        else:
             resultado_texto = capture_output.getvalue().strip()
        
        self.txt_resultado_reporte.insert(tk.END, resultado_texto)
        self.txt_resultado_reporte.config(state='disabled')


# --- EJECUCIÓN ---
if __name__ == "__main__":
    app = FarmaciaApp()
    if app.manager_status:
        app.mainloop()