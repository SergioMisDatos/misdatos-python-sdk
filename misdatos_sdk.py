# -*- coding: utf-8 -*-
import json
import base64
import os
import requests
from datetime import datetime, date

class mdapi2:
    """
    Cliente API nativo (Pure Python) para interactuar con los servicios de MisDatos.
    """
    def __init__(self):
        self.ultimomensajeerror = ""
        self.usuario = "" 
        self.password = "" 
        self.modo = 1  # 1 = Producción, otro valor = Test
        self.endpoint = "https://api.misdatos.com.ar/"
        self.endpointtest = "http://127.0.0.1:8000/gae2api/"
        self.service = None
        self.revision = "010.90"
        self.respuesta = None

     def conectar(self):
        self.ultimomensajeerror = ""
        bresultado = False
        if not self.password:
            self.ultimomensajeerror = "Debe asignar un token antes de conectar"
            return False
            
        try:
            # 1. Instanciamos la sesión
            self._service = requests.Session()
            
            # 2. Configuramos la estrategia de reintentos (NUEVO)
            retries = Retry(
                total=3,                # Número máximo de reintentos (3 es un buen estándar)
                backoff_factor=0.5,     # Espera 0.5s, 1s, 2s entre reintentos
                status_forcelist=[429, 500, 502, 503, 504], # Reintentar si GAE devuelve error temporal
                allowed_methods=["HEAD", "GET", "OPTIONS", "POST"] # Forzamos reintento también en POST
            )
            
            # 3. Montamos el adaptador en la sesión (NUEVO)
            adapter = HTTPAdapter(max_retries=retries)
            self._service.mount("https://", adapter)
            self._service.mount("http://", adapter)

            # 4. Actualizamos los headers (Tú código original)
            self.service.headers.update({
                "Authorization": f"Bearer {self.usuario} {self.password}",
                "Content-Type": "application/json"
            })
            bresultado = True
        except Exception as e:
            self.ultimomensajeerror = f"Error al preparar conexión API: {e}"
            
        return bresultado
    def leerPropiedad(self, cmetodo="", cpropiedad="", nindice=0, nsubindice=0, nsubsubindice=0):
        """
        Método de utilidad para recorrer la respuesta JSON estructurada.
        """
        cresultado = ""
        self.ultimomensajeerror = ""
        cpropiedad = cpropiedad.strip()
        cmetodo = cmetodo.lower().strip()
        lpropiedad = cpropiedad.split(".")
        nindicediccionario = 0
        nindicelista = 0
        ldiccionario = []
        llista = []
        
        if cmetodo in ["mdwhatsappenlacev01", "mdwhatssappenviarplantilla01v01", "mdsumarv01", "respuesta"]:
            objeto = self.respuesta
            if objeto is not None:
                if isinstance(objeto, list):
                    llista.append(objeto)
                elif isinstance(objeto, dict):
                    ldiccionario.append(objeto)
                try:
                    nindice_prop = 0
                    while nindice_prop <= len(lpropiedad)-1:
                        if lpropiedad[nindice_prop] == "diccionario":
                            nindice_prop += 1
                            if lpropiedad[nindice_prop] == "itemcantidad":
                                objeto = str(len(ldiccionario[nindicediccionario]))
                            else:
                                objeto = ldiccionario[nindicediccionario][lpropiedad[nindice_prop]]
                                nindicediccionario += 1
                        elif lpropiedad[nindice_prop] == "lista":
                            nindice_prop += 1
                            if lpropiedad[nindice_prop] == "itemcantidad":
                                objeto = str(len(llista[nindicelista]))
                            else:
                                objeto = llista[nindicelista][int(lpropiedad[nindice_prop])]
                                nindicelista += 1
                        cresultado = objeto
                        nindice_prop += 1
                        if isinstance(objeto, list):
                           llista.append(objeto)
                        elif isinstance(objeto, dict):
                           ldiccionario.append(objeto)
                except Exception as e:
                    self.ultimomensajeerror = f"error objeto {nindice_prop}{e}"
                    cresultado = ""
        else:
            self.ultimomensajeerror = "Método no definido o no compatible con leerPropiedad"
        return cresultado

    def mdwhatsappenlaceurlv01(self, nid_enlace=0, cruta_archivo=""):
        self.ultimomensajeerror = ""
        cresultado = "0"
        
        if not self.service:
            self.ultimomensajeerror = "No hay conexión. Ejecute conectar() primero."
            return cresultado
            
        if not os.path.exists(cruta_archivo):
            self.ultimomensajeerror = f"El archivo no existe: {cruta_archivo}"
            return cresultado

        # Validación de tamaño en el lado del cliente (aprox 1000 MB)
        LIMITE_KB = 1000000
        LIMITE_BYTES = LIMITE_KB * 1024
        peso_archivo = os.path.getsize(cruta_archivo)
        
        if peso_archivo > LIMITE_BYTES:
            self.ultimomensajeerror = f"El archivo supera el tamaño máximo permitido de {LIMITE_KB} KB."
            return cresultado

        try:
            with open(cruta_archivo, "rb") as f:
                contenido_bytes = f.read()
            archivo_b64 = base64.b64encode(contenido_bytes).decode('utf-8')
            nombre_archivo = os.path.basename(cruta_archivo)
            
            payload = {
                "id_enlace": nid_enlace,
                "archivo_b64": archivo_b64,
                "nombre_archivo": nombre_archivo
            }
            
            url = self.endpoint + "mdwhatsappenlaceurlv01" if self.modo == 1 else self.endpointtest + "mdwhatsappenlaceurlv01"
            respuesta = self.service.post(url, json=payload)            
            
            if respuesta.status_code == 200:
                datos_respuesta = respuesta.json()
                self.respuesta = datos_respuesta
                if datos_respuesta.get("status") == "ok":
                    cresultado = str(datos_respuesta.get("resultado", "0"))
                else:
                    self.ultimomensajeerror = datos_respuesta.get("error", "Error lógico en servidor")
            else:
                self.ultimomensajeerror = f"HTTP {respuesta.status_code}: {respuesta.text}"
                    
        except Exception as e:
            self.ultimomensajeerror = f"Error local al ejecutar mdwhatsappenlaceurlv01: {str(e)}"
            
        return cresultado
    
    def mdobteneraccesov02(self, nproveedor=0, cplan="gratuito", cservicio="", csubservicio="", cdestino="", ncantidad=1):
        self.ultimomensajeerror = ""
        cresultado = "0"
        
        if not self.service:
            self.ultimomensajeerror = "No hay conexión. Ejecute conectar() primero."
            return cresultado

        try:
            payload = {
                "proveedor": nproveedor,
                "plan": cplan,
                "servicio": cservicio,
                "subservicio": csubservicio,
                "destino": cdestino,
                "cantidad": ncantidad
            }
            
            url = self.endpoint + "mdobteneraccesov02" if self.modo == 1 else self.endpointtest + "mdobteneraccesov02"
            respuesta = self.service.post(url, json=payload)            
            
            if respuesta.status_code == 200:
                datos_respuesta = respuesta.json()
                self.respuesta = datos_respuesta
                if datos_respuesta.get("status") == "ok":
                    cresultado = str(datos_respuesta.get("resultado", "0"))
                else:
                    self.ultimomensajeerror = datos_respuesta.get("error", "Error lógico en servidor")
            else:
                self.ultimomensajeerror = f"HTTP {respuesta.status_code}: {respuesta.text}"
                    
        except Exception as e:
            self.ultimomensajeerror = f"Error local al ejecutar mdobteneraccesov02: {str(e)}"
            
        return cresultado

    def mdsumarv01(self, numero1=0, numero2=0):
        self.ultimomensajeerror = ""
        if not self.service:
            self.ultimomensajeerror = "No hay conexión. Ejecute conectar() primero."
            return 0.0

        try:
            payload = {"numero1": numero1, "numero2": numero2}
            
            url = self.endpoint + "mdsumarv01" if self.modo == 1 else self.endpointtest + "mdsumarv01"
            respuesta = self.service.post(url, json=payload)
            
            if respuesta.status_code == 200:
                datos_respuesta = respuesta.json()
                if datos_respuesta.get("status") == "ok":
                    return float(datos_respuesta.get("resultado", 0))
                else:
                    self.ultimomensajeerror = "Error lógico en servidor"
            else:
                self.ultimomensajeerror = f"HTTP {respuesta.status_code}: {respuesta.text}"
                
        except Exception as e:
            self.ultimomensajeerror = f"Error al ejecutar sumar: {e}"
            
        return 0.0

    def mdwhatsappdestinov01(self, cdestino="", ccodigo="", cemail="", nestadoproveedor="", cfecha="", cnombre="", caccionclave=""):
        self.ultimomensajeerror = ""
        cresultado = "0" 
        
        if not self.service:
            self.ultimomensajeerror = "No hay conexión. Ejecute conectar() primero."
            return cresultado

        try:
            payload = {}
            if cdestino != "": payload["destino"] = str(cdestino)
            if cemail != "": payload["email"] = str(cemail)
            if nestadoproveedor != "": payload["estadoproveedor"] = nestadoproveedor
            if cfecha != "": payload["fecha"] = str(cfecha)
            if cnombre != "": payload["nombre"] = str(cnombre)
            if ccodigo != "": payload["codigo"] = str(ccodigo)
            if caccionclave != "": payload["accionclave"] = str(caccionclave)

            url = self.endpoint + "mdwhatsappdestinov01" if self.modo == 1 else self.endpointtest + "mdwhatsappdestinov01"
            respuesta = self.service.post(url, json=payload)
            
            if respuesta.status_code == 200:
                datos_respuesta = respuesta.json()
                self.respuesta = datos_respuesta
                if datos_respuesta.get("status") == "ok":
                    cresultado = str(datos_respuesta.get("resultado", "0"))
                else:
                    self.ultimomensajeerror = datos_respuesta.get("error", "Error lógico en servidor")
            else:
                self.ultimomensajeerror = f"HTTP {respuesta.status_code}: {respuesta.text}"
                    
        except Exception as e:
            self.ultimomensajeerror = f"Error local al ejecutar mdwhatsappdestinov01: {str(e)}"
            
        return cresultado

    def mdwhatsappenlacev01(self, ctipo="", ccodigo="", cnombre="", cfecha="", cenlace="", cusuariosql="", cdescripcion="", ntotal="", nprocesado="", caccionclave=""):
        return self.mdhwatsappenlacev01(ctipo, ccodigo, cnombre, cfecha, cenlace, cusuariosql, cdescripcion, ntotal, nprocesado, caccionclave)
        
    def mdhwatsappenlacev01(self, ctipo="", ccodigo="", cnombre="", cfecha="", cenlace="", cusuariosql="", cdescripcion="", ntotal="", nprocesado="", caccionclave=""):
        self.ultimomensajeerror = ""
        cresultado = "0"
        
        if not self.service:
            self.ultimomensajeerror = "No hay conexión. Ejecute conectar() primero."
            return cresultado

        try:
            payload = {}
            if ctipo != "": payload["tipo"] = str(ctipo)
            if ccodigo != "": payload["codigo"] = str(ccodigo)
            if cnombre != "": payload["nombre"] = str(cnombre)
            if cfecha != "": payload["fecha"] = str(cfecha)
            if cenlace != "": payload["enlace"] = str(cenlace)
            if cusuariosql != "": payload["usuariosql"] = str(cusuariosql)
            if cdescripcion != "": payload["descripcion"] = str(cdescripcion)
            if ntotal != "": payload["total"] = str(ntotal)
            if nprocesado != "": payload["procesado"] = str(nprocesado)
            if caccionclave != "": payload["accionclave"] = str(caccionclave)

            url = self.endpoint + "mdhwatsappenlacev01" if self.modo == 1 else self.endpointtest + "mdhwatsappenlacev01"
            respuesta = self.service.post(url, json=payload)            
            
            if respuesta.status_code == 200:
                datos_respuesta = respuesta.json()
                self.respuesta = datos_respuesta
                if datos_respuesta.get("status") == "ok":
                    cresultado = str(datos_respuesta.get("resultado", "0"))
                else:
                    self.ultimomensajeerror = datos_respuesta.get("error", "Error lógico en servidor")
            else:
                self.ultimomensajeerror = f"HTTP {respuesta.status_code}: {respuesta.text}"
                    
        except Exception as e:
            self.ultimomensajeerror = f"Error local al ejecutar mdhwatsappenlacev01: {str(e)}"
            
        return cresultado    

    def mdwhatssappenviarplantilla01v01(self, cdestino="", ccodigo="", caccion=""):
        self.ultimomensajeerror = ""
        if not self.service:
            self.ultimomensajeerror = "No hay conexión. Ejecute conectar() primero."
            return 0.0

        try:
            payload = {
                "destino": cdestino,
                "codigo": ccodigo,
                "accion": caccion
            }
            url = self.endpoint + "mdswhatssappenviarplantilla01v01" if self.modo == 1 else self.endpointtest + "mdswhatssappenviarplantilla01v01"
            respuesta = self.service.post(url, json=payload)           
            
            if respuesta.status_code == 200:
                datos_respuesta = respuesta.json()
                self.respuesta = datos_respuesta
                if datos_respuesta.get("status") == "ok":
                    return datos_respuesta.get("resultado", 0)
                else:
                    self.ultimomensajeerror = datos_respuesta.get("error", "Error lógico en servidor")
            else:
                self.ultimomensajeerror = f"HTTP {respuesta.status_code}: {respuesta.text}"
                try:
                    self.ultimomensajeerror = respuesta.json().get("error", self.ultimomensajeerror)
                except:
                    pass
                
        except Exception as e:
            self.ultimomensajeerror = f"Error al ejecutar plantilla: {e}"
            
        return 0.0
# -- Propiedades --
    @property
    def ultimomensajeerror(self): return self._ultimomensajeerror
    @ultimomensajeerror.setter
    def ultimomensajeerror(self, v): self._ultimomensajeerror = v
    
    @property
    def password(self): return self._password
    @password.setter
    def password(self, v): self._password = v

    @property
    def usuario(self): return self._usuario
    @usuario.setter
    def usuario(self, v): self._usuario = v
    
    @property
    def modo(self): return self._modo
    @modo.setter
    def modo(self, v): self._modo = v

    @property
    def revision(self): return self._revision

    @property
    def service(self): return self._service

    @property
    def endpoint(self): return self._endpoint

    @property
    def endpointtest(self): return self._endpointtest

    @property
    def respuesta(self): return self._respuesta
    @respuesta.setter
    def respuesta(self, v): self._respuesta = v        
