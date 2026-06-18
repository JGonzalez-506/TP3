#Elaborado por Derian Segura y Juan Gonzalez
#Fecha de creacion: 11/06/26 a las 6:41
#Ultima modificacion: 11/06/26 10:32
#Version: 3.14.3

#Importaciones
import tkinter as tk
from funciones import interfazParqueo

if __name__ == "__main__":
    #Creamos la raíz de Tkinter
    ventanaPrincipal = tk.Tk()
    ventanaPrincipal.title("Sistema de Estacionamiento Inteligente - TEC")
    #Instanciamos la clase pasando la raíz (tal como harías con VentanaPrincipal en basarte.py)
    app = interfazParqueo(ventanaPrincipal)
    #Corremos el ciclo principal de eventos
    ventanaPrincipal.mainloop()