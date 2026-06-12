#Elaborado por Derian Segura y Juan Gonzalez
#Fecha de creacion: 11/06/26 a las 6:41
#Ultima modificacion: 12/06/26 15:12
#Version: 3.14.3

#importaciones
import tkinter as tk
from tkinter import messagebox
import pickle

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
                    for parqueo in listaCargada:
                        parqueo["libre"] = True  # Modificado: Ahora siempre se cargan como vacíos
                    with open("bdParqueo.txt", "wb") as archivoEscribir:
                        pickle.dump(listaCargada, archivoEscribir)
                    self.baseDatosParqueos = listaCargada
                    self.totalParqueos = len(listaCargada)
                    return True
        except:
            pass
        return False

    def verificarYCrear(self):
        textoUsuario = self.entradaCantidad.get()
        if not textoUsuario.isdigit():
            messagebox.showwarning("Datos Inválidos", "Por favor, ingrese un número entero válido.")
            return
        cantidad = int(textoUsuario)
        if 1 <= cantidad <= 75:
            #Se crean los espacios vacíos junto con su número
            parqueosGenerados = []
            for contador in range(cantidad):
                parqueosGenerados.append({"id": f"E{contador + 1}", "libre": True})  # Modificado: Ahora solo se crean vacíos
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
            self.ventana.grid_columnconfigure(0, weight=0)
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
        self.entradaCantidad.focus()
        self.ventana.grid_columnconfigure(0, weight=1)
        self.ventana.grid_rowconfigure(0, weight=1)
        #En command se apunta directo al método sin paréntesis como en basarte.py
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
                colorFondoBoton = self.colorSensorVerde
            else:
                colorFondoBoton = self.colorSensorRojo

            botonParqueo = tk.Button(self.ventana, 
                                     text=parqueoEspecifico["id"], 
                                     font=("Arial", 10, "bold"), 
                                     bg=colorFondoBoton, 
                                     fg=self.colorTexto, 
                                     relief="solid", bd=1, 
                                     width=10, 
                                     height=5)
            botonParqueo.grid(row=2, column=columnaActual + 1, padx=6, pady=5)
            self.listaBotonesDinamicos.append(botonParqueo)
            columnaActual += 1
        #Se crea un espacio entre la fila superior y la del medio, solo si la fila del medio se crea
        if len(espaciosFilaSuperior) > 0 or len(espaciosFilaMedio) > 0:
            pasilloSuperior = tk.Label(self.ventana, bg=self.colorFondoCrema, height=2)
            pasilloSuperior.grid(row=3, column=1, columnspan=9)
            self.listaBotonesDinamicos.append(pasilloSuperior)
        #Se crea la fila de parqueos del medio
        columnaActual = 0
        for parqueoEspecifico in espaciosFilaMedio:
            if parqueoEspecifico["libre"]:
                colorFondoBoton = self.colorSensorVerde 
            else:
                colorFondoBoton = self.colorSensorRojo
            botonParqueo = tk.Button(self.ventana, 
                                   text=parqueoEspecifico["id"], 
                                   font=("Arial", 10, "bold"),
                                   bg=colorFondoBoton,
                                   fg=self.colorTexto,
                                   relief="solid", 
                                   bd=1,
                                   width=10,
                                   height=5)
            botonParqueo.grid(row=4, column=columnaActual + 1, padx=6, pady=5)
            self.listaBotonesDinamicos.append(botonParqueo)
            columnaActual += 1
        #Se crea el espacio entre la fila del medio y la fila inferior, solo si se crea la fila inferior
        if len(espaciosFilaMedio) > 0 or len(spacesFilaInferior) > 0:
            pasilloInferior = tk.Label(self.ventana, bg=self.colorFondoCrema, height=2)
            pasilloInferior.grid(row=5, column=1, columnspan=9)
            self.listaBotonesDinamicos.append(pasilloInferior)
        #Se crea la fila de parqueos inferior
        columnaActual = 0
        for parqueoEspecifico in spacesFilaInferior:
            if parqueoEspecifico["libre"]:
                colorFondoBoton = self.colorSensorVerde
            else: 
                colorFondoBoton = self.colorSensorRojo
            botonParqueo = tk.Button(self.ventana,
                                   text=parqueoEspecifico["id"],
                                   font=("Arial", 10, "bold"),
                                   bg=colorFondoBoton,
                                   fg=self.colorTexto,
                                   relief="solid",
                                   bd=1,
                                   width=10,
                                   height=5)
            botonParqueo.grid(row=6, column=columnaActual + 1, padx=6, pady=5)
            self.listaBotonesDinamicos.append(botonParqueo)
            columnaActual += 1
        self.actualizarEstadoFlechas()

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