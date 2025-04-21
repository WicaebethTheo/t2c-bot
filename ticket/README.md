# Module Ticket

Système de tickets de support pour les utilisateurs avec gestion avancée.

## 📋 Commandes

### Commandes Utilisateurs
- `!ticket` - Crée un nouveau ticket de support
- `!close` - Ferme un ticket en cours (dans le canal du ticket)

### Commandes Administrateurs
- `!ticketsetup` - Configure le système de tickets
- `!adduser [utilisateur]` - Ajoute un utilisateur à un ticket existant
- `!removeuser [utilisateur]` - Retire un utilisateur d'un ticket
- `!ticketrename [nom]` - Renomme un ticket existant

## 🔧 Fonctionnalités

- Interface avec boutons interactifs Discord
- Création de salons privés pour chaque ticket
- Système de logs pour les tickets ouverts et fermés
- Permissions automatiques pour l'équipe de support
- Transcription des tickets fermés
- Notifications aux utilisateurs concernés
- Restriction de visibilité aux rôles spécifiques

## 🔄 Fonctionnement

1. L'utilisateur crée un ticket via la commande ou un bouton
2. Un canal textuel privé est créé avec les permissions appropriées
3. L'équipe de support et le créateur du ticket peuvent communiquer
4. Le ticket peut être fermé par l'utilisateur ou l'équipe de support
5. Une transcription est générée et archivée lors de la fermeture

## ⚙️ Personnalisation

Le système de tickets peut être personnalisé avec :
- Des catégories spécifiques pour différents types de demandes
- Des messages d'accueil personnalisés
- Des rôles d'équipe de support configurables
- Des logs dans des canaux dédiés 