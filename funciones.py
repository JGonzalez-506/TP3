# Elaborado por Derian Segura y Juan Gonzalez
# Fecha de creacion: 11/06/26 a las 6:41
# Ultima modificacion: 17/06/26 18:00
# Version: 3.14.3

# importaciones
import re
import tkinter as tk
from tkinter import messagebox
import pickle
import json
import requests
import random
import math
from datetime import datetime
from tkinter import ttk
import qrcode
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

class vehiculo:
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

class espacioParqueo:
    def __init__(self, numCampo, infoVehiculo, estadiaEspacio, pagoEspacio, tipoEspacio, libre):
        # Se almacena los datos de los espacios invidualmente
        self.id= numCampo
        self.info = infoVehiculo
        self.estadia = estadiaEspacio
        self.pago = pagoEspacio
        self.tipoEspacio = tipoEspacio
        self.libre = libre

    def obtenerDatosEspacio(self, llave, valorDefecto):
        # Se crea un diccionario con los atributos de los estacionamiento para que se pueda consultar por sus datos especificos
        datosEspacios = {"numCampo": self.id,
                         "tipoEspacio": self.tipoEspacio,
                         "libre": self.libre,
                         "infoVehiculo": self.info,
                         "estadiaEspacio": self.estadia,
                         "pagoEspacio": self.pago}
        return datosEspacios.get(llave, valorDefecto)

