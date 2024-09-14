import re
from datetime import datetime

def extract_year_with_context(text: str) -> str:
    # Regex pour capturer les années entre 1000 et 2999
    year_pattern = r'\b(1[0-9]{3}|2[0-9]{3})\b'
    
    # Expressions temporelles relatives avec variantes
    relative_keywords_patterns = {
        r'\baujourd\'hui\b': 0,  # Même année
        r'\bhier\b': -1,  # L'année dernière
        r'\bavant-hier\b': -1,  # Même année (éventuellement ajustée selon le mois)
        r'\bdemain\b': 0,  # Même année (ou prochaine si fin d'année)
        r'\baprès-demain\b': 0,  # Idem que demain
        
        # Mots-clés pour l'instant présent
        r'\bactuel(le)?\b': 0,  # Même année
        r'\bactuellement\b': 0,  # Même année
        r'\bprésentement\b': 0,  # Même année
        r'\bà ce jour\b': 0,  # Même année
        r'\ben ce moment\b': 0,  # Même année
        r'\bces jours-ci\b': 0,  # Même année
        r'\bmaintenant\b': 0,  # Même année
        
        # Pour les années récentes
        r'\bl\'année dernière\b': -1,
        r'\bl\'an dernier\b': -1,
        r'\bl\'an passé\b': -1,
        r'\bil y a un an\b': -1,
        r'\bl\'année prochaine\b': 1,
        r'\bdans un an\b': 1,
        r'\bdans deux ans\b': 2,
        r'\bdans trois ans\b': 3,
        r'\bdans quatre ans\b': 4,
        r'\bdans cinq ans\b': 5,
        r'\bil y a deux ans\b': -2,
        r'\bil y a trois ans\b': -3,
        r'\bil y a quatre ans\b': -4,
        r'\bil y a cinq ans\b': -5,
        r'\bil y a quelques années\b': -2,
        
        # Expressions plus vagues
        r'\bdans quelques années\b': 2,
        r'\bil y a longtemps\b': -10,
        r'\bil y a un certain temps\b': -5,
        r'\bdans un certain temps\b': 3,
        
        # Expressions spécifiant des périodes
        r'\bl\'année précédente\b': -1,
        r'\bl\'année suivante\b': 1,
        r'\bl\'année d\'avant\b': -1,
        r'\bl\'année d\'après\b': 1,
        r'\bl\'an passé\b': -1,
        r'\bl\'an prochain\b': 1,
        
        # Autres mots-clés temporels
        r'\bprochainement\b': 1,  # Prochaine année
        r'\bplus tard\b': 1,  # Prochaine année
        r'\bbientôt\b': 0,  # Même année
        r'\btrès bientôt\b': 0,  # Même année
        r'\bà venir\b': 1,  # Prochaine année
        r'\bdans un avenir proche\b': 1,  # Prochaine année
        r'\bdans un avenir lointain\b': 5,  # Cinq ans plus tard
        r'\bà moyen terme\b': 2,  # Deux ans plus tard
        r'\bà long terme\b': 5,  # Cinq ans plus tard
        r'\bdans quelques mois\b': 0,  # Même année ou l'année suivante si très proche de la fin de l'année
    }
    
    # Rechercher des années spécifiques dans le texte
    years = re.findall(year_pattern, text)
    
    # Rechercher des expressions temporelles relatives
    for pattern, offset in relative_keywords_patterns.items():
        if re.search(pattern, text, re.IGNORECASE):
            # Calculer l'année relative à partir de la date actuelle
            current_year = datetime.now().year
            calculated_year = current_year + offset
            return str(calculated_year)  # Retourne l'année calculée
    
    # Rechercher des mots-clés associés à des années spécifiques
    for keyword in [r'\b' + re.escape(keyword) + r'\b' for keyword in ["en", "année", "depuis", "jusqu'à", "de", "dans", "au cours de", "à partir de", "environ", "vers", "autour de", "entre", "à cette époque"]]:
        pattern_with_keyword = rf'{keyword}\s*(1[0-9]{3}|2[0-9]{3})'
        match = re.search(pattern_with_keyword, text, re.IGNORECASE)
        
        if match:
            year_found = match.group(1)
            if is_valid_year(year_found):
                return year_found  # Retourne l'année trouvée après un mot-clé

    # Si aucune année n'est trouvée par mots-clés, retourner la première année détectée
    for year in years:
        if is_valid_year(year):
            return year
    
    return None  # Si aucune année n'est trouvée ou si aucune n'est valide

def is_valid_year(year: str) -> bool:
    """Vérifie si l'année est valide dans une plage réaliste."""
    year_int = int(year)
    return 1000 <= year_int <= 2999

