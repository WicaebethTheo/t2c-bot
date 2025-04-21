# Module DiscordRanks

Système complet de niveaux et d'expérience avec récompenses de rôles et reset automatique.

## 📋 Commandes

### Commandes Utilisateurs
- `!level` ou `!rank` - Affiche votre niveau et votre expérience
- `!level @membre` - Affiche le niveau et l'expérience d'un autre membre
- `!top` ou `!leaderboard` - Affiche le classement des membres par niveau
  - Utilisez `!top [page]` pour voir les différentes pages du classement

### Commandes Administrateurs
- `!levelset` - Affiche la configuration actuelle du système
- `!levelset channel [#canal]` - Définit le canal pour les annonces de level up
- `!levelset toggle` - Active ou désactive le système de niveaux
- `!levelset xpmessage [montant]` - Définit l'XP gagné par message
- `!levelset xpvoice [montant]` - Définit l'XP gagné par minute en vocal
- `!levelset cooldown [secondes]` - Définit le cooldown entre les gains d'XP
- `!levelset formula [base]` - Définit la formule de calcul des niveaux
- `!levelset addrole [niveau] [@role]` - Ajoute une récompense de rôle
- `!levelset removerole [niveau]` - Supprime une récompense de rôle
- `!levelset reset [@membre]` - Réinitialise les statistiques d'un membre
- `!levelset forcereset` - Force un reset complet des niveaux
- `!levelset checkroles` - Vérifie et attribue les rôles manquants
- `!announce` - Crée une annonce pour présenter le système de niveaux
- `!checklevels` - Vérifie les niveaux de tous les membres

## 🔧 Fonctionnalités

- Gain d'XP par message avec cooldown configurable
- Gain d'XP par temps passé en vocal
- Système de niveau basé sur une formule paramétrable
- Récompenses de rôles automatiques à des niveaux spécifiques
- Réinitialisation automatique tous les 90 jours
- Annonces de level up personnalisées
- Barre de progression visuelle
- Classement des membres
- Statistiques détaillées (messages, temps vocal)

## ⚙️ Configuration par défaut

- XP par message : 15 (±20%)
- XP par minute en vocal : 10
- Cooldown entre les gains d'XP : 60 secondes
- Formule de niveau : XP = 100 × niveau²
- Récompenses de rôles :
  - Niveau 20 : Rôle "Actifs" (ID: 1352739404657201175)
  - Niveau 30 : Rôle "Actif+" (ID: 1352739400261304463)
- Reset automatique tous les 90 jours 