import mysql.connector
from mysql.connector import Error
from datetime import datetime, timedelta
import heapq
import sys
# -----------------------------------------------------------------------
# I. CLASES DE ESTRUCTURAS DE DATOS Y OBJETOS (Requisito 2)
# -----------------------------------------------------------------------

class Medicamento:
    """Objeto de dominio para representar un medicamento."""
    # Los nombres de parámetros coinciden con los alias usados en la SELECT de la BD.
    def __init__(self, Id, Nombre, Categoria, Precio, Stock, Codigo_Barras):
        self.id = Id                                                            
        self.nombre = Nombre
        self.categoria = Categoria
        self.precio = Precio # Corresponde a la columna 'Precio' de la BD
        self.stock = Stock
        self.codigo_barras = Codigo_Barras
    def __str__(self):
        return f"[{self.codigo_barras}] {self.nombre} ({self.categoria}) | Stock: {self.stock} | Precio: ${self.precio:.2f}"

# --- 1. Tabla Hash (Búsqueda en O(1)) ---
class TablaHashMedicamentos:
    """Tabla Hash para búsqueda O(1) por código de barras."""
    def __init__(self):
        # Key: codigo_barras (str), Value: Objeto Medicamento
        self.hash_table = {} 

    def insertar(self, medicamento: Medicamento):
        """Inserta o actualiza un medicamento."""
        self.hash_table[medicamento.codigo_barras] = medicamento

    def buscar(self, codigo_barras: str) -> Medicamento:
        """Busca en O(1)."""
        return self.hash_table.get(codigo_barras)

# --- 2. Árbol para Categorías (Filtros rápidos) ---
class ArbolCategorias:
    """Estructura tipo Diccionario para simular un Árbol, agrupando por categoría."""
    def __init__(self):
        # Key: categoria (str), Value: Lista de objetos Medicamento
        self.categorias = {} 

    def insertar(self, medicamento: Medicamento):
        """Inserta un medicamento y mantiene la lista de su categoría sincronizada."""
        categoria = medicamento.categoria
        self.categorias.setdefault(categoria, [])
        
        # Elimina la versión antigua del medicamento para actualizar
        self.categorias[categoria] = [m for m in self.categorias[categoria] if m.id != medicamento.id]
        self.categorias[categoria].append(medicamento)
        
    def buscar_por_categoria(self, categoria: str) -> list[Medicamento]:
        """Devuelve todos los medicamentos de una categoría."""
        return self.categorias.get(categoria, [])

# --- 3. Cola Prioritaria (Pedidos Urgentes) ---
class ColaPrioritariaPedidos:
    """Gestiona pedidos urgentes usando un Min-Heap (heapq)."""
    def __init__(self):
        # Formato: (prioridad, ID_Medicamento, cantidad_solicitada)
        self.cola = [] 

    def agregar_pedido(self, prioridad: int, id_medicamento: int, cantidad: int):
        """Agrega un pedido a la cola (menor número de prioridad = más urgente)."""
        heapq.heappush(self.cola, (prioridad, id_medicamento, cantidad))

    def atender_pedido_urgente(self):
        """Extrae y atiende el pedido de mayor prioridad."""
        if self.cola:
            prioridad, id_medicamento, cantidad = heapq.heappop(self.cola)
            return f"✅ Pedido Urgente Atendido: Prioridad {prioridad}, ID Medicamento {id_medicamento}, Cantidad solicitada: {cantidad}"
        return "No hay pedidos pendientes."

# --- 4. Grafo (Contraindicaciones) ---
class GrafoContraindicaciones:
    """Grafo de Lista de Adyacencia para alertar interacciones medicamentosas."""
    def __init__(self):
        self.grafo = {}

    def agregar_contraindicacion(self, id_med1: int, id_med2: int, descripcion: str):
        """Agrega una arista de contraindicación (bidireccional)."""
        self.grafo.setdefault(id_med1, [])
        self.grafo.setdefault(id_med2, [])
        self._agregar_arista_simple(id_med1, id_med2, descripcion)
        self._agregar_arista_simple(id_med2, id_med1, descripcion)

    def _agregar_arista_simple(self, u, v, desc):
        if not any(item[0] == v for item in self.grafo[u]):
            self.grafo[u].append((v, desc))

    def verificar_contraindicacion(self, id_med1: int, id_med2: int) -> str:
        """Verifica la conexión (contraindicación) entre dos medicamentos (Simulación)."""
        # Se simula una contraindicación de ejemplo (Paracetamol ID 1 vs Omeprazol ID 5)
        if (id_med1, id_med2) == (1, 5) or (id_med1, id_med2) == (5, 1):
             return f"⚠️ **ALERTA DE CONTRAINDICACIÓN** entre Medicamento ID {id_med1} y ID {id_med2}: La combinación puede causar toxicidad hepática."
        return "✅ Sin contraindicaciones directas conocidas entre estos medicamentos."

# -----------------------------------------------------------------------
# II. CLASE PRINCIPAL DE GESTIÓN (Requisito 3 - Integración)
# -----------------------------------------------------------------------

class FarmaciaManager:
    """Clase principal que integra MySQL y las Estructuras de Datos."""
    
    # ⚠️ AJUSTAR ESTAS CREDENCIALES ⚠️
    DB_CONFIG = {
        'host': 'localhost',
        'user': 'root', 
        'password': '', 
        'database': 'farmacy' # Base de datos del schema final
    }

    def __init__(self):
        self.hash_medicamentos = TablaHashMedicamentos()
        self.arbol_categorias = ArbolCategorias()
        self.cola_pedidos = ColaPrioritariaPedidos()
        self.grafo_contraindicaciones = GrafoContraindicaciones()
        
        self.conexion = None
        self.cargar_datos_iniciales()
        
    # --- Métodos de Conexión y Transacción a BD ---
    
    def _conectar(self):
        """Establece la conexión a la base de datos."""
        try:
            self.conexion = mysql.connector.connect(**self.DB_CONFIG)
            return self.conexion.cursor(dictionary=True) 
        except Error as e:
            print(f"❌ Error fatal al conectar a MySQL. Verifique las credenciales y el servidor: {e}")
            return None

    def _ejecutar_consulta(self, query, params=None, fetch_all=False):
        """Ejecuta una consulta SQL genérica (SELECT/INSERT/UPDATE/DELETE)."""
        cursor = self._conectar()
        if not cursor: return [] if fetch_all else None
        
        try:
            cursor.execute(query, params or ())
            
            if query.strip().upper().startswith(('INSERT', 'UPDATE', 'DELETE')):
                self.conexion.commit()
                # Retorna ID para INSERT, o True para UPDATE/DELETE
                return cursor.lastrowid if 'INSERT INTO' in query.upper() else True
            elif fetch_all:
                return cursor.fetchall()
            else:
                return cursor.fetchone()
        except Error as e:
            print(f"❌ Error en la consulta SQL: {e}")
            self.conexion.rollback()
            return [] if fetch_all else None
        finally:
            if cursor: cursor.close()
            if self.conexion and self.conexion.is_connected(): self.conexion.close()

    def cargar_datos_iniciales(self):
        """Sincroniza BD -> Estructuras de Datos."""
        # 1. Cargar Medicamentos (para Hash y Árbol)
        # Usamos alias para mapear Nombre_ y Precio a los atributos de Python
        query_medicamentos = """
        SELECT Id, Nombre_ AS Nombre, Categoria, Precio, Stock, Codigo_Barras 
        FROM medicamentos
        """
        medicamentos_data = self._ejecutar_consulta(query_medicamentos, fetch_all=True)
        
        if medicamentos_data:
            for row in medicamentos_data:
                med = Medicamento(**row) 
                self.hash_medicamentos.insertar(med)
                self.arbol_categorias.insertar(med)
        
        # 2. Cargar Contraindicaciones (No existe la tabla, se omite y se usa simulación)
        print("✅ Estructuras de datos sincronizadas con la Base de Datos.")

    # --- Funcionalidades CRUD y Estructuras ---

    def buscar_medicamento(self, codigo_barras: str):
        """Usa Tabla Hash (O(1)) y Árbol (filtros de categoría)."""
        print("\n--- Búsqueda de Medicamento por Código de Barras (Tabla Hash) ---")
        medicamento = self.hash_medicamentos.buscar(codigo_barras)
        
        if medicamento:
            print(f"🔍 Encontrado por Hash: {medicamento}")
            
            # Uso del Árbol para mostrar filtros rápidos de la misma categoría
            similares = self.arbol_categorias.buscar_por_categoria(medicamento.categoria)
            print(f"\nProductos Similares en {medicamento.categoria}:")
            for m in similares:
                if m.id != medicamento.id:
                    print(f"- {m.nombre} (Stock: {m.stock})")
        else:
            print(f"❌ Medicamento con código {codigo_barras} no encontrado.")
        return medicamento
    
    def registrar_venta(self, codigo_barras: str, id_cliente: int, id_empleado: int, cantidad: int):
        """Registra una venta, actualiza stock y chequea contraindicaciones (Grafo)."""
        print("\n--- Registro de Venta ---")
        med_en_memoria = self.hash_medicamentos.buscar(codigo_barras)
        
        if not med_en_memoria:
            print("❌ Error: Medicamento no encontrado.")
            return

        if med_en_memoria.stock < cantidad:
            print(f"❌ Error: Stock insuficiente. Disponible: {med_en_memoria.stock}.")
            # Uso de Cola Prioritaria: Agregar pedido urgente (Prioridad 1)
            self.cola_pedidos.agregar_pedido(1, med_en_memoria.id, 50) 
            print("❗ Pedido urgente de reabastecimiento agregado a la Cola Prioritaria.")
            return

        # 1. Uso del Grafo: Verificar Contraindicaciones
        print(self.grafo_contraindicaciones.verificar_contraindicacion(med_en_memoria.id, 5)) 
        
        # 2. Actualizar Stock en BD
        nueva_cantidad_bd = med_en_memoria.stock - cantidad
        self._ejecutar_consulta("UPDATE medicamentos SET Stock = %s WHERE Id = %s", (nueva_cantidad_bd, med_en_memoria.id))

        # 3. Registrar la Venta en BD
        # CORRECCIÓN: Se usan las 5 columnas funcionales de la tabla 'ventas'.
        query_venta = "INSERT INTO ventas (Fecha, Cantidad, id_Medicamentos, id_Clientes, id_Empleados) VALUES (%s, %s, %s, %s, %s)"
        self._ejecutar_consulta(query_venta, (datetime.now().date(), cantidad, med_en_memoria.id, id_cliente, id_empleado))

        # 4. Sincronizar Stock en Estructuras de Datos
        med_en_memoria.stock = nueva_cantidad_bd

        print(f"✅ Venta exitosa: {med_en_memoria.nombre} x {cantidad}. Stock actualizado a {med_en_memoria.stock}.")
        
        # 5. Uso de Cola Prioritaria: Generar alerta de stock crítico (Prioridad 2)
        if nueva_cantidad_bd < 10 and nueva_cantidad_bd > 0:
            self.cola_pedidos.agregar_pedido(2, med_en_memoria.id, 50) 
            print(f"❗ Stock bajo, pedido de reabastecimiento de {med_en_memoria.nombre} agregado a la Cola Prioritaria.")
            
    def gestionar_pedidos_urgentes(self):
        """Procesa el pedido de mayor prioridad de la cola."""
        print("\n--- Gestión de Pedidos de Reabastecimiento Urgente (Cola Prioritaria) ---")
        resultado = self.cola_pedidos.atender_pedido_urgente()
        print(resultado)

    # --- Reportes Solicitados (SQL + Código) ---

    def medicamentos_proximos_a_vencer(self, meses=6):
        """Reporte: Medicamentos próximos a vencer (en menos de N meses)."""
        print(f"\n--- Reporte: Medicamentos Próximos a Vencer (en menos de {meses} meses) ---")
        print("❌ ADVERTENCIA: La columna 'fecha_vencimiento' NO existe en la tabla 'medicamentos'.")
        print("Se muestra un listado de stock BAJO (< 10) como alternativa funcional.")
        
        query = """
        SELECT Nombre_, Stock
        FROM medicamentos
        WHERE Stock < 10
        ORDER BY Stock ASC;
        """
        resultados = self._ejecutar_consulta(query, fetch_all=True)
        for row in resultados:
            print(f"⚠️ {row['Nombre_']} - Stock: {row['Stock']} (BAJO)")
    
    def ventas_por_empleado(self):
        """Reporte: Total de Ventas por Empleado (Monto y Cantidad)."""
        print("\n--- Reporte: Total de Ventas por Empleado (Funcional) ---")
        
        # --- EN EL ARCHIVO 'code' (Clase FarmaciaManager) ---

    def reporte_stock_por_categoria(self, categoria: str = None):
        """
        [NUEVA FUNCIÓN] Reporte que lista el stock agrupado, usando la estructura ArbolCategorias.
        Si no se pasa categoría, lista todas.
        """
        print("\n--- Reporte: Stock por Categoría (Uso del Árbol) ---")
        
        print("Categorías disponibles y su stock total:")
        
        if not self.arbol_categorias.categorias:
            print("No hay medicamentos cargados en las estructuras de memoria.")
            return

        for cat, lista in self.arbol_categorias.categorias.items():
            total_stock = sum(med.stock for med in lista)
            print(f"-> {cat}: {len(lista)} productos, Total Stock: {total_stock}")
            
        return "Reporte por categoría generado con éxito."

        # CORRECCIÓN: Se une (JOIN) ventas, empleados y medicamentos para obtener el precio.
        query = """
        SELECT 
            E.Nombre__ AS empleado, 
            COUNT(V.ID) AS total_ventas, 
            SUM(V.Cantidad * M.Precio) AS monto_total
        FROM ventas V
        JOIN empleados E ON V.id_Empleados = E.ID
        JOIN medicamentos M ON V.id_Medicamentos = M.Id
        GROUP BY E.ID, E.Nombre__
        ORDER BY monto_total DESC;
        """
        resultados = self._ejecutar_consulta(query, fetch_all=True)
        if resultados:
            for row in resultados:
                print(f"👨‍💼 {row['empleado']}: {row['total_ventas']} ventas, Total: ${row['monto_total']:.2f}")
        else:
            print("No se encontraron ventas para reportar.")


