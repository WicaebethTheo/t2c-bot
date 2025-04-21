# Module Ranks

Système de gestion des rôles avec attribution par réactions et commandes.

## 📋 Commandes

- `!roleinfo [rôle]` - Affiche des informations sur un rôle
  - Montre le nombre de membres ayant ce rôle, sa couleur, ses permissions, etc.
  - Exemple : `!roleinfo Modérateur`

- `!rolemembers [rôle]` - Liste tous les membres ayant un rôle spécifique
  - Exemple : `!rolemembers Admin`

- `!addrole [@utilisateur] [rôle]` - Ajoute un rôle à un utilisateur
  - Exemple : `!addrole @Wicaebeth Joueur`

- `!removerole [@utilisateur] [rôle]` - Retire un rôle à un utilisateur
  - Exemple : `!removerole @Wicaebeth Joueur`

- `!ranks` - Affiche un menu des rôles disponibles avec réactions
  - Les utilisateurs peuvent réagir pour obtenir ou retirer des rôles

- `!addreactionrole [#canal] [message_id] [emoji] [rôle]` - Ajoute un rôle par réaction à un message existant
  - Exemple : `!addreactionrole #rôles 123456789012345678 🎮 Gamer`

- `!removereactionrole [#canal] [message_id] [emoji]` - Supprime un rôle par réaction d'un message
  - Exemple : `!removereactionrole #rôles 123456789012345678 🎮`

## 🔧 Fonctionnalités

- Attribution de rôles via commandes directes
- Système de rôles par réactions aux messages
- Menu interactif de rôles avec réactions
- Vérification des permissions
- Protection contre les conflits de rôles
- Journalisation des actions d'attribution/retrait de rôles
- Gestion de plusieurs ensembles de rôles pour différentes catégories

## 🛡️ Permissions

La plupart des commandes nécessitent la permission `manage_roles`. Les utilisateurs peuvent toujours utiliser les systèmes de réactions configurés pour obtenir/retirer les rôles autorisés.

## 🎭 Types de rôles

Le module peut gérer différents types de rôles :

- **Rôles couleur** - Rôles purement esthétiques pour changer la couleur du nom
- **Rôles de jeux** - Rôles pour indiquer les jeux auxquels un membre joue
- **Rôles de notification** - Rôles pour recevoir des notifications spécifiques
- **Rôles d'accès** - Rôles donnant accès à des canaux spécifiques

## 📝 Exemple de menu de rôles

Le menu créé par la commande `!ranks` ressemble à :

```
🎮 Rôles de jeux
-----------------
🎯 Valorant
🚗 Rocket League
⚔️ League of Legends

🎨 Couleurs de nom
------------------
🔴 Rouge
🟢 Vert
🔵 Bleu

📢 Notifications
---------------
📣 Annonces
🎉 Événements
```

Les utilisateurs peuvent réagir avec les émojis pour obtenir ou retirer les rôles correspondants. 