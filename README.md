# IntelliFlow CRM - Marketing Automation Module (CS411 Project #2)

## Structure du Projet
- `marketing_automation/`: Contient tous les fichiers d'implémentation du Module MA.
    - `models.py`: Définit les classes Customer, Product, Campaign.
    - `event_bus.py`: Implémentation du pattern Publish/Subscribe.
    - `campaign_manager.py`: Logique pour gérer et mettre à jour les métriques de campagne.
    - `app.py`: Point d'entrée principal pour la démonstration (inclut la simulation d'UI et des interactions).
- `requirements.txt`: Liste les dépendances Python nécessaires (si vous en avez).
- `README.md`: Ce fichier.

## Comment Exécuter le Projet
1. S'assurer que Python est installé.
2. Installer les dépendances (si nécessaire) : `pip install -r requirements.txt`
3. Exécuter l'application de démonstration : `python marketing_automation/app.py`