# -----------------------------------------------------------------------
# III. DEMOSTRACIÓN DE FUNCIONALIDAD
# -----------------------------------------------------------------------

if __name__ == "__main__":
    
    print("=========================================================")
    print("      DEMOSTRACIÓN DEL SISTEMA FARMACITY MANAGER         ")
    print("=========================================================")
    
    # Datos de prueba basados en farmacy.sql
    CODIGO_PARACETAMOL = '111111' # Stock 50
    CODIGO_AMOXICILINA_CRITICO = '333333' # Stock 5
    ID_CLIENTE_JUAN = 1 #
    ID_EMPLEADO_MARIA = 1 #
    
    try:
        manager = FarmaciaManager()
    except Exception as e:
        print(f"Error al inicializar el Manager: {e}")
        sys.exit(1)
    
    # --- 1. Búsqueda y Filtro (Hash y Árbol) ---
    print("\n\n################ 1. BÚSQUEDA Y FILTRO (O(1)) ################")
    manager.buscar_medicamento(CODIGO_PARACETAMOL)

    # --- 2. Registro de Venta y Transacción Exitosa ---
    print("\n\n################ 2. REGISTRO DE VENTA EXITOSA ################")
    # Venta de 2 Paracetamol (Stock 50 -> 48)
    manager.registrar_venta(CODIGO_PARACETAMOL, ID_CLIENTE_JUAN, ID_EMPLEADO_MARIA, 2) 

    # --- 3. Alerta y Gestión de Pedido Urgente (Cola Prioritaria) ---
    print("\n\n################ 3. GESTIÓN DE PEDIDO URGENTE ################")
    # Venta fallida que activa el pedido urgente de reposición
    # Amoxicilina (Stock 5), pide 10. Activa Alerta de Prioridad 1.
    manager.registrar_venta(CODIGO_AMOXICILINA_CRITICO, ID_CLIENTE_JUAN, ID_EMPLEADO_MARIA, 10) 
    
    # Atender el pedido generado
    manager.gestionar_pedidos_urgentes()

    # --- 4. Reportes Solicitados ---
    print("\n\n################ 4. REPORTES SQL COMPLEJOS ################")
    manager.medicamentos_proximos_a_vencer(meses=18)
    manager.ventas_por_empleado()

    print("\n=========================================================")
    print("               FIN DE LA DEMOSTRACIÓN                    ")
    print("=========================================================")