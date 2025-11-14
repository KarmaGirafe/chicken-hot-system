"""
Script de test Firebase - Vérifie que tout fonctionne
"""

import os
import requests

def test_firebase_connection():
    """Teste la connexion Firebase"""
    
    firebase_url = os.environ.get('FIREBASE_URL')
    
    if not firebase_url:
        print("❌ FIREBASE_URL manquant dans les variables d'environnement")
        print("   Ajoute : export FIREBASE_URL=https://ton-projet.firebaseio.com")
        return False
    
    print(f"🔍 Test de connexion à Firebase...")
    print(f"   URL : {firebase_url}")
    
    try:
        # Test de lecture
        url = f"{firebase_url}/orders.json"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if data:
                nb_commandes = len(data)
                print(f"\n✅ CONNEXION RÉUSSIE !")
                print(f"   {nb_commandes} commande(s) trouvée(s) dans la BDD")
                print(f"\n📊 Aperçu des commandes :")
                
                for order_id, order in list(data.items())[:3]:
                    print(f"\n   ID: {order_id}")
                    print(f"   Type: {order.get('type_service', 'N/A')}")
                    print(f"   Total: {order.get('total', 0)}€")
                    print(f"   Timestamp: {order.get('timestamp', 'N/A')}")
                
                if nb_commandes > 3:
                    print(f"\n   ... et {nb_commandes - 3} autre(s)")
                
                return True
            else:
                print(f"\n⚠️ Base de données vide")
                print(f"   Aucune commande trouvée")
                return True
        
        elif response.status_code == 401:
            print(f"\n❌ ERREUR D'AUTHENTIFICATION")
            print(f"   Les règles Firebase bloquent l'accès")
            print(f"\n💡 Solution : Change les règles Firebase en mode test :")
            print(f"""
   {
     "rules": {
       ".read": true,
       ".write": true
     }
   }
            """)
            return False
        
        else:
            print(f"\n❌ ERREUR HTTP {response.status_code}")
            print(f"   {response.text}")
            return False
    
    except requests.exceptions.Timeout:
        print(f"\n❌ TIMEOUT")
        print(f"   Firebase ne répond pas")
        return False
    
    except Exception as e:
        print(f"\n❌ ERREUR : {e}")
        return False


def test_firebase_write():
    """Teste l'écriture dans Firebase"""
    
    firebase_url = os.environ.get('FIREBASE_URL')
    
    if not firebase_url:
        return False
    
    print(f"\n🔍 Test d'écriture dans Firebase...")
    
    try:
        url = f"{firebase_url}/test.json"
        test_data = {"test": "ok", "timestamp": "test"}
        
        response = requests.put(url, json=test_data, timeout=10)
        
        if response.status_code == 200:
            print(f"✅ ÉCRITURE RÉUSSIE !")
            
            # Supprime le test
            requests.delete(url, timeout=10)
            print(f"✅ Nettoyage effectué")
            return True
        else:
            print(f"❌ ERREUR ÉCRITURE : {response.status_code}")
            return False
    
    except Exception as e:
        print(f"❌ ERREUR : {e}")
        return False


if __name__ == '__main__':
    print("=" * 70)
    print("🍗 TEST FIREBASE - CHICKEN HOT DREUX")
    print("=" * 70)
    
    # Test lecture
    read_ok = test_firebase_connection()
    
    # Test écriture
    if read_ok:
        write_ok = test_firebase_write()
    
    print("\n" + "=" * 70)
    if read_ok:
        print("✅ FIREBASE FONCTIONNE !")
        print("\nTon interface web devrait maintenant afficher les commandes.")
    else:
        print("❌ PROBLÈME AVEC FIREBASE")
        print("\nSuis les instructions ci-dessus pour corriger.")
    print("=" * 70)
