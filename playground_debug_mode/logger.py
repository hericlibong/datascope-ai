"""
Utilitaires de logging avancé pour le debug mode
Fournit des logs riches et structurés pour le debug de la chaîne IA
"""

import json
import logging
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional
from functools import wraps

# Configuration des couleurs pour le terminal
class Colors:
    """Codes couleur ANSI pour le terminal"""
    RESET = '\033[0m'
    BOLD = '\033[1m'
    
    # Couleurs de base
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    
    # Couleurs pour les logs
    SUCCESS = '\033[92m'    # Vert
    WARNING = '\033[93m'    # Jaune
    ERROR = '\033[91m'      # Rouge
    INFO = '\033[94m'       # Bleu
    DEBUG = '\033[95m'      # Magenta


class DebugLogger:
    """Logger enrichi pour le debug mode avec support couleur et métriques"""
    
    def __init__(self, name: str = "playground_debug", output_dir: str = "outputs"):
        self.name = name
        self.output_dir = Path(__file__).parent / output_dir
        self.output_dir.mkdir(exist_ok=True)
        
        # Configuration du logger Python standard
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # Éviter les doublons de handlers
        if not self.logger.handlers:
            self._setup_handlers()
    
    def _setup_handlers(self):
        """Configure les handlers pour console et fichier"""
        # Handler console avec couleurs
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)
        console_formatter = ColorFormatter()
        console_handler.setFormatter(console_formatter)
        
        # Handler fichier sans couleurs
        log_file = self.output_dir / f"{self.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
    
    def success(self, message: str, **kwargs):
        """Log de succès avec icône verte"""
        formatted_msg = f"✅ {message}"
        if kwargs:
            formatted_msg += f" | {self._format_extras(**kwargs)}"
        self.logger.info(f"{Colors.SUCCESS}{formatted_msg}{Colors.RESET}")
    
    def warning(self, message: str, **kwargs):
        """Log d'avertissement avec icône jaune"""
        formatted_msg = f"⚠️  {message}"
        if kwargs:
            formatted_msg += f" | {self._format_extras(**kwargs)}"
        self.logger.warning(f"{Colors.WARNING}{formatted_msg}{Colors.RESET}")
    
    def error(self, message: str, error: Optional[Exception] = None, **kwargs):
        """Log d'erreur avec icône rouge"""
        formatted_msg = f"❌ {message}"
        if error:
            formatted_msg += f" | Error: {str(error)}"
        if kwargs:
            formatted_msg += f" | {self._format_extras(**kwargs)}"
        self.logger.error(f"{Colors.ERROR}{formatted_msg}{Colors.RESET}")
    
    def info(self, message: str, **kwargs):
        """Log informatif avec icône bleue"""
        formatted_msg = f"🔍 {message}"
        if kwargs:
            formatted_msg += f" | {self._format_extras(**kwargs)}"
        self.logger.info(f"{Colors.INFO}{formatted_msg}{Colors.RESET}")
    
    def debug(self, message: str, **kwargs):
        """Log de debug avec icône magenta"""
        formatted_msg = f"🐛 {message}"
        if kwargs:
            formatted_msg += f" | {self._format_extras(**kwargs)}"
        self.logger.debug(f"{Colors.DEBUG}{formatted_msg}{Colors.RESET}")
    
    def metrics(self, operation: str, **metrics_data):
        """Log de métriques avec icône graphique"""
        formatted_msg = f"📊 {operation}"
        if metrics_data:
            formatted_msg += f" | {self._format_extras(**metrics_data)}"
        self.logger.info(f"{Colors.CYAN}{formatted_msg}{Colors.RESET}")
    
    def separator(self, title: str = "", char: str = "=", length: int = 80):
        """Affiche un séparateur décoratif"""
        if title:
            # Centrer le titre dans le séparateur
            title_with_spaces = f" {title} "
            remaining = length - len(title_with_spaces)
            left_chars = remaining // 2
            right_chars = remaining - left_chars
            separator = char * left_chars + title_with_spaces + char * right_chars
        else:
            separator = char * length
        
        print(f"{Colors.BOLD}{Colors.CYAN}{separator}{Colors.RESET}")
    
    def _format_extras(self, **kwargs) -> str:
        """Formate les données supplémentaires en string lisible"""
        parts = []
        for key, value in kwargs.items():
            if isinstance(value, (dict, list)):
                value_str = json.dumps(value, ensure_ascii=False, indent=None, separators=(',', ':'))[:100]
                if len(str(value)) > 100:
                    value_str += "..."
            else:
                value_str = str(value)
            parts.append(f"{key}={value_str}")
        return " | ".join(parts)
    
    def save_json(self, data: Dict[str, Any], filename: str):
        """Sauvegarde des données en JSON pour analyse"""
        filepath = self.output_dir / f"{filename}.json"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        self.info(f"Données sauvegardées", file=str(filepath))


class ColorFormatter(logging.Formatter):
    """Formatter personnalisé pour les couleurs dans la console"""
    
    def format(self, record):
        # Le message est déjà formaté avec les couleurs dans DebugLogger
        return record.getMessage()


def timer_decorator(logger: DebugLogger):
    """Décorateur pour mesurer le temps d'exécution des fonctions"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            logger.info(f"Début de {func.__name__}")
            
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                logger.success(f"Fin de {func.__name__}", duration_s=f"{execution_time:.2f}")
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                logger.error(f"Erreur dans {func.__name__}", error=e, duration_s=f"{execution_time:.2f}")
                raise
        
        return wrapper
    return decorator


# Instance globale du logger pour faciliter l'import
debug_logger = DebugLogger()