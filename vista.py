import tkinter as tk
from tkinter import Menu, messagebox
from tkinter import ttk





class Plantilla(tk.Toplevel):

    def __init__(self,parent,clase_objeto,modo):
        super().__init__(parent)
        self.clase_objeto = clase_objeto
        self.modo = modo
        self.lista_de_widgets = []  #[etiqueta,widget,clave:bool]  
        self.lista_de_comboboxes = [] # [[objeto combox,"campo clave externa db",lista de id],] Sin incluir la clave principal
        self.clave_principal = [] #[objeto combobox, lista de id] cuando está implementada con un combobox
                                  #[objeto entry] cuando se trata de una entrada de texto y el valor se obtiene con get
        self.campos_obligatorios=[] #[campo de entrada] tiene que ser el objeto del input, sea un combobox o un entry simple 
        self.validacion_decimales = (self.register(self.solo_decimales_con_coma), '%P')
        self.validacion_enteros = (self.register(self.solo_numeros),'%P')

    def cancelar(self):
        self.reset_formulario()
        if self.modo == "modificar":
            self.switch_widgets()
            self.reset_formulario() #hay que resetear antes y despues de switchear los widgets

    def guardar(self):
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
        ventana_emergente = tk.Toplevel()
        ventana_emergente.title(titulo)
        ventana_emergente.geometry("300x100")
                
        ventana_emergente.transient()
        ventana_emergente.grab_set()
        
        mensaje_label = tk.Label(ventana_emergente, text=mensaje, wraplength=250)
        mensaje_label.pack(expand=True, fill="both", padx=10, pady=10)
               
        ventana_emergente.after(duracion, ventana_emergente.destroy)

    def reset_formulario(self):       
        for widget in self.winfo_children():
            print(f"Widget detectado: {widget}, Tipo: {type(widget)}")            
            if isinstance(widget, ttk.Combobox):                
                widget.set("")
                print ("combobox detectado")
            elif isinstance(widget, tk.Entry):
                widget.delete(0, tk.END)  
                print ("entry detectado")

    def switch_widgets(self):
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
        return texto.isdigit() or texto == ""    



    def crear_entry(self, obligatorio:bool, etiqueta: str, nombre_campo:str, validacion = None):
        parametros = self.clase_objeto.ver_parametros()
        tabla = parametros[0]
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
            parametros = self.clase_objeto.ver_parametros()
            tabla = parametros[0]
            campo_clave = parametros[1]
            modulo = parametros[2]

            es_clave = (campo_clave==nombre_campo)
            if self.modo != "guardar" or not es_clave:                
                if es_clave:
                    lista_clase = getattr(modulo, "Lista" + tabla)
                else:
                    lista_clase = getattr(modulo, "Lista" + nombre_campo)
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
        






