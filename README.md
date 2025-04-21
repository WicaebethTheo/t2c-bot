# RedBot - Bot Discord Multifonction

Un bot Discord puissant basé sur [Red-Bot](https://github.com/Cog-Creators/Red-DiscordBot), extensible via des modules (cogs) personnalisés.

## 🎮 Fonctionnalités

Le bot comprend de nombreux modules (cogs) offrant une variété de fonctionnalités :

### 🔄 Animation
- Organisation et planification d'événements de jeu
- Sélection de jeux et d'horaires via interface interactive

### 🎙️ Création de Salons Vocaux
- Création automatique de salons vocaux personnalisés
- Contrôles pour rendre les salons publics/privés
- Gestion des limites de membres

### 🎯 MapRoulette
- Sélection aléatoire de cartes pour Valorant
- Système de vote pour accepter/refuser une carte
- Animation de chargement personnalisée

### 📊 Système de Niveaux et XP
- Attribution d'XP pour les messages et le temps passé en vocal
- Système de niveaux avec récompenses de rôles
- Classements et statistiques des membres
- Réinitialisation automatique tous les 90 jours

### 📢 Publication
- Système de publication formatée vers des canaux spécifiques
- Personnalisation du titre et du contenu

### 📋 Règlements
- Affichage des règles avec formatage avancé
- Système d'acceptation des règles

### 📊 ShowStats
- Affichage automatique des statistiques du serveur dans les noms de canaux
- Suivi du nombre de membres et de boosts

### 🎫 Ticket
- Création de tickets de support
- Gestion des demandes d'aide

### 🧹 Clear
- Nettoyage de messages avec diverses options

## ⚙️ Installation

1. Installer Red-Bot en suivant les [instructions officielles](https://docs.discord.red/en/stable/install_guides/index.html)
2. Cloner ce dépôt dans le dossier des cogs de Red-Bot
3. Charger les modules souhaités avec la commande `[p]load <nom_du_module>`

## 📚 Commandes Principales

- `!animation` - Créer une nouvelle annonce d'animation de jeu
- `!roulette` - Lancer la sélection aléatoire d'une carte
- `!level` - Voir votre niveau actuel
- `!top` - Afficher le classement des membres
- `!publication` - Démarrer une nouvelle publication
- `!creationvoc` - Configurer le système de création de salons vocaux

## 👨‍💻 Développement

Pour ajouter de nouveaux modules ou modifier les existants, suivez la structure standard des cogs Red-Bot :

```python
from redbot.core import commands

class MonModule(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command()
    async def macommande(self, ctx):
        await ctx.send("Hello World!")

async def setup(bot):
    await bot.add_cog(MonModule(bot))
```

## 🔧 Configuration

Chaque module dispose de ses propres commandes de configuration, généralement accessibles via `!<module>set` (ex: `!levelset`).

## 📄 Licence

Ce projet est sous licence MIT - voir le fichier LICENSE pour plus de détails. 