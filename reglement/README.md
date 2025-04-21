# Module Reglement

Système d'affichage de règles avec formatage avancé et système d'acceptation.

## 📋 Commandes

- `!reglement` - Affiche les règles du serveur
  - Présente un embed formaté avec toutes les sections des règles
  - Inclut un bouton d'acceptation pour les nouveaux membres

- `!regles` - Alias pour la commande reglement
  - Fonctionnalité identique à `!reglement`

- `!reglementsetup` - Configure le système de règlement
  - Commande réservée aux administrateurs
  - Permet de définir le canal et le message des règles

## 🔧 Fonctionnalités

- Affichage formaté des règles en sections claires
- Système d'acceptation des règles avec boutons interactifs
- Attribution automatique d'un rôle aux membres acceptant les règles
- Personnalisation complète du contenu des règles
- Configuration des canaux et des rôles associés
- Logs d'acceptation des règles

## 🔄 Sections des règles

Les règles sont organisées en sections pour faciliter la lecture :
- **Règles générales** - Comportement attendu et respect mutuel
- **Canaux de discussion** - Utilisation appropriée des différents canaux
- **Contenu partagé** - Règles concernant les images, liens et fichiers
- **Salons vocaux** - Comportement dans les salons vocaux
- **Sanctions** - Conséquences en cas de non-respect des règles

## ⚙️ Configuration

Le module est préconfiguré avec :
- Rôle attribué après acceptation : "Membre"
- Canal par défaut des règles : #règles
- Système de log pour suivre les acceptations

## 🛡️ Permissions

Les commandes administratives nécessitent la permission `administrator` ou les permissions équivalentes. Les membres standard peuvent uniquement utiliser la commande `!reglement` pour consulter les règles. 