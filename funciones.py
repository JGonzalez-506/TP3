#Elaborado por Derian Segura y Juan Gonzalez
#Fecha de creacion: 11/06/26 a las 6:41
#Ultima modificacion: 15/06/26 18:38
#Version: 3.14.3

#importaciones
import tkinter as tk
from tkinter import messagebox
import pickle
import json 
import requests
import random
import math
from datetime import datetime
from tkinter import ttk

class AplicacionParqueo:
    def __init__(self, ventanaPrincipal):
        #Almacenamos la ventana raíz dentro del objeto
        self.ventana = ventanaPrincipal
        #Atributos de la aplicación (Antes estaban en el diccionario estadoApp)
        self.parqueosPorPagina = 25
        self.paginaActual = 0
        self.baseDatosParqueos = []
        self.totalParqueos = 0
        self.colorFondoCrema = "#FFF3DD"
        self.colorSensorVerde = "#C8E6C9"
        self.colorSensorRojo = "#FFCDD2"
        self.colorDiscapacitado = "#B3E5FC" # Azul claro para espacio de discapacidad libre
        self.colorElectrico = "#E0E050"     # Morado claro para auto eléctrico libre
        self.colorTexto = "#000000"
        self.colorFlechas = "#6B9FCF"
        self.mensSubtitulo = None
        self.botonIzquierda = None
        self.botonDerecha = None
        self.listaBotonesDinamicos = []
        #Inicialización de componentes gráficos iniciales
        self.ventana.configure(bg=self.colorFondoCrema)
        self.dimensionarVentana()
        #Lógica de bifurcación inicial de base de datos
        if self.cargarBaseDatosExistente():
            self.crearEstructuraVentanas()
            self.dibujarPantallaActual()
        else:
            self.mostrarPantallaConfiguracion()

    def dimensionarVentana(self):
        anchoPantalla = self.ventana.winfo_screenwidth()
        altoPantalla = self.ventana.winfo_screenheight()
        anchoVentana = 1200
        altoVentana = 650
        posicionX = round((anchoPantalla / 2) - (anchoVentana / 2))
        posicionY = round((altoPantalla / 2) - (altoVentana / 2))
        self.ventana.geometry(f"{anchoVentana}x{altoVentana}+{posicionX}+{posicionY}")

    def cargarBaseDatosExistente(self):
        try:
            with open("bdParqueo.txt", "rb") as archivoBinario:
                listaCargada = pickle.load(archivoBinario)
                if isinstance(listaCargada, list) and len(listaCargada) > 0:
                    self.baseDatosParqueos = listaCargada
                    self.totalParqueos = len(listaCargada)
                    return True
        except:
            pass
        return False
    
    def guardarDatosParqueo(self, cantidad, nombreArchivo):
        #Base URL de tu API de Mockaroo
        urlBase = "https://my.api.mockaroo.com/parqueo.json?key=95e5d290"
        apiUrl = f"{urlBase}&qty={cantidad}"  #&qty= le indica a Mockaroo cuantos registros necesita que devuelva
        try:
            print(f"Obteniendo {cantidad} registros desde la API...")
            #Se descargan los datos de la API
            response = requests.get(apiUrl)
            data = response.json() #Se traduce el contenido del json para ser utilizado
            #Se guardan los datos en un archivo .json local, usamos encoding='utf-8' para que soporte tildes o caracteres especiales sin romperse
            with open(nombreArchivo, "w", encoding='utf-8') as archivo:
                #Indent=4 hace que el archivo JSON no se guarde en una sola línea, 
                #sino ordenado y legible visualmente
                json.dump(data, archivo, indent=4, ensure_ascii=False) #ensure_ascii=Flase permite guardar tildes y ñ. json.dump toma los datos de manera en que python entienda
            print(f"Los datos se han guardado en el archivo: {nombreArchivo}")
            return data
        except:
            print(f"No se establecer conexion con la API o descargar de los datos")
            return None

    def verificarYCrear(self):
        textoUsuario = self.entradaCantidad.get()
        if not textoUsuario.isdigit():
            messagebox.showwarning("Datos Inválidos", "Por favor, ingrese un número entero válido.")
            return
        cantidad = int(textoUsuario)
        if 1 <= cantidad <= 75:
            #Se crean los espacios vacíos junto con su número
            datosDescargados = self.guardarDatosParqueo(cantidad, "parqueo.json")
            if datosDescargados == None:
                return
            random.shuffle(datosDescargados)    #random.shuffle permite tener aleatoriedad en las marcas, colores, etc y asi que no salgan igual siempre
            placaVehiculo = 0
            cantDiscapacidad = math.ceil(cantidad * 0.05)    #math.ceil redondea los numeros
            if cantDiscapacidad < 2:
                cantDiscapacidad = 2
            incluyeElectrico = messagebox.askyesno("Vehículo Eléctrico", "¿Desea incorporar un espacio para vehículos eléctricos?")
            if incluyeElectrico:
                cantElectrico = 1 
            else:
                cantElectrico = 0
            campoActual = 1
            parqueosGenerados = []
            for indice in range(cantDiscapacidad):
                vehiculo = {}
                if placaVehiculo < len(datosDescargados):
                    vehiculo = datosDescargados[placaVehiculo].copy()    #.copy permite utilizar el valor de los datos sin modificarlos 
                    placaVehiculo += 1
                    vehiculo["hora de entrada"] = self.generarHoraEntradaAleatoria()
                parqueosGenerados.append({"numCampo": f"C{campoActual}",
                                          "tipoEspacio": "discapacidad",
                                          "libre": False,
                                          "vehiculo": vehiculo})
                campoActual += 1
            if incluyeElectrico:
                vehiculo = {}
                if placaVehiculo < len(datosDescargados):
                    vehiculo = datosDescargados[placaVehiculo].copy() #.copy permite utilizar el valor de los datos sin modificarlos
                    placaVehiculo += 1
                    vehiculo["hora de entrada"] = self.generarHoraEntradaAleatoria()
                parqueosGenerados.append({"numCampo": f"C{campoActual}",
                                          "tipoEspacio": "electrico",
                                          "libre": False,
                                          "vehiculo": vehiculo})
                campoActual += 1
            espaciosRestantes = cantidad - cantDiscapacidad - cantElectrico
            cantLibresNormales = math.ceil(espaciosRestantes * 0.05)   #math.ceil redondea los numeros
            cantOcupadosNormales = espaciosRestantes - cantLibresNormales
            estadosNormales = [True] * cantLibresNormales + [False] * cantOcupadosNormales #Se crea una lista con el estado de todos los parqueos normales
            random.shuffle(estadosNormales)   #random.shuffle permite tener aleatoriedad a la hora de visualizar los espacios normales del parqueo
            for indice in range(espaciosRestantes):
                estaLibre = estadosNormales[indice]
                vehiculo = None
                if not estaLibre:
                    if placaVehiculo < len(datosDescargados):
                        vehiculo = datosDescargados[placaVehiculo].copy()  #.copy permite utilizar el valor de los datos sin modificarlos
                    else: 
                        vehiculo ={}  
                    placaVehiculo += 1
                    vehiculo["hora de entrada"] = self.generarHoraEntradaAleatoria()
                parqueosGenerados.append({"numCampo": f"C{campoActual}",
                                          "tipoEspacio": "normal",
                                          "libre": estaLibre,
                                          "vehiculo": vehiculo})
                campoActual += 1
            try:
                with open("bdParqueo.txt", "wb") as archivoBinario:
                    pickle.dump(parqueosGenerados, archivoBinario)
            except:
                messagebox.showerror("Error", "No se pudo crear el archivo de base de datos.")
            self.baseDatosParqueos = parqueosGenerados
            self.totalParqueos = cantidad
            #Se borra el texto que dice que no se encontró base de datos, entrada y botón
            self.mensInstruccion.destroy()
            self.entradaCantidad.destroy()
            self.botonConfirmar.destroy()
            self.ventana.grid_columnconfigure(0, weight=0)  #.grid_columnconfigure y grid_rowconfigure hacen que no hayan mudificaciones visuales cuando se agranda la ventana
            self.ventana.grid_rowconfigure(0, weight=0)
            self.crearEstructuraVentanas()
            self.dibujarPantallaActual()
        else:
            messagebox.showwarning("Rango Incorrecto", "La cantidad debe estar entre 1 y 75 espacios.")

    def mostrarPantallaConfiguracion(self):
        self.mensInstruccion = tk.Label(self.ventana, 
                                    text="No se detectó una base de datos activa.\n\nIngrese la cantidad de parqueos a registrar (Máximo 75):", 
                                    font=("Arial", 14, "bold"), 
                                    bg=self.colorFondoCrema, 
                                    fg=self.colorTexto)
        self.mensInstruccion.place(x=330, y=190)
        self.entradaCantidad = tk.Entry(self.ventana, 
                                   font=("Arial", 14), 
                                   width=10, 
                                   justify="center")
        self.entradaCantidad.place(x=520, y=290)
        self.ventana.grid_columnconfigure(0, weight=1)  #.grid_columnconfigure y grid_rowconfigure hacen que no hayan mudificaciones visuales cuando se agranda la ventana
        self.ventana.grid_rowconfigure(0, weight=1)
        self.botonConfirmar = tk.Button(self.ventana,
                                 text="Ingresar cantidad",
                                 font=("Arial", 12, "bold"),
                                 command=self.verificarYCrear,
                                 padx=10,
                                 pady=5)
        self.botonConfirmar.place(x=490, y=330)

    def crearEstructuraVentanas(self):
        mensTitulo = tk.Label(self.ventana,
                              text="Espacios vacíos y ocupados del Parqueo",
                              font=("Arial", 16, "bold"),
                              bg=self.colorFondoCrema,
                              fg=self.colorTexto)
        mensTitulo.grid(row=0, column=0, columnspan=11, pady=(15, 0))
        #Muestra el mensaje de la página actual y la cantidad de páginas
        self.mensSubtitulo = tk.Label(self.ventana,
                                               text="",
                                               font=("Arial", 11, "italic"),
                                               bg=self.colorFondoCrema,
                                               fg="#595959")
        self.mensSubtitulo.grid(row=1, column=0, columnspan=11, pady=(2, 15))
        #Flecha Izquierda
        self.botonIzquierda = tk.Button(self.ventana,
                                                text="◀",
                                                font=("Arial", 22, "bold"),
                                                bg=self.colorFlechas,
                                                fg="white",
                                                relief="flat",
                                                width=3,
                                                height=5,
                                                command=self.paginaAnterior)
        self.botonIzquierda.grid(row=2, column=0, rowspan=5, padx=(20, 15), sticky="ns")
        #Flecha Derecha
        self.botonDerecha = tk.Button(self.ventana,
                                            text="▶",
                                            font=("Arial", 22, "bold"),
                                            bg=self.colorFlechas,
                                            fg="white",
                                            relief="flat",
                                            width=3,
                                            height=5,
                                            command=self.paginaSiguiente)
        self.botonDerecha.grid(row=2, column=10, rowspan=5, padx=(15, 20), sticky="ns")

    def dibujarPantallaActual(self):
        #Desaparece los parqueos de la página anterior
        for botonAnterior in self.listaBotonesDinamicos:
            botonAnterior.destroy()
        self.listaBotonesDinamicos = []
        #Se calculan cuáles parqueos van en qué página
        inicioIndice = self.paginaActual * self.parqueosPorPagina
        finIndice = inicioIndice + self.parqueosPorPagina
        if finIndice > self.totalParqueos:
            finIndice = self.totalParqueos
        parqueosPantalla = self.baseDatosParqueos[inicioIndice:finIndice]
        #Se calcula el total de páginas de parqueos
        totalPaginas = (self.totalParqueos + self.parqueosPorPagina - 1) // self.parqueosPorPagina
        if totalPaginas == 0:
            totalPaginas = 1
        self.mensSubtitulo.config(text=f"Pantalla {self.paginaActual + 1} de {totalPaginas}")
        #Segmentación por filas
        espaciosFilaSuperior = parqueosPantalla[0:9]
        espaciosFilaMedio = parqueosPantalla[9:17]
        spacesFilaInferior = parqueosPantalla[17:25]
        #Se crea la fila de parqueos superior
        columnaActual = 0
        for parqueoEspecifico in espaciosFilaSuperior:  
            if parqueoEspecifico["libre"]:
                tipoEspacio = parqueoEspecifico.get("tipoEspacio", "normal")
                if tipoEspacio == "discapacidad":
                    colorFondoBoton = self.colorDiscapacitado
                elif tipoEspacio == "electrico":
                    colorFondoBoton = self.colorElectrico
                else:
                    colorFondoBoton = self.colorSensorVerde
            else:
                #Si está ocupado pero es de discapacidad o eléctrico, se le asigna un color diferente al normal
                tipoEspacio = parqueoEspecifico.get("tipoEspacio", "normal")
                if tipoEspacio == "discapacidad":
                    colorFondoBoton = "#7D7FC1"
                elif tipoEspacio == "electrico":
                    colorFondoBoton = "#BEC19F"
                else:
                    colorFondoBoton = self.colorSensorRojo
            botonParqueo = tk.Button(self.ventana, 
                                     text=parqueoEspecifico["numCampo"], 
                                     font=("Arial", 10, "bold"), 
                                     bg=colorFondoBoton, 
                                     fg=self.colorTexto, 
                                     relief="solid", bd=1, 
                                     width=10, 
                                     height=5,
                                     command=lambda datosVehiculo=parqueoEspecifico: self.clickEspacio(datosVehiculo))
            botonParqueo.grid(row=2, column=columnaActual + 1, padx=6, pady=5)
            self.listaBotonesDinamicos.append(botonParqueo)
            columnaActual += 1
        #Se crea un espacio entre la fila superior y la del medio, solo si la fila del medio se crea
        if len(espaciosFilaSuperior) > 0 or len(espaciosFilaMedio) > 0:
            pasilloSuperior = tk.Label(self.ventana, 
                                       bg=self.colorFondoCrema, 
                                       height=2)
            pasilloSuperior.grid(row=3, column=1, columnspan=9)
            self.listaBotonesDinamicos.append(pasilloSuperior)
        #Se crea la fila de parqueos del medio
        columnaActual = 0
        for parqueoEspecifico in espaciosFilaMedio:
            if parqueoEspecifico["libre"]:
                tipoEspacio = parqueoEspecifico.get("tipoEspacio", "normal")
                if tipoEspacio == "discapacidad":
                    colorFondoBoton = self.colorDiscapacitado
                elif tipoEspacio == "electrico":
                    colorFondoBoton = self.colorElectrico
                else:
                    colorFondoBoton = self.colorSensorVerde 
            else:
                #Si está ocupado pero es de discapacidad o eléctrico, se le asigna un color diferente al normal
                tipoEspacio = parqueoEspecifico.get("tipoEspacio", "normal")
                if tipoEspacio == "discapacidad":
                    colorFondoBoton = "#2E3078"
                elif tipoEspacio == "electrico":
                    colorFondoBoton = "#5F623B"
                else:
                    colorFondoBoton = self.colorSensorRojo
            botonParqueo = tk.Button(self.ventana, 
                                   text=parqueoEspecifico["numCampo"], 
                                   font=("Arial", 10, "bold"),
                                   bg=colorFondoBoton,
                                   fg=self.colorTexto,
                                   relief="solid", 
                                   bd=1,
                                   width=10,
                                   height=5,
                                   command=lambda datosVehiculo=parqueoEspecifico: self.clickEspacio(datosVehiculo))
            botonParqueo.grid(row=4, column=columnaActual + 1, padx=6, pady=5)
            self.listaBotonesDinamicos.append(botonParqueo)
            columnaActual += 1
        #Se crea el espacio entre la fila del medio y la fila inferior, solo si se crea la fila inferior
        if len(espaciosFilaMedio) > 0 or len(spacesFilaInferior) > 0:
            pasilloInferior = tk.Label(self.ventana, 
                                       bg=self.colorFondoCrema, 
                                       height=2)
            pasilloInferior.grid(row=5, column=1, columnspan=9)
            self.listaBotonesDinamicos.append(pasilloInferior)
        #Se crea la fila de parqueos inferior
        columnaActual = 0
        for parqueoEspecifico in spacesFilaInferior:
            if parqueoEspecifico["libre"]:
                tipoEspacio = parqueoEspecifico.get("tipoEspacio", "normal")
                if tipoEspacio == "discapacidad":
                    colorFondoBoton = self.colorDiscapacitado
                elif tipoEspacio == "electrico":
                    colorFondoBoton = self.colorElectrico
                else:
                    colorFondoBoton = self.colorSensorVerde
            else:
                #Si está ocupado pero es de discapacidad o eléctrico, se le asigna un color diferente al normal
                tipoEspacio = parqueoEspecifico.get("tipoEspacio", "normal")
                if tipoEspacio == "discapacidad":
                    colorFondoBoton = "#2E3078"
                elif tipoEspacio == "electrico":
                    colorFondoBoton = "#5F623B"
                else:
                    colorFondoBoton = self.colorSensorRojo
            botonParqueo = tk.Button(self.ventana,
                                   text=parqueoEspecifico["numCampo"],
                                   font=("Arial", 10, "bold"),
                                   bg=colorFondoBoton,
                                   fg=self.colorTexto,
                                   relief="solid",
                                   bd=1,
                                   width=10,
                                   height=5,
                                   command=lambda datosVehiculo=parqueoEspecifico: self.clickEspacio(datosVehiculo))
            botonParqueo.grid(row=6, column=columnaActual + 1, padx=6, pady=5)
            self.listaBotonesDinamicos.append(botonParqueo)
            columnaActual += 1
        self.actualizarEstadoFlechas()

    def generarHoraEntradaAleatoria(self):
        #Se Obtiene la hora actual
        momentoActual = datetime.now()
        fechaDeHoy = momentoActual.strftime("%Y-%m-%d")
        #Se establecen variables que funcionaran como limites de horas y minutos
        horaLimite = momentoActual.hour
        minutoLimite = momentoActual.minute
        #Si se ejecuta antes de las 7 am, forzamos a que empiece a las 7 am en punto para evitar errores
        if horaLimite < 7:
            horaLimite = 7
            minutoLimite = 0
        #Se elige la hora al azar entre las 7 y la hora actual
        horaAleatoria = random.randint(7, horaLimite)
        #Si cayó en la hora actual, no podemos pasarnos del minuto límite
        if horaAleatoria == horaLimite:
            minutoAleatorio = random.randint(0, minutoLimite)
        else:
            minutoAleatorio = random.randint(0, 59)
        #Se elige los segundos de manera aleatoria
        segundoAleatorio = random.randint(0, 59)
        #Se convierten los números a texto con un formato limpio
        #Usamos .zfill(2) para que si el número es un 5, se transforme en 05
        textoHora = str(horaAleatoria).zfill(2)
        textoMinuto = str(minutoAleatorio).zfill(2)
        textoSegundo = str(segundoAleatorio).zfill(2)
        resultadoFinal = f"{fechaDeHoy} {textoHora}:{textoMinuto}:{textoSegundo}"
        return resultadoFinal

    def actualizarEstadoFlechas(self):
        if self.totalParqueos <= self.parqueosPorPagina:
            self.botonIzquierda.config(state="disabled", bg="#A6B9CB")
            self.botonDerecha.config(state="disabled", bg="#A6B9CB")
            return
        if self.paginaActual > 0:
            self.botonIzquierda.config(state="normal", bg=self.colorFlechas)
        else:
            self.botonIzquierda.config(state="disabled", bg="#A6B9CB")
        limiteSuperior = (self.paginaActual + 1) * self.parqueosPorPagina
        if limiteSuperior < self.totalParqueos:
            self.botonDerecha.config(state="normal", bg=self.colorFlechas)
        else:
            self.botonDerecha.config(state="disabled", bg="#A6B9CB")

    def paginaSiguiente(self):
        self.paginaActual += 1
        self.dibujarPantallaActual()

    def paginaAnterior(self):
        self.paginaActual -= 1
        self.dibujarPantallaActual()

    def clickEspacio(self, parqueoEspecifico):
        if parqueoEspecifico["libre"]:
            return
        vehiculo = parqueoEspecifico["vehiculo"]
        if not vehiculo:
            messagebox.showerror("Error", "Este espacio no tiene un vehículo asignado correctamente.")
            return
        #Se crea la pequeña ventana
        ventanaInfoVehiculo = tk.Toplevel(self.ventana)
        ventanaInfoVehiculo.title(f"Espacio {parqueoEspecifico["numCampo"]}")
        ventanaInfoVehiculo.geometry("280x420") 
        ventanaInfoVehiculo.configure(bg=self.colorFondoCrema)
        #Campo
        mensCampo = tk.Label(ventanaInfoVehiculo,
                             text="Campo:", 
                             bg=self.colorFondoCrema,
                             font=("Arial", 10))
        mensCampo.place(x=25, y=15)
        comboCampo = ttk.Combobox(ventanaInfoVehiculo,
                                  values=[parqueoEspecifico["numCampo"]])
        comboCampo.set(parqueoEspecifico["numCampo"])
        comboCampo.config(state="disabled")
        comboCampo.place(x=25, y=38, width=230) 
        #Placa
        mensPlaca = tk.Label(ventanaInfoVehiculo,
                             text="Placa:",
                             bg=self.colorFondoCrema, 
                             font=("Arial", 10))
        mensPlaca.place(x=25, y=75)
        entryPlaca = tk.Entry(ventanaInfoVehiculo,
                              font=("Arial", 10))
        entryPlaca.insert(0, vehiculo.get("placa"))
        entryPlaca.config(state="disabled")
        entryPlaca.place(x=25, y=98, width=230)
        #Marca
        mensMarca = tk.Label(ventanaInfoVehiculo,
                             text="Marca:",
                             bg=self.colorFondoCrema,
                             font=("Arial", 10))
        mensMarca.place(x=25, y=135)
        comboMarca = ttk.Combobox(ventanaInfoVehiculo,
                                  font=("Arial", 10))
        comboMarca.set(vehiculo.get("marca"))
        comboMarca.config(state="disabled")
        comboMarca.place(x=25, y=158, width=230)
        #Color
        mensColor = tk.Label(ventanaInfoVehiculo,
                             text="Color:",
                             bg=self.colorFondoCrema,
                             font=("Arial", 10))
        mensColor.place(x=25, y=195)
        comboColor = ttk.Combobox(ventanaInfoVehiculo,
                                  font=("Arial", 10))
        comboColor.set(vehiculo.get("color"))
        comboColor.config(state="disabled")
        comboColor.place(x=25, y=218, width=230)
        #Hora de entrada
        mensHora = tk.Label(ventanaInfoVehiculo,
                            text="Hora de entrada:",
                            bg=self.colorFondoCrema,
                            font=("Arial", 10))
        mensHora.place(x=25, y=255)
        horaSucia = vehiculo.get("hora de entrada")
        horaFormateada = horaSucia
        try:
            objetoFecha = datetime.strptime(horaSucia, "%Y-%m-%d %H:%M:%S")
            horaFormateada = objetoFecha.strftime("%d/%m/%y %H:%M:%S")
        except:
            pass
        entryEntrada = tk.Entry(ventanaInfoVehiculo,
                                font=("Arial", 10))
        entryEntrada.insert(0, horaFormateada)
        entryEntrada.config(state="disabled")
        entryEntrada.place(x=25, y=278, width=230)
        #Pagar
        botonPagar = tk.Button(ventanaInfoVehiculo, 
                               text="Pagar", 
                               font=("Arial", 10, "bold"), 
                               bg="#A6B9CB", 
                               fg="black", 
                               relief="solid", 
                               bd=1)
        #Usamos height=2 para hacer mas grande el boton
        botonPagar.place(x=25, y=330, width=230, height=50)