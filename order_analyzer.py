from openai import OpenAI
import json

class OrderAnalyzer:
    """Analyse les commandes téléphoniques avec OpenAI"""
    
    def __init__(self, api_key):
        self.client = OpenAI(api_key=api_key)
        
        # Menu complet avec prix
        self.menu = """
=== NAANS ===
Naan Nature: 6.00€
Naan Kebab: 8.00€
Naan Poulet: 8.00€
Naan Kefta: 8.00€
Naan Cordon Bleu: 8.00€
Naan Nuggets: 7.50€
Naan Américain: 8.50€
Naan Végétarien: 7.50€
Naan Mixte: 9.00€

=== CHICKENBURGERS ===
Chickenburger Simple: 6.50€
Chickenburger Bacon: 7.50€
Chickenburger Double: 8.50€
Chickenburger XXL: 10.00€

=== EXTRAS ===
Frites: 3.00€
Boisson 33cl: 2.00€
Boisson 50cl: 3.00€
Sauce supplémentaire: 0.50€
Fromage supplémentaire: 1.00€

=== MENUS FAMILLE ===
Menu Famille 2 personnes (2 naans + 2 frites + 2 boissons): 20.00€
Menu Famille 4 personnes (4 naans + 4 frites + 4 boissons): 38.00€
"""
    
    def analyze_order(self, transcript):
        """
        Analyse une transcription d'appel et extrait la commande
        
        Args:
            transcript: Texte de la conversation téléphonique
            
        Returns:
            dict: {
                'items': [...],
                'delivery_address': 'adresse',
                'subtotal': montant,
                'notes': 'remarques'
            }
        """
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": f"""Tu es un assistant qui analyse les commandes téléphoniques pour Chicken Hot Dreux.

MENU ET PRIX:
{self.menu}

INSTRUCTIONS:
1. Extrais TOUS les articles commandés avec leurs quantités exactes
2. Identifie l'adresse de livraison complète (rue, numéro, ville)
3. Calcule le prix total en utilisant EXACTEMENT les prix du menu
4. Si un article n'est pas dans le menu, mets son prix à 0.00€ et note "Prix inconnu"
5. Note toutes les remarques importantes (allergies, demandes spéciales, etc.)

FORMAT DE RÉPONSE (JSON uniquement):
{{
    "items": [
        {{"name": "Nom exact de l'article", "quantity": nombre, "unit_price": prix, "total_price": prix_total}}
    ],
    "delivery_address": "adresse complète avec numéro, rue et ville",
    "subtotal": montant_total,
    "notes": "remarques éventuelles"
}}

IMPORTANT: Réponds UNIQUEMENT avec du JSON valide, sans texte avant ou après."""
                    },
                    {
                        "role": "user",
                        "content": f"Transcription de l'appel:\n{transcript}"
                    }
                ],
                temperature=0.3
            )
            
            result = response.choices[0].message.content
            
            # Nettoyer le JSON si nécessaire
            if "```json" in result:
                result = result.split("```json")[1].split("```")[0].strip()
            elif "```" in result:
                result = result.split("```")[1].split("```")[0].strip()
            
            # Parser le JSON
            order_data = json.loads(result)
            
            # Vérifier que les champs requis sont présents
            if 'items' not in order_data:
                order_data['items'] = []
            if 'delivery_address' not in order_data:
                order_data['delivery_address'] = ''
            if 'subtotal' not in order_data:
                order_data['subtotal'] = 0.0
            if 'notes' not in order_data:
                order_data['notes'] = ''
            
            return order_data
            
        except json.JSONDecodeError as e:
            print(f"❌ Erreur parsing JSON: {e}")
            print(f"Réponse brute: {result}")
            return None
            
        except Exception as e:
            print(f"❌ Erreur analyse OpenAI: {e}")
            import traceback
            traceback.print_exc()
            return None
