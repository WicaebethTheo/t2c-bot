#!/bin/bash

# Journal pour le débogage
echo "----------------------------------------"
echo "Déploiement démarré à $(date)"

# Aller dans le dossier du projet
cd /home/cogs

# Sauvegarder l'état actuel (pour le débogage)
echo "État Git avant pull:"
git status

# Récupérer les dernières modifications
echo "Récupération des modifications depuis GitHub..."
git pull origin master  # ou 'main' selon votre branche par défaut

# Vérifier si le pull a fonctionné
if [ $? -eq 0 ]; then
    echo "Pull réussi, redémarrage du bot..."
    
    # Redémarrer votre bot Discord ici
    # Exemple si vous utilisez systemd:
    # sudo systemctl restart discord-bot.service
    
    # OU si vous utilisez un script pour démarrer/redémarrer votre bot:
    # /home/restart-bot.sh
    
    echo "Bot redémarré avec succès!"
else
    echo "ERREUR: Échec du pull. Vérifiez les conflits ou problèmes d'accès."
fi

echo "Déploiement terminé à $(date)"
echo "----------------------------------------"
