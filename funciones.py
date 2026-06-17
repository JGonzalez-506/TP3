# Elaborado por Derian Segura y Juan Gonzalez
# Fecha de creacion: 11/06/26 a las 6:41
# Ultima modificacion: 17/06/26 18:00
# Version: 4.1.0

# importaciones
import tkinter as tk
from tkinter import messagebox
import pickle
import json
import requests
import random
import math
from datetime import datetime
from tkinter import ttk

class Vehiculo:
    def __init__(self, datosDict):
        # Toma los datos por separado de cada vehiculo y los "modela"
        self.placa = datosDict.get("placa")
        self.marca = datosDict.get("marca")
        self.color = datosDict.get("color")
        self.horaEntrada = datosDict.get("hora de entrada")
        self.tipo = datosDict.get("tipo")

    def obtenerDatosVehiculos(self, llave, valorDefecto):
        # Se crea un diccionario con los atributos de los vehiculos para que se pueda consultar por sus datos especificos
        datosVehiculos = {"placa": self.placa,
                          "marca": self.marca,
                          "color": self.color,
                          "hora de entrada": self.horaEntrada,
                          "tipo": self.tipo}
        return datosVehiculos.get(llave, valorDefecto)

class EspacioParqueo:
    def __init__(self, numCampo, tipoEspacio, libre, vehiculo):
        # Se almacena los datos de los espacios invidualmente
        self.numCampo = numCampo
        self.tipoEspacio = tipoEspacio
        self.libre = libre
        self.vehiculo = vehiculo  # Aquí se guarda la instancia de Vehiculo

    def obtenerDatosEspacio(self, llave, valorDefecto):
        # Se crea un diccionario con los atributos de los estacionamiento para que se pueda consultar por sus datos especificos
        datosEspacios = {"numCampo": self.numCampo,
                         "tipoEspacio": self.tipoEspacio,
                         "libre": self.libre,
                         "vehiculo": self.vehiculo}
        return datosEspacios.get(llave, valorDefecto)

