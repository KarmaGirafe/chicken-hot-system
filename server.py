from flask import Flask, request, jsonify, send_from_directory
from order_analyzer import OrderAnalyzer
import firebase_admin
from firebase_admin import credentials, db
import os
import json
from datetime import datetime
import requests
from geopy.distance import geodesic

app = Flask(__name__, static_folder='static')

# Configuration
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
FIREBASE_URL = os.environ.get('FIREBASE_URL')

# Coordonnées du restaurant Chicken Hot Dreux
RESTAURANT_COORDS = (48.7333, 1.3667)  # Dreux, France

# Initialiser Firebase
firebase_key = os.environ.get('FIREBASE_KEY')
if firebase_key:
    # Si la clé est une chaîne JSON
    if isinstance(firebase_key, str):
        cred_dict = json.loads(firebase_key)
    else:
        cred_dict = firebase_key
    cred = credentials.Certificate(cred_dict)
else:
    # Sinon utiliser le fichier
    cred = credentials.Certificate('firebase-key.json')

firebase_admin.initialize_app(cred, {
    'databaseURL': FIREBASE_URL
})

# Initialiser l'analyseur de commandes
analyzer = OrderAnalyzer(OPENAI_API_KEY)

def verify_address(address):
    """Vérifie l'adresse avec Nominatim et retourne les coordonnées"""
    try:
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            'q': address,
            'format': 'json',
            'limit': 1,
            'countrycodes': 'fr'
        }
        headers = {
            'User-Agent': 'ChickenHotDreux/1.0'
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=5)
        data = response.json()
        
        if data and len(data) > 0:
            lat = float(data[0]['lat'])
            lon = float(data[0]['lon'])
            display_name = data[0]['display_name']
            return {
                'valid': True,
                'coordinates': (lat, lon),
                'formatted_address': display_name
            }
        else:
            return {'valid': False, 'error': 'Adresse introuvable'}
    except Exception as e:
        print(f"Erreur vérification adresse: {e}")
        return {'valid': False, 'error': str(e)}

def calculate_distance(coords1, coords2):
    """Calcule la distance en km entre deux coordonnées"""
    return round(geodesic(coords1, coords2).km, 2)

def calculate_delivery_fee(distance_km, order_total):
    """Calcule les frais de livraison - GRATUIT si commande > 20€"""
    if order_total > 20:
        return 0.00
    
    # Sinon, frais basés sur la distance
    if distance_km <= 3:
        return 2.00
    elif distance_km <= 5:
        return 3.00
    elif distance_km <= 8:
        return 4.00
    else:
        return 5.00

@app.route('/')
def index():
    """Serve l'interface web"""
    return send_from_directory('static', 'index.html')

@app.route('/webhook/retell', methods=['POST'])
def retell_webhook():
    """Webhook pour recevoir les appels de Retell AI"""
    try:
        data = request.json
        print(f"Webhook Retell reçu: {json.dumps(data, indent=2)}")
        
        # Extraire les données de l'appel
        call_data = data.get('call', {})
        call_id = call_data.get('call_id')
        transcript = call_data.get('transcript', '')
        
        # Extraire le numéro de téléphone de l'appelant
        from_number = call_data.get('from_number', 'Non fourni')
        
        if not transcript:
            return jsonify({
                'status': 'error',
                'message': 'Pas de transcription disponible'
            }), 400
        
        # Vérifier les doublons
        ref = db.reference('orders')
        existing_orders = ref.order_by_child('call_id').equal_to(call_id).get()
        
        if existing_orders:
            print(f"Commande {call_id} déjà traitée")
            return jsonify({
                'status': 'duplicate',
                'call_id': call_id
            }), 200
        
        # Analyser la commande avec OpenAI
        order_analysis = analyzer.analyze_order(transcript)
        
        if not order_analysis:
            return jsonify({
                'status': 'error',
                'message': 'Impossible d\'analyser la commande'
            }), 500
        
        # Vérifier l'adresse de livraison
        delivery_address = order_analysis.get('delivery_address', '')
        address_info = verify_address(delivery_address)
        
        distance_km = 0
        delivery_fee = 0
        
        if address_info['valid']:
            # Calculer la distance
            distance_km = calculate_distance(RESTAURANT_COORDS, address_info['coordinates'])
            
            # Calculer les frais de livraison (gratuit si > 20€)
            subtotal = order_analysis.get('subtotal', 0)
            delivery_fee = calculate_delivery_fee(distance_km, subtotal)
        
        # Calculer le total final
        subtotal = order_analysis.get('subtotal', 0)
        total = subtotal + delivery_fee
        
        # Créer la commande
        order = {
            'call_id': call_id,
            'phone_number': from_number,
            'timestamp': datetime.now().isoformat(),
            'items': order_analysis.get('items', []),
            'delivery_address': delivery_address,
            'address_verified': address_info['valid'],
            'formatted_address': address_info.get('formatted_address', delivery_address),
            'distance_km': distance_km,
            'subtotal': subtotal,
            'delivery_fee': delivery_fee,
            'delivery_fee_waived': delivery_fee == 0 and subtotal > 20,
            'total': total,
            'notes': order_analysis.get('notes', ''),
            'status': 'pending',
            'transcript': transcript[:500]
        }
        
        # Sauvegarder dans Firebase
        new_order_ref = ref.push(order)
        
        print(f"✅ Commande {call_id} créée: {new_order_ref.key}")
        print(f"   📞 Tel: {from_number}")
        print(f"   📍 Distance: {distance_km}km")
        print(f"   💰 Total: {total}€ (Livraison: {delivery_fee}€)")
        
        return jsonify({
            'status': 'success',
            'order_id': new_order_ref.key,
            'call_id': call_id,
            'total': total,
            'delivery_fee': delivery_fee,
            'delivery_fee_waived': delivery_fee == 0 and subtotal > 20
        }), 200
        
    except Exception as e:
        print(f"❌ Erreur webhook: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Chicken Hot Dreux - Order System'
    }), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
