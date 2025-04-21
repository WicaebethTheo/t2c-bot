# Module Twitch

Intégration avec Twitch pour les notifications de stream et gestion des rôles.

## 📋 Commandes

### Commandes Utilisateurs
- `!twitch set [nom_chaîne]` - Lie votre compte Twitch à votre profil Discord
  - Exemple : `!twitch set wicaebeth`

- `!twitch info [utilisateur]` - Affiche les informations Twitch d'un utilisateur
  - Si aucun utilisateur n'est spécifié, affiche vos propres informations
  - Exemple : `!twitch info @Utilisateur`

- `!twitch status [nom_chaîne]` - Vérifie si une chaîne Twitch est en ligne
  - Exemple : `!twitch status wicaebeth`

### Commandes Administrateurs
- `!twitchset` - Affiche la configuration actuelle du module Twitch

- `!twitchset channel [#canal]` - Définit le canal pour les annonces de stream
  - Exemple : `!twitchset channel #streams`

- `!twitchset role [rôle]` - Définit le rôle à attribuer aux streamers
  - Exemple : `!twitchset role Streamer`

- `!twitchset toggle` - Active/désactive les annonces de stream

- `!twitchset add [nom_chaîne]` - Ajoute une chaîne Twitch à la liste de suivi
  - Exemple : `!twitchset add wicaebeth`

- `!twitchset remove [nom_chaîne]` - Retire une chaîne Twitch de la liste de suivi
  - Exemple : `!twitchset remove wicaebeth`

- `!twitchset list` - Affiche la liste des chaînes Twitch suivies

- `!twitchset message [message]` - Personnalise le message d'annonce
  - Utilise des placeholders comme {streamer}, {title}, {game}
  - Exemple : `!twitchset message {streamer} est en direct ! Rejoignez le stream : {url}`

## 🔧 Fonctionnalités

- Notifications automatiques lorsqu'un membre du serveur commence à streamer
- Suivi de chaînes Twitch spécifiques
- Attribution/retrait automatique d'un rôle aux streamers en direct
- Messages d'annonce personnalisables avec informations du stream
- Vérification périodique du statut des streams
- Intégration avec l'API Twitch
- Embeds personnalisés avec aperçu du stream

## ⚙️ Configuration

Le module nécessite :
- Un Client ID et Secret Twitch pour l'API
- Un canal d'annonce configuré
- Éventuellement un rôle de streamer

Les configurations sont stockées via le système Config de Red Bot.

## 🔄 Cycle de vie des notifications

1. Le module vérifie périodiquement le statut des chaînes suivies
2. Quand un stream démarre, le bot envoie une notification dans le canal configuré
3. Le rôle de streamer est attribué si configuré
4. Quand le stream se termine, le rôle est retiré
5. Une vérification anti-spam empêche les notifications trop fréquentes

## 📝 Message d'annonce personnalisable

Le message d'annonce peut contenir les placeholders suivants :
- `{streamer}` - Nom de la chaîne Twitch
- `{title}` - Titre du stream
- `{game}` - Jeu diffusé
- `{viewers}` - Nombre de spectateurs
- `{url}` - Lien vers le stream
- `{preview}` - Image d'aperçu (pour les embeds) 