class AplicacionParqueo:
    def __init__(self, ventanaPrincipal):
        # Almacenamos la ventana raíz dentro del objeto, funcionará como el Menú Principal
        self.ventana = ventanaPrincipal
        # Atributos de la aplicación
        self.parqueosPorPagina = 25
        self.paginaActual = 0
        self.baseDatosParqueos = []
        self.totalParqueos = 0
        self.colorFondoCrema = "#FFF3DD"
        self.colorSensorVerde = "#C8E6C9"
        self.colorSensorRojo = "#FFCDD2"
        self.colorDiscapacitado = "#B3E5FC"
        self.colorElectrico = "#E0E050"
        self.colorTexto = "#000000"
        self.colorFlechas = "#6B9FCF"
        self.mensSubtitulo = None
        self.botonIzquierda = None
        self.botonDerecha = None
        self.listaBotonesDinamicos = []
        self.venParqueo = None
        self.venConfig = None
        self.tiempo_gracia = 0
        self.monto_hora = 0
        # Inicialización de componentes gráficos iniciales
        self.ventana.configure(bg=self.colorFondoCrema)
        self.dimensionarVentana(self.ventana, 650, 650)  # Se ajusta para el menú principal
        # Verifica si existe bd
        self.hayBaseDatos = self.cargarBaseDatosExistente()
        # Se lanza el menú principal
        self.mostrarMenuPrincipal()

    def dimensionarVentana(self, ventanaDestino, anchoVentana, altoVentana):
        anchoPantalla = ventanaDestino.winfo_screenwidth()
        altoPantalla = ventanaDestino.winfo_screenheight()
        posicionX = round((anchoPantalla / 2) - (anchoVentana / 2))
        posicionY = round((altoPantalla / 2) - (altoVentana / 2))
        ventanaDestino.geometry(f"{anchoVentana}x{altoVentana}+{posicionX}+{posicionY}")

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
        # Base url de la api de Mockaroo
        urlBase = "https://my.api.mockaroo.com/parqueo.json?key=95e5d290"
        apiUrl = f"{urlBase}&qty={cantidad}"  # &qty= le indica a Mockaroo cuantos registros necesita que devuelva
        try:
            print(f"Obteniendo {cantidad} registros desde la API...")
            # Se descargan los datos de la api
            response = requests.get(apiUrl)
            data = response.json()  # Se traduce el contenido del json para ser utilizado
            # Se guardan los datos en un archivo .json local, usamos encoding='utf-8' para que soporte tildes o caracteres especiales sin romperse
            with open(nombreArchivo, "w", encoding='utf-8') as archivo:
                # Indent=4 hace que el archivo JSON no se guarde en una sola línea,
                # sino ordenado y legible visualmente
                json.dump(data, archivo, indent=4,
                          ensure_ascii=False)  # ensure_ascii=False permite guardar tildes y ñ. json.dump toma los datos de manera en que python entienda
            print(f"Los datos se han guardado en el archivo: {nombreArchivo}")
            return data
        except:
            print(f"No se establecio conexion con la API o descargar de los datos")
            return None

    #Menu Principal
    def mostrarMenuPrincipal(self):
        # Se configura el titulo del menú principal
        self.ventana.title("Sistema de Estacionamiento Inteligente - TEC")

        mensInstruccion = tk.Label(self.ventana,
                                   text="Está en el Menú Principal. Presione el botón de la opción que desea",
                                   font=("Arial", 13),
                                   bg=self.colorFondoCrema)
        mensInstruccion.pack(pady=(30, 25))

        fuente_boton = ("Arial", 11)
        margenIzquierdo = (130, 0)

        self.botonObtener = tk.Button(self.ventana, text="Obtener vehículos y vouchers", font=fuente_boton,
                                      command=lambda: print(f"opción 1"))
        self.botonObtener.pack(anchor="w", padx=margenIzquierdo, pady=8)

        self.botonVer = tk.Button(self.ventana, text="Ver estacionamiento", font=fuente_boton,
                                  command=self.abrirVerEstacionamiento)
        self.botonVer.pack(anchor="w", padx=margenIzquierdo, pady=8)

        self.botonEstacionar = tk.Button(self.ventana, text="Estacionar un vehículo", font=fuente_boton,
                                         command=lambda: print(f"opción 3"))
        self.botonEstacionar.pack(anchor="w", padx=margenIzquierdo, pady=8)

        self.botonFacturar = tk.Button(self.ventana, text="Facturar 1 espacio", font=fuente_boton,
                                       command=lambda: print(f"opción 4"))
        self.botonFacturar.pack(anchor="w", padx=margenIzquierdo, pady=8)

        self.botonReportes = tk.Button(self.ventana, text="Reportes", font=fuente_boton,
                                       command=lambda: print(f"opción 5"))
        self.botonReportes.pack(anchor="w", padx=margenIzquierdo, pady=8)

        self.botonConfig = tk.Button(self.ventana, text="Configuración", font=fuente_boton,
                                     command=self.mostrarPantallaConfiguracion)
        self.botonConfig.pack(anchor="w", padx=margenIzquierdo, pady=8)

        self.botonAcerca = tk.Button(self.ventana, text="Acerca de", font=fuente_boton,
                                     command=lambda: print(f"opción 7"))
        self.botonAcerca.pack(anchor="w", padx=margenIzquierdo, pady=8)

        self.botonSalir = tk.Button(self.ventana, text="Salir", font=fuente_boton, command=self.ventana.quit)
        self.botonSalir.pack(anchor="w", padx=margenIzquierdo, pady=(8, 30))

        # Se aplica el estado (habilitado/deshabilitado) de cada botón según si hay base de datos
        self.actualizarEstadoBotonesMenu()

    def actualizarEstadoBotonesMenu(self):
        # Si no existe una base de datos de parqueos, se deshabilitan todas las opciones
        # excepto "Configuración" (que es la que permite crear la base de datos) y "Salir"
        estado = "normal" if self.hayBaseDatos else "disabled"
        self.botonObtener.config(state=estado)
        self.botonVer.config(state=estado)
        self.botonEstacionar.config(state=estado)
        self.botonFacturar.config(state=estado)
        self.botonReportes.config(state=estado)
        self.botonAcerca.config(state=estado)
        # Estas dos opciones siempre quedan disponibles
        self.botonConfig.config(state="normal")
        self.botonSalir.config(state="normal")

    def cerrarVentanaSecundariaYRegresar(self, ventanaSecundaria):
        # Cierra la ventana secundaria actual y vuelve a mostrar el Menú Principal
        ventanaSecundaria.destroy()
        self.ventana.deiconify()

    #Configuración
    def mostrarPantallaConfiguracion(self):
        # Se oculta el Menú Principal mientras se usa esta ventana
        self.ventana.withdraw()
        # Se crea una ventana secundaria para la configuración
        self.venConfig = tk.Toplevel(self.ventana)
        self.venConfig.title("Configuración del Sistema")
        self.dimensionarVentana(self.venConfig, 500, 480)
        self.venConfig.configure(bg=self.colorFondoCrema)
        self.venConfig.protocol("WM_DELETE_WINDOW", lambda: self.cerrarVentanaSecundariaYRegresar(self.venConfig))
        tk.Label(self.venConfig, text="Configuración del Parqueo", font=("Arial", 16, "bold"),
                 bg=self.colorFondoCrema).pack(pady=20)

        tk.Label(self.venConfig, text="Tamaño del estacionamiento (1-75):", bg=self.colorFondoCrema,
                 font=("Arial", 12)).pack(pady=(10, 5))
        self.entradaCantidad = tk.Entry(self.venConfig, font=("Arial", 14), justify="center", width=10)
        self.entradaCantidad.pack()

        # Si ya existe base de datos, se bloquea la entrada del tamaño
        if self.hayBaseDatos:
            self.entradaCantidad.insert(0, str(self.totalParqueos))
            self.entradaCantidad.config(state="disabled")

        # Cajas de texto para Tiempo de gracia y Monto por hora
        tk.Label(self.venConfig, text="Tiempo de gracia (minutos):", bg=self.colorFondoCrema, font=("Arial", 12)).pack(
            pady=(15, 5))
        self.entradaGracia = tk.Entry(self.venConfig, font=("Arial", 14), justify="center", width=10)
        self.entradaGracia.pack()
        self.entradaGracia.insert(0, str(self.tiempo_gracia))

        tk.Label(self.venConfig, text="Monto por hora (colones):", bg=self.colorFondoCrema, font=("Arial", 12)).pack(
            pady=(15, 5))
        self.entradaMonto = tk.Entry(self.venConfig, font=("Arial", 14), justify="center", width=10)
        self.entradaMonto.pack()
        self.entradaMonto.insert(0, str(self.monto_hora))

        # Boton para ingresar la cantidad y guardar variables
        self.botonConfirmar = tk.Button(self.venConfig, text="Guardar Configuración", font=("Arial", 12, "bold"),
                                        command=self.verificarYCrear)
        self.botonConfirmar.pack(pady=(30, 10))

        # Boton para regresar al Menú Principal sin guardar cambios
        self.botonRegresarConfig = tk.Button(self.venConfig, text="Regresar", font=("Arial", 11),
                                             command=lambda: self.cerrarVentanaSecundariaYRegresar(self.venConfig))
        self.botonRegresarConfig.pack(pady=(0, 20))

    def verificarYCrear(self):
        # Se validan y guardan los datos de configuración en memoria (Tiempo de gracia y Monto)
        try:
            gracia = int(self.entradaGracia.get())
            monto = int(self.entradaMonto.get())
        except ValueError:
            messagebox.showwarning("Datos Inválidos", "El tiempo de gracia y el monto deben ser numéricos.")
            return

        self.tiempo_gracia = gracia
        self.monto_hora = monto

        # Si ya hay BD, solo actualiza las variables en memoria y sale
        if self.hayBaseDatos:
            messagebox.showinfo("Éxito", "Configuración actualizada (en memoria).")
            self.venConfig.destroy()
            self.ventana.deiconify()
            return

        # Se valida si el numero de espacios que ingreso el usuario sea realmente un numero
        textoUsuario = self.entradaCantidad.get()
        if not textoUsuario.isdigit():
            messagebox.showwarning("Datos Inválidos", "Por favor, ingrese un número entero válido.")
            return
        cantidad = int(textoUsuario)
        # Todavia tenemos dudas de cual es el minimo y el maximo de estacionamientos, de momento, este es el rango que pensamos
        if 1 <= cantidad <= 75:
            # Se cualculan cuantos espacios del total se veran reflejados en la interfaz de espacios segun su tipo(normal, discapacitado o electrico)
            datosDescargados = self.guardarDatosParqueo(cantidad, "parqueo.json")
            placaVehiculo = 0
            cantDiscapacidad = math.ceil(
                cantidad * 0.05)  # Se redondea hacia arriba el 5% de los espacios para discapacitados para que no queden en decimales
            if cantDiscapacidad < 2:
                cantDiscapacidad = 2
            incluyeElectrico = messagebox.askyesno("Vehículo Eléctrico",
                                                   "¿Desea incorporar un espacio para vehículos eléctricos?")
            if incluyeElectrico:
                cantElectrico = 1
            else:
                cantElectrico = 0
            campoActual = 1
            parqueosGenerados = []
            # Se crean y se les asignan los datos de los vehiculos y el numero de campo que ocupan los espacios para discapacitados
            for indice in range(cantDiscapacidad):
                vehiculo = {}
                if placaVehiculo < len(datosDescargados):
                    vehiculo = datosDescargados[
                        placaVehiculo].copy()  # Se utiliza el valor de la placa del vehiculo sin modificarlo
                    placaVehiculo += 1
                    vehiculo["hora de entrada"] = self.generarHoraEntradaAleatoria()
                objetoVehiculo = Vehiculo(vehiculo)
                parqueosGenerados.append(EspacioParqueo(numCampo=f"C{campoActual}",
                                                        tipoEspacio="discapacidad",
                                                        libre=False,
                                                        vehiculo=objetoVehiculo))
                campoActual += 1
            # Si el usuario confimara que quiere un espacio para un vehiculo electrico, se crea y se asignan los datos del vehiculo y el numero de campo que ocupara el espacio
            if incluyeElectrico:
                vehiculo = {}
                if placaVehiculo < len(datosDescargados):
                    vehiculo = datosDescargados[
                        placaVehiculo].copy()  # Se utiliza el valor de la placa del vehiculo sin modificarlo
                    placaVehiculo += 1
                    vehiculo["hora de entrada"] = self.generarHoraEntradaAleatoria()
                objetoVehiculo = Vehiculo(vehiculo)
                parqueosGenerados.append(EspacioParqueo(numCampo=f"C{campoActual}",
                                                        tipoEspacio="electrico",
                                                        libre=False,
                                                        vehiculo=objetoVehiculo))
                campoActual += 1
            # Se calculan cuantos espacios normales quedaran ocupados y cuantos quedaran libres, acomodandolos de manera aleatoria
            espaciosRestantes = cantidad - cantDiscapacidad - cantElectrico
            cantLibresNormales = math.ceil(
                espaciosRestantes * 0.05)  # Se redondea hacia arriba el 5% de los espacios normales libres para que no quede en decimales
            cantOcupadosNormales = espaciosRestantes - cantLibresNormales
            estadosNormales = [True] * cantLibresNormales + [
                False] * cantOcupadosNormales  # Se crea una lista con el estado de todos los parqueos normales
            random.shuffle(
                estadosNormales)  # random.shuffle permite tener aleatoriedad a la hora de visualizar los espacios normales del parqueo
            # Se crean y se les asignan los datos de los vehiculos y el numero de campo que ocupan los espacios normales
            for indice in range(espaciosRestantes):
                estaLibre = estadosNormales[indice]
                vehiculo = None
                if not estaLibre:
                    if placaVehiculo < len(datosDescargados):
                        vehiculo = datosDescargados[
                            placaVehiculo].copy()  # Se utiliza el valor de la placa del vehiculo sin modificarlo
                    else:
                        vehiculo = {}
                    placaVehiculo += 1
                    vehiculo["hora de entrada"] = self.generarHoraEntradaAleatoria()
                if vehiculo:
                    objetoVehiculo = Vehiculo(vehiculo)
                else:
                    None
                parqueosGenerados.append(EspacioParqueo(numCampo=f"C{campoActual}",
                                                        tipoEspacio="normal",
                                                        libre=estaLibre,
                                                        vehiculo=objetoVehiculo))
                campoActual += 1
            # Se crea el archivo que contendra de forma binaria la base de datos del parqueo
            try:
                with open("bdParqueo.txt", "wb") as archivoBinario:
                    pickle.dump(parqueosGenerados, archivoBinario)
            except:
                messagebox.showerror("Error", "No se pudo crear el archivo de base de datos.")
            self.baseDatosParqueos = parqueosGenerados
            self.totalParqueos = cantidad
            self.hayBaseDatos = True
            # Como ya existe base de datos, se habilitan las opciones del menú principal
            self.actualizarEstadoBotonesMenu()

            # Se destruye la ventana de configuración, se regresa al menú y se notifica el éxito
            self.venConfig.destroy()
            self.ventana.deiconify()
            messagebox.showinfo("Éxito", "Base de datos generada y configuración inicial guardada.")
        else:
            messagebox.showwarning("Rango Incorrecto", "La cantidad debe estar entre 1 y 75 espacios.")

    #Ver estacionamiento
    def abrirVerEstacionamiento(self):
        # Si no hay base de datos, no se permite abrir el estacionamiento
        if not self.hayBaseDatos:
            messagebox.showwarning("Aviso", "No hay una base de datos activa. Vaya a Configuración primero.")
            return

        # Se oculta el Menú Principal mientras se usa esta ventana
        self.ventana.withdraw()

        # Se crea la ventana secundaria para ver el parqueo
        self.venParqueo = tk.Toplevel(self.ventana)
        self.venParqueo.title("Ver Estacionamiento")
        self.dimensionarVentana(self.venParqueo, 1200, 700)
        self.venParqueo.configure(bg=self.colorFondoCrema)
        self.venParqueo.protocol("WM_DELETE_WINDOW", lambda: self.cerrarVentanaSecundariaYRegresar(self.venParqueo))

        self.mostrarEspaciosParqueo()
        self.mostrarEspaciosPaginaActual()

    def mostrarEspaciosParqueo(self):
        mensTitulo = tk.Label(self.venParqueo,
                              text="Espacios vacíos y ocupados del Parqueo",
                              font=("Arial", 16, "bold"),
                              bg=self.colorFondoCrema,
                              fg=self.colorTexto)
        mensTitulo.grid(row=0, column=0, columnspan=11, pady=(15, 0))
        # Muestra el mensaje de la página actual y la cantidad de páginas
        self.mensSubtitulo = tk.Label(self.venParqueo,
                                      text="",
                                      font=("Arial", 11, "italic"),
                                      bg=self.colorFondoCrema,
                                      fg="#595959")
        self.mensSubtitulo.grid(row=1, column=0, columnspan=11, pady=(2, 15))
        # Flecha Izquierda
        self.botonIzquierda = tk.Button(self.venParqueo,
                                        text="◀",
                                        font=("Arial", 22, "bold"),
                                        bg=self.colorFlechas,
                                        fg="white",
                                        relief="flat",
                                        width=3,
                                        height=5,
                                        command=self.paginaAnterior)
        self.botonIzquierda.grid(row=2, column=0, rowspan=5, padx=(20, 15), sticky="ns")
        # Flecha Derecha
        self.botonDerecha = tk.Button(self.venParqueo,
                                      text="▶",
                                      font=("Arial", 22, "bold"),
                                      bg=self.colorFlechas,
                                      fg="white",
                                      relief="flat",
                                      width=3,
                                      height=5,
                                      command=self.paginaSiguiente)
        self.botonDerecha.grid(row=2, column=10, rowspan=5, padx=(15, 20), sticky="ns")
        # Boton Regresar, debajo de todo el contenido del parqueo
        self.botonRegresarParqueo = tk.Button(self.venParqueo,
                                              text="Regresar",
                                              font=("Arial", 11),
                                              command=lambda: self.cerrarVentanaSecundariaYRegresar(self.venParqueo))
        self.botonRegresarParqueo.grid(row=7, column=0, columnspan=11, pady=(15, 15))

    def mostrarEspaciosPaginaActual(self):
        # Desaparece los parqueos de la página anterior
        for botonAnterior in self.listaBotonesDinamicos:
            botonAnterior.destroy()
        self.listaBotonesDinamicos = []
        # Se calculan cuáles parqueos van en qué página
        inicioIndice = self.paginaActual * self.parqueosPorPagina
        finIndice = inicioIndice + self.parqueosPorPagina
        if finIndice > self.totalParqueos:
            finIndice = self.totalParqueos
        parqueosPantalla = self.baseDatosParqueos[inicioIndice:finIndice]
        # Se calcula el total de páginas de parqueos
        totalPaginas = (self.totalParqueos + self.parqueosPorPagina - 1) // self.parqueosPorPagina
        if totalPaginas == 0:
            totalPaginas = 1
        self.mensSubtitulo.config(text=f"Pantalla {self.paginaActual + 1} de {totalPaginas}")
        # Segmentación por filas
        espaciosFilaSuperior = parqueosPantalla[0:9]
        espaciosFilaMedio = parqueosPantalla[9:17]
        espaciosFilaInferior = parqueosPantalla[17:25]
        # Se crea la fila de parqueos superior
        columnaActual = 0
        for parqueoEspecifico in espaciosFilaSuperior:
            if parqueoEspecifico.libre:
                tipoEspacio = parqueoEspecifico.tipoEspacio
                if tipoEspacio == "discapacidad":
                    colorFondoBoton = self.colorDiscapacitado
                elif tipoEspacio == "electrico":
                    colorFondoBoton = self.colorElectrico
                else:
                    colorFondoBoton = self.colorSensorVerde
            else:
                # Si está ocupado pero es de discapacidad o eléctrico, se le asigna un color diferente al normal
                tipoEspacio = parqueoEspecifico.tipoEspacio
                if tipoEspacio == "discapacidad":
                    colorFondoBoton = "#7D7FC1"
                elif tipoEspacio == "electrico":
                    colorFondoBoton = "#BEC19F"
                else:
                    colorFondoBoton = self.colorSensorRojo
            botonParqueo = tk.Button(self.venParqueo,
                                     text=parqueoEspecifico.numCampo,
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
        # Se crea un espacio entre la fila superior y la del medio, solo si la fila del medio se crea
        if len(espaciosFilaSuperior) > 0 or len(espaciosFilaMedio) > 0:
            pasilloSuperior = tk.Label(self.venParqueo,
                                       bg=self.colorFondoCrema,
                                       height=2)
            pasilloSuperior.grid(row=3, column=1, columnspan=9)
            self.listaBotonesDinamicos.append(pasilloSuperior)
        # Se crea la fila de parqueos del medio
        columnaActual = 0
        for parqueoEspecifico in espaciosFilaMedio:
            if parqueoEspecifico.libre:
                tipoEspacio = parqueoEspecifico.tipoEspacio
                if tipoEspacio == "discapacidad":
                    colorFondoBoton = self.colorDiscapacitado
                elif tipoEspacio == "electrico":
                    colorFondoBoton = self.colorElectrico
                else:
                    colorFondoBoton = self.colorSensorVerde
            else:
                # Si está ocupado pero es de discapacidad o eléctrico, se le asigna un color diferente al normal
                tipoEspacio = parqueoEspecifico.tipoEspacio
                if tipoEspacio == "discapacidad":
                    colorFondoBoton = "#2E3078"
                elif tipoEspacio == "electrico":
                    colorFondoBoton = "#5F623B"
                else:
                    colorFondoBoton = self.colorSensorRojo
            botonParqueo = tk.Button(self.venParqueo,
                                     text=parqueoEspecifico.numCampo,
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
        # Se crea el espacio entre la fila del medio y la fila inferior, solo si se crea la fila inferior
        if len(espaciosFilaMedio) > 0 or len(espaciosFilaInferior) > 0:
            pasilloInferior = tk.Label(self.venParqueo,
                                       bg=self.colorFondoCrema,
                                       height=2)
            pasilloInferior.grid(row=5, column=1, columnspan=9)
            self.listaBotonesDinamicos.append(pasilloInferior)
        # Se crea la fila de parqueos inferior
        columnaActual = 0
        for parqueoEspecifico in espaciosFilaInferior:
            if parqueoEspecifico.libre:
                tipoEspacio = parqueoEspecifico.tipoEspacio
                if tipoEspacio == "discapacidad":
                    colorFondoBoton = self.colorDiscapacitado
                elif tipoEspacio == "electrico":
                    colorFondoBoton = self.colorElectrico
                else:
                    colorFondoBoton = self.colorSensorVerde
            else:
                # Si está ocupado pero es de discapacidad o eléctrico, se le asigna un color diferente al normal
                tipoEspacio = parqueoEspecifico.tipoEspacio
                if tipoEspacio == "discapacidad":
                    colorFondoBoton = "#2E3078"
                elif tipoEspacio == "electrico":
                    colorFondoBoton = "#5F623B"
                else:
                    colorFondoBoton = self.colorSensorRojo
            botonParqueo = tk.Button(self.venParqueo,
                                     text=parqueoEspecifico.numCampo,
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
        # Se Obtiene la hora actual
        momentoActual = datetime.now()
        fechaDeHoy = momentoActual.strftime("%Y-%m-%d")
        # Se establecen variables que funcionaran como limites de horas y minutos
        horaLimite = momentoActual.hour
        minutoLimite = momentoActual.minute
        # Si se ejecuta antes de las 7 am, forzamos a que empiece a las 7 am en punto para evitar errores
        if horaLimite < 7:
            horaLimite = 7
            minutoLimite = 0
        # Se elige la hora al azar entre las 7 y la hora actual
        horaAleatoria = random.randint(7, horaLimite)
        if horaAleatoria == horaLimite:
            minutoAleatorio = random.randint(0, minutoLimite)
        else:
            minutoAleatorio = random.randint(0, 59)
        segundoAleatorio = random.randint(0, 59)
        # Usamos .zfill(2) para que si el número es un 5, se transforme en 05
        textoHora = str(horaAleatoria).zfill(2)
        textoMinuto = str(minutoAleatorio).zfill(2)
        textoSegundo = str(segundoAleatorio).zfill(2)
        resultadoFinal = f"{fechaDeHoy} {textoHora}:{textoMinuto}:{textoSegundo}"
        return resultadoFinal

    def actualizarEstadoFlechas(self):
        # Se habilitan y deshabilitan las flechas dependiendo si hay mas paginas para avanzar o retroceder o si ya llego a un tope
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
        self.mostrarEspaciosPaginaActual()

    def paginaAnterior(self):
        self.paginaActual -= 1
        self.mostrarEspaciosPaginaActual()

    def clickEspacio(self, parqueoEspecifico):
        if parqueoEspecifico.libre:
            return
        vehiculo = parqueoEspecifico.vehiculo
        if not vehiculo:
            messagebox.showerror("Error", "Este espacio no tiene un vehículo asignado correctamente.")
            return
        # Se crea la pequeña ventana
        ventanaInfoVehiculo = tk.Toplevel(self.venParqueo)
        ventanaInfoVehiculo.title(f"Espacio {parqueoEspecifico.numCampo}")
        ventanaInfoVehiculo.geometry("280x420")
        ventanaInfoVehiculo.configure(bg=self.colorFondoCrema)
        # Campo
        mensCampo = tk.Label(ventanaInfoVehiculo,
                             text="Campo:",
                             bg=self.colorFondoCrema,
                             font=("Arial", 10))
        mensCampo.place(x=25, y=15)
        comboCampo = ttk.Combobox(ventanaInfoVehiculo,
                                  values=[parqueoEspecifico.numCampo])
        comboCampo.set(parqueoEspecifico.numCampo)
        comboCampo.config(state="disabled")
        comboCampo.place(x=25, y=38, width=230)
        # Placa
        mensPlaca = tk.Label(ventanaInfoVehiculo,
                             text="Placa:",
                             bg=self.colorFondoCrema,
                             font=("Arial", 10))
        mensPlaca.place(x=25, y=75)
        entryPlaca = tk.Entry(ventanaInfoVehiculo,
                              font=("Arial", 10))
        entryPlaca.insert(0,
                          vehiculo.placa)  # Se coloca la placa del vehiculo en la caja de texto, y el 0 para que se acomo desde el inicio de la caja de texto
        entryPlaca.config(state="disabled")
        entryPlaca.place(x=25, y=98, width=230)
        # Marca
        mensMarca = tk.Label(ventanaInfoVehiculo,
                             text="Marca:",
                             bg=self.colorFondoCrema,
                             font=("Arial", 10))
        mensMarca.place(x=25, y=135)
        comboMarca = ttk.Combobox(ventanaInfoVehiculo,
                                  font=("Arial", 10))
        comboMarca.set(vehiculo.marca)
        comboMarca.config(state="disabled")
        comboMarca.place(x=25, y=158, width=230)
        # Color
        mensColor = tk.Label(ventanaInfoVehiculo,
                             text="Color:",
                             bg=self.colorFondoCrema,
                             font=("Arial", 10))
        mensColor.place(x=25, y=195)
        comboColor = ttk.Combobox(ventanaInfoVehiculo,
                                  font=("Arial", 10))
        comboColor.set(vehiculo.color)
        comboColor.config(state="disabled")
        comboColor.place(x=25, y=218, width=230)
        # Hora de entrada
        mensHora = tk.Label(ventanaInfoVehiculo,
                            text="Hora de entrada:",
                            bg=self.colorFondoCrema,
                            font=("Arial", 10))
        mensHora.place(x=25, y=255)
        horaSucia = vehiculo.horaEntrada
        horaFormateada = horaSucia
        try:
            objetoFecha = datetime.strptime(horaSucia, "%Y-%m-%d %H:%M:%S")
            horaFormateada = objetoFecha.strftime("%d/%m/%y %H:%M:%S")
        except:
            pass
        entryEntrada = tk.Entry(ventanaInfoVehiculo,
                                font=("Arial", 10))
        entryEntrada.insert(0,
                            horaFormateada)  # Se coloca el hora de entrada del vehiculo en la caja de texto, y el 0 para que se acomo desde el inicio de la caja de texto
        entryEntrada.config(state="disabled")
        entryEntrada.place(x=25, y=278, width=230)
        # Pagar
        botonPagar = tk.Button(ventanaInfoVehiculo,
                               text="Pagar",
                               font=("Arial", 10, "bold"),
                               bg="#A6B9CB",
                               fg="black",
                               relief="solid",
                               bd=1)
        # Usamos height=50 para hacer mas grande el boton
        botonPagar.place(x=25, y=330, width=230, height=50)