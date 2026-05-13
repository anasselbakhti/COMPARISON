#!/usr/bin/env python3
# ============================================================
#  finalize.py - Script d'intégration et de test
#  Utilisation: python finalize.py
# ============================================================

import os
import sys
import subprocess
from pathlib import Path

class TechCompareFinalizer:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.success_count = 0
        self.error_count = 0
    
    def print_header(self, text):
        print(f"\n{'='*60}")
        print(f"  {text}")
        print(f"{'='*60}\n")
    
    def print_step(self, text):
        print(f"✓ {text}")
        self.success_count += 1
    
    def print_error(self, text):
        print(f"✗ {text}")
        self.error_count += 1
    
    def run_command(self, command, description):
        """Exécute une commande shell."""
        print(f"\n➜ {description}")
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                self.print_step(description)
                return True
            else:
                self.print_error(f"{description} - Erreur: {result.stderr}")
                return False
        except subprocess.TimeoutExpired:
            self.print_error(f"{description} - Timeout")
            return False
        except Exception as e:
            self.print_error(f"{description} - {str(e)}")
            return False
    
    def check_file_exists(self, filepath, description):
        """Vérifie si un fichier existe."""
        if Path(filepath).exists():
            self.print_step(description)
            return True
        else:
            self.print_error(description)
            return False
    
    def run_tests(self):
        """Exécute la procédure complète d'intégration et test."""
        self.print_header("TechCompare - Intégration Finale")
        
        print("📋 Vérification de la structure du projet...\n")
        
        # Vérifier les fichiers créés
        files_to_check = [
            ("products/compare.py", "✓ Module de comparaison créé"),
            ("products/notifications.py", "✓ Module de notifications créé"),
            ("products/serializers_extended.py", "✓ Serializers étendus créés"),
            ("products/views_extended.py", "✓ Views étendues créés"),
            ("COLLABORATION.md", "✓ Guide collaboration créé"),
            ("INTEGRATION_GUIDE.md", "✓ Guide intégration créé"),
            ("INSTRUCTIONS_FOR_FRIEND.md", "✓ Instructions pour ami créées"),
        ]
        
        for filepath, description in files_to_check:
            full_path = self.project_root / filepath
            self.check_file_exists(full_path, description)
        
        # Vérifier les fichiers backend essentiels
        self.print_header("Vérification Backend")
        
        backend_files = [
            ("manage.py", "✓ Django manage.py trouvé"),
            ("requirements.txt", "✓ Requirements.txt trouvé"),
            ("products/models.py", "✓ Models.py trouvé"),
            ("products/admin.py", "✓ Admin.py trouvé"),
            ("products/views.py", "✓ Views.py trouvé"),
            ("products/serializers.py", "✓ Serializers.py trouvé"),
            ("techcompare/settings.py", "✓ Settings.py trouvé"),
            ("techcompare/urls.py", "✓ URLs.py trouvé"),
        ]
        
        for filepath, description in backend_files:
            full_path = self.project_root / filepath
            self.check_file_exists(full_path, description)
        
        # Vérifier l'environment Python
        self.print_header("Vérification Environment Python")
        self.run_command("python --version", "Vérifier Python version")
        
        # Vérifier les dépendances
        self.print_header("Vérification Dépendances")
        
        try:
            import django
            self.print_step("Django est installé")
        except ImportError:
            self.print_error("Django n'est pas installé - Exécutez: pip install -r requirements.txt")
        
        try:
            import rest_framework
            self.print_step("Django REST Framework est installé")
        except ImportError:
            self.print_error("DRF n'est pas installé")
        
        try:
            import django_filters
            self.print_step("django-filter est installé")
        except ImportError:
            self.print_error("django-filter n'est pas installé")
        
        # Vérifier Git
        self.print_header("Vérification Git")
        self.run_command("git --version", "Vérifier Git version")
        self.run_command("git status", "Vérifier statut Git")
        self.run_command("git log --oneline -n 5", "Afficher derniers commits")
        
        # Vérifier Frontend (optionnel)
        self.print_header("Vérification Frontend")
        frontend_path = self.project_root / "frontend"
        if frontend_path.exists():
            self.print_step("Dossier frontend trouvé")
            if (frontend_path / "package.json").exists():
                self.print_step("✓ Package.json trouvé")
        else:
            print("ℹ️  Frontend non encore créé (à faire par votre ami)\n")
        
        # Résumé
        self.print_header("Résumé de l'Intégration")
        print(f"✅ Vérifications réussies: {self.success_count}")
        print(f"❌ Vérifications échouées: {self.error_count}\n")
        
        if self.error_count == 0:
            print("🎉 Tout est prêt ! Voici les prochaines étapes:\n")
            print("1. Partagez ce message avec votre ami:")
            print("   📄 Fichier: INSTRUCTIONS_FOR_FRIEND.md\n")
            print("2. Une fois que votre ami a pushé son code:")
            print("   $ git pull origin main\n")
            print("3. Puis lancez l'intégration finale:")
            print("   $ python manage.py migrate")
            print("   $ python manage.py runserver\n")
            print("4. Et testez le frontend:")
            print("   $ cd frontend && npm start\n")
            return True
        else:
            print("⚠️  Il y a quelques problèmes à corriger avant de continuer.\n")
            print("Action recommandée:")
            print("   $ pip install -r requirements.txt\n")
            return False


def main():
    finalizer = TechCompareFinalizer()
    success = finalizer.run_tests()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
