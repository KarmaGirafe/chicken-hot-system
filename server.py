from flask import Flask, request, jsonify, send_from_directory
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, db
import os
import json
from order_analyzer import analyser_commande

app = Flask(__name__, static_folder='static')

# Cache pour éviter les duplicatas
call_cache = {}
CACHE_EXPIRY = 300  # 5 minutes

def is_duplicate_call(call_id, timestamp):
    """Vérifie si l'appel a déjà été traité"""
    now = datetime.now().timestamp()
    
    # Nettoie le cache des vieux appels
    expired = [cid for cid, ts in call_cache.items() if now - ts > CACHE_EXPIRY]
    for cid in expired:
        del call_cache[cid]
    
    # Vérifie si déjà traité
    if call_id in call_cache:
        print(f"⚠️ Appel {call_id} déjà traité - Ignoré")
        return True
    
    call_cache[call_id] = timestamp
    return False

# Initialise Firebase
firebase_key = os.environ.get('FIREBASE_KEY')
if firebase_key:
    cred_dict = json.loads(firebase_key)
    cred = credentials.Certificate(cred_dict)
else:
    cred = credentials.Certificate('firebase-key.json')

firebase_admin.initialize_app(cred, {
    'databaseURL': os.environ.get('FIREBASE_URL', 'https://TON-PROJET.firebaseio.com')
})

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('static', path)

@app.route('/api/config')
def get_config():
    return jsonify({
        'databaseURL': os.environ.get('FIREBASE_URL', 'https://TON-PROJET.firebaseio.com')
    })

@app.route('/health')
def health():
    return jsonify({'status': 'ok', 'timestamp': datetime.now().isoformat()}), 200

@app.route('/webhook/retell', methods=['POST'])
def webhook_retell():
    try:
        data = request.json
        call = data.get('call', {})
        
        transcript = call.get('transcript', '')
        start_time = call.get('start_timestamp')
        call_id = call.get('call_id')
        duration = call.get('duration_ms', 0) // 1000
        
        # ✅ VÉRIFIE SI DÉJÀ TRAITÉ
        if is_duplicate_call(call_id, start_time):
            return jsonify({'status': 'duplicate', 'message': 'Call already processed'}), 200
        
        date_obj = datetime.fromtimestamp(start_time / 1000)
        date_str = date_obj.strftime('%d/%m/%Y')
        heure_str = date_obj.strftime('%H:%M')
        
        # Analyse avec OpenAI
        print(f"📞 Analyse appel {call_id} avec OpenAI...")
        analyse = analyser_commande(transcript)
        
        print(f"✅ Résultat: {analyse['type_appel']} - {analyse['articles']} - {analyse['prix_total']}€")
        
        # Sauvegarde appel
        ref_appels = db.reference('appels')
        ref_appels.push({
            'date': date_str,
            'heure': heure_str,
            'call_id': call_id,
            'duree': duration,
            'type': analyse['type_appel'],
            'cout': 0.79,
            'timestamp': start_time
        })
        
        # Si commande valide
        if analyse['type_appel'] == 'commande' and analyse['nombre_articles'] > 0:
            numero_commande = f"CMD-{date_obj.strftime('%Y%m%d-%H%M%S')}"
            
            ref_commandes = db.reference('commandes')
            new_ref = ref_commandes.push({
                'numero': numero_commande,
                'date': date_str,
                'heure': heure_str,
                'type_service': analyse['type_service'],
                'articles': analyse['articles'],
                'total': analyse['prix_total'],
                'statut': 'En attente',
                'call_id': call_id,
                'notes': analyse.get('notes', ''),
                'timestamp': start_time
            })
            
            print(f"💾 Commande sauvegardée: {numero_commande}")
        
        return jsonify({
            'status': 'success',
            'type': analyse['type_appel'],
            'articles': analyse['articles'],
            'total': analyse['prix_total']
        }), 200
        
    except Exception as e:
        print(f"❌ Erreur webhook: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/commande/<commande_id>/statut', methods=['PUT'])
def update_statut(commande_id):
    try:
        data = request.json
        nouveau_statut = data.get('statut', 'Prête')
        
        ref = db.reference(f'commandes/{commande_id}')
        ref.update({'statut': nouveau_statut})
        
        return jsonify({'status': 'success'}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
