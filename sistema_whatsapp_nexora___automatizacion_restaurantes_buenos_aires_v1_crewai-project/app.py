from flask import Flask, request, jsonify
import os
import logging
import requests
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

database_url = os.getenv('DATABASE_URL', '')
if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
logging.basicConfig(level=logging.INFO)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(255), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    customer_phone = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

@app.route('/')
def index():
    return 'Nexora WhatsApp Bot funcionando ✅', 200

@app.route('/webhook', methods=['GET'])
def verify_webhook():
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    if mode == 'subscribe' and token == os.getenv('VERIFY_TOKEN', 'nexora2026'):
        return challenge, 200
    return 'Verification failed', 403

@app.route('/webhook', methods=['POST'])
def handle_webhook():
    data = request.json
    logging.info("Webhook recibido: %s", data)
    try:
        if 'entry' in data:
            for entry in data['entry']:
                for change in entry.get('changes', []):
                    value = change.get('value', {})
                    messages = value.get('messages', [])
                    if messages:
                        msg = messages[0]
                        phone = msg['from']
                        text = msg.get('text', {}).get('body', '')
                        response = process_message(text, phone)
                        send_whatsapp_message(phone, response)
    except Exception as e:
        logging.error(f"Error procesando webhook: {e}")
    return 'EVENT_RECEIVED', 200

def process_message(message, phone_number):
    message = message.lower().strip()
    if message in ['1', 'ver menu', 'ver menú', 'menu', 'menú']:
        return get_restaurant_menu()
    elif message in ['2', 'hacer pedido', 'pedido']:
        return get_order_menu()
    elif message in ['3', 'consultar horario', 'horario', 'horarios']:
        return get_business_hours()
    elif message in ['4', 'hablar con humano', 'humano', 'operador']:
        return get_human_transfer()
    else:
        return get_main_menu()

def get_main_menu():
    return """🍽️ *BIENVENIDO A NEXORA RESTAURANT* 🍽️

¿En qué puedo ayudarte hoy?

1️⃣ Ver menú
2️⃣ Hacer pedido
3️⃣ Consultar horarios
4️⃣ Hablar con un operador

Escribí el número de la opción que preferís."""

def get_restaurant_menu():
    return """🍽️ *NUESTRO MENÚ* 🍽️

🥩 *CARNES*
1. Bife de Chorizo - $8.500
2. Entraña - $7.200
3. Milanesa Napolitana - $6.800

🍝 *PASTAS*
4. Ñoquis con Salsa - $4.500
5. Ravioles de Ricota - $5.200

🍕 *PIZZAS*
6. Margherita - $4.800
7. Napolitana - $5.500

🥗 *ENSALADAS*
8. Mixta - $3.200

¿Querés hacer un pedido? Escribí *2*"""

def get_order_menu():
    return """🛒 *REALIZAR PEDIDO* 🛒

Escribí el número del producto que querés:

1. Bife de Chorizo - $8.500
2. Entraña - $7.200
3. Milanesa Napolitana - $6.800
4. Ñoquis con Salsa - $4.500
5. Ravioles de Ricota - $5.200
6. Margherita - $4.800
7. Napolitana - $5.500
8. Mixta - $3.200

Te vamos a confirmar tu pedido en breve 🙌"""

def get_business_hours():
    return """🕒 *HORARIOS* 🕒

📅 *Lunes a Viernes:* 12:00 - 15:00 y 19:00 - 24:00
📅 *Sábados:* 12:00 - 24:00
📅 *Domingos:* 12:00 - 23:00

📍 Buenos Aires, Argentina
📞 +54 11 2664-7764

¿Puedo ayudarte con algo más?"""

def get_human_transfer():
    return """🤝 *ATENCIÓN PERSONALIZADA* 🤝

Te estoy conectando con un operador.

En breve alguien de nuestro equipo te va a escribir.

⏰ Tiempo estimado: 2-3 minutos
📞 O llamanos: +54 11 2664-7764

¡Gracias por tu paciencia!"""

def send_whatsapp_message(phone_number, message_text):
    phone_id = os.getenv('WHATSAPP_PHONE_ID')
    token = os.getenv('WHATSAPP_TOKEN')
    if not phone_id or not token:
        logging.error("Faltan variables WHATSAPP_PHONE_ID o WHATSAPP_TOKEN")
        return None
    url = f"https://graph.facebook.com/v17.0/{phone_id}/messages"
    headers = {
        'Authorization': f"Bearer {token}",
        'Content-Type': 'application/json'
    }
    payload = {
        'messaging_product': 'whatsapp',
        'to': phone_number,
        'type': 'text',
        'text': {'body': message_text}
    }
    try:
        response = requests.post(url, json=payload, headers=headers)
        logging.info(f"Mensaje enviado a {phone_number}: {response.status_code}")
        return response.json()
    except Exception as e:
        logging.error(f"Error enviando mensaje: {e}")
        return None

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
