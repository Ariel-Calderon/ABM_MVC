import sqlite3

class Modelo:
    """
    Clase que gestiona la conexión y operaciones en la base de datos
    """
    def __init__(self, db_path="database.db"):       
        """
        Constructor de clase, guarda en el atributo self.db_path la ubicación y nombre de la base de datos.

        Args:
            db_path (str, optional): Ruta y nombre de la base. Defaults to "database.db".
        """
        self.db_path = db_path

    def abrir_conexion(self):
        """
        Establece y devuelve una conexión con la base de datos.

        Returns:
            sqlite3.Connection: Objeto que representa la conexión con la base de datos.
        """
        return sqlite3.connect(self.db_path)

    def ejecutar_consulta(self, query, params=None, fetchall=True):      
        """
        Ejecuta un requerimiento en la base de datos

        Args:
            query (str): Instrucción SQL
            params (List[Any] | Tuple[Any], optional): Valores relacionados con el query. Defaults to None.
            fetchall (bool, optional): Indica si se deben obtener todos los registros (para consultas SELECT). Defaults to True.

        Returns:
            List | Tuple | int | None: 
                - Una lista o una tupla con los registros si la consulta es un SELECT.
                - Un entero con la cantidad de registros afectados si la consulta es de tipo INSERT, UPDATE o DELETE.
                - None si ocurre un error durante la ejecución.
        """
        conexion = self.abrir_conexion()
        try:
            cursor = conexion.cursor()
            cursor.execute(query, params or [])
            if query.strip().upper().startswith("SELECT"):
                return cursor.fetchall() if fetchall else cursor.fetchone()
            else:
                conexion.commit()
                return cursor.rowcount
        except sqlite3.Error as e:
            print(f"Error en la consulta SQL: {e}")
            return None
        finally:
            conexion.close()

    def crear_tabla(self, tabla, esquema):
        """
        Crea una tabla en la base de datos si no existe.

        Args:
            tabla (str): Nombre de la tabla.
            esquema (str): Esquema de la tabla en formato SQL (ej. "id INTEGER PRIMARY KEY, nombre TEXT").
        
        Returns:
            int | None: 
                - Un entero indicando el resultado de la consulta (generalmente -1 para CREATE TABLE en SQLite).
                - None si ocurre un error durante la ejecución.
        """
        query = f"CREATE TABLE IF NOT EXISTS {tabla} ({esquema})"
        return self.ejecutar_consulta(query)
        
    def insertar(self, tabla:str, columnas , valores):              
        """
        Inserta un registro en una tabla de la base de datos.

        Args:
            tabla (str): Nombre de la tabla donde se insertará el registro
            columnas (List[str]): Lista con los nombres de las columnas que recibirán valores
            valores (List): Lista con los valores que se insertarán

        Returns:
            int | None: 
                -El ID de la última fila insertada si la operación fue exitosa.
                -None si ocurre un error durante la inserción.
        """
        placeholders = ", ".join(["?"] * len(valores))
        columnas_str = ", ".join(columnas)
        query = f"INSERT INTO {tabla} ({columnas_str}) VALUES ({placeholders})"
        conexion = self.abrir_conexion()
        try:
            cursor = conexion.cursor()
            cursor.execute(query, valores)
            conexion.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Error al insertar en la tabla {tabla}: {e}")
            return None
        finally:
            conexion.close()
    
    def actualizar(self, tabla, columnas, valores, condicion):
        """
        Modifica un registro ya existente en la base de datos.

        Args:
            tabla (str): Nombre de la tabla
            columnas (List[str]): Lista con los nombres de las columnas que recibirán valores
            valores (List): Lista con los valores que se insertarán
            condicion (str): Expresión que debe cumplirse para modificar el/los registro/s. Ej. "id = ?"
                             
        Returns:            
            int | None:               
                - Un entero con la cantidad de registros modificados.
                - None si ocurre un error durante la ejecución.
        """
        set_clause = ", ".join([f"{col} = ?" for col in columnas])
        query = f"UPDATE {tabla} SET {set_clause} WHERE {condicion}"
        return self.ejecutar_consulta(query, valores, fetchall=False)

    def eliminar(self, tabla, condicion, valores):
        """
        Elimina uno o varios registros de una tabla de una base de datos

        Args:
            tabla (str): Nombre de la tabla.
            condicion (str): Condicion que debe cumplirse para eliminar el registro. Ej. "id = ?"
            valores (List): Valores asociados a la condición.

        Returns:            
            int | None:               
                - Un entero con la cantidad de registros eliminados.
                - None si ocurre un error durante la ejecución.
        """
        query = f"DELETE FROM {tabla} WHERE {condicion}"
        return self.ejecutar_consulta(query, valores, fetchall=False)

    def seleccionar(self, tabla, columnas="*", condicion=None, valores=None):
        """
        Selecciona un grupo de registros de una tabla de la base

        Args:
            tabla (str): Nombre de la tabla.
            columnas (List[str], optional): Columnas que serán retornadas en un array. Defaults to "*".
            condicion (str, optional): Condición que debe cumplir uno o varios campos. Defaults to None.
            valores (Any, optional): Los valores que determinan la condición, si la hubiera. Defaults to None.

        Returns:
            List | Tuple | None: 
                - Una lista o una tupla con los registros.
                - None si ocurre un error durante la ejecución.
        """
        query = f"SELECT {columnas} FROM {tabla}"
        if condicion:
            query += f" WHERE {condicion}"
        return self.ejecutar_consulta(query, valores)
    
    def obtener_campos(self,tabla):
        """
        Obtiene una lista con los nombres de los campos de una tabla de la base de datos.

        Args:
            tabla (str): Nombre de la tabla.

        Returns:
            List[str]: Lista con los nombres de los campos de la tabla de referencia.
        """
        conexion = self.abrir_conexion()
        try:
            cursor = conexion.cursor()
            cursor.execute(f"PRAGMA table_info ({tabla})")
            lista_de_campos = []
            for fila in cursor.fetchall():
                lista_de_campos.append(fila[1])                
            return lista_de_campos
        finally:
            conexion.close()

    def contar_registros(self,tabla,campo,valor):
        """
        Obtiene, de una tabla de la base de datos, la cantidad de registros que hay con un determinado valor en un campo.

        Args:
            tabla (str): Nombre de la tabla.
            campo (str): Nombre del campo de la tabla donde se buscará un valor.
            valor (Any): Valor que se buscará en la respectiva columna/campo.

        Returns:
            int: Cantidad de registros que cumplen la condición requerida.
        """
        conexion = self.abrir_conexion()
        try:
            cursor = conexion.cursor()
            cursor.execute(f"SELECT COUNT(*) FROM {tabla} WHERE {campo} = ?", (valor,))
            return cursor.fetchall()[0][0]
        finally:
            conexion.close()
