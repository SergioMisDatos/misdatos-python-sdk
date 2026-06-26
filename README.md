# MisDatos Python SDK

Un cliente ligero y *Pure Python* para interactuar con la API REST de los servicios de **MisDatos**.

Este SDK proporciona una interfaz orientada a objetos para autenticarse y consumir los endpoints de la plataforma (acceso a servicios, gestión de WhatsApp, enlaces URL, entre otros) sin depender de librerías complejas.

## Requisitos

- Python 3.7 o superior.
- Librería `requests`.

## Instalación

1. Clona este repositorio o descarga el archivo `misdatos_sdk.py`.
2. Instala las dependencias:

```bash
pip install -r requirements.txt

Abre el archivo ejemplo.py y reemplaza "tu_usuario_token" y "tu_clave_token" con tus credenciales reales obtenidas en www.misdatos.com.ar/whatsapp/0.

Ejecuta el script desde tu terminal:
python ejemplo.py
recordar que el numero destino debe entrar a www.misatos.com.ar/bot para aceptar recibir mensaje desde el chatbot
