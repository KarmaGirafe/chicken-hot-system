"""
Analyseur intelligent de commandes avec OpenAI
Compatible avec le nouveau système de livraison
"""

from openai import OpenAI
import json
import os

# Menu pour le contexte de l'IA
MENU_CONTEXT = """
=== MENU CHICKEN HOT DREUX ===

NAANS (Wraps):
- Mixte (7,50€ seul / 9,50€ menu)
- Spécial (7,50€ seul / 9,50€ menu)
- Country (7,50€ seul / 9,50€ menu)
- Classico (6,90€ seul / 8,90€ menu)
- Classic (6,90€ seul / 8,90€ menu)
- Curry (6,90€ seul / 8,90€ menu)
- Royal (7,50€ seul / 9,50€ menu)
- Oriental (7,50€ seul / 9,50€ menu)
- RoyalBacon (7,50€ seul / 9,50€ menu)
- DoubleFish (6,50€ seul / 8,50€ menu)

CHICKENBURGERS:
- Légende (7,00€ seul / 9,00€ menu)
- Wafelé (6,50€ seul / 8,50€ menu)
- FiletBurger (5,90€ seul / 7,90€ menu)
- BigBacon (6,50€ seul / 8,50€ menu)
- BigChicken (6,50€ seul / 8,50€ menu)
- FiletBBQ (6,50€ seul / 8,50€ menu)

CLASSIQUEBURGERS:
- Fish (5,30€ seul / 7,30€ menu)
- Cheese (3,50€ seul / 5,50€ menu)
- BigCheese (4,90€ seul / 6,90€ menu)

EXTRAS:
- Tenders x3 (3,50€) / x7 (6,90€) / x14 (12,50€)
- Pilons x3 (4,90€) / x5 (7,90€)
- Wings x3 (2,90€) / x6 (4,90€) / x10 (8,00€) / x15 (11,40€)
- Nuggets x6 (4,90€)
- Frites (1,70€)
- Camembert x6 (4,90€)
- Jalapeños x6 (4,90€)
- MozzaSticks x6 (4,90€)
- Cheese Naan (2,90€)

CHICKEN BOX (avec frites & boisson):
- Menu Wings x6 (6,90€) / x10 (10,00€) / x15 (13,40€)
- Menu Tenders x7 (8,90€) / x14 (14,50€)
- Menu Pilons x3 (6,90€) / x5 (9,90€)

FAMILY BOX:
- Menu XXL (18,50€)
- Menu Friends (27,90€)
- Menu Only (36,50€)
- Menu Family (34,90€)

MENU ENFANT (5,90€): Burger Junior ou 5 Nuggets ou 1 Wrap + frites + jus + compote ou Kinder

IMPORTANT: 
- "Menu" = article + frites + boisson
- "Seul" = juste l'article
"""

