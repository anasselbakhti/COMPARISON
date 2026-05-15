# ============================================================
#  products/validation.py
#  Service de validation et nettoyage des données de scraping
# ============================================================

import logging
from decimal import Decimal
from datetime import datetime

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Exception levée lors d'une erreur de validation."""
    pass


class DataValidator:
    """Classe pour valider et nettoyer les données de scraping."""
    
    # Intervales valides pour les spécifications
    VALID_RANGES = {
        'ram_gb': (0, 128),                    # 0 à 128 Go
        'storage_gb': (0, 8192),              # 0 à 8 To
        'screen_in': (3.0, 20.0),             # 3" à 20"
        'camera_mp': (0, 200),                # 0 à 200 MP
        'battery_mah': (0, 10000),            # 0 à 10000 mAh
        'battery_wh': (0, 500),               # 0 à 500 Wh
        'weight_kg': (0.1, 5.0),              # 0.1 kg à 5 kg
        'price': (500, 100000),               # 500 à 100000 MAD
        'release_year': (2000, datetime.now().year + 1),
    }
    
    VALID_OS_CHOICES = {
        'smartphone': ['Android', 'iOS', 'HarmonyOS', 'Windows Phone'],
        'laptop': ['Windows', 'macOS', 'Linux', 'FreeDOS', 'Chrome OS', 'Ubuntu'],
    }
    
    VALID_NETWORKS = ['2G', '3G', '4G', '5G']
    
    @staticmethod
    def validate_required_fields(data, required_fields):
        """
        Valide que tous les champs requis sont présents et non vides.
        
        Args:
            data (dict): Données à valider
            required_fields (list): Liste des champs requis
            
        Raises:
            ValidationError: Si un champ requis est manquant ou vide
        """
        missing = []
        for field in required_fields:
            if field not in data or data[field] is None or str(data[field]).strip() == '':
                missing.append(field)
        
        if missing:
            raise ValidationError(f"Champs requis manquants: {', '.join(missing)}")
    
    @staticmethod
    def validate_numeric_field(value, field_name, min_val=None, max_val=None, allow_zero=True):
        """
        Valide et convertit une valeur numérique.
        
        Args:
            value: Valeur à valider
            field_name: Nom du champ (pour logs)
            min_val: Valeur minimale acceptable
            max_val: Valeur maximale acceptable
            allow_zero: Si False, rejette les valeurs 0
            
        Returns:
            int ou float: Valeur validée et convertie
            
        Raises:
            ValidationError: Si la valeur est invalide
        """
        try:
            num = float(value) if isinstance(value, str) else value
            
            if not allow_zero and num == 0:
                raise ValidationError(f"{field_name}: valeur zéro non autorisée")
            
            if min_val is not None and num < min_val:
                raise ValidationError(f"{field_name}: {num} < min {min_val}")
            
            if max_val is not None and num > max_val:
                raise ValidationError(f"{field_name}: {num} > max {max_val}")
            
            # Retourne int si pas de décimales, sinon float
            return int(num) if num == int(num) else num
        except (ValueError, TypeError) as e:
            raise ValidationError(f"{field_name}: impossible de convertir '{value}' en nombre")
    
    @staticmethod
    def validate_string_field(value, field_name, max_length=200, allowed_values=None):
        """
        Valide et nettoie une chaîne de caractères.
        
        Args:
            value: Valeur à valider
            field_name: Nom du champ
            max_length: Longueur maximale
            allowed_values: Liste des valeurs autorisées (enum)
            
        Returns:
            str: Valeur nettoyée
            
        Raises:
            ValidationError: Si la valeur est invalide
        """
        if not isinstance(value, str):
            value = str(value)
        
        value = value.strip()
        
        if not value:
            raise ValidationError(f"{field_name}: valeur vide")
        
        if len(value) > max_length:
            raise ValidationError(f"{field_name}: dépasse {max_length} caractères")
        
        if allowed_values and value not in allowed_values:
            raise ValidationError(
                f"{field_name}: '{value}' non autorisé. Choix: {', '.join(allowed_values)}"
            )
        
        return value
    
    @staticmethod
    def validate_price(price):
        """Valide et convertit le prix."""
        return DataValidator.validate_numeric_field(
            price, 'price',
            min_val=500,      # Prix min: 500 MAD
            max_val=100000,   # Prix max: 100000 MAD
            allow_zero=False
        )
    
    @staticmethod
    def validate_smartphone_data(data):
        """
        Valide les données complètes d'un smartphone.
        
        Args:
            data (dict): Données du smartphone
            
        Returns:
            dict: Données validées et nettoyées
            
        Raises:
            ValidationError: Si validation échoue
        """
        validated = {}
        
        # Champs requis
        DataValidator.validate_required_fields(
            data,
            ['name', 'brand', 'price']
        )
        
        validated['name'] = DataValidator.validate_string_field(data['name'], 'name', max_length=200)
        validated['brand'] = DataValidator.validate_string_field(data['brand'], 'brand', max_length=100)
        validated['price'] = Decimal(str(DataValidator.validate_price(data['price'])))
        validated['source_url'] = data.get('source_url', '')
        validated['category'] = 'smartphone'
        
        # Champs optionnels avec validation
        if data.get('ram_gb'):
            validated['ram_gb'] = DataValidator.validate_numeric_field(
                data['ram_gb'], 'ram_gb', min_val=0, max_val=128
            )
        else:
            validated['ram_gb'] = 0
        
        if data.get('storage_gb'):
            validated['storage_gb'] = DataValidator.validate_numeric_field(
                data['storage_gb'], 'storage_gb', min_val=0, max_val=8192
            )
        else:
            validated['storage_gb'] = 0
        
        if data.get('camera_mp'):
            validated['camera_mp'] = DataValidator.validate_numeric_field(
                data['camera_mp'], 'camera_mp', min_val=0, max_val=200
            )
        else:
            validated['camera_mp'] = 0
        
        if data.get('battery_mah'):
            validated['battery_mah'] = DataValidator.validate_numeric_field(
                data['battery_mah'], 'battery_mah', min_val=0, max_val=10000
            )
        else:
            validated['battery_mah'] = 0
        
        if data.get('screen_in'):
            validated['screen_in'] = DataValidator.validate_numeric_field(
                data['screen_in'], 'screen_in', min_val=3.0, max_val=20.0
            )
        else:
            validated['screen_in'] = None
        
        # OS validation
        if data.get('os'):
            validated['os'] = DataValidator.validate_string_field(
                data['os'], 'os', max_length=50,
                allowed_values=DataValidator.VALID_OS_CHOICES['smartphone']
            )
        else:
            validated['os'] = 'Android'
        
        # Network validation
        if data.get('network'):
            validated['network'] = DataValidator.validate_string_field(
                data['network'], 'network', max_length=10,
                allowed_values=DataValidator.VALID_NETWORKS
            )
        else:
            validated['network'] = '4G'
        
        if data.get('release_year'):
            validated['release_year'] = DataValidator.validate_numeric_field(
                data['release_year'], 'release_year',
                min_val=2000, max_val=datetime.now().year + 1
            )
        else:
            validated['release_year'] = None
        
        return validated
    
    @staticmethod
    def validate_laptop_data(data):
        """
        Valide les données complètes d'un laptop.
        
        Args:
            data (dict): Données du laptop
            
        Returns:
            dict: Données validées et nettoyées
            
        Raises:
            ValidationError: Si validation échoue
        """
        validated = {}
        
        # Champs requis
        DataValidator.validate_required_fields(
            data,
            ['name', 'brand', 'price']
        )
        
        validated['name'] = DataValidator.validate_string_field(data['name'], 'name', max_length=200)
        validated['brand'] = DataValidator.validate_string_field(data['brand'], 'brand', max_length=100)
        validated['price'] = Decimal(str(DataValidator.validate_price(data['price'])))
        validated['source_url'] = data.get('source_url', '')
        validated['category'] = 'laptop'
        
        # Champs optionnels avec validation
        if data.get('cpu'):
            validated['cpu'] = DataValidator.validate_string_field(data['cpu'], 'cpu', max_length=100)
        else:
            validated['cpu'] = 'Inconnu'
        
        if data.get('ram_gb'):
            validated['ram_gb'] = DataValidator.validate_numeric_field(
                data['ram_gb'], 'ram_gb', min_val=0, max_val=128
            )
        else:
            validated['ram_gb'] = 0
        
        if data.get('storage_gb'):
            validated['storage_gb'] = DataValidator.validate_numeric_field(
                data['storage_gb'], 'storage_gb', min_val=0, max_val=8192
            )
        else:
            validated['storage_gb'] = 0
        
        if data.get('screen_in'):
            validated['screen_in'] = DataValidator.validate_numeric_field(
                data['screen_in'], 'screen_in', min_val=3.0, max_val=20.0
            )
        else:
            validated['screen_in'] = None
        
        if data.get('gpu'):
            validated['gpu'] = DataValidator.validate_string_field(data['gpu'], 'gpu', max_length=100)
        else:
            validated['gpu'] = 'Intégré'
        
        if data.get('battery_wh'):
            validated['battery_wh'] = DataValidator.validate_numeric_field(
                data['battery_wh'], 'battery_wh', min_val=0, max_val=500
            )
        else:
            validated['battery_wh'] = 0
        
        if data.get('weight_kg'):
            validated['weight_kg'] = DataValidator.validate_numeric_field(
                data['weight_kg'], 'weight_kg', min_val=0.1, max_val=5.0
            )
        else:
            validated['weight_kg'] = 0.0
        
        # OS validation
        if data.get('os'):
            validated['os'] = DataValidator.validate_string_field(
                data['os'], 'os', max_length=50,
                allowed_values=DataValidator.VALID_OS_CHOICES['laptop']
            )
        else:
            validated['os'] = 'FreeDOS'
        
        if data.get('release_year'):
            validated['release_year'] = DataValidator.validate_numeric_field(
                data['release_year'], 'release_year',
                min_val=2000, max_val=datetime.now().year + 1
            )
        else:
            validated['release_year'] = None
        
        return validated
    
    @staticmethod
    def detect_anomalies(data, category):
        """
        Détecte les anomalies dans les données (valeurs suspectes).
        
        Args:
            data (dict): Données à analyser
            category (str): 'smartphone' ou 'laptop'
            
        Returns:
            list: Liste des anomalies détectées
        """
        anomalies = []
        
        # Anomalies de prix
        if data.get('price'):
            if data['price'] < 1000:
                anomalies.append(f"Prix très bas: {data['price']} MAD")
            elif data['price'] > 50000:
                anomalies.append(f"Prix très élevé: {data['price']} MAD")
        
        # Anomalies spécifiques smartphones
        if category == 'smartphone':
            if data.get('ram_gb', 0) > 24:
                anomalies.append(f"RAM excessif pour smartphone: {data['ram_gb']} Go")
            if data.get('camera_mp', 0) > 150:
                anomalies.append(f"Caméra anormale: {data['camera_mp']} MP")
            if data.get('battery_mah', 0) > 7000:
                anomalies.append(f"Batterie surdimensionnée: {data['battery_mah']} mAh")
        
        # Anomalies spécifiques laptops
        if category == 'laptop':
            if data.get('weight_kg', 0) > 4.0:
                anomalies.append(f"Poids élevé pour laptop: {data['weight_kg']} kg")
            if data.get('ram_gb', 0) > 64:
                anomalies.append(f"RAM élevé pour laptop: {data['ram_gb']} Go")
        
        return anomalies


class ScrapingStats:
    """Statistiques du scraping."""
    
    def __init__(self):
        self.total_processed = 0
        self.successfully_validated = 0
        self.validation_errors = 0
        self.anomalies_detected = 0
        self.errors = []
    
    def add_error(self, item_name, error_msg):
        """Enregistre une erreur."""
        self.validation_errors += 1
        self.errors.append({
            'item': item_name,
            'error': str(error_msg)
        })
    
    def log_summary(self, logger_instance):
        """Enregistre un résumé des statistiques."""
        logger_instance.info(f"=== RÉSUMÉ DU SCRAPING ===")
        logger_instance.info(f"Total traité: {self.total_processed}")
        logger_instance.info(f"Valide: {self.successfully_validated}")
        logger_instance.info(f"Erreurs validation: {self.validation_errors}")
        logger_instance.info(f"Anomalies détectées: {self.anomalies_detected}")
        
        if self.errors:
            logger_instance.warning(f"\n=== DÉTAILS DES ERREURS ===")
            for error in self.errors[:10]:  # Affiche les 10 premières
                logger_instance.warning(f"  • {error['item']}: {error['error']}")
            if len(self.errors) > 10:
                logger_instance.warning(f"  ... et {len(self.errors) - 10} autres erreurs")
