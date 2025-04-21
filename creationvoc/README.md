# Module CreationVoc

Système de création automatique de salons vocaux personnalisés avec contrôles interactifs.

## 📋 Commandes

- `!creationvoc` - Configure le système de création de salons vocaux
  - Commande réservée aux administrateurs
  - Permet de définir le salon de création pour le système

- `!nettoyer_voc` - Nettoie les salons vocaux temporaires inactifs
  - Commande réservée aux administrateurs
  - Supprime les salons vocaux créés par le système qui sont vides

## 🔧 Fonctionnalités

- Création automatique d'un salon vocal personnel lorsqu'un utilisateur rejoint le salon de création
- Génération d'un salon textuel de contrôle visible uniquement par le créateur
- Interface avec boutons interactifs pour la gestion du salon :
  - 🔒 Rendre le salon privé (accès restreint)
  - 🔓 Rendre le salon public (accès ouvert à tous)
  - 👥 Définir une limite de membres (0-99)
- Permissions avancées pour le créateur (mute, déplacement, etc.)
- Suppression automatique des salons lorsqu'ils sont vides
- Suppression du salon de contrôle lors de la fermeture du salon vocal

## ⚙️ Configuration

Le module est préconfiguré avec :
- ID du salon de création : 1352995736803086366

## 🔄 Fonctionnement

1. L'utilisateur rejoint le salon de création
2. Un nouveau salon vocal est créé automatiquement
3. L'utilisateur est déplacé dans son nouveau salon
4. Un canal textuel de contrôle est créé avec les boutons de gestion
5. Le salon est supprimé automatiquement quand tout le monde le quitte 