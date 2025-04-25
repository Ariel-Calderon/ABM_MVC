import tkinter as tk
from tkinter import Menu, messagebox
from tkinter import ttk
import ABM_MVC.controlador as controlador





class Plantilla(tk.Toplevel):
    """Clase heredera de tk.Toplevel y SúperClase de las diferentes vistas que gestionarán las operaciones entre la vista del usuario y el controlador.

    Args:
        tk (object): Objeto de tkinter.

    Attributes:
            clase_objeto(class): Clase heredera de Entidad que será gestionada por el objeto creado.
            lista_de_widgets(List[List[str,object,bool]]): Lista que contiene listas con el formato [etiqueta,widget,es_campo_clave:bool] que servirá para contruir el formulario una vez que estén declarados los widgets.
            lista_de_comboboxes(List[List[object,str,List[Any]]]): Lista de comboboxes que representan claves externas (si hubiera un combobox para la clave principal, no se registra en esta lista). La lista contiene [[objeto combox,"campo clave externa en la tabla",lista de [id]]].
            clave_principal(List[object] | List[object,List[Any]]): Si la clave principal es ingresada por el usuario deberá usarse un entry, el argumento es una lista con un sólo objeto [objeto entry]. Si se trata de una clave autoincrement en la base de datos, no tendrá un input en el formulario de carga, pero puede seleccionarse con un combobox para modificarse, en este caso el argumento será una lista con dos elementos [objeto combobox, lista de id].
            campos_obligatorios(List[object]): En esta lista se registran todos los campos obligatorios en la carga, deben agregarse a la lista los objetos widgets, no las variables asociadas.
            validacion_decimales(Tuple[Callable, str]):Tupla que contiene la función de validación para números decimales y un patrón de formato asociado ('%P').
            validacion_enteros(Tuple[Callable, str]):Tupla que contiene una función de validación para números enteros y un patrón de formato asociado ('%P').
    """

    def __init__(self,parent,clase_objeto,modo):
        """Construye una instancia de clase donde se definen los atributos necesarios para que puedan construirse y gestionarse los los widgets.

        Args:
            parent (object): Ventana desde la cual se construye la Plantilla.
            clase_objeto (class): Clase heredera de Entidad que será gestionada por el objeto creado.
            modo (str): Objetivo de la ventana/formulario: "guardar", "modificar" o "borrar".        
        """
        super().__init__(parent)
        self.clase_objeto = clase_objeto
        self.modo = modo
        self.lista_de_widgets = []  #[etiqueta,widget,es_campo_clave:bool]
        self.lista_de_comboboxes = [] # [[objeto combox,"campo clave externa db",lista de id],] Sin incluir la clave principal
        self.clave_principal = [] #[objeto combobox, lista de id] cuando está implementada con un combobox
                                  #[objeto entry] cuando se trata de una entrada de texto y el valor se obtiene con get
        self.campos_obligatorios=[] #[campo de entrada] tiene que ser el objeto del input, sea un combobox o un entry simple 
        self.validacion_decimales = (self.register(self.solo_decimales_con_coma), '%P')
        self.validacion_enteros = (self.register(self.solo_numeros),'%P')

    def cancelar(self):
        """Borra el contenido de los widgets y los switchea de habilitados a deshabilitados al cancelar una acción.
        """
        self.reset_formulario()
        if self.modo == "modificar":
            self.switch_widgets()
            self.reset_formulario() #hay que resetear antes y despues de switchear los widgets

    def guardar(self):
        """Chequea si los campos obligatorios tienen valores, en ese caso contruye el objeto de la clase gestionada por el formulario, le asigna los valores de los widgets a los respectivos atributos e intenta guardarlo en la base de datos, informando si lo logró o no.
        """
        if self.chequear_campos_obligatorios():
            self.objeto = self.clase_objeto()        
            self.objeto.asignar_valores(self)
            guardado = self.objeto.guardar()
            if guardado[0]:
                 self.messagebox_temporal("Guardado",guardado[1],1500)
                 self.reset_formulario()
            else:
                self.messagebox_temporal("Error",guardado[1],1500)

    def modificar(self):
        """Chequea si los campos obligatorios tienen valores, en ese caso le asigna los valores de los widgets a los atributos del objeto (ya construido cuando fue seleccionado el registro) e intenta relizar el update en la base, informando si lo logró o no.
        En caso de resultar exitosa la modificación se borran los valores de los widgets y se switchean.
        """
        if self.chequear_campos_obligatorios():
            self.objeto.asignar_valores(self)
            if self.objeto.modificar() is not None:
                self.messagebox_temporal("Modificado","El registro fue modificado correctamente.",1500)
                self.reset_formulario() #se resetean sólo los widgets activos
                self.switch_widgets()
                self.reset_formulario() #se resetean los widgets restantes
            else:
                self.messagebox_temporal("Error", "El registro no pudo ser modificado",1500)

    
    def seleccionar(self,id = None):
        """Selecciona un registro de la base de datos y completa los widgets del formulario con los valores obtenidos.
        Si no se ingresa un id, buscará ese dato en el atributo self.clave_principal y completará el resto de los campos con los datos obtenidos.

        Args:
            id (Any, optional): Id/clave del registro seleccionado. Defaults to None.
        """
        if id is None: #Si no recibe el id significa se encuentra en un Combobox o un Entry:
            if (len(self.clave_principal)>1):  #Si hay dos elementos self.clave_principal > es un Combobox:
                indice = self.clave_principal[0].current() 
                id = self.clave_principal[1][indice]
            else:                              #Si hay uno sólo > es un Entry:
                id = self.clave_principal[0].get()
        
        self.objeto = self.clase_objeto(id)
        self.objeto.completar_campos(self)
        self.switch_widgets()
    
    def messagebox_temporal(self,titulo, mensaje, duracion=2000):
        """Crea una ventana con un mensaje y lo destruye en el tiempo estipulado.

        Args:
            titulo (str): Título de la ventana.
            mensaje (str): Mensaje que se mostrará.
            duracion (int, optional): Tiempo de duración de la ventana, expresado en milisegundos. Defaults to 2000.
        """
        ventana_emergente = tk.Toplevel()
        ventana_emergente.title(titulo)
        ventana_emergente.geometry("300x100")
                
        ventana_emergente.transient()
        ventana_emergente.grab_set()
        
        mensaje_label = tk.Label(ventana_emergente, text=mensaje, wraplength=250)
        mensaje_label.pack(expand=True, fill="both", padx=10, pady=10)
               
        ventana_emergente.after(duracion, ventana_emergente.destroy)

    def reset_formulario(self):
        """Pone en blanco todos los widgets.
        """
        for widget in self.winfo_children():
            print(f"Widget detectado: {widget}, Tipo: {type(widget)}")            
            if isinstance(widget, ttk.Combobox):                
                widget.set("")
                print ("combobox detectado")
            elif isinstance(widget, tk.Entry):
                widget.delete(0, tk.END)  
                print ("entry detectado")

    def switch_widgets(self):
        """Habilita los widgets que están desabilitados y viceversa. En el caso de los comboboxes no se usa el modo "normal" sino "readonly", es decir que no se permite escribir en ningún caso.
        """
        for widget in self.winfo_children():
            try:
                estado_actual = str(widget.cget("state"))
                if isinstance(widget,ttk.Combobox):
                    nuevo_estado = "readonly" if estado_actual == "disabled" else "disabled"
                else:
                    nuevo_estado = "normal" if estado_actual == "disabled" else "disabled"             
                widget.configure(state=nuevo_estado)
            except (tk.TclError, AttributeError):
                pass  

    def chequear_campos_obligatorios(self):  
        """Chequea si los widgets incluidos en la lista self.campos_obligatorios tienen valores.
        En caso de no confirmarse en todos los casos se muestra un mensaje informando los campos vacíos.

        Returns:
            bool: Devuelve True si todos los campos obligatorios tiene valores, o False en caso contrario.
        """
        mensaje = ""  
        check = True 
        print (self.campos_obligatorios)     
        for campo in self.campos_obligatorios:
            variable = campo.cget("textvariable")
            valor = self.getvar(variable) #.strip()
            print (valor)
            if valor is None or valor == "":                
                mensaje += f"El campo {self.obtener_label(campo)} está vacío\n"
        if mensaje != "":
            check = False 
            messagebox.showinfo("Falta información", mensaje)
            print (mensaje)                   
        return check


    def obtener_label(self, widget_objetivo):
        """Obtiene y retorna el texto de la etiqueta anterior a un determinado widget.

        Args:
            widget_objetivo (object): Widget del cual se quiere obtener la etiqueta.

        Returns:
            str | None: Retorna el texto de la etiqueta buscada, o None en caso de no encontrarla.
        """
        info = widget_objetivo.grid_info()
        fila = int(info["row"])
        columna = int(info["column"])
        contenedor = widget_objetivo.master

        for widget in contenedor.winfo_children():
            if isinstance(widget, tk.Label):
                info_label = widget.grid_info()
                if int(info_label["row"]) == fila and int(info_label["column"]) == columna -1:
                    return widget.cget("text")
        return None
    
    def solo_decimales_con_coma(self, texto):
        """Valida el ingreso de números decimales usando una sola coma (no punto) como separador.

        Args:
            texto (str): texto a evaluar.

        Returns:
            bool: False si no se cumple la condición y verdadero en caso contrario.
        """
        if texto == "":
            return True
        if texto.count(",") > 1:
            return False
        try:
            float(texto.replace(",", "."))
            return True
        except ValueError:
            return False
        
    def solo_numeros(self, texto):
        """Evalúa si una cadena de texto es un núemro entero.

        Args:
            texto (str): Texto a evaluar.

        Returns:
            bool: False si no se cumple la condición y verdadero en caso contrario.
        """
        return texto.isdigit() or texto == ""    



    def crear_entry(self, obligatorio:bool, etiqueta: str, nombre_campo:str, validacion = None):
        """Crea un widget Entry de tkinter, junto con la etiqueta, en caso de haber una regla de validación se agrega en la construcción del Entry.
        Agrega el respectivo objeto a la lista self.lista_de_widgets para que pueda ser gestionado por otros métodos.
        Agrega el widget a la lista self.clave_principal en caso de inferir, por el nombre de campo, que es la clave principal.
        Agrega el widget a la lista self.campos_obligatorios en caso que así estuviera definido.


        Args:
            obligatorio (bool): Indica si es obligatorio completar el campo.
            etiqueta (str): Texto de la etiqueta que se mostrará junto al widget.
            nombre_campo (str): Nombre del campo en la base de datos al que apuntará el widget y por lo tanto también es el nombre del respectivo atributo de la entidad gestionada.
            validacion (str, optional): Tipo de validación, "decimales" o "enteros", no se ingresa argumento si no se requiere validación. Defaults to None.
        """
        parametros = self.clase_objeto.ver_parametros() #se obtienen el nombre de la tabla y el campo clave a través de un método de clase
        tabla = parametros[0] #evaluar esta línea
        campo_clave = parametros[1]

        etiqueta = tk.Label(self, text=etiqueta)
        setattr(self,nombre_campo, tk.StringVar())
        variable = getattr(self, nombre_campo)

        if validacion is not None:
            if validacion == "decimales":
                setattr(self,nombre_campo + "_entrada", tk.Entry(self,textvariable=variable,validate="key",validatecommand=self.validacion_decimales))
            elif validacion == "enteros":
                setattr(self,nombre_campo + "_entrada", tk.Entry(self,textvariable=variable,validate="key",validatecommand=self.validacion_enteros))            
        else:
            setattr(self,nombre_campo + "_entrada", tk.Entry(self,textvariable=variable))

        entry = getattr(self,nombre_campo + "_entrada")

        if campo_clave == nombre_campo:
            self.clave_principal.append(entry)

        if obligatorio:
            self.campos_obligatorios.append(entry)

        self.lista_de_widgets.append([etiqueta,entry,(campo_clave==nombre_campo)])

  
        


    def crear_combobox(self, obligatorio:bool, etiqueta: str, nombre_campo:str,campo_para_mostrar="descripcion",campo_para_guardar="id"):
        """Crea un widget Combobox de tkinter, junto con la etiqueta. En este caso no hay reglas de validación ya que el combobox tendrá el status de "readonly" o "disabled", por lo tanto sólo podrá seleccionar, no escribir.
        Agrega el respectivo objeto a la lista self.lista_de_widgets para que pueda ser gestionado por otros métodos.
        Agrega el widget a la lista self.clave_principal en caso de inferir, por el nombre de campo, que es la clave principal, en caso contrario lo agrega a self.lista_de_comboboxes.
        Agrega el widget a la lista self.campos_obligatorios en caso que así estuviera definido.

        Args:
            obligatorio (bool): Indica si es obligatorio completar el campo.
            etiqueta (str): Texto de la etiqueta que se mostrará junto al widget.
            nombre_campo (str): Nombre del campo de la tabla al que apuntará el widget que, en caso de ser una clave externa, deberá coincidir con el nombre de la tabla vinculada a través del mismo.
            campo_para_mostrar (str, optional): En caso de que usemos este combobox para una clave externa, en este argumento declaramos el nombre del campo que se mostrará, de la tabla vinculada. Defaults to "descripcion".
            campo_para_guardar (str, optional): Al igual que lo mencionado para el argumento anterior, aquí declaramos el campo de la tabla relacionada que contiene los ids, estos son los valores que se guardan efectivamente en el campo de la tabla-entidad que estamos gestionando. Defaults to "id".
        """
        parametros = self.clase_objeto.ver_parametros()
        tabla = parametros[0]
        campo_clave = parametros[1]        

        es_clave = (campo_clave==nombre_campo)
        if self.modo != "guardar" or not es_clave:                
            if es_clave:
                lista_clase = getattr(controlador, "Lista" + tabla)
            else:
                lista_clase = getattr(controlador, "Lista" + nombre_campo)
            print(lista_clase)
            lista_objeto=lista_clase()
            lista_mostrar= lista_objeto.listar_columnas([campo_para_mostrar])
            lista_guardar=lista_objeto.listar_columnas([campo_para_guardar])

            etiqueta = tk.Label(self, text=etiqueta)
            setattr(self,nombre_campo + "_variable", tk.StringVar())
            variable = getattr(self, nombre_campo + "_variable")
                    
            setattr(self,nombre_campo + "_entrada", ttk.Combobox(self,textvariable=variable,values=lista_mostrar,state="readonly"))
            combobox = getattr(self,nombre_campo + "_entrada")
            combobox.grid(row=0, column=1, padx=10, pady=5)  
            if es_clave:
                self.clave_principal.append(combobox)
                self.clave_principal.append(lista_guardar)
            else:
                self.lista_de_comboboxes.append([combobox,nombre_campo,lista_guardar])

            if obligatorio:
                self.campos_obligatorios.append(combobox)

            self.lista_de_widgets.append([etiqueta,combobox,es_clave])


    

    def render_formulario_ABM (self):
        """Asigna una ubicación a los widgets creados y agrega los botones para Guardar, Seleccionar, Modificar, Borrar y Cancelar.
        """
        fila = 0
        for widget in self.lista_de_widgets:
            widget[0].grid(row=fila, column=0, padx=10, pady=5, sticky="w")
            widget[1].grid(row=fila, column=1, padx=10, pady=5)  
            if widget[2] and self.modo=="modificar":
                    widget[0].configure(state="disabled") 
                    widget[1].configure(state="disabled")          
                    tk.Button(self, text="Seleccionar", command= self.seleccionar,state="disabled").grid(row=fila, column=2, columnspan=2, pady=20)
            fila += 1

        tk.Button(self, text="Cancelar", command=self.cancelar).grid(row=fila, column=1, columnspan=2, pady=20)
        if(self.modo=="guardar"):            
            tk.Button(self, text="Guardar", command=self.guardar).grid(row=fila, column=0, columnspan=2, pady=20)
        else:
            tk.Button(self, text="Modificar", command=self.modificar).grid(row=fila, column=0, columnspan=2, pady=20)
            self.switch_widgets()
            