def analyser_commande_avec_openai(transcript):
    """
    Analyse la transcription avec OpenAI GPT-4o
    
    Args:
        transcript (str): Transcription de l'appel
    
    Returns:
        dict: Analyse de la commande avec adresse de livraison
    """
    
    # Initialise le client OpenAI
    try:
        api_key = os.environ.get('OPENAI_API_KEY')
        if not api_key:
            print("⚠️ OPENAI_API_KEY manquant - utilisation du fallback")
            return analyser_commande_simple(transcript)
        
        client = OpenAI(api_key=api_key)
    except Exception as e:
        print(f"❌ Erreur initialisation OpenAI: {e}")
        return analyser_commande_simple(transcript)
    
    prompt = f"""Tu es un système d'analyse de commandes pour le restaurant Chicken Hot Dreux.

TRANSCRIPTION DE L'APPEL CLIENT :
{transcript}

MENU DISPONIBLE :
{MENU_CONTEXT}

TÂCHE : Analyse cette transcription et extrais TOUTES les informations de commande.

Réponds UNIQUEMENT avec un JSON strict (pas de markdown, pas de texte avant/après) :

{{
  "type_appel": "commande" ou "renseignement",
  "type_service": "Sur place" ou "À emporter" ou "Livraison" ou "Non spécifié",
  "articles": [
    {{"nom": "Nom exact", "prix": 0.00, "quantite": 1}}
  ],
  "adresse_livraison": "Adresse complète si livraison (rue, numéro, ville)",
  "prix_total": 0.00,
  "notes": "Précisions éventuelles (épicé, nature, etc.)"
}}

RÈGLES IMPORTANTES :
1. Si le client demande juste des informations/horaires/question → type_appel = "renseignement"
2. Si le client commande de la nourriture → type_appel = "commande"
3. Détecte si c'est "Menu" (avec frites+boisson) ou "Seul" (juste le sandwich)
4. Si le client mentionne une adresse → type_service = "Livraison" et extrais l'adresse complète dans adresse_livraison
5. Si "sur place" mentionné → type_service = "Sur place"
6. Si "emporter" ou "à emporter" → type_service = "À emporter"
7. Détecte TOUTES les quantités mentionnées
8. Si le client se corrige, prends SEULEMENT la dernière version
9. Pour les extras (tenders, wings, pilons), détecte bien la quantité exacte
10. Calcule le prix_total en additionnant tous les articles × quantités

EXEMPLES :
- "Un curry" → Menu Curry (8,90€)
- "Deux curry pour livrer au 15 rue de la République à Dreux" → 2× Menu Curry (17,80€), Livraison, adresse: "15 rue de la République, Dreux"
- "Un curry et 6 wings" → Menu Curry (8,90€) + 6 Wings (4,90€) = 13,80€
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "Tu es un expert en extraction de données de commandes de restaurant. Tu réponds UNIQUEMENT en JSON strict, sans texte supplémentaire."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.1,
            max_tokens=500,
            response_format={"type": "json_object"}
        )
        
        result_text = response.choices[0].message.content.strip()
        result = json.loads(result_text)
        
        # Validation
        if 'type_appel' not in result:
            result['type_appel'] = 'commande'
        
        if 'type_service' not in result:
            result['type_service'] = 'Non spécifié'
        
        if 'articles' not in result or not result['articles']:
            result['articles'] = []
        
        if 'prix_total' not in result:
            result['prix_total'] = 0
        
        if 'adresse_livraison' not in result:
            result['adresse_livraison'] = ''
        
        # Formatte les articles
        articles_str = ', '.join([
            f"{art['quantite']}× {art['nom']}" if art['quantite'] > 1 else art['nom']
            for art in result['articles']
        ])
        
        return {
            'type_appel': result['type_appel'],
            'type_service': result['type_service'],
            'articles': articles_str if articles_str else 'Non spécifié',
            'adresse_livraison': result.get('adresse_livraison', ''),
            'prix_total': round(float(result['prix_total']), 2),
            'nombre_articles': len(result['articles']),
            'notes': result.get('notes', ''),
            'articles_detailles': result['articles']
        }
        
    except Exception as e:
        print(f"❌ Erreur OpenAI: {e}")
        return analyser_commande_simple(transcript)


def analyser_commande_simple(transcript):
    """Fallback simple si OpenAI échoue"""
    transcript_lower = transcript.lower()
    
    mots_commande = ['prendre', 'commander', 'commande', 'voudrai', 'menu', 'curry', 'burger']
    type_appel = 'commande' if any(mot in transcript_lower for mot in mots_commande) else 'renseignement'
    
    type_service = 'Non spécifié'
    adresse_livraison = ''
    
    if 'livraison' in transcript_lower or 'livrer' in transcript_lower:
        type_service = 'Livraison'
        # Essai simple d'extraction d'adresse
        if 'rue' in transcript_lower or 'avenue' in transcript_lower:
            adresse_livraison = transcript  # Garde toute la transcription
    elif 'sur place' in transcript_lower:
        type_service = 'Sur place'
    elif 'emporter' in transcript_lower or 'à emporter' in transcript_lower:
        type_service = 'À emporter'
    
    articles = []
    prix_total = 0
    
    if 'curry' in transcript_lower:
        articles.append({'nom': 'Menu Curry', 'prix': 8.90, 'quantite': 1})
        prix_total += 8.90
    
    if 'mixte' in transcript_lower:
        articles.append({'nom': 'Menu Mixte', 'prix': 9.50, 'quantite': 1})
        prix_total += 9.50
    
    if 'classic' in transcript_lower:
        articles.append({'nom': 'Menu Classic', 'prix': 8.90, 'quantite': 1})
        prix_total += 8.90
    
    articles_str = ', '.join([art['nom'] for art in articles]) if articles else 'Non spécifié'
    
    return {
        'type_appel': type_appel,
        'type_service': type_service,
        'articles': articles_str,
        'adresse_livraison': adresse_livraison,
        'prix_total': round(prix_total, 2),
        'nombre_articles': len(articles),
        'notes': 'Analyse simple (OpenAI indisponible)',
        'articles_detailles': articles
    }


def analyser_commande(transcript):
    """
    Point d'entrée principal pour l'analyse de commande
    
    Args:
        transcript (str): Transcription de l'appel téléphonique
        
    Returns:
        dict: Analyse complète de la commande
    """
    return analyser_commande_avec_openai(transcript)
