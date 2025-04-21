# Module Stats-Staff

Système de suivi d'activité et statistiques pour l'équipe de modération.

## 📋 Commandes

### Commandes de base
- `!staffstats` - Affiche vos statistiques personnelles de modération
  - Montre le nombre d'actions effectuées par catégorie
  - Exemple : `!staffstats`

- `!staffstats [@utilisateur]` - Affiche les statistiques d'un membre du staff
  - Exemple : `!staffstats @Wicaebeth`

- `!staffreport` - Génère un rapport d'activité du staff pour la semaine
  - Exemple : `!staffreport`

### Commandes administratives
- `!staffset` - Affiche les paramètres actuels du module
  - Exemple : `!staffset`

- `!staffset roles [role1] [role2]...` - Définit les rôles considérés comme staff
  - Exemple : `!staffset roles @Modérateur @Admin`

- `!staffset channel [#canal]` - Définit le canal pour les rapports automatiques
  - Exemple : `!staffset channel #staff-logs`

- `!staffset reset` - Réinitialise toutes les statistiques
  - Exemple : `!staffset reset`

- `!staffset reportday [jour]` - Définit le jour d'envoi du rapport hebdomadaire
  - Exemple : `!staffset reportday lundi`

## 🔧 Fonctionnalités

- Suivi automatique des actions de modération
- Statistiques détaillées par membre du staff
- Rapports hebdomadaires automatiques
- Graphiques d'activité visuels
- Comparaison d'activité entre les périodes
- Suivi des types d'actions (warns, mutes, bans, etc.)
- Détection des périodes d'inactivité
- Alertes pour les membres inactifs

## 📊 Statistiques suivies

Le module suit plusieurs catégories d'actions :
- **Messages supprimés** - Nombre de messages supprimés
- **Avertissements** - Nombre d'avertissements donnés
- **Mutes** - Nombre d'utilisateurs réduits au silence
- **Kicks** - Nombre d'utilisateurs expulsés
- **Bans** - Nombre d'utilisateurs bannis
- **Tickets** - Nombre de tickets traités
- **Temps en vocal** - Temps passé en salons vocaux de modération

## 🔄 Rapports automatiques

Le module génère automatiquement des rapports hebdomadaires contenant :
- Résumé de l'activité globale du staff
- Classement des membres les plus actifs
- Statistiques par type d'action
- Graphiques d'évolution
- Tendances par rapport aux semaines précédentes

## ⚙️ Configuration

Les administrateurs peuvent configurer :
- Les rôles considérés comme staff
- Le jour d'envoi du rapport hebdomadaire
- Le canal de destination des rapports
- Les types d'actions à suivre
- La fréquence des rapports (quotidien, hebdomadaire, mensuel) 