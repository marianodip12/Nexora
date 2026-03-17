from flask import Flask, request, jsonify
import os
import logging
import requests
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

logging.basicConfig(level=logging.INFO)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(255), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    customer_phone = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Order {self.id}: {self.item_name} x {self.quantity}>'

with app.app_context():
    db.create_all()

@app.route('/webhook', methods=['GET'])
def verify_webhook():
    verify_token = request.args.get('hub.verify_token')
    if verify_token == os.getenv('VERIFY_TOKEN', 'nexora2026'):
        return request.args.get('hub.challenge'), 200
    return 'Verification failed', 403

@app.route('/webhook', methods=['POST'])
def handle_webhook():
    data = request.json
    logging.info("Received webhook data: %s", data)

    if 'entry' in data:
        for entry in data['entry']:
            if 'changes' in entry:
                for change in entry['changes']:
                    if 'value' in change and 'messages' in change['value']:
                        message_data = change['value']['messages'][0]
                        phone_number = message_data['from']
                        user_message = message_data.get('text', {}).get('body', '')
                        response = process_message(user_message, phone_number)
                        send_whatsapp_message(phone_number, response)

    return 'EVENT_RECEIVED', 200

def process_message(message, phone_number):
    message = message.lower().strip()

    if not message:
        return get_main_menu()
    if message in ['1', 'ver menu', 'ver menú', 'menu']:
        return get_restaurant_menu()
    elif message in ['2', 'hacer pedido', 'pedido']:
        return get_order_menu()
    elif message in ['3', 'consultar horario', 'horario']:
        return get_business_hours()
    elif message in ['4', 'hablar con humano', 'humano']:
        return get_human_transfer()
    else:
        return get_main_menu()

def get_main_menu():
    return """🍽️ *BIENVENIDO A NEXORA RESTAURANT* 🍽️

¿En qué puedo ayudarte hoy?

1️⃣ Ver menú
2️⃣ Hacer pedido
3️⃣ Consultar horario
4️⃣ Hablar con humano

Escribí el número de la opción que preferís."""

def get_restaurant_menu():
    return """🍽️ *MENÚ* 🍽️

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

¿Querés hacer un pedido? Escribí '2'"""

def get_order_menu():
    return """🛒 *REALIZAR PEDIDO* 🛒

Escribí el número del producto que querés pedir:

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
8. Mixta - $3.200"""

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
📞 También podés llamarnos: +54 11 2664-7764

¡Gracias por tu paciencia!"""

def send_whatsapp_message(phone_number, message_text):
    url = f"https://graph.facebook.com/v17.0/{os.getenv('WHATSAPP_PHONE_ID')}/messages"
    headers = {
        'Authorization': f"Bearer {os.getenv('WHATSAPP_TOKEN')}",
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
        logging.info(f"Sent message to {phone_number}: {response.status_code}")
        return response.json()
    except Exception as e:
        logging.error(f"Error sending message: {str(e)}")
        return None

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