class interfazParqueo:
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
        self.tiempoGracia = 0
        self.montoHora = 0
        # Decidimos que lo mejor que se podia hacer para poder guardas las configuraciones en segundo plano era hacer un pequeño json
        # por aparte llamado configuracion.json el cual almacena el tiempo de gracia, precio por hota y cantidad de espacios
        self.cargarConfiguracionExistente()
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
        fuenteBoton = ("Arial", 11)
        margenIzquierdo = (130, 0)
        self.botonObtener = tk.Button(self.ventana,
                                      text="Obtener vehículos y vouchers",
                                      font=fuenteBoton,
                                      command=lambda: print(f"opción 1"))
        self.botonObtener.pack(anchor="w", padx=margenIzquierdo, pady=8)
        self.botonVer = tk.Button(self.ventana,
                                  text="Ver estacionamiento",
                                  font=fuenteBoton,
                                  command=self.abrirVerEstacionamiento)
        self.botonVer.pack(anchor="w", padx=margenIzquierdo, pady=8)
        self.botonFacturar = tk.Button(self.ventana,
                                       text="Facturar 1 espacio",
                                       font=fuenteBoton,
                                       command=lambda: print(f"opción 3"))
        self.botonFacturar.pack(anchor="w",
                                padx=margenIzquierdo,
                                pady=8)
        self.botonReportes = tk.Button(self.ventana,
                                       text="Reportes",
                                       font=fuenteBoton,
                                       command=lambda: print(f"opción 4"))
        self.botonReportes.pack(anchor="w", padx=margenIzquierdo, pady=8)
        self.botonConfig = tk.Button(self.ventana,
                                     text="Configuración",
                                     font=fuenteBoton,
                                     command=self.mostrarPantallaConfiguracion)
        self.botonConfig.pack(anchor="w", padx=margenIzquierdo, pady=8)
        self.botonAcerca = tk.Button(self.ventana,
                                     text="Acerca de",
                                     font=fuenteBoton,
                                     command=lambda: print(f"opción 6"))
        self.botonAcerca.pack(anchor="w", padx=margenIzquierdo, pady=8)
        self.botonSalir = tk.Button(self.ventana,
                                    text="Salir",
                                    font=fuenteBoton,
                                    command=self.ventana.quit)
        self.botonSalir.pack(anchor="w", padx=margenIzquierdo, pady=(8, 30))
        # Se aplica el estado (habilitado/deshabilitado) de cada botón según si hay base de datos
        self.actualizarEstadoBotonesMenu()

    def actualizarEstadoBotonesMenu(self):
        # Si no existe una base de datos de parqueos, se deshabilitan todas las opciones
        # excepto "Configuración y ver estacionamiento" (que es la que permite crear la base de datos) y "Salir"
        if self.hayBaseDatos:
            estado = "normal"
        else:
            estado = "disabled"
        self.botonObtener.config(state=estado)
        self.botonVer.config(state="normal")
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
        self.venConfig.protocol(lambda: self.cerrarVentanaSecundariaYRegresar(self.venConfig))
        mensConfiguracionParqueo = tk.Label(self.venConfig,
                                            text="Configuración del Parqueo",
                                            font=("Arial", 16, "bold"),
                                            bg=self.colorFondoCrema)
        mensConfiguracionParqueo.pack(pady=20)
        mensTamannoEstacionamiento = tk.Label(self.venConfig,
                                              text="Tamaño del estacionamiento (1-75):",
                                              bg=self.colorFondoCrema,
                                              font=("Arial", 12))
        mensTamannoEstacionamiento.pack(pady=(10, 5))
        self.entradaCantidad = tk.Entry(self.venConfig,
                                        font=("Arial", 14),
                                        justify="center", width=10)
        self.entradaCantidad.pack()
        # Si ya existe base de datos, se bloquea la entrada del tamaño
        if self.hayBaseDatos:
            self.entradaCantidad.insert(0, str(self.totalParqueos))
        # Cajas de texto para Tiempo de gracia y Monto por hora
        mensTipoGracia = tk.Label(self.venConfig,
                                  text="Tiempo de gracia (minutos):",
                                  bg=self.colorFondoCrema,
                                  font=("Arial", 12))
        mensTipoGracia.pack(pady=(15, 5))
        self.entradaGracia = tk.Entry(self.venConfig,
                                      font=("Arial", 14),
                                      justify="center",
                                      width=10)
        self.entradaGracia.pack()
        self.entradaGracia.insert(0, str(self.tiempoGracia))
        mensMontoHora = tk.Label(self.venConfig,
                                text="Monto por hora (colones):", 
                                bg=self.colorFondoCrema, font=("Arial", 12))
        mensMontoHora.pack(pady=(15, 5))
        self.entradaMonto = tk.Entry(self.venConfig,
                                     font=("Arial", 14),
                                     justify="center", width=10)
        self.entradaMonto.pack()
        self.entradaMonto.insert(0, str(self.montoHora))
        # Boton para ingresar la cantidad y guardar variables
        self.botonConfirmar = tk.Button(self.venConfig,
                                        text="Guardar Configuración",
                                        font=("Arial", 12, "bold"),
                                        command=self.verificarYCrear)
        self.botonConfirmar.pack(pady=(30, 10))
        # Boton para regresar al Menú Principal sin guardar cambios
        self.botonRegresarConfig = tk.Button(self.venConfig,
                                             text="Regresar",
                                             font=("Arial", 11),
                                             command=lambda: self.cerrarVentanaSecundariaYRegresar(self.venConfig))
        self.botonRegresarConfig.pack(pady=(0, 20))

    def verificarYCrear(self):
        # Se validan y guardan los datos de configuración en memoria (Tiempo de gracia y Monto)
        try:
            gracia = int(self.entradaGracia.get())
            monto = int(self.entradaMonto.get())
            textoUsuario = self.entradaCantidad.get()
            cantidad = int(textoUsuario)
        except ValueError:
            messagebox.showwarning("Datos Inválidos", "Por favor, ingrese números enteros válidos en todos los campos.")
            return
        
        if self.hayBaseDatos:
            # Todos los datos son idénticos a los guardados
            if cantidad == self.totalParqueos and gracia == self.tiempoGracia and monto == self.montoHora:
                messagebox.showinfo("Información", "Digitó los mismos datos.")
                return
            
            # El usuario cambió la cantidad de espacios (recreación de BD)
            if cantidad != self.totalParqueos:
                confirmar = messagebox.askyesno("Base de Datos Existente", 
                                                "Ya hay una base de datos activa.\n\n"
                                                "¿Desea borrar la actual y hacer una nueva con la cantidad de espacios solicitada?\n"
                                                "Si selecciona 'No', se cancelará la acción y no se guardará ningún cambio.")
                if not confirmar:
                    return  # Termina la ejecución inmediatamente sin alterar nada
                # Si el usuario dice que si, el flujo continúa hacia abajo para sobreescribir la bd antigua
                
            # La cantidad es la misma, pero cambió el tiempo de gracia o el precio por hora
            else:
                self.tiempoGracia = gracia
                self.montoHora = monto
                # Se escriben los cambios en el JSON antes de cerrar la ventana
                datosConfig = {"tiempoGracia": self.tiempoGracia,
                               "montoHora": self.montoHora,
                               "totalParqueos": self.totalParqueos}
                try:
                    with open("configuracion.json", "w") as archivoJson:
                        json.dump(datosConfig, archivoJson, indent=4)
                except:
                    print("No se pudo guardar la configuración en memoria secundaria.")
                messagebox.showinfo("Éxito", "Los cambios se han guardado.")
                self.venConfig.destroy()
                self.ventana.deiconify()
                return

        self.tiempoGracia = gracia
        self.montoHora = monto
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
            diccionarioMasivo = {}
            for infoVehiculo in datosDescargados:
                placa = infoVehiculo.get("placa")
                diccionarioMasivo[placa] = {"marca": infoVehiculo.get("marca"),
                                            "color": infoVehiculo.get("color"),
                                            "tipo": infoVehiculo.get("tipo"),
                                            "ubicacion": "",
                                            "fechaHoraEntrada": "",
                                            "fechaHoraSalida": "",
                                            "monto": 0,
                                            "tipoPago": 0}
            print(json.dumps(diccionarioMasivo, indent=4, ensure_ascii=False))
            placaVehiculo = 0
            cantDiscapacidad = math.ceil(cantidad * 0.05)  # Se redondea hacia arriba el 5% de los espacios para discapacitados para que no queden en decimales
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
                numCampo = f"C{campoActual}"
                horaEntrada = self.generarHoraEntradaAleatoria()
                placa, marca, color, tipo = "", "", "", "discapacidad"
                if placaVehiculo < len(datosDescargados):
                    infoVehiculo = datosDescargados[placaVehiculo]
                    placa = infoVehiculo.get("placa")
                    marca = infoVehiculo.get("marca")
                    color = infoVehiculo.get("color")
                    tipo = infoVehiculo.get("tipo")
                    placaVehiculo += 1
                infoVehiculo = (placa, marca, color, tipo)
                estadiaEspacio = [numCampo, horaEntrada, ""]
                pagoEspacio = (0, 0)
                parqueosGenerados.append(espacioParqueo(
                    numCampo = numCampo,
                    infoVehiculo = infoVehiculo,
                    estadiaEspacio = estadiaEspacio,
                    pagoEspacio = pagoEspacio,
                    tipoEspacio = "discapacidad",
                    libre = True))
                campoActual += 1
            # Si el usuario confimara que quiere un espacio para un vehiculo electrico, se crea y se asignan los datos del vehiculo y el numero de campo que ocupara el espacio
            if incluyeElectrico:
                numCampo = f"C{campoActual}"
                horaEntrada = self.generarHoraEntradaAleatoria()
                placa, marca, color, tipo = "", "", "", "electrico"
                if placaVehiculo < len(datosDescargados):
                    infoVehiculo = datosDescargados[placaVehiculo]
                    placa = infoVehiculo.get("placa")
                    marca = infoVehiculo.get("marca")
                    color = infoVehiculo.get("color")
                    tipo = infoVehiculo.get("tipo")
                    placaVehiculo += 1
                infoVehiculo = (placa, marca, color, tipo)
                estadiaEspacio = [numCampo, horaEntrada, ""]
                pagoEstadia = (0, 0)
                parqueosGenerados.append(espacioParqueo(
                    numCampo = numCampo,
                    infoVehiculo = infoVehiculo,
                    estadiaEspacio = estadiaEspacio,
                    pagoEspacio = pagoEstadia,
                    tipoEspacio = "electrico",
                    libre=True))
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
                numCampo = f"C{campoActual}"
                if not estaLibre:
                    horaEntrada = self.generarHoraEntradaAleatoria()
                    placa, marca, color, tipo = "", "", "", "normal"
                    if placaVehiculo < len(datosDescargados):
                        infoVehiculo = datosDescargados[placaVehiculo]
                        placa = infoVehiculo.get("placa")
                        marca = infoVehiculo.get("marca")
                        color = infoVehiculo.get("color")
                        tipo = infoVehiculo.get("tipo")
                        placaVehiculo += 1
                    infoVehiculo = (placa, marca, color, tipo)
                    estadiaEspacio = [numCampo, horaEntrada, ""]
                else:
                    # Si está libre, van vacíos
                    infoVehiculo = ("", "", "", "")
                    estadiaEspacio = [numCampo, "", ""]
                    pagoEspacio = (0, 0)
                parqueosGenerados.append(espacioParqueo(
                    numCampo = numCampo,
                    infoVehiculo = infoVehiculo,
                    estadiaEspacio = estadiaEspacio,
                    pagoEspacio = pagoEspacio,
                    tipoEspacio = "normal",
                    libre = estaLibre))
                campoActual += 1
            # Se crea el archivo que contendra de forma binaria la base de datos del parqueo
            try:
                with open("bdParqueo.txt", "wb") as archivoBinario:
                    pickle.dump(parqueosGenerados, archivoBinario)
            except:
                messagebox.showerror("Error", "No se pudo crear el archivo de base de datos.")
            datosConfig = {"tiempoGracia": self.tiempoGracia,
                           "montoHora": self.montoHora,
                           "totalParqueos": cantidad}
            try:
                with open("configuracion.json", "w") as archivoJson:
                    json.dump(datosConfig, archivoJson, indent=4)
            except:
                print("No se pudo guardar la configuración en memoria secundaria.")
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

    def cargarConfiguracionExistente(self):
        try:
            with open("configuracion.json", "r") as archivoJson:
                datosConfig = json.load(archivoJson)
                self.tiempoGracia = datosConfig.get("tiempoGracia")
                self.montoHora = datosConfig.get("montoHora")
        except:
            # Si el archivo no existe aún, mantiene los valores en 0
            self.tiempoGracia = 0
            self.montoHora = 0

    #Ver estacionamiento
    def abrirVerEstacionamiento(self):
        # Si no hay base de datos, no se permite abrir el estacionamiento
        if not self.hayBaseDatos:
            messagebox.showinfo("Configuración Requerida", 
                                "No se detectó una base de datos activa.\n\n"
                                "Por favor, establezca la cantidad de vehículos y parámetros en la configuración.")
            self.mostrarPantallaConfiguracion()
            return
        # Se oculta el Menú Principal mientras se usa esta ventana
        self.ventana.withdraw()
        # Se crea la ventana secundaria para ver el parqueo
        self.venParqueo = tk.Toplevel(self.ventana)
        self.venParqueo.title("Ver Estacionamiento")
        self.dimensionarVentana(self.venParqueo, 1200, 700)
        self.venParqueo.configure(bg=self.colorFondoCrema)
        self.venParqueo.protocol(lambda: self.cerrarVentanaSecundariaYRegresar(self.venParqueo))
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
                                     text=parqueoEspecifico.id,
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
                                     text=parqueoEspecifico.id,
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
                                     text=parqueoEspecifico.id,
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
        esLibre = parqueoEspecifico.libre

        # Listas de opciones requeridas
        listaMarcas = ["Toyota", "Hyundai", "Nissan", "Suzuki", "Honda", "Mitsubishi", "Kia", "Ford", "Chevrolet",
                       "Mazda", "Isuzu", "BYD", "Geely", "BMW", "Volkswagen"]
        listaColores = ["Blanco", "Negro", "Gris", "Plata", "Rojo", "Azul", "Verde", "Dorado", "Beige", "Bronce"]
        listaTipos = ["Sedan", "SUV", "Pick-up", "Hatchback", "Microbus"]

        if esLibre:
            placa = ""
            marca = ""
            color = ""
            tipo = ""
            # Se toma la hora exacta del sistema al momento de abrir el espacio
            horaEntradaInterna = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            horaFormateada = datetime.now().strftime("%d/%m/%y %H:%M:%S")
            textoBoton = "Estacionar"
        else:
            placa, marca, color, tipo = parqueoEspecifico.info
            ubicacion, horaEntradaInterna, horaSalida = parqueoEspecifico.estadia
            monto, tipoPago = parqueoEspecifico.pago
            horaFormateada = horaEntradaInterna
            try:
                objetoFecha = datetime.strptime(horaEntradaInterna, "%Y-%m-%d %H:%M:%S")
                horaFormateada = objetoFecha.strftime("%d/%m/%y %H:%M:%S")
            except:
                pass
            textoBoton = "Pagar"

        # Se crea la pequeña ventana (Altura ajustada a 480 para soportar el campo "Tipo")
        ventanaInfoVehiculo = tk.Toplevel(self.venParqueo)
        ventanaInfoVehiculo.title(f"Espacio {parqueoEspecifico.id}")
        ventanaInfoVehiculo.geometry("280x480")
        ventanaInfoVehiculo.configure(bg=self.colorFondoCrema)

        # Estado dinámico: "normal"/"readonly" para escribir/seleccionar si está libre, "disabled" si está ocupado
        estadoCampos = "normal" if esLibre else "disabled"
        estadoComboBox = "readonly" if esLibre else "disabled"

        # Campo
        tk.Label(ventanaInfoVehiculo,
                 text="Campo:",
                 bg=self.colorFondoCrema,
                 font=("Arial", 10)).place(x=25, y=15)
        comboCampo = ttk.Combobox(ventanaInfoVehiculo,
                                  values=[parqueoEspecifico.id])
        comboCampo.set(parqueoEspecifico.id)
        comboCampo.config(state="disabled")
        comboCampo.place(x=25, y=38, width=230)

        # Placa
        tk.Label(ventanaInfoVehiculo,
                 text="Placa:",
                 bg=self.colorFondoCrema,
                 font=("Arial", 10)).place(x=25, y=75)
        entryPlaca = tk.Entry(ventanaInfoVehiculo,
                              font=("Arial", 10))
        entryPlaca.insert(0, placa)
        entryPlaca.config(state=estadoCampos)
        entryPlaca.place(x=25, y=98, width=230)

        # Marca
        tk.Label(ventanaInfoVehiculo,
                 text="Marca:",
                 bg=self.colorFondoCrema,
                 font=("Arial", 10)).place(x=25, y=135)
        comboMarca = ttk.Combobox(ventanaInfoVehiculo,
                                  values=listaMarcas,
                                  font=("Arial", 10),
                                  state=estadoComboBox)
        if marca: comboMarca.set(marca)
        comboMarca.place(x=25, y=158, width=230)

        # Color
        tk.Label(ventanaInfoVehiculo,
                 text="Color:",
                 bg=self.colorFondoCrema,
                 font=("Arial", 10)).place(x=25, y=195)
        comboColor = ttk.Combobox(ventanaInfoVehiculo,
                                  values=listaColores,
                                  font=("Arial", 10),
                                  state=estadoComboBox)
        if color: comboColor.set(color)
        comboColor.place(x=25, y=218, width=230)

        # Tipo
        tk.Label(ventanaInfoVehiculo,
                 text="Tipo:",
                 bg=self.colorFondoCrema,
                 font=("Arial", 10)).place(x=25, y=255)
        comboTipo = ttk.Combobox(ventanaInfoVehiculo,
                                 values=listaTipos,
                                 font=("Arial", 10),
                                 state=estadoComboBox)
        if tipo: comboTipo.set(tipo)
        comboTipo.place(x=25, y=278, width=230)

        # Hora de entrada (Solo lectura, se llena automático del sistema)
        tk.Label(ventanaInfoVehiculo,
                 text="Hora de entrada:",
                 bg=self.colorFondoCrema,
                 font=("Arial", 10)).place(x=25,
                                                                                                                  y=315)
        entryEntrada = tk.Entry(ventanaInfoVehiculo,
                                font=("Arial", 10))
        entryEntrada.insert(0, horaFormateada)
        entryEntrada.config(state="disabled")
        entryEntrada.place(x=25, y=338, width=230)

        # Botón dinámico: Cambia entre "Estacionar" y "Pagar"
        botonAccion = tk.Button(ventanaInfoVehiculo,
                                text=textoBoton,
                                font=("Arial", 10, "bold"),
                                bg="#A6B9CB",
                                fg="black",
                                relief="solid",
                                bd=1)
        botonAccion.place(x=25, y=390, width=230, height=50)

        # Asignación de funciones según el estado
        if esLibre:
            botonAccion.config(command=lambda: self.procesarEstacionamiento(
                parqueoEspecifico, entryPlaca.get(), comboMarca.get(), comboColor.get(), comboTipo.get(),
                horaEntradaInterna, ventanaInfoVehiculo))
        else:
            botonAccion.config(command=lambda: self.abrirVentanaPago(parqueoEspecifico, ventanaInfoVehiculo))

    def abrirVentanaPago(self, parqueoEspecifico, ventanaInfoVehiculo):
        horaEntrada = parqueoEspecifico.estadia[1]
        try:
            objetoEntrada = datetime.strptime(horaEntrada, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            messagebox.showerror("Error", "Formato de hora de entrada no válido.")
            return
        objetoSalida = datetime.now()
        diferencia = objetoSalida - objetoEntrada
        minutosTranscurridos = diferencia.total_seconds() / 60
        # Regla del tiempo de gracia y cálculo de horas/fracción
        if minutosTranscurridos <= self.tiempoGracia:
            montoFinal = 0
        else:
            # Se resta el tiempo de gracia para cobrar únicamente el tiempo cobrable efectivo
            minutosCobrables = minutosTranscurridos - self.tiempoGracia
            horasACobrar = math.ceil(minutosCobrables / 60)
            montoFinal = horasACobrar * self.montoHora
        # Ventana emergente para seleccionar método de pago
        ventanaPago = tk.Toplevel(self.venParqueo)
        ventanaPago.title("Procesar Facturación")
        self.dimensionarVentana(ventanaPago, 320, 240)
        ventanaPago.configure(bg=self.colorFondoCrema)
        mensMontoPagar = tk.Label(ventanaPago, 
                 text=f"Monto a Pagar: ₡{montoFinal}", 
                 font=("Arial", 12, "bold"), 
                 bg=self.colorFondoCrema)
        mensMontoPagar.pack(pady=15)
        mensTipoPago = tk.Label(ventanaPago,
                                text="Tipo de pago:",
                                font=("Arial", 10),
                                bg=self.colorFondoCrema)
        mensTipoPago.pack()
        comboTipoPago = ttk.Combobox(ventanaPago,
                                     values=["Efectivo", "SINPE", "Tarjeta"])
        comboTipoPago.set("Efectivo")
        comboTipoPago.pack(pady=10)
        def ejecutarPago():
            # Mapeo de la especificación: 1 efectivo, 2 sinpe, 3 tarjeta
            diccionarioPagos = {"Efectivo": 1, "SINPE": 2, "Tarjeta": 3}
            idPago = diccionarioPagos[comboTipoPago.get()]
            placa, marca, color, tipoVehiculo = parqueoEspecifico.info
            fEntrada = objetoEntrada.strftime("%d-%m-%Y %H:%M:%S")
            fSalida = objetoSalida.strftime("%d-%m-%Y %H:%M:%S")
            # Intentar generar el PDF de la factura
            exitoPDF = self.crearFacturaPDF(parqueoEspecifico.id, placa, marca, color, fEntrada, fSalida, montoFinal, idPago)
            if exitoPDF:
                # Modificar el estado del espacio para liberarlo
                parqueoEspecifico.libre = True
                parqueoEspecifico.info = ("", "", "", "")
                parqueoEspecifico.estadia = [parqueoEspecifico.id, "", ""]
                parqueoEspecifico.pago = (montoFinal, idPago)
                # Actualizar la base de datos binaria (.txt con pickle)
                try:
                    with open("bdParqueo.txt", "wb") as archivoBinario:
                        pickle.dump(self.baseDatosParqueos, archivoBinario)
                except:
                    print("Error al guardar la base de datos de manera binaria.")
                # Redibujar la cuadrícula en tiempo real
                self.mostrarEspaciosPaginaActual()
                messagebox.showinfo("Pago Exitoso", f"Espacio {parqueoEspecifico.id} liberado correctamente.\nFactura PDF generada.")
                ventanaPago.destroy()
                ventanaInfoVehiculo.destroy()
        botonFinalizarPago = tk.Button(ventanaPago,
                                       text="Finalizar Pago",
                                       font=("Arial", 10, "bold"), 
                                       command=ejecutarPago,
                                       bd=1)
        botonFinalizarPago.pack(pady=15)

    def crearFacturaPDF(self, idCampo, placa, marca, color, fechaEntrada, fechaSalida, monto, idPago):
        # Formato solicitado: factura_#PLACA_DD-MM-AAAA_HH:mm.pdf
        # Nota técnica: Windows prohíbe el carácter ':' en los nombres de archivos. 
        # Reemplazamos los dos puntos de la hora por guiones bajos SOLO en el nombre del archivo para evitar crash.
        fechaParaNombre = fechaSalida.replace(":", "-").replace(" ", "_")
        nombreFactura = f"factura_{placa}_{fechaParaNombre}.pdf"
        diccTipoPago = {1: "Efectivo", 2: "SINPE", 3: "Tarjeta"}
        textoPagoMostrar = diccTipoPago.get(idPago, "Desconocido")
        # Contenido codificado del QR
        infoQR = (f"Campo: {idCampo}\n"
                  f"Placa: {placa}\n"
                  f"Entrada: {fechaEntrada}\n"
                  f"Salida: {fechaSalida}\n"
                  f"Método Pago: {textoPagoMostrar}\n"
                  f"Monto: ₡{monto}")
        # Generación del archivo QR temporal
        imgQR = qrcode.make(infoQR)
        rutaQR = f"temp_qr_{placa}.png"
        imgQR.save(rutaQR)
        try:
            # Creación del lienzo PDF
            c = canvas.Canvas(nombreFactura, pagesize=letter)
            # Título del documento
            c.drawString(50, 695, "COMPROBANTE DE COMPRA - ESTACIONAMIENTO")
            # Estructuración de datos de estadía completos
            ejeY = 660
            lineasTexto = [f"Número de Campo: {idCampo}",
                           f"Placa del Vehículo: {placa}",
                           f"Marca: {marca}",
                           f"Color: {color}",
                           f"Fecha y Hora Entrada: {fechaEntrada}",
                           f"Fecha y Hora Salida: {fechaSalida}",
                           f"Identificador de Pago: {textoPagoMostrar}",
                           f"Monto Total Cobrado: ₡{monto}"]
            for linea in lineasTexto:
                c.drawString(50, ejeY, linea)
                ejeY -= 20
            # Dibujar el código QR
            ejeY -= 140
            c.setFont("Helvetica-Bold", 11)
            c.drawString(50, ejeY + 125, "Código QR de Verificación:")
            c.drawImage(rutaQR, 50, ejeY, width=110, height=110)
            c.save()
            return True
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo estructurar el PDF: {str(e)}")
            return False

    def procesarEstacionamiento(self, parqueoEspecifico, placa, marca, color, tipo, horaEntrada, ventanaInfoVehiculo):
        if not placa.strip() or not marca or not color or not tipo:
            messagebox.showwarning("Campos Incompletos",
                                   "Por favor, complete todos los campos requeridos.")
            return
        placa = placa.strip()
        patronPlaca = r"^[A-Z]{3}\d{3}|\d{6}$"
        if not re.match(patronPlaca, placa):
            messagebox.showerror(
                "Formato de Placa Inválido",
                "La placa ingresada no cuenta con un formato permitido.\n\n"
                "Formatos válidos:\n"
                "- 3 letras mayúsculas y 3 números (Ej: ABC123)\n"
                "- 6 números exactos (Ej: 123456)"
            )
            return  # Este return es vital para detener el proceso y no dejar que avance
        # Modifica el estado del espacio
        parqueoEspecifico.libre = False
        parqueoEspecifico.info = (placa, marca, color, tipo)
        parqueoEspecifico.estadia = [parqueoEspecifico.id, horaEntrada, ""]
        parqueoEspecifico.pago = (0, 0)
        # Actualiza la base de datos
        try:
            with open("bdParqueo.txt", "wb") as archivoBinario:
                pickle.dump(self.baseDatosParqueos, archivoBinario)
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar la base de datos de manera binaria: {e}")
            return
        # Genera el PDF del Voucher de entrada
        self.crearVoucherPDF(placa, marca, tipo, horaEntrada)
        # Redibuja la cuadrícula en tiempo real y cierra la ventana
        self.mostrarEspaciosPaginaActual()
        messagebox.showinfo("Éxito", f"El vehículo placa {placa} ha sido estacionado.\nVoucher PDF generado.")
        ventanaInfoVehiculo.destroy()

    def crearVoucherPDF(self, placa, marca, tipo, horaEntrada):
        try:
            # Formateo de fecha
            objetoFecha = datetime.strptime(horaEntrada, "%Y-%m-%d %H:%M:%S")
            fechaNombre = objetoFecha.strftime("%d-%m-%Y_%H-%M")
            nombreVoucher = f"voucher#{placa}_{fechaNombre}.pdf"
            # Información exclusiva del QR (Placa-Marca-Tipo-FechaHoraEntrada)
            infoQR = f"{placa}-{marca}-{tipo}-{horaEntrada}"
            # Generación del QR temporal
            imgQR = qrcode.make(infoQR)
            rutaQR = f"tempQRingreso{placa}.png"
            imgQR.save(rutaQR)
            # Creación del PDF
            c = canvas.Canvas(nombreVoucher, pagesize=letter)

            c.drawString(50, 695, "VOUCHER DE INGRESO - ESTACIONAMIENTO")
            c.drawString(50, 660, f"Placa del Vehículo: {placa}")
            c.drawString(50, 640, f"Marca: {marca}")
            c.drawString(50, 620, f"Tipo de Vehículo: {tipo}")
            c.drawString(50, 600, f"Fecha y Hora de Entrada: {horaEntrada}")

            # Dibujar el código QR
            c.setFont("Helvetica-Bold", 11)
            c.drawString(50, 560, "Código QR de Verificación:")
            c.drawImage(rutaQR, 50, 440, width=110, height=110)

            c.save()
        except Exception as e:
            print(f"Error al estructurar el PDF del Voucher: {e}")