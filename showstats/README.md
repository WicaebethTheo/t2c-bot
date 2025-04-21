# Module ShowStats

Affichage automatique des statistiques du serveur dans les noms de canaux vocaux.

## 📋 Commandes

### Commandes de base
- `!showstats` - Affiche la configuration actuelle du système
- `!showstats refresh` - Force une mise à jour immédiate des statistiques

### Commandes de configuration
- `!showstats toggle` - Active ou désactive le système de statistiques
- `!showstats interval [minutes]` - Définit l'intervalle de mise à jour (minimum 5 minutes)
- `!showstats memberchannel [ID]` - Définit le canal pour afficher le nombre de membres
- `!showstats boostchannel [ID]` - Définit le canal pour afficher le nombre de boosts
- `!showstats memberformat [format]` - Définit le format d'affichage des membres
  - Utilisez `{count}` comme placeholder pour le nombre de membres
  - Exemple : `!showstats memberformat 👥 Membres: {count}`
- `!showstats boostformat [format]` - Définit le format d'affichage des boosts
  - Utilisez `{count}` comme placeholder pour le nombre de boosts
  - Exemple : `!showstats boostformat 🚀 Boosts: {count}`

## 🔧 Fonctionnalités

- Mise à jour automatique à intervalle régulier
- Affichage personnalisable avec formats configurables
- Actualisation des statistiques en temps réel
- Mise à jour intelligente (uniquement si les valeurs changent)
- Sauvegarde de la configuration entre les redémarrages

## ⚙️ Configuration par défaut

- Canaux prédéfinis :
  - Canal des membres : 1352736642045182112
  - Canal des boosts : 1352976542858481795
- Formats par défaut :
  - Membres : `👥 Membres: {count}`
  - Boosts : `🚀 Boosts: {count}`
- Intervalle de mise à jour : 5 minutes
- État initial : Activé

## 🔄 Fonctionnement

1. Le module vérifie périodiquement les statistiques du serveur
2. Si un changement est détecté, il met à jour les noms des canaux vocaux
3. Les statistiques sont affichées selon les formats configurés
4. Le système respecte les limites de l'API Discord (2 changements de nom de canal par 10 minutes) 