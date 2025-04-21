# Module Welcome

Système de messages de bienvenue personnalisés pour les nouveaux membres.

## 📋 Commandes

### Commandes de Configuration
- `!welcomeset` - Affiche la configuration actuelle du système
- `!welcomeset channel [#canal]` - Définit le canal pour les messages de bienvenue
- `!welcomeset toggle` - Active ou désactive les messages de bienvenue
- `!welcomeset message [message]` - Définit le message de bienvenue personnalisé
- `!welcomeset embed` - Configure un message de bienvenue en format embed
- `!welcomeset test` - Teste le message de bienvenue sans attendre un nouvel utilisateur
- `!welcomeset image [on/off]` - Active ou désactive l'image de bienvenue personnalisée

## 🔧 Fonctionnalités

- Messages de bienvenue personnalisables avec variables dynamiques
- Support des formats texte simple ou embed Discord
- Images de bienvenue générées dynamiquement
- Possibilité d'inclure les informations du membre
- Placeholders pour personnaliser le message :
  - `{user}` - Mention de l'utilisateur
  - `{username}` - Nom d'utilisateur sans discriminateur
  - `{server}` - Nom du serveur
  - `{membercount}` - Nombre total de membres
  - `{joinposition}` - Position d'arrivée du membre
- Sauvegarde des configurations entre redémarrages

## 🖼️ Image de Bienvenue

L'image de bienvenue peut inclure :
- Avatar de l'utilisateur
- Nom d'utilisateur
- Message personnalisable
- Arrière-plan configurable
- Compteur de membres

## ⚙️ Configuration par défaut

- Message par défaut : "Bienvenue {user} sur {server} ! Nous sommes maintenant {membercount} membres."
- Format par défaut : Message texte simple
- Image de bienvenue : Désactivée par défaut

## 🔄 Exemples

### Message texte simple
```
Bienvenue @Utilisateur sur Notre Serveur ! Nous sommes maintenant 150 membres.
```

### Message embed
Un embed Discord personnalisé avec titre, description, champs et image. 