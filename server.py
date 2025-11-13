from flask import Flask, request, jsonify, send_from_directory
import firebase_admin
from firebase_admin import credentials, db
import os
import json
from datetime import datetime
import requests
from geopy.distance import geodesic

# Import de la fonction d'analyse
from order_analyzer import analyser_commande

app = Flask(__name__, static_folder='static')

# Configuration
FIREBASE_URL = os.environ.get('FIREBASE_URL')

# Coordonnées du restaurant Chicken Hot Dreux
RESTAURANT_COORDS = (48.7333, 1.3667)  # Dreux, France

# Initialiser Firebase
firebase_key = os.environ.get('FIREBASE_KEY')
if firebase_key:
    if isinstance(firebase_key, str):
        cred_dict = json.loads(firebase_key)
    else:
        cred_dict = firebase_key
    cred = credentials.Certificate(cred_dict)
else:
    cred = credentials.Certificate('firebase-key.json')

firebase_admin.initialize_app(cred, {
    'databaseURL': FIREBASE_URL
})

def verify_address(address):
    """Vérifie l'adresse avec Nominatim et retourne les coordonnées"""
    if not address or address == '':
        return {'valid': False, 'error': 'Pas d\'adresse'}
    
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
        print(f"📞 Webhook Retell reçu")
        
        # Extraire les données de l'appel
        call_data = data.get('call', {})
        call_id = call_data.get('call_id')
        transcript = call_data.get('transcript', '')
        from_number = call_data.get('from_number', 'Non fourni')
        
        if not transcript:
            return jsonify({
                'status': 'error',
                'message': 'Pas de transcription'
            }), 400
        
        # Vérifier les doublons (sans index)
        ref = db.reference('orders')
        all_orders = ref.get()
        
        if all_orders:
            for order_id, order_data in all_orders.items():
                if order_data.get('call_id') == call_id:
                    print(f"⚠️ Commande {call_id} déjà traitée")
                    return jsonify({'status': 'duplicate', 'call_id': call_id}), 200
        
        # Analyser la commande
        print(f"🤖 Analyse de la commande...")
        analysis = analyser_commande(transcript)
        
        if not analysis:
            return jsonify({'status': 'error', 'message': 'Analyse impossible'}), 500
        
        print(f"✅ Analyse OK: {analysis.get('articles', 'N/A')}")
        
        # Traiter l'adresse de livraison SEULEMENT si c'est une livraison
        type_service = analysis.get('type_service', 'Non spécifié')
        delivery_address = analysis.get('adresse_livraison', '')
        address_info = {'valid': False}
        distance_km = 0
        delivery_fee = 0
        
        # Calculer les frais de livraison UNIQUEMENT si c'est une livraison
        if type_service == 'Livraison' and delivery_address and delivery_address != '':
            print(f"📍 Vérification adresse: {delivery_address}")
            address_info = verify_address(delivery_address)
            
            if address_info['valid']:
                distance_km = calculate_distance(RESTAURANT_COORDS, address_info['coordinates'])
                print(f"🗺️ Distance: {distance_km} km")
                
                subtotal = analysis.get('prix_total', 0)
                delivery_fee = calculate_delivery_fee(distance_km, subtotal)
                print(f"💰 Frais livraison: {delivery_fee}€ (sous-total: {subtotal}€)")
        else:
            # Pas de frais de livraison pour sur place ou à emporter
            delivery_fee = 0
        
        # Calculer le total
        subtotal = analysis.get('prix_total', 0)
        total = subtotal + delivery_fee
        
        # Préparer les items
        items = []
        if 'articles_detailles' in analysis and analysis['articles_detailles']:
            items = [
                {
                    'name': art['nom'],
                    'quantity': art.get('quantite', 1),
                    'unit_price': art.get('prix', 0),
                    'total_price': art.get('prix', 0) * art.get('quantite', 1)
                }
                for art in analysis['articles_detailles']
            ]
        else:
            items = [{
                'name': analysis.get('articles', 'Non spécifié'),
                'quantity': 1,
                'unit_price': subtotal,
                'total_price': subtotal
            }]
        
        # Créer la commande
        order = {
            'call_id': call_id,
            'phone_number': from_number,
            'timestamp': datetime.now().isoformat(),
            'type_appel': analysis.get('type_appel', 'commande'),
            'type_service': type_service,
            'items': items,
            'delivery_address': delivery_address if type_service == 'Livraison' else '',
            'address_verified': address_info.get('valid', False),
            'formatted_address': address_info.get('formatted_address', delivery_address) if type_service == 'Livraison' else '',
            'distance_km': distance_km,
            'subtotal': subtotal,
            'delivery_fee': delivery_fee,
            'delivery_fee_waived': delivery_fee == 0 and subtotal > 20 and type_service == 'Livraison',
            'total': total,
            'notes': analysis.get('notes', ''),
            'status': 'pending',
            'transcript': transcript[:500]
        }
        
        # Sauvegarder dans Firebase
        new_order_ref = ref.push(order)
        
        print(f"✅ Commande {call_id} sauvegardée")
        print(f"   📞 Tel: {from_number}")
        print(f"   📍 Distance: {distance_km}km")
        print(f"   💰 Total: {total}€ (Livraison: {delivery_fee}€)")
        
        return jsonify({
            'status': 'success',
            'order_id': new_order_ref.key,
            'call_id': call_id,
            'total': total,
            'delivery_fee': delivery_fee
        }), 200
        
    except Exception as e:
        print(f"❌ ERREUR webhook: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Chicken Hot Dreux - Order System'
    }), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 Démarrage serveur sur port {port}")
    app.run(host='0.0.0.0', port=port, debug=True)
