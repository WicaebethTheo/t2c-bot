# Module Sanction

Système complet de gestion des sanctions avec historique, durées configurables et modération avancée.

## 📋 Commandes

### Commandes de modération
- `!warn [@utilisateur] [raison]` - Donne un avertissement à un utilisateur
  - Exemple : `!warn @Utilisateur Non-respect des règles`

- `!mute [@utilisateur] [durée] [raison]` - Rend un utilisateur muet pour une durée définie
  - Exemple : `!mute @Utilisateur 2h Spam dans le chat`

- `!tempmute [@utilisateur] [durée] [raison]` - Alias pour la commande mute

- `!unmute [@utilisateur]` - Retire le statut muet d'un utilisateur
  - Exemple : `!unmute @Utilisateur`

- `!ban [@utilisateur] [durée] [raison]` - Bannit un utilisateur pour une durée définie ou de façon permanente
  - Exemple : `!ban @Utilisateur 7d Comportement toxique répété`

- `!tempban [@utilisateur] [durée] [raison]` - Bannit temporairement un utilisateur
  - Exemple : `!tempban @Utilisateur 24h Publicité non autorisée`

- `!unban [ID utilisateur]` - Débannit un utilisateur
  - Exemple : `!unban 123456789012345678`

- `!kick [@utilisateur] [raison]` - Expulse un utilisateur du serveur
  - Exemple : `!kick @Utilisateur Comportement inapproprié`

### Commandes de gestion
- `!sanctions [@utilisateur]` - Affiche l'historique des sanctions d'un utilisateur
  - Exemple : `!sanctions @Utilisateur`

- `!delsanction [ID sanction]` - Supprime une sanction de l'historique
  - Exemple : `!delsanction 42`

- `!clearsanctions [@utilisateur]` - Efface tout l'historique des sanctions d'un utilisateur
  - Exemple : `!clearsanctions @Utilisateur`

## 🔧 Fonctionnalités

- Système complet de gestion des sanctions (warn, mute, ban, kick)
- Durées configurables avec notation flexible (30m, 2h, 7d, etc.)
- Historique détaillé des sanctions par utilisateur
- Système de points de sanction cumulatifs
- Sanctions automatiques basées sur les points accumulés
- Notifications aux utilisateurs sanctionnés
- Logs détaillés pour l'équipe de modération
- Expiration automatique des sanctions temporaires

## ⚙️ Configuration

Le module permet de configurer :
- Les rôles de modération autorisés à utiliser les commandes
- Les seuils de points pour les sanctions automatiques
- Les messages de notification
- Les canaux de logs
- Les durées par défaut pour chaque type de sanction

## 📊 Système de points

Chaque type de sanction attribue un certain nombre de points qui s'accumulent :
- Avertissement : 1 point
- Mute : 2 points
- Kick : 3 points
- Ban temporaire : 4 points
- Ban permanent : 5 points

Ces points peuvent déclencher des sanctions automatiques selon les seuils configurés.

## 🛡️ Permissions requises

- `kick_members` - Pour les commandes kick et warn
- `ban_members` - Pour les commandes ban/unban
- `manage_messages` - Pour la commande mute/unmute
- `manage_roles` - Pour les fonctionnalités de mute via rôle 