# Module Clear

Module de nettoyage de messages avec diverses options de filtrage.

## 📋 Commandes

- `!clear [nombre]` - Supprime un nombre spécifié de messages dans le canal actuel
  - Par défaut, supprime 10 messages si aucun nombre n'est spécifié
  - Exemple : `!clear 20`

- `!clear [nombre] @utilisateur` - Supprime les messages d'un utilisateur spécifique
  - Exemple : `!clear 50 @Wicaebeth`

- `!clear [nombre] --bots` - Supprime uniquement les messages des bots
  - Exemple : `!clear 30 --bots`

- `!clear [nombre] --humans` - Supprime uniquement les messages des humains
  - Exemple : `!clear 30 --humans`

- `!clear [nombre] --links` - Supprime uniquement les messages contenant des liens
  - Exemple : `!clear 50 --links`

- `!clear [nombre] --images` - Supprime uniquement les messages contenant des images
  - Exemple : `!clear 30 --images`

- `!clear [nombre] --embeds` - Supprime uniquement les messages contenant des embeds
  - Exemple : `!clear 25 --embeds`

## 🔒 Permissions

Cette commande nécessite les permissions suivantes :
- `manage_messages` - Pour supprimer les messages
- `read_message_history` - Pour lire l'historique des messages

## ⚠️ Limitations

- Discord ne permet pas de supprimer des messages datant de plus de 14 jours via l'API
- La commande est limitée à 100 messages maximum par exécution
- Un message de confirmation s'affiche temporairement après l'exécution

## 🔧 Exemples d'utilisation

```
!clear 50
```
Supprime les 50 derniers messages dans le canal

```
!clear 30 @Utilisateur
```
Supprime jusqu'à 30 messages de l'utilisateur mentionné

```
!clear 25 --links
```
Supprime jusqu'à 25 messages contenant des liens 