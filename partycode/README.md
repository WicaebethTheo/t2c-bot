# Module PartyCode

Système de création et gestion de parties personnalisées avec codes d'accès.

## 📋 Commandes

- `!party create [jeu] [description]` - Crée une nouvelle partie personnalisée
  - Exemple : `!party create Valorant 5v5 Custom Game`

- `!party join [code]` - Rejoint une partie existante via son code
  - Exemple : `!party join ABC123`

- `!party leave` - Quitte la partie actuelle
  - Exemple : `!party leave`

- `!party list` - Affiche la liste des parties disponibles
  - Exemple : `!party list`

- `!party info [code]` - Affiche les détails d'une partie
  - Si aucun code n'est spécifié, affiche les détails de votre partie actuelle
  - Exemple : `!party info ABC123`

- `!party invite [@utilisateur]` - Invite un utilisateur à rejoindre votre partie
  - Exemple : `!party invite @Wicaebeth`

- `!party kick [@utilisateur]` - Expulse un utilisateur de votre partie
  - Réservé à l'hôte de la partie
  - Exemple : `!party kick @Utilisateur`

- `!party close` - Ferme votre partie
  - Réservé à l'hôte de la partie
  - Exemple : `!party close`

- `!party rank [rang]` - Définit votre rang pour les matchmaking équilibrés
  - Exemple : `!party rank Diamond`

## 🔧 Fonctionnalités

- Création de parties personnalisées pour différents jeux
- Génération automatique de codes d'invitation
- Système de matchmaking équilibré basé sur les rangs
- Interface utilisateur intuitive avec boutons et menus déroulants
- Suivi des statistiques des parties
- Notification des joueurs lors des événements importants
- Système d'invitation direct via mentions Discord
- Filtrage des parties par jeu, taille et visibilité

## 🎮 Jeux supportés

Le module prend en charge plusieurs jeux populaires :
- Valorant
- League of Legends
- Rocket League
- Minecraft
- Autres (personnalisable)

## 📊 Système de rangs

Pour les jeux compétitifs, les joueurs peuvent définir leur rang pour faciliter la création d'équipes équilibrées :
- Iron
- Bronze
- Silver
- Gold
- Platinum
- Diamond
- Ascendant
- Immortal
- Radiant

## 🔄 Cycle de vie d'une partie

1. Création de la partie par l'hôte avec un jeu et une description
2. Génération d'un code unique pour la partie
3. Invitation des joueurs via code ou commande d'invitation
4. Gestion des joueurs par l'hôte (ajout/expulsion)
5. Lancement de la partie
6. Fermeture automatique après une période d'inactivité ou manuellement par l'hôte

## ⚙️ Configuration

Les administrateurs peuvent configurer :
- Les jeux disponibles
- La durée d'inactivité avant fermeture automatique
- Les permissions requises pour créer une partie
- Les canaux d'annonce des nouvelles parties
- Le nombre maximal de parties simultanées 