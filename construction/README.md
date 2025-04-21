# Module Construction

Module d'affichage de messages "En construction" avec animations et différents formats.

## 📋 Commandes

- `!construction` - Affiche un message simple "En construction"
  - Message basique indiquant qu'une fonctionnalité est en développement

- `!construction2` - Affiche un message animé "En construction"
  - Version animée avec progression visuelle

- `!construction3` - Affiche un message détaillé de projet en construction
  - Version élaborée avec informations sur le projet et son développement

## 🔧 Fonctionnalités

- Plusieurs formats de messages disponibles
- Animation avec barres de progression
- Embeds personnalisés avec détails du projet
- Possibilité d'inclure des informations sur l'état d'avancement
- Contrôle d'accès via système de permissions

## 🔒 Permissions

Ces commandes nécessitent un rôle spécifique pour être utilisées. La fonction `has_required_role()` vérifie si l'utilisateur possède les permissions nécessaires.

## 🎨 Styles de messages

### Message simple
Un message textuel simple indiquant qu'une fonctionnalité est en cours de développement.

### Message animé
Un message avec une barre de progression simulant l'avancement des travaux.

### Message détaillé
Un embed complet avec :
- Titre du projet
- Description
- État d'avancement
- Date prévue de fin
- Équipe impliquée

## 📝 Exemple d'utilisation

Utilisez ces commandes dans les canaux où vous souhaitez informer les utilisateurs qu'une fonctionnalité est en cours de développement. Par exemple :

```
!construction3
```

Affichera un embed détaillé avec les informations sur le projet en cours. 