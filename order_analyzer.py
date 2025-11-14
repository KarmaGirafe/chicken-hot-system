"""
Analyseur intelligent de commandes avec OpenAI - VERSION CORRIGÉE
"""

from openai import OpenAI
import json
import os
import re

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
"""

def analyser_commande_avec_openai(transcript):
    """
    Analyse la transcription avec OpenAI GPT-4o
    """
    
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

TRANSCRIPTION DE L'APPEL :
{transcript}

MENU :
{MENU_CONTEXT}

TÂCHE : Extrais TOUTES les informations de commande.

Réponds UNIQUEMENT en JSON (sans markdown, sans texte avant/après) :

{{
  "type_appel": "commande" ou "renseignement",
  "type_service": "Sur place" ou "À emporter" ou "Livraison",
  "articles": [
    {{"nom": "Nom exact du menu", "prix": 8.90, "quantite": 2}}
  ],
  "adresse_livraison": "Adresse complète avec numéro de rue, nom de rue et ville",
  "prix_total": 17.80,
  "notes": ""
}}

RÈGLES CRITIQUES :
1. Pour "type_service" :
   - Si adresse mentionnée = "Livraison"
   - Si "sur place" = "Sur place"
   - Si "emporter" ou "à emporter" = "À emporter"

2. Pour "adresse_livraison" (TRÈS IMPORTANT) :
   - TOUJOURS extraire l'adresse COMPLÈTE si livraison
   - Format : "numéro rue, ville"
   - Exemple : "15 rue de la République, Dreux"
   - Si pas de livraison : mettre ""

3. Pour "articles" :
   - Par défaut les articles sont en "Menu" (avec frites+boisson)
   - Si client dit "seul" ou "sans menu" = prix seul
   - Chaque article doit avoir : nom, prix, quantite
   - Pour plusieurs articles identiques, mettre quantite > 1

4. "prix_total" = somme de tous les (prix × quantite)

EXEMPLES :
- "Un curry" → Menu Curry (8.90€)
- "Deux curry" → 2× Menu Curry (17.80€)
- "Un curry et 6 wings" → Menu Curry (8.90€) + Wings x6 (4.90€) = 13.80€
- "Livraison au 15 rue de la Gare à Dreux" → type_service: "Livraison", adresse_livraison: "15 rue de la Gare, Dreux"
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "Tu es un expert en extraction de données de commandes. Tu réponds UNIQUEMENT en JSON strict."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.1,
            max_tokens=800,
            response_format={"type": "json_object"}
        )
        
        result_text = response.choices[0].message.content.strip()
        print(f"🤖 Réponse OpenAI brute : {result_text[:200]}...")
        
        result = json.loads(result_text)
        
        # Validation et nettoyage
        type_appel = result.get('type_appel', 'commande')
        type_service = result.get('type_service', 'Non spécifié')
        articles = result.get('articles', [])
        adresse = result.get('adresse_livraison', '').strip()
        prix_total = float(result.get('prix_total', 0))
        notes = result.get('notes', '')
        
        # Si pas d'articles, créer un article par défaut
        if not articles or len(articles) == 0:
            print("⚠️ Aucun article détecté, création article par défaut")
            articles = [{
                'nom': 'Article non spécifié',
                'prix': 0,
                'quantite': 1
            }]
        
        # Nettoyer les articles (gérer les erreurs de format)
        articles_propres = []
        for art in articles:
            try:
                articles_propres.append({
                    'nom': str(art.get('nom', 'Article')),
                    'prix': float(art.get('prix', 0)),
                    'quantite': int(art.get('quantite', 1))
                })
            except Exception as e:
                print(f"⚠️ Erreur format article : {e}")
                articles_propres.append({
                    'nom': 'Article',
                    'prix': 0,
                    'quantite': 1
                })
        
        # Nettoyer l'adresse
        if type_service == 'Livraison' and not adresse:
            print("⚠️ Livraison détectée mais pas d'adresse, tentative extraction manuelle")
            adresse = extraire_adresse_manuel(transcript)
        
        # Formater la liste des articles pour affichage
        articles_str = ', '.join([
            f"{art['quantite']}× {art['nom']}" if art['quantite'] > 1 else art['nom']
            for art in articles_propres
        ])
        
        print(f"✅ Analyse réussie : {len(articles_propres)} article(s), {type_service}")
        print(f"   Articles : {articles_str}")
        print(f"   Adresse : {adresse if adresse else 'Aucune'}")
        
        return {
            'type_appel': type_appel,
            'type_service': type_service,
            'articles': articles_str if articles_str else 'Non spécifié',
            'adresse_livraison': adresse,
            'prix_total': round(prix_total, 2),
            'nombre_articles': len(articles_propres),
            'notes': notes,
            'articles_detailles': articles_propres
        }
        
    except json.JSONDecodeError as e:
        print(f"❌ Erreur parsing JSON : {e}")
        print(f"   Réponse brute : {result_text}")
        return analyser_commande_simple(transcript)
    except Exception as e:
        print(f"❌ Erreur OpenAI : {e}")
        import traceback
        traceback.print_exc()
        return analyser_commande_simple(transcript)


def extraire_adresse_manuel(transcript):
    """Extraction manuelle d'adresse si OpenAI échoue"""
    transcript_lower = transcript.lower()
    
    # Patterns d'adresse
    patterns = [
        r'(\d+\s+(?:rue|avenue|boulevard|av|bd|place)\s+[^,\.]+(?:,\s*\w+)?)',
        r'(au\s+\d+\s+[^,\.]+(?:,\s*\w+)?)',
        r'(\d+\s+[^,\.]+(?:dreux|vernouillet|cherisy))',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, transcript_lower, re.IGNORECASE)
        if match:
            adresse = match.group(1).strip()
            # Ajouter Dreux si pas de ville
            if 'dreux' not in adresse.lower() and 'vernouillet' not in adresse.lower():
                adresse += ', Dreux'
            return adresse
    
    return ''


