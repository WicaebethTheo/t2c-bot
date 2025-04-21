# Module RulesPP

Système de règles spécifiques pour les parties personnalisées (PP) avec interface d'acceptation interactive.

## 📋 Commandes

- `!rulespp` - Affiche les règles des parties personnalisées
  - Présente un embed formaté avec toutes les sections des règles
  - Inclut un bouton d'acceptation pour participer aux PP

- `!rulespp setup` - Configure le système de règles PP
  - Commande réservée aux administrateurs
  - Permet de définir le canal d'affichage des règles

- `!rulespp edit` - Modifie le contenu des règles PP
  - Commande réservée aux administrateurs
  - Ouvre un assistant interactif pour éditer les sections

## 🔧 Fonctionnalités

- Affichage formaté des règles en sections bien organisées
- Système d'acceptation des règles avec boutons interactifs
- Attribution automatique d'un rôle aux membres acceptant les règles
- Personnalisation complète du contenu des règles
- Interface utilisateur intuitive
- Logs d'acceptation des règles

## 🎮 Sections des règles PP

Les règles des parties personnalisées sont organisées en sections :
- **Préparation** - Comment se préparer avant une partie
- **En jeu** - Limites d'armes et comportement attendu
- **Objectif** - Description du but des parties personnalisées
- **Comportement** - Attitude attendue des participants

## ⚙️ Configuration

Le module est préconfiguré avec :
- Rôle attribué après acceptation : "PP"
- Canal par défaut des règles PP : #parties-personnalisées
- Système de log pour suivre les acceptations

## 🛡️ Permissions

Les commandes administratives (`setup` et `edit`) nécessitent la permission `administrator` ou les permissions équivalentes. Les membres standard peuvent uniquement utiliser la commande `!rulespp` pour consulter les règles.

## 📝 Exemple de règles

Le système affiche les règles selon un format similaire à :

```
PRÉPARATION
• Staff PP en ligne
• Équipes équilibrées
• Annonce des règles

EN JEU
🔶 LIMITES D'ARMES
• Interdiction de certaines armes ou compétences
• Restrictions sur les équipements

OBJECTIF
Les parties personnalisées visent à créer un environnement amusant et compétitif, où tout le monde peut s'amuser dans le respect des règles.
```

Le bouton "J'accepte les règles" permet aux utilisateurs d'obtenir le rôle requis pour participer. 