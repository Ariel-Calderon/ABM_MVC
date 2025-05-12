from .modelo import Modelo
import csv

base_ubicacion = ""

def pasar_ubicacion_db(ubicacion:str):
    global base_ubicacion
    base_ubicacion = ubicacion

def registrar_entidades(lista_de_entidades:list):
    for entidad in lista_de_entidades:
        tabla = entidad.ver_parametros()[0]
        nombre_clase = f"Lista{tabla}"
        nueva_clase = type(nombre_clase, (Lista,), {"clase_principal" : entidad})
        globals()[nombre_clase] = nueva_clase #VERIFICAR SI REALMENTE ES NECESARIO REGISTRARLA EN GLOBALS
        print(f"Clase creada: {nombre_clase}, Módulo: {nueva_clase.__module__}")


class Entidad:
    """
    SúperClase que gestionará las Altas, Bajas y Modificaciones de cualquier entidad representada en una base de datos.
    
    Attributes:
        tabla (str): Nombre de la tabla.
        campo_clave(str):Nombre del campo que contiene la clave/id.
        id(Any): Identificador de un registro en la table.
        lista_de_campos(List[str]):Lista que contiene los nombres de los campos de la tabla.        
        modulo_ubicacion(module):Módulo en el que se encuentran las clases concretas, se define como atributo de clase.
        base(object): Objeto que gestiona la conexión y operaciones en la base.
    """

    #se asignan los atributos de manera dinámica, usando los nombres de los campos de la tabla
    def __init__(self, id=None, lista_de_campos=None,lista_de_valores=None):
        """
        Genera los atributos de forma dinámica en función de los campos de la tabla de referencia.
        Construye un objeto con atributos vacíos si no se ingresan argumentos.
        Si se ingresa el id, construye un objeto con atributos y valores obtenidos de la base.
        También se puede ingresar la lista de campos y los valores como argumentos, de modo que pueda ser construido en la iteración de una matriz/array.
        
        Args:
            id (Any, optional): Identificador del registro. Defaults to None.
            lista_de_campos (List[str], optional): Lista con los campos que dan nombre a los atributos. Defaults to None.
            lista_de_valores (List[Any], optional): Lista con el valor de cada campo. Defaults to None.
        """
        self.tabla = self.__class__.tabla
        self.campo_clave = self.__class__.campo_clave
        self.id = id         
        self.base = Modelo(base_ubicacion)
        #La lista de campos y valores vienen como argumento cuando es para una lista de objetos
        #de manera que no tenga que consultar a la base con cada construcción
        if (lista_de_campos is not None):
            self.lista_de_campos = lista_de_campos
        elif(id is not None):
            self.lista_de_campos = self.base.obtener_campos(self.tabla)
            lista_de_valores = self.base.seleccionar(self.tabla, "*", f"{self.campo_clave} = ?",[id])[0]
        else:
            self.lista_de_campos = self.base.obtener_campos(self.tabla)

        if (id is None and lista_de_valores is None):
            for campo in self.lista_de_campos:
                setattr(self,campo,None)
        else:
            for campo, valor in zip(self.lista_de_campos,lista_de_valores):
                setattr(self,campo,valor)

    @classmethod
    def ver_parametros(cls):
        """
        Método de clase que devuelve información sobre la clase para ser usada en una capa superior.

        Returns:
            List[str,str]: Lista que contiene el nombre de la tabla y el nombre del campo clave.
        """              
        return [cls.tabla,cls.campo_clave]
    
    """
    @classmethod
    def pasar_ubicacion_modulo(cls, modulo):
       
        Asigna un valor al atributo de clase modulo_ubicacion, que indica en que módulo se tienen que buscar las clases herederas.

        Args:
            modulo (module): Consiste en el módulo donde se encuentran definidas las clases herederas de la presente SúperClase
        
        cls.modulo_ubicacion = modulo
    """
    def borrar(self):
        """Elimina el registro de la base de datos correspondiente al objeto.
        """
        self.base.eliminar(self.tabla,f"{self.campo_clave} = ?",[self.id])

    def modificar(self):
        """Modifica el registro de la base de datos correspondiente al objeto.

        Returns:            
            int | None:               
                - Un entero con la cantidad de registros modificados.
                - None si ocurre un error durante la ejecución.
        """
        valores = []
        campos_sin_id = []
        for campo in self.lista_de_campos:
            if (campo != self.campo_clave):
                campos_sin_id.append(campo)
                valores.append(getattr(self,campo,None))
        return self.base.actualizar(self.tabla,campos_sin_id,valores,f" {self.campo_clave} = {self.id}")

    def guardar(self):
        """Guarda los datos de un objeto en un nuevo registro de la Base de datos.

        Returns:
            List[bool,str]: El primer valor de la lista corresponde a la confirmación de la acción y el segundo el mensaje a mostrar al usuario.
        """
        valores = []
        campos = []
        for campo in self.lista_de_campos:
            valor = getattr(self,campo,None)
            if(campo != self.campo_clave):
                valores.append(valor)
                campos.append(campo)
            elif(valor is not None):
                if(self.base.contar_registros(self.tabla,self.campo_clave,valor) == 0 ):
                    valores.append(valor)
                    campos.append(campo)
                else:
                    return [False, "Ya existe un registro con la misma clave"] #si ya un registro con ese id
        id_insertado = self.base.insertar(self.tabla,campos,valores)
        if id_insertado is not None:
            return [True, "El registro ha sido guardado exitosamente.",id_insertado]
        else:
            return [False, "Error al intentar guardar el registro"]
        
    def asignar_valores(self,formulario):
        """Asigna valores a los atributos de un objeto vacío a partir de los valores obtenidos de un formulario de una capa superior.
        Para que la operación sea posible es necesario que los nombres de los widgets del formulario coincidan con los nombres de los campos de la tabla en la base de datos.
        En la capa con la vista del usuario se definen los métodos que garantizan la creación de widgets con los nombres adecuados.
        
        Args:
            formulario (objet): Formulario con nombres de widgets compatibles con los atributos del objeto.
        """
        for campo in self.lista_de_campos:
            atributo = getattr(formulario, campo,None)
            if (atributo is not None):
                valor = atributo.get()
                setattr(self,campo,valor)
        if (formulario.lista_de_comboboxes is not None):
            for combo in formulario.lista_de_comboboxes:
                valor = combo[2][combo[0].current()]
                setattr(self,combo[1],valor)

    def completar_campos(self,formulario):
        """Completa los inputs de un formulario con los valores de los atributos del objeto.

        Args:
            formulario (object): Formulario con nombres de widgets compatibles con los atributos del objeto.
        """
        for campo in self.lista_de_campos:
            variable_input= getattr(formulario, campo, None)
            if (variable_input is not None):
                valor=getattr(self,campo)
                variable_input.set(valor)
        if formulario.lista_de_comboboxes is not None:
            for combo in formulario.lista_de_comboboxes:
                id = getattr(self,combo[1])
                indice = 0
                for clave in combo[2]:
                    if clave == id:
                        break
                    indice += 1
                combo[0].current(indice)

    def obtener_valor(self,campo):
        """Devuelve el valor de un atributo del objeto.

        Args:
            campo (str): Nombre del atributo

        Returns:
            Any: Valor del atributo en cuestión.
        """
        return getattr(self,campo)
    
        
            