def analyser_commande_simple(transcript):
    """Fallback simple si OpenAI échoue"""
    print("⚠️ Mode fallback activé")
    
    transcript_lower = transcript.lower()
    
    # Type d'appel
    mots_commande = ['prendre', 'commander', 'commande', 'voudrai', 'menu', 'curry', 'burger']
    type_appel = 'commande' if any(mot in transcript_lower for mot in mots_commande) else 'renseignement'
    
    # Type de service
    type_service = 'Non spécifié'
    adresse_livraison = ''
    
    if 'livraison' in transcript_lower or 'livrer' in transcript_lower or 'rue' in transcript_lower:
        type_service = 'Livraison'
        adresse_livraison = extraire_adresse_manuel(transcript)
    elif 'sur place' in transcript_lower:
        type_service = 'Sur place'
    elif 'emporter' in transcript_lower or 'à emporter' in transcript_lower:
        type_service = 'À emporter'
    
    # Articles basiques
    articles = []
    prix_total = 0
    
    # Détection simple des articles populaires
    items_detectes = []
    if 'curry' in transcript_lower:
        items_detectes.append(('Menu Curry', 8.90))
    if 'mixte' in transcript_lower:
        items_detectes.append(('Menu Mixte', 9.50))
    if 'classic' in transcript_lower:
        items_detectes.append(('Menu Classic', 8.90))
    if 'wings' in transcript_lower or 'wing' in transcript_lower:
        items_detectes.append(('Wings x6', 4.90))
    if 'tenders' in transcript_lower or 'tender' in transcript_lower:
        items_detectes.append(('Tenders x7', 6.90))
    
    # Si aucun article détecté
    if not items_detectes:
        items_detectes.append(('Article non spécifié', 0))
    
    for nom, prix in items_detectes:
        articles.append({'nom': nom, 'prix': prix, 'quantite': 1})
        prix_total += prix
    
    articles_str = ', '.join([art['nom'] for art in articles])
    
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
    """Point d'entrée principal"""
    print(f"\n{'='*60}")
    print(f"📝 ANALYSE DE COMMANDE")
    print(f"{'='*60}")
    print(f"Transcription : {transcript[:100]}...")
    
    result = analyser_commande_avec_openai(transcript)
    
    print(f"\n{'='*60}")
    print(f"📊 RÉSULTAT ANALYSE")
    print(f"{'='*60}")
    print(f"Type : {result['type_service']}")
    print(f"Articles : {result['articles']}")
    print(f"Prix : {result['prix_total']}€")
    print(f"Adresse : {result['adresse_livraison']}")
    print(f"{'='*60}\n")
    
    return result
