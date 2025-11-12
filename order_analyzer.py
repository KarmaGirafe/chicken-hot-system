"""
Analyseur intelligent de commandes avec OpenAI
"""

from openai import OpenAI
import json
import os

client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))

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
        dict: Analyse de la commande
    """
    
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
  "prix_total": 0.00,
  "notes": "Précisions éventuelles (épicé, nature, etc.)"
}}

RÈGLES IMPORTANTES :
1. Si le client demande juste des informations/horaires/question → type_appel = "renseignement"
2. Si le client commande de la nourriture → type_appel = "commande"
3. Détecte si c'est "Menu" (avec frites+boisson) ou "Seul" (juste le sandwich)
4. Si le client dit "menu curry" → Menu Curry à 8,90€
5. Si le client dit juste "un curry" → considère que c'est un menu (défaut)
6. Détecte TOUTES les quantités mentionnées
7. Si le client se corrige, prends SEULEMENT la dernière version
8. Pour les extras (tenders, wings, pilons), détecte bien la quantité exacte
9. Calcule le prix_total en additionnant tous les articles × quantités
10. Si "sur place" mentionné → type_service = "Sur place"
11. Si "emporter" ou "à emporter" → type_service = "À emporter"

EXEMPLES :
- "Un curry" → Menu Curry (8,90€)
- "Un curry seul" → Curry seul (6,90€)
- "Deux curry" → 2× Menu Curry (17,80€)
- "Un curry et 6 wings" → Menu Curry (8,90€) + 6 Wings (4,90€) = 13,80€
- "Euh non pas curry, plutôt mixte" → Seulement Menu Mixte (9,50€)
- "3 tenders" → 3 Tenders (3,50€)
- "C'est ouvert jusqu'à quelle heure ?" → renseignement
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
        
        # Formatte les articles
        articles_str = ', '.join([
            f"{art['quantite']}× {art['nom']}" if art['quantite'] > 1 else art['nom']
            for art in result['articles']
        ])
        
        return {
            'type_appel': result['type_appel'],
            'type_service': result['type_service'],
            'articles': articles_str if articles_str else 'Non spécifié',
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
    if 'sur place' in transcript_lower:
        type_service = 'Sur place'
    elif 'emporter' in transcript_lower or 'à emporter' in transcript_lower:
        type_service = 'À emporter'
    
    articles = []
    prix_total = 0
    
    if 'curry' in transcript_lower:
        articles.append('Menu Curry')
        prix_total += 8.90
    
    if 'mixte' in transcript_lower:
        articles.append('Menu Mixte')
        prix_total += 9.50
    
    if 'classic' in transcript_lower:
        articles.append('Menu Classic')
        prix_total += 8.90
    
    return {
        'type_appel': type_appel,
        'type_service': type_service,
        'articles': ', '.join(articles) if articles else 'Non spécifié',
        'prix_total': round(prix_total, 2),
        'nombre_articles': len(articles),
        'notes': 'Analyse simple (OpenAI indisponible)'
    }


def analyser_commande(transcript):
    """Point d'entrée principal"""
    return analyser_commande_avec_openai(transcript)