class Lista:
    """SúperClase que crea, contiene y gestiona una lista de objetos.

    Attributes:
        clase_principal (Class): Clase de objetos que contendrá la lista.
        lista(List[object]): La lista de objetos propiamente dicha.
    """
    def __init__(self,condicion=None,valores=None,lista_con_encabezado=None): #tabla,
        """Crea una lista de objetos de la misma clase, obteniendo los valores de la base de datos o de una lista ingresada como argumento.
        En caso de crearse una instancia sólo especificando la clase, la lista contendrá todos los registros/objetos de la tabla correspondiente a la clase consignada.
        Si se especifican condiciones y sus respectivos valores, se filtrará la lista obtenida de la base de acuerdo a eso.
        En caso de utilizarse una lista con los valores se constuirá una lista de objetos con esos valores.


        Args:
            clase_principal (Class): Clase de objetos que contendrá la lista. 
            condicion (str, optional): Condición para filtrar registros, ej. "campo1 > ? AND campo2 < ?". Defaults to None.
            valores (List | Tuple, optional): Los valores para la condición, continuando con el ejemplo anterior podría ser: (100,200). Defaults to None.
            lista_con_encabezado(List[List[Any]]): Lista que contiene las líneas con los valores para los objetos, la primera línea debe contener los nombres de los campos/columnas de acuerdo a la respectiva tabla de la base.
        """
        self.clase_principal= self.__class__.clase_principal
        self.lista = []
        if lista_con_encabezado is None:
            tabla = self.clase_principal.ver_parametros()[0]
            self.base = Modelo(base_ubicacion)
            matriz = self.base.seleccionar(tabla,"*",condicion,valores)
            campos = self.base.obtener_campos(tabla)            
            for registro in matriz:
                self.lista.append(self.clase_principal(lista_de_campos=campos,lista_de_valores=registro))
        else:
            campos = lista_con_encabezado.pop(0)
            print(campos)
            for linea in lista_con_encabezado:
                print (linea)
                self.lista.append(self.clase_principal(lista_de_campos=campos,lista_de_valores=linea))
                

    def listar_columnas(self,columnas):
        """Devuelve una lista con la/s columna/s solicitada/s.

        Args:
            columnas (str | List[str]): El nombre del campo requerido en la base de datos si se trata de uno sólo o una lista con los nombres si son varios.

        Returns:
            List[Any]: Lista con los valores solicitados
        """
        valores= []
        for linea in self.lista:
            if len(columnas)!= 1:
                valor = []
                for columna in columnas:
                    valor.append(getattr(linea, columna, None))
            else:
                valor = getattr(linea, columnas[0],None)
            valores.append(valor)        
        return valores
    
    def guardar(self):
        """Hace un insert en la base de datos de los objetos de la lista.

        Returns:
            Tuple(List[bool, str, Any]): Lista que contiene una lista por cada línea que se intentó guardar [True, mensaje, número de registro] en caso de éxito y [False, mensaje] en caso contrario.
        """
        tupla_resultados = []
        for elemento in self.lista:
            tupla_resultados.append(elemento.guardar())
        return tupla_resultados
    
    def modificar(self):
        """Hace un update en la base de datos de los registros representados en los objetos de la lista.

        Returns:
           Tuple(int,int): Tupla con la cantidad de registros modificados y la cantidad de registros que se intentó modificar.
        """
        registros_modificados = 0
        for elemento in self.lista:
            registros_modificados += elemento.modificar() or 0 #modificar() devuelve 1 o None
        return registros_modificados,len(self.lista)
    



class ArchivoCsv:    
    def __init__(self, clase_principal):
        self.clase_principal = clase_principal

    def abrir_archivo(self, ruta_archivo, delimitador=','):
        try:
            with open(ruta_archivo, mode='r', encoding='utf-8') as archivo:
                lector_csv = csv.reader(archivo, delimiter= delimitador)  
                self.lista_contenido = [fila for fila in lector_csv]                
        except FileNotFoundError:
            print(f"Error: El archivo '{ruta_archivo}' no fue encontrado.")
        except Exception as e:
            print(f"Ocurrió un error al abrir el archivo: {e}")

    def crear_lista_de_objetos(self, campos = None):
        if campos is not None:
                self.lista_contenido.insert(0,campos) #agrego encabezados en la primera línea de la lista.
        tabla = self.clase_principal.ver_parametros()[0]
        clase_lista_string = f"Lista{tabla}"
        clase_lista = globals()[clase_lista_string]
        self.lista_objetos = clase_lista(lista_con_encabezado=self.lista_contenido)
        
        

    def guardar_lista_de_objetos(self):
        return self.lista_objetos.guardar()

