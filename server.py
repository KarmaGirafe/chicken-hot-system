from flask import Flask, request, jsonify
import firebase_admin
from firebase_admin import credentials, db
import os
import json
from datetime import datetime
import requests
from geopy.distance import geodesic

# Import de la fonction d'analyse
from order_analyzer import analyser_commande

app = Flask(__name__)

# Configuration
FIREBASE_URL = os.environ.get('FIREBASE_URL')

# HTML embarqué (version standalone)
INDEX_HTML = '''<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🍗 Chicken Hot Dreux - Commandes</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container { max-width: 1400px; margin: 0 auto; }
        header { text-align: center; margin-bottom: 40px; color: white; }
        header h1 { font-size: 3rem; margin-bottom: 10px; text-shadow: 2px 2px 4px rgba(0,0,0,0.2); }
        .subtitle { font-size: 1.2rem; opacity: 0.9; margin-bottom: 20px; }
        .legend { display: flex; justify-content: center; gap: 20px; flex-wrap: wrap; margin-top: 20px; }
        .badge {
            padding: 12px 24px;
            border-radius: 25px;
            font-weight: bold;
            font-size: 1.1rem;
            text-transform: uppercase;
            box-shadow: 0 4px 6px rgba(0,0,0,0.2);
        }
        .badge-livraison { background: linear-gradient(135deg, #ff6b6b, #ee5a6f); color: white; }
        .badge-emporter { background: linear-gradient(135deg, #ffa500, #ff8c00); color: white; }
        .badge-surplace { background: linear-gradient(135deg, #51cf66, #37b24d); color: white; }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }
        .stat-card { background: white; padding: 25px; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center; }
        .stat-number { display: block; font-size: 2.5rem; font-weight: bold; color: #667eea; margin-bottom: 10px; }
        .stat-label { display: block; color: #666; font-size: 0.9rem; }
        .orders-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(400px, 1fr)); gap: 25px; }
        .order-card {
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 8px 16px rgba(0,0,0,0.15);
            border-left: 8px solid;
            transition: transform 0.3s;
            animation: slideIn 0.5s ease;
        }
        .order-card:hover { transform: translateY(-5px); }
        .order-card[data-type="Livraison"] { border-left-color: #ff6b6b; background: linear-gradient(to right, #fff5f5 0%, white 10%); }
        .order-card[data-type="À emporter"] { border-left-color: #ffa500; background: linear-gradient(to right, #fff9f0 0%, white 10%); }
        .order-card[data-type="Sur place"] { border-left-color: #51cf66; background: linear-gradient(to right, #f0fff4 0%, white 10%); }
        .order-header { display: flex; justify-content: space-between; margin-bottom: 20px; padding-bottom: 15px; border-bottom: 2px solid #f0f0f0; }
        .order-time { font-size: 0.9rem; color: #666; }
        .order-type {
            font-size: 1.4rem;
            font-weight: bold;
            text-transform: uppercase;
            padding: 10px 20px;
            border-radius: 8px;
            text-align: center;
            margin-bottom: 15px;
        }
        .order-type.type-livraison { background: linear-gradient(135deg, #ff6b6b, #ee5a6f); color: white; }
        .order-type.type-emporter { background: linear-gradient(135deg, #ffa500, #ff8c00); color: white; }
        .order-type.type-surplace { background: linear-gradient(135deg, #51cf66, #37b24d); color: white; }
        .contact-info { background: #f8f9fa; padding: 15px; border-radius: 8px; margin-bottom: 15px; }
        .contact-info p { margin: 5px 0; font-size: 0.95rem; }
        .phone-number { color: #667eea; font-weight: bold; font-size: 1.1rem; }
        .delivery-address { color: #ff6b6b; font-weight: 500; }
        .order-items { margin: 20px 0; }
        .item { display: flex; justify-content: space-between; padding: 12px; background: #f8f9fa; border-radius: 8px; margin-bottom: 10px; }
        .item-name { font-weight: 500; color: #333; }
        .item-quantity { color: #667eea; font-weight: bold; margin-right: 5px; }
        .item-price { font-weight: bold; color: #2d3748; }
        .order-pricing { border-top: 2px solid #f0f0f0; padding-top: 15px; margin-top: 15px; }
        .price-row { display: flex; justify-content: space-between; margin: 8px 0; font-size: 0.95rem; }
        .price-row.total { font-size: 1.5rem; font-weight: bold; color: #667eea; margin-top: 10px; padding-top: 10px; border-top: 2px solid #667eea; }
        .status-badge { padding: 6px 12px; border-radius: 20px; font-size: 0.85rem; font-weight: bold; background: #fff3cd; color: #856404; }
        .empty-state { text-align: center; padding: 60px 20px; color: white; }
        .empty-state h2 { font-size: 2rem; margin-bottom: 10px; }
        @keyframes slideIn { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
        @media (max-width: 768px) { .orders-grid { grid-template-columns: 1fr; } header h1 { font-size: 2rem; } }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🍗 Chicken Hot Dreux</h1>
            <p class="subtitle">Commandes en temps réel</p>
            <div class="legend">
                <span class="badge badge-livraison">Livraison</span>
                <span class="badge badge-emporter">À emporter</span>
                <span class="badge badge-surplace">Sur place</span>
            </div>
        </header>
        <div id="stats" class="stats">
            <div class="stat-card"><span class="stat-number" id="total-orders">0</span><span class="stat-label">Commandes totales</span></div>
            <div class="stat-card"><span class="stat-number" id="pending-orders">0</span><span class="stat-label">En attente</span></div>
            <div class="stat-card"><span class="stat-number" id="total-revenue">0€</span><span class="stat-label">Chiffre d'affaires</span></div>
        </div>
        <div id="orders-container" class="orders-grid"></div>
    </div>
    <script>
        const FIREBASE_URL = 'https://chicken-hot-dreux-default-rtdb.europe-west1.firebasedatabase.app';
        let orders = {};
        function formatDateTime(d) {
            const date = new Date(d);
            return date.toLocaleString('fr-FR', {day:'2-digit',month:'2-digit',year:'numeric',hour:'2-digit',minute:'2-digit'});
        }
        function getTypeClass(t) {
            if (t === 'Livraison') return 'type-livraison';
            if (t === 'À emporter') return 'type-emporter';
            if (t === 'Sur place') return 'type-surplace';
            return 'type-default';
        }
        function createOrderHTML(id, o) {
            const t = o.type_service || 'Non spécifié';
            const isDel = t === 'Livraison';
            let contact = '';
            if (isDel && (o.phone_number || o.delivery_address)) {
                contact = '<div class="contact-info">';
                if (o.phone_number && o.phone_number !== 'Non fourni') contact += `<p><strong>📞 Téléphone:</strong> <span class="phone-number">${o.phone_number}</span></p>`;
                if (o.formatted_address || o.delivery_address) contact += `<p><strong>📍 Adresse:</strong> <span class="delivery-address">${o.formatted_address || o.delivery_address}</span></p>`;
                if (o.distance_km > 0) contact += `<p>Distance: ${o.distance_km} km</p>`;
                contact += '</div>';
            }
            const items = o.items.map(i => `<div class="item"><span class="item-name"><span class="item-quantity">${i.quantity}×</span>${i.name}</span><span class="item-price">${i.total_price.toFixed(2)}€</span></div>`).join('');
            let delFee = '';
            if (isDel && o.delivery_fee > 0) delFee = `<div class="price-row"><span>Frais de livraison</span><span>+${o.delivery_fee.toFixed(2)}€</span></div>`;
            return `<div class="order-card" data-type="${t}"><div class="order-header"><span class="order-time">${formatDateTime(o.timestamp)}</span><span class="status-badge">Nouvelle</span></div><div class="order-type ${getTypeClass(t)}">${t}</div>${contact}<div class="order-items">${items}</div><div class="order-pricing"><div class="price-row"><span>Sous-total</span><span>${o.subtotal.toFixed(2)}€</span></div>${delFee}<div class="price-row total"><span>TOTAL</span><span>${o.total.toFixed(2)}€</span></div></div></div>`;
        }
        function updateStats() {
            const ol = Object.values(orders);
            document.getElementById('total-orders').textContent = ol.length;
            document.getElementById('pending-orders').textContent = ol.filter(o => o.status === 'pending').length;
            document.getElementById('total-revenue').textContent = ol.reduce((s, o) => s + (o.total || 0), 0).toFixed(2) + '€';
        }
        function displayOrders() {
            const c = document.getElementById('orders-container');
            if (Object.keys(orders).length === 0) {
                c.innerHTML = '<div class="empty-state"><h2>🍗 En attente de commandes...</h2><p>Les nouvelles commandes apparaîtront automatiquement ici</p></div>';
                return;
            }
            const sorted = Object.entries(orders).sort((a, b) => new Date(b[1].timestamp) - new Date(a[1].timestamp));
            c.innerHTML = sorted.map(([id, o]) => createOrderHTML(id, o)).join('');
        }
        function listenToOrders() {
            const ref = `${FIREBASE_URL}/orders.json`;
            fetch(ref).then(r => r.json()).then(d => { if (d) { orders = d; displayOrders(); updateStats(); } }).catch(e => console.error(e));
            setInterval(() => {
                fetch(ref).then(r => r.json()).then(d => { if (d) { orders = d; displayOrders(); updateStats(); } }).catch(e => console.error(e));
            }, 2000);
        }
        document.addEventListener('DOMContentLoaded', () => { console.log('🍗 Chargé'); listenToOrders(); });
    </script>
</body>
</html>
'''

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
    return INDEX_HTML

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
