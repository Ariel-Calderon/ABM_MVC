from cProfile import label
import tkinter as tk
from tkinter import Menu

from setuptools import Command

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Gestión de Precios para Qendra")
        self.geometry("800x600")
        self.crear_menu()

    def crear_menu(self):
        menu_principal = Menu(self)
        self.config(menu=menu_principal)

        menu_archivo = Menu(menu_principal, tearoff=0)
        menu_principal.add_cascade(label="Archivo", menu=menu_archivo)
        menu_archivo.add_command(label="Cargar Archivo CSV", command=self.cargar_archivo)
        menu_archivo.add_command(label="Generar Archivo CSV", command=self.generar_archivo)
        menu_archivo.add_command(label="Salir", command=self.quit)


        menu_productos = Menu(menu_principal, tearoff=0)
        menu_principal.add_cascade(label="Productos", menu=menu_productos)
        menu_productos.add_command(label="Listar Productos", command=self.listar_productos)
        menu_productos.add_command(label="Cargar Producto", command=self.cargar_producto)
        menu_productos.add_command(label="Borrar Producto", command=self.borrar_producto)
        menu_productos.add_command(label="Modificar Producto", command=self.modificar_producto)

        menu_proveedores = Menu(menu_principal, tearoff=0)
        menu_principal.add_cascade(label="Proveedores", menu=menu_proveedores)
        menu_proveedores.add_command(label="Listar Proveedores",command=self.listar_proveedores)
        menu_proveedores.add_command(label="Cargar Proveedores",command=self.cargar_proveedores)
        menu_proveedores.add_command(label="Borrar Proveedores",command=self.borrar_proveedores)
        menu_proveedores.add_command(label="Modificar Proveedores",command=self.modificar_proveedores)

        menu_gestion = Menu(menu_principal, tearoff=0)
        menu_principal.add_cascade(label="Gestión de Precios", menu=menu_gestion)
        

    def cargar_archivo(self):
        pass

    def generar_archivo(self):
        pass

    def listar_productos(self):
        pass

    def cargar_producto(self):
        pass

    def borrar_producto(self):
        pass

    def modificar_producto(self):
        pass

    def listar_proveedores(self):
        pass
    
    def cargar_proveedores(self):
        pass

    def borrar_proveedores(self):
        pass

    def modificar_proveedores(self):
        pass


if __name__ == "__main__":
    app = App()
    app.mainloop()