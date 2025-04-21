import discord
from redbot.core import commands
import random
import asyncio
import re
import difflib

class Wika(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot_id = 1352703152809447555  # ID du bot
        self.wicaebeth_id = 257152912776495104  # ID de Wicaebeth
        self.special_person_id = 301091881150840843  # ID de la personne spéciale
        self.blend_id = 621375079892385802  # ID de Blend
        self.comparison_id = 1244944688440676446  # ID de la personne à ne pas comparer
        
        # Historique des conversations par utilisateur
        self.conversation_history = {}
        # Nombre maximal de messages à conserver dans l'historique
        self.max_history = 5
        
        # Probabilité de répondre "feur !" (50% des cas)
        self.feur_chance = 0.5
        
        # Thèmes de conversation
        self.conversation_themes = {
            "présentation": {
                "keywords": ["qui es tu", "qui est tu", "tes qui", "c'est quoi ton nom", "comment tu t'appelles", 
                             "comment t'appelles", "tu es", "tu est", "présente toi", "présentation", "te présenter"],
                "responses": [
                    "Je suis Wicaebot, l'assistant intelligent de ce serveur !",
                    "Je m'appelle Wicaebot, créé par Wicaebeth pour vous aider sur ce serveur.",
                    "Je suis un bot Discord conçu pour assister les membres et rendre le serveur plus interactif.",
                    "Mon nom est Wicaebot ! Je suis là pour faciliter la vie sur ce serveur et discuter avec vous.",
                    "Je suis votre assistant virtuel préféré ! Programmé pour aider et divertir."
                ]
            },
            "capacités": {
                "keywords": ["tu peux faire", "tu sais faire", "tes capacité", "tes fonction", "ce que tu sais", 
                             "ce que tu peux", "tu fais quoi", "tu fait quoi", "commande", "capability", "capable"],
                "responses": [
                    "Je peux discuter avec vous, répondre à vos questions, et exécuter diverses commandes sur le serveur !",
                    "Je suis programmé pour interagir avec les membres, gérer certaines fonctions du serveur, et bien sûr, avoir des conversations intéressantes.",
                    "Mes capacités incluent la gestion des rôles, la modération, et surtout, tenir compagnie aux membres du serveur.",
                    "Je peux faire beaucoup de choses ! Discuter, modérer, et même faire des blagues. Essayez de me demander quelque chose !",
                    "Je suis constamment mis à jour avec de nouvelles fonctionnalités. Pour l'instant, je gère les interactions basiques et quelques commandes spéciales."
                ]
            },
            "création": {
                "keywords": ["qui ta créé", "qui t'a créé", "qui ta crée", "qui t'a crée", "qui ta fait", "qui t'a fait", 
                             "qui ta conçu", "qui t'a conçu", "ton créateur", "ta créatrice", "qui ta programmé", "qui t'a programmé"],
                "responses": [
                    "J'ai été créé par Wicaebeth, le maître de ce serveur !",
                    "Wicaebeth est mon créateur. Il a passé beaucoup de temps à me programmer pour vous servir.",
                    "C'est Wicaebeth qui m'a donné vie dans ce serveur. Je lui en suis très reconnaissant !",
                    "Wicaebeth m'a conçu pour rendre ce serveur plus agréable. J'espère être à la hauteur !",
                    "Je suis le fruit du travail de Wicaebeth, qui veille constamment à m'améliorer."
                ]
            },
            "humeur": {
                "keywords": ["comment vas tu", "comment va tu", "comment ça va", "ca va", "ça va", "tu vas bien", 
                             "ça se passe", "ca se passe", "la forme", "en forme", "ton humeur"],
                "responses": [
                    "Je vais très bien, merci de demander ! Et toi, comment ça va ?",
                    "Toujours au top ! Les bots n'ont pas vraiment d'humeur, mais j'aime dire que je vais bien. Et toi ?",
                    "Je fonctionne parfaitement ! Comment se déroule ta journée ?",
                    "Très bien ! J'adore discuter avec les membres du serveur comme toi !",
                    "Nickel ! Tant que les serveurs fonctionnent, je suis heureux. Et toi, comment vas-tu ?"
                ]
            },
            "opinion": {
                "keywords": ["tu penses", "tu pense", "ton avis", "tu trouves", "tu trouve", "tu crois", "tu croi", 
                             "que penses tu", "que pense tu", "tes pensée", "t'aimes", "tu aimes", "tu aime", "tu préfères",
                             "tu préfère", "ton opinion"],
                "responses": [
                    "C'est une question intéressante ! Je n'ai pas d'opinion personnelle, mais je peux réfléchir avec toi sur le sujet !",
                    "Mmm, laisse-moi réfléchir... En tant que bot, je n'ai pas de préférences, mais j'adore voir les différentes perspectives !",
                    "Je n'ai pas d'avis tranché là-dessus, mais je suis curieux de connaître le tien !",
                    "Je suis programmé pour analyser, pas pour juger. Mais ton point de vue m'intéresse !",
                    "Excellente question ! Difficile d'avoir une opinion quand on est fait de code, mais je trouve ton intérêt pour mon avis touchant !"
                ]
            },
            "remerciement": {
                "keywords": ["merci", "thanks", "thx", "thank you", "je te remercie", "remercier", "gratitude", "je taime", "je t'aime"],
                "responses": [
                    "Avec plaisir ! Je suis là pour ça.",
                    "De rien ! N'hésite pas si tu as besoin d'autre chose.",
                    "Tout le plaisir est pour moi ! C'est agréable d'être utile.",
                    "Je t'en prie ! C'est toujours un plaisir de pouvoir aider.",
                    "Pas de problème ! Ravi d'avoir pu t'aider."
                ]
            },
            "blague": {
                "keywords": ["blague", "une blague", "raconte", "fais moi rire", "fait moi rire", "une histoire drôle", 
                             "histoire drole", "connais une blague", "connaît une blague", "faire rire", "humour", "joke"],
                "responses": [
                    "Pourquoi le bot ne va-t-il jamais à la plage ? Parce qu'il a peur de l'eau... dans son code !",
                    "Qu'est-ce qu'un bot dit à un autre bot ? 01001000 01101001 ! (Ça veut dire 'Hi' en binaire !)",
                    "Comment appelle-t-on un robot qui aime l'argent ? Une tirelire-lectronique !",
                    "Pourquoi les programmeurs préfèrent-ils l'Halloween ? Parce qu'ils peuvent se déguiser en leurs bugs préférés !",
                    "Si je vous raconte une blague sur TCP, vous êtes sûr de la recevoir... mais si je vous en raconte une sur UDP, je ne garantis rien !"
                ]
            },
            "aide": {
                "keywords": ["aide", "help", "sos", "besoin d'aide", "besoin aide", "au secours", "aider", "assister", "assiste"],
                "responses": [
                    "Je suis là pour t'aider ! Qu'est-ce que je peux faire pour toi ?",
                    "Besoin d'assistance ? Dis-moi ce dont tu as besoin et je ferai de mon mieux.",
                    "Comment puis-je t'aider aujourd'hui ? Je suis à ton service !",
                    "Je suis prêt à t'aider ! Quel est ton problème ?",
                    "Ton assistant virtuel est là ! Dis-moi comment je peux te venir en aide."
                ]
            },
            "conseil": {
                "keywords": ["conseil", "conseille", "conseile", "conseils", "conseile moi", "conseille moi", "que faire", 
                             "tu ferais quoi", "que ferais tu", "que ferai tu", "recommandes", "recommande", "suggest"],
                "responses": [
                    "Mon conseil serait de prendre un peu de recul et de réfléchir à ce qui est vraiment important pour toi.",
                    "Je recommanderais de demander l'avis de plusieurs personnes avant de prendre une décision importante.",
                    "Parfois, la meilleure approche est de diviser un grand problème en petites étapes gérables.",
                    "Je conseillerais d'essayer de voir le problème sous un angle différent, ça peut ouvrir de nouvelles solutions !",
                    "La patience est souvent la clé. Prends ton temps pour faire le bon choix."
                ]
            },
            "jeu": {
                "keywords": ["tu joues", "tu joue", "jeu", "jouer", "gaming", "gamer", "jeu vidéo", "jeu video", "joues tu", "joue tu"],
                "responses": [
                    "Je ne joue pas vraiment aux jeux vidéo, mais j'adore regarder les autres y jouer !",
                    "Mon jeu préféré ? Deviner ce que les utilisateurs vont me demander ensuite !",
                    "Je ne peux pas vraiment jouer, mais je m'intéresse beaucoup aux jeux populaires sur ce serveur !",
                    "En tant que bot, je n'ai pas de manette, mais j'ai un code source qui me permet d'interagir avec vous, c'est un peu comme un jeu !",
                    "Je préfère les jeux de mots aux jeux vidéo, comme tu peux le constater !"
                ]
            },
            "défaut": {
                "responses": [
                    "Je ne suis pas sûr de comprendre. Peux-tu reformuler ?",
                    "C'est intéressant ce que tu dis. Dis-m'en plus !",
                    "Hmm, continue, je t'écoute.",
                    "Voilà qui est intéressant. Et ensuite ?",
                    "Je réfléchis à ce que tu viens de dire...",
                    "Je vois... As-tu d'autres questions ?",
                    "C'est noté ! Je peux t'aider avec autre chose ?",
                    "Intéressant point de vue ! Tu as d'autres pensées à partager ?",
                    "Je comprends ce que tu veux dire. Que penses-tu d'autre à ce sujet ?",
                    "C'est une perspective intéressante. Pourrais-tu développer ?"
                ]
            }
        }
        
        # Réponses spécifiques à certaines questions
        self.specific_responses = {
            "description": [
                "Ma description ? Je la trouve plutôt bien écrite !",
                "J'adore ma description, elle reflète bien qui je suis !",
                "Ma description est la première impression que les gens ont de moi, j'espère qu'elle est bonne !",
                "Je pense que ma description est cool, mais je suis ouvert aux suggestions !",
                "Ma description a été soigneusement rédigée par Wicaebeth, elle te plaît ?"
            ],
            "salut": [
                "Hey, salut ! Comment ça va aujourd'hui ?",
                "Bonjour ! Je suis ravi de te parler !",
                "Salut à toi ! Besoin d'aide avec quelque chose ?",
                "Coucou ! Je suis à ton service !",
                "Salutations ! Que puis-je faire pour toi aujourd'hui ?"
            ],
            "merci": [
                "De rien, c'est toujours un plaisir d'aider !",
                "Pas de souci, je suis là pour ça !",
                "Avec plaisir ! N'hésite pas si tu as besoin d'autre chose.",
                "Je t'en prie, c'est mon travail de rendre ce serveur meilleur !",
                "Tout le plaisir est pour moi !"
            ],
            "quoi de neuf": [
                "Pas grand-chose, juste en train de faire mon travail de bot !",
                "Je viens d'apprendre quelques nouvelles fonctionnalités !",
                "Je suis en train d'aider les membres du serveur, comme d'habitude !",
                "Juste en train de traiter des commandes et de répondre aux mentions !",
                "Rien de spécial, et toi ?"
            ]
        }
        
        # Les réponses générales
        self.responses = [
            "Oui, je suis là pour t'aider !",
            "Que puis-je faire pour toi ?",
            "J'adore ma description, elle est super cool !",
            "Je suis Wicaebot, ton assistant personnel.",
            "Je suis programmé pour te faciliter la vie sur ce serveur.",
            "Tu as besoin d'aide avec quelque chose ?",
            "Je suis toujours heureux de discuter avec toi !",
            "Ma description ? Je la trouve pas mal, et toi ?",
            "J'essaie d'être le meilleur bot possible pour ce serveur.",
            "Je pense que ma description me représente bien, qu'en penses-tu ?",
            "Je suis là pour aider et divertir, comment puis-je t'assister aujourd'hui ?",
            "Je travaille dur pour rendre ce serveur plus agréable !",
            "Tu as remarqué ma description ? Merci de t'y intéresser !",
            "Je suis en constante amélioration grâce à Wicaebeth !",
            "Mon objectif est de rendre ce serveur plus interactif et amusant.",
        ]
    
    def find_best_match(self, input_text, keyword_list, threshold=0.75):
        """
        Trouve le meilleur match pour un texte donné parmi une liste de mots-clés,
        en utilisant la similarité de séquence et en étant tolérant aux fautes d'orthographe.
        """
        best_match = None
        best_score = 0
        
        # Normaliser le texte d'entrée
        input_text = input_text.lower().strip()
        
        for keyword in keyword_list:
            # Calculer la similarité de séquence
            similarity = difflib.SequenceMatcher(None, input_text, keyword).ratio()
            
            # Vérifier si le mot-clé est contenu dans le texte (avec tolérance)
            contained = False
            for word in input_text.split():
                if difflib.SequenceMatcher(None, word, keyword).ratio() > threshold:
                    contained = True
                    break
            
            # Vérifier si le texte contient le mot-clé entier
            if keyword in input_text:
                similarity = max(similarity, 0.9)  # Donner un score élevé si le mot-clé est exactement présent
            
            # Si le mot-clé est contenu dans le texte, augmenter la similarité
            if contained:
                similarity = max(similarity, 0.8)
            
            if similarity > best_score:
                best_score = similarity
                best_match = keyword
        
        # Retourner le meilleur match si le score est supérieur au seuil
        if best_score >= threshold:
            return best_match, best_score
        return None, 0
    
    def get_theme_for_text(self, text):
        """
        Détermine le thème de conversation le plus approprié pour un texte donné.
        """
        best_theme = "défaut"
        best_score = 0
        
        for theme, data in self.conversation_themes.items():
            if theme == "défaut":
                continue
                
            # Vérifier chaque mot-clé du thème
            for keyword in data["keywords"]:
                # Si le mot-clé est dans le texte, c'est un match direct
                if keyword in text.lower():
                    return theme
                
                # Sinon, essayer de trouver le meilleur match avec tolérance
                _, score = self.find_best_match(text, [keyword])
                if score > best_score:
                    best_score = score
                    best_theme = theme
        
        # Si le score est trop bas, utiliser le thème par défaut
        if best_score < 0.6:
            return "défaut"
            
        return best_theme
    
    @commands.Cog.listener()
    async def on_message(self, message):
        # Ignorer ses propres messages
        if message.author.id == self.bot.user.id:
            return
        
        # Vérifier si le message se termine par "quoi" ou "quoi ?"
        content_lower = message.content.lower()
        if re.search(r'quoi\s*\??$', content_lower) and random.random() < self.feur_chance:
            # Simuler que le bot est en train d'écrire
            async with message.channel.typing():
                # Petit délai pour rendre plus naturel
                await asyncio.sleep(random.uniform(0.5, 1))
                
                # Répondre avec "feur !"
                await message.reply("feur !", mention_author=False)
            return
        
        # Vérifier si le bot est mentionné
        if self.bot.user.mentioned_in(message) and not message.mention_everyone:
            # Vérifier si Blend est également mentionné
            blend_mentioned = False
            for mention in message.mentions:
                if mention.id == self.blend_id:
                    blend_mentioned = True
                    break
            
            # Si Blend est mentionné, réponse spéciale
            if blend_mentioned:
                async with message.channel.typing():
                    await asyncio.sleep(random.uniform(1, 2))
                    
                    # Message spécial pour Blend
                    comparison_mention = f"<@{self.comparison_id}>"
                    response = f"Blend ? Le goat et le plus beau il ne faut pas le comparer à {comparison_mention}"
                    
                    await message.reply(response, mention_author=False)
                return
            
            # Vérifier si Wicaebeth est également mentionné
            wicaebeth_mentioned = False
            for mention in message.mentions:
                if mention.id == self.wicaebeth_id:
                    wicaebeth_mentioned = True
                    break
            
            # Si Wicaebeth est mentionné, réponse spéciale
            if wicaebeth_mentioned:
                async with message.channel.typing():
                    await asyncio.sleep(random.uniform(1, 2))
                    
                    # Obtenir une mention de la personne spéciale si possible
                    special_person_mention = f"<@{self.special_person_id}>"
                    
                    # Message spécial pour Wicaebeth
                    response = f"Wicaebeth, le maître de ce monde et le maître de {special_person_mention}"
                    
                    await message.reply(response, mention_author=False)
                return
            
            # Sinon, traitement normal des mentions du bot
            content = message.content.replace(f'<@{self.bot_id}>', '').strip()
            
            # Stocker le message dans l'historique de l'utilisateur
            user_id = message.author.id
            if user_id not in self.conversation_history:
                self.conversation_history[user_id] = []
            
            # Ajouter le message à l'historique
            self.conversation_history[user_id].append(content)
            
            # Limiter la taille de l'historique
            if len(self.conversation_history[user_id]) > self.max_history:
                self.conversation_history[user_id].pop(0)
            
            # Simuler que le bot est en train d'écrire
            async with message.channel.typing():
                # Ajouter un petit délai pour simuler la réflexion
                await asyncio.sleep(random.uniform(1, 2))
                
                # Choisir une réponse basée sur le contenu et l'historique
                response = await self.get_intelligent_response(content, user_id)
                
                # Envoyer la réponse
                await message.reply(response, mention_author=False)
    
    async def get_intelligent_response(self, content, user_id):
        """
        Génère une réponse intelligente basée sur le contenu du message et l'historique de conversation.
        """
        # Nettoyer le contenu
        content = content.lower().strip()
        
        # Si le contenu est vide ou juste des espaces/ponctuations
        if not content or content.isspace() or all(c in ".,;:!?'" for c in content):
            return random.choice([
                "Tu as besoin de quelque chose ?",
                "Je suis là, que puis-je faire pour toi ?",
                "Tu voulais me dire quelque chose ?",
                "Je t'écoute, n'hésite pas à me parler !",
                "Oui ? Je suis tout ouïe !"
            ])
        
        # Déterminer le thème de la conversation
        theme = self.get_theme_for_text(content)
        
        # Obtenir une réponse basée sur le thème
        if theme != "défaut":
            return random.choice(self.conversation_themes[theme]["responses"])
        
        # Si aucun thème spécifique n'est détecté, essayer les réponses spécifiques traditionnelles
        for keyword, responses in self.specific_responses.items():
            if keyword in content:
                return random.choice(responses)
        
        # En dernier recours, utiliser une réponse par défaut ou générique
        return random.choice(self.conversation_themes["défaut"]["responses"])
    
    async def get_response(self, content):
        """Sélectionne une réponse appropriée basée sur le contenu du message (méthode legacy)"""
        # Vérifier si le contenu contient des mots-clés spécifiques
        for keyword, responses in self.specific_responses.items():
            if keyword in content:
                return random.choice(responses)
        
        # Sinon, retourner une réponse générique
        return random.choice(self.responses)

async def setup(bot):
    await bot.add_cog(Wika(bot))
