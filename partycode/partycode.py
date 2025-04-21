import discord
from discord import ui, app_commands
from discord.ui import Button, Select, View
from redbot.core import commands, Config
import random
import string
import asyncio
import datetime
import re

# Dictionnaire des rangs avec leurs émojis Unicode
RANK_EMOJIS = {
    "Fer": "🔘",
    "Bronze": "🟤",
    "Argent": "⚪",
    "Or": "🟡",
    "Platine": "🔷",
    "Diamant": "💎",
    "Ascendant": "🔺",
    "Immortel": "⭐",
    "Radiant": "👑"
}

# Configuration des rangs
RANKS_CONFIG = [
    {"name": "Fer", "emoji": "🔘"},
    {"name": "Bronze", "emoji": "🟤"},
    {"name": "Argent", "emoji": "⚪"},
    {"name": "Or", "emoji": "🟡"},
    {"name": "Platine", "emoji": "🔷"},
    {"name": "Diamant", "emoji": "💎"},
    {"name": "Ascendant", "emoji": "🔺"},
    {"name": "Immortel", "emoji": "⭐"}
]

# Nombre maximum de participants
MAX_PARTICIPANTS = 10

class RankSelect(ui.Select):
    def __init__(self, parent_view):
        self.parent_view = parent_view
        options = []
        for rank_data in RANKS_CONFIG:
            options.append(discord.SelectOption(
                label=rank_data["name"], 
                value=rank_data["name"],
                description=f"Rang {rank_data['name']}"
            ))
        
        super().__init__(
            placeholder="Sélectionne ton rang (optionnel)",
            min_values=1,
            max_values=1,
            options=options
        )
    
    async def callback(self, interaction: discord.Interaction):
        # Stocke le rang sélectionné
        selected_rank = self.values[0]
        
        # Crée le modal pour demander le pseudo en lui passant la référence à la vue parent
        modal = UsernameModal(selected_rank, self.parent_view)
        await interaction.response.send_modal(modal)

class RankSelectView(View):
    def __init__(self, parent_view):
        super().__init__(timeout=180)
        self.parent_view = parent_view
        self.add_item(RankSelect(parent_view))

class UsernameModal(ui.Modal, title="Entre ton pseudo in-game"):
    def __init__(self, rank, party_view):
        super().__init__()
        self.rank = rank
        self.party_view = party_view
        
    username = ui.TextInput(
        label="Pseudo (avec serveur, ex: Wicaebeth#EUW)",
        placeholder="Pseudo#Serveur",
        required=True,
        min_length=3,
        max_length=50
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            # Trouver l'emoji du rang
            rank_emoji = "🎮"  # Emoji par défaut
            for rank_data in RANKS_CONFIG:
                if rank_data["name"] == self.rank:
                    rank_emoji = rank_data["emoji"]
                    break
                    
            # Ajouter le participant à la liste
            user_info = {
                "user_id": interaction.user.id,
                "username": self.username.value,
                "rank": self.rank,
                "rank_emoji": rank_emoji
            }
            
            self.party_view.participants[interaction.user.id] = user_info
            
            # Créer l'embed de confirmation
            embed = discord.Embed(
                title="✅ Inscription confirmée!",
                description=f"Tu as rejoint la partie en tant que {rank_emoji} {self.rank} avec le pseudo `{self.username.value}`.",
                color=discord.Color.green()
            )
            
            # Ajouter des instructions si nécessaire
            if self.party_view.voice_channel:
                embed.add_field(
                    name="Prochaine étape",
                    value=f"Rejoins le salon vocal {self.party_view.voice_channel.mention} pour participer à la partie!",
                    inline=False
                )
            
            # Révéler le code uniquement dans le message privé
            embed.add_field(
                name="🔑 Code de partie",
                value=f"`{self.party_view.code}`",
                inline=False
            )
            
            # Mettre à jour le message d'origine avec la liste des participants
            await self.party_view.update_message()
            
            # Envoyer la confirmation à l'utilisateur
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
            # Si le nombre de participants atteint le maximum, envoyer un récapitulatif
            if len(self.party_view.participants) >= MAX_PARTICIPANTS:
                await self.party_view.send_summary()
                
        except Exception as e:
            print(f"Erreur lors de l'inscription: {e}")
            await interaction.response.send_message(f"Une erreur est survenue lors de l'inscription: {str(e)}. Veuillez réessayer.", ephemeral=True)

class JoinButton(Button):
    def __init__(self, party_owner):
        super().__init__(
            style=discord.ButtonStyle.primary,
            label="Rejoindre la partie", 
            emoji="🎮"
        )
        self.party_owner = party_owner
    
    async def callback(self, interaction: discord.Interaction):
        # Vérifier si l'utilisateur est déjà inscrit
        if interaction.user.id in self.view.participants:
            return await interaction.response.send_message(
                "Tu es déjà inscrit à cette partie. Si tu souhaites modifier tes informations, contacte l'organisateur.",
                ephemeral=True
            )
        
        # Vérifier si l'utilisateur est dans le salon vocal requis
        if self.view.voice_channel:
            voice_state = interaction.user.voice
            if not voice_state or voice_state.channel.id != self.view.voice_channel.id:
                return await interaction.response.send_message(
                    f"⚠️ Tu dois rejoindre le salon vocal {self.view.voice_channel.mention} pour participer!",
                    ephemeral=True
                )
        
        # Créer un embed pour la sélection du rang
        embed = discord.Embed(
            title="🎮 Rejoindre la partie",
            description="Pour rejoindre cette partie, sélectionne ton rang puis entre ton pseudo in-game.",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="Instructions",
            value="1. Sélectionne ton rang dans le menu ci-dessous\n2. Entre ton pseudo in-game quand demandé\n3. Le code de partie te sera alors révélé",
            inline=False
        )
        
        # Créer une vue temporaire pour la sélection du rang, en passant directement la référence à la vue parent
        rank_view = RankSelectView(self.view)
        
        await interaction.response.send_message(embed=embed, view=rank_view, ephemeral=True)

class PartyCodeView(discord.ui.View):
    def __init__(self, bot, code, party_owner, voice_channel=None, timeout=3600):
        super().__init__(timeout=timeout)
        self.bot = bot
        self.code = code
        self.party_owner = party_owner
        self.participants = {}  # {user_id: {"username": string, "rank": string}}
        self.message = None
        self.voice_channel = voice_channel
        self.created_at = datetime.datetime.now()
        
        # Ajouter le bouton de participation
        self.add_item(JoinButton(party_owner))
    
    def get_embed(self):
        """Crée l'embed pour afficher les informations de la partie"""
        # Déterminer le titre en fonction du salon vocal
        if self.voice_channel:
            channel_name = self.voice_channel.name
            # Extraire le numéro du salon pour les salons Préparation
            prep_num = ""
            if "préparation" in channel_name.lower() or "preparation" in channel_name.lower() or "prépa" in channel_name.lower():
                for char in channel_name:
                    if char.isdigit():
                        prep_num = char
                        break
                if prep_num:
                    title = f"Partie Personnalisée dans le salon Prépa {prep_num}"
                else:
                    title = f"Partie Personnalisée dans {channel_name}"
            else:
                title = f"Partie Personnalisée dans {channel_name}"
        else:
            title = "Partie Personnalisée Valorant"
            
        embed = discord.Embed(
            title=title,
            description="Rejoignez cette partie personnalisée de Valorant!",
            color=discord.Color.purple()
        )
        
        # Ajouter l'organisateur
        embed.add_field(
            name="👑 Organisateur",
            value=f"<@{self.party_owner.id}>",
            inline=False
        )
        
        # Afficher la liste des participants avec leurs noms d'utilisateur et rangs
        if self.participants:
            participants_text = ""
            for user_id, info in self.participants.items():
                username = info["username"]
                rank = info["rank"]
                rank_emoji = info.get("rank_emoji", "")
                
                user_text = f"<@{user_id}> - **{username}** ({rank_emoji} {rank})"
                participants_text += f"• {user_text}\n"
                
            embed.add_field(
                name=f"👥 Participants ({len(self.participants)}/{MAX_PARTICIPANTS})",
                value=participants_text,
                inline=False
            )
        else:
            embed.add_field(
                name=f"👥 Participants (0/{MAX_PARTICIPANTS})",
                value="Aucun participant pour le moment.",
                inline=False
            )
        
        # Ajouter des informations sur le salon vocal si applicable
        if self.voice_channel:
            embed.add_field(
                name="🎙️ Salon vocal",
                value=f"Cette partie se déroulera dans {self.voice_channel.mention}",
                inline=False
            )
            
            embed.add_field(
                name="⚠️ Important",
                value="Vous devez être présent dans ce salon vocal pour rejoindre la partie!",
                inline=False
            )
        
        # Ajouter des informations sur comment rejoindre
        embed.add_field(
            name="Comment rejoindre?",
            value="Clique sur le bouton ci-dessous pour t'inscrire et recevoir le code de partie!",
            inline=False
        )
        
        # Calculer le temps restant
        now = datetime.datetime.now()
        elapsed = now - self.created_at
        remaining_seconds = max(0, 3600 - elapsed.total_seconds())
        minutes = int(remaining_seconds // 60)
        seconds = int(remaining_seconds % 60)
        
        # Ajouter le logo du serveur
        if self.message and self.message.guild and self.message.guild.icon:
            embed.set_thumbnail(url=self.message.guild.icon.url)
        
        embed.set_footer(text=f"Créé par {self.party_owner.display_name} • Fermeture dans {minutes:02d}:{seconds:02d}")
        return embed
    
    async def update_message(self):
        """Met à jour le message avec l'embed actualisé"""
        if self.message:
            await self.message.edit(embed=self.get_embed(), view=self)
    
    async def send_summary(self):
        """Envoie un récapitulatif des participants à l'organisateur"""
        if not self.participants:
            return
            
        summary_embed = discord.Embed(
            title="🎮 Récapitulatif des participants",
            description=f"**Code de partie:** {self.code}",
            color=discord.Color.green()
        )
        
        # Liste des participants
        participants_list = ""
        for user_id, info in self.participants.items():
            username = info["username"]
            rank = info["rank"]
            rank_emoji = info.get("rank_emoji", "")
            
            participants_list += f"• **{username}** ({rank_emoji} {rank}) - <@{user_id}>\n"
        
        summary_embed.add_field(
            name=f"Participants ({len(self.participants)})",
            value=participants_list or "Aucun participant",
            inline=False
        )
        
        # Ajouter des informations sur le salon vocal si applicable
        if self.voice_channel:
            summary_embed.add_field(
                name="🎙️ Salon vocal",
                value=f"Cette partie se déroulera dans {self.voice_channel.mention}",
                inline=False
            )
        
        try:
            await self.party_owner.send(embed=summary_embed)
        except discord.HTTPException:
            pass  # Ignore si on ne peut pas envoyer de MP
    
    async def on_timeout(self):
        # Désactiver tous les éléments interactifs
        for item in self.children:
            item.disabled = True
        
        if self.message:
            await self.message.edit(view=self)
            
        # Envoyer un récapitulatif final
        await self.send_summary()

async def create_party_embed(guild, author, channel_title, channel):
    """Crée un embed pour une annonce de partie"""
    # Vérifier si le canal est vocal
    is_voice_channel = isinstance(channel, discord.VoiceChannel)
    
    # Adapter le titre en fonction du type de canal
    if is_voice_channel:
        channel_name = channel.name
        # Extraire le numéro du salon pour les salons Préparation
        prep_num = ""
        if "préparation" in channel_name.lower() or "preparation" in channel_name.lower() or "prépa" in channel_name.lower():
            for char in channel_name:
                if char.isdigit():
                    prep_num = char
                    break
            if prep_num:
                embed_title = f"Partie Personnalisée dans le salon Prépa {prep_num}"
            else:
                embed_title = f"Partie Personnalisée dans {channel_name}"
        else:
            embed_title = f"Partie Personnalisée dans {channel_name}"
    else:
        embed_title = "Partie Personnalisée Valorant"
    
    # Créer l'embed
    embed = discord.Embed(
        title=embed_title,
        description=f"{author.mention} a créé une nouvelle partie" + (f" pour le salon vocal {channel.mention}!" if is_voice_channel else f" dans {channel.mention}!"),
        color=0x3498db,
        timestamp=datetime.datetime.now()
    )
    
    embed.add_field(name="Statut", value="📱 En attente de joueurs", inline=False)
    
    # Adapter le message du salon en fonction du type de canal
    if is_voice_channel:
        embed.add_field(
            name="Salon vocal", 
            value=f"🎙️ Cette partie se déroulera dans {channel.mention}", 
            inline=False
        )
        
        # Ajouter un avertissement pour les salons vocaux
        embed.add_field(
            name="⚠️ Important", 
            value="Vous devez être présent dans ce salon vocal pour rejoindre la partie!", 
            inline=False
        )
    else:
        embed.add_field(
            name="Salon", 
            value=f"📍 Cette partie se déroulera dans {channel.mention}", 
            inline=False
        )
    
    embed.add_field(
        name="Comment rejoindre?", 
        value="Clique sur le bouton ci-dessous pour t'inscrire et recevoir le code de partie!", 
        inline=False
    )
    
    # Ajouter le logo du serveur en haut à droite
    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)
    
    # Le footer sera mis à jour avec le compteur
    embed.set_footer(text=f"Créé par {author.display_name} • Fermeture dans 60:00")
    
    return embed

async def update_countdown(view):
    """Tâche qui met à jour régulièrement le contenu de l'embed avec le temps restant"""
    try:
        while not view.is_finished() and view.message:
            await view.update_message()
            await asyncio.sleep(30)  # Mise à jour toutes les 30 secondes
    except:
        pass

class PartyCode(commands.Cog):
    """Système de codes de partie pour Valorant avec protection et collecte d'informations"""
    
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=160220161329789440)
        
        default_guild = {
            "allowed_channels": [],  # Liste des canaux où la commande est autorisée
            "auto_detection": True   # Détection automatique des party-codes
        }
        
        self.config.register_guild(**default_guild)
        
        # Regex pour détecter divers formats de party-codes
        # - Format XXX000 (3 lettres, 3 chiffres)
        # - Format alphanumérique de 6 caractères
        # - Format alphanumérique de 8 caractères
        self.party_code_pattern = re.compile(r'([A-Z0-9]{6}|[A-Z0-9]{8})')
        
        # Mapping des canaux spéciaux et leurs titres personnalisés
        self.special_channels = {
            1352768734904979517: "Partie Personnalisée 1",
            1360965851502874865: "Partie Personnalisée 2",
            1360968736940625982: "Partie Personnalisée 3",
            1360968699535687720: "Partie Personnalisée 4"
        }

        # Mapping des canaux vocaux et leurs titres personnalisés
        self.voice_channels = {
            # Ajouter ici les canaux vocaux spécifiques
            1352768734904979517: "Préparation 1",
            1360965851502874865: "Préparation 2",
            1360968736940625982: "Préparation 3",
            1360968699535687720: "Préparation 4"
        }
    
    def generate_party_code(self, length=6):
        """Génère un code de partie aléatoire au format XXX000 ou de 8 caractères"""
        if length == 8:
            # Format de 8 caractères : mélange de lettres et chiffres
            chars = string.ascii_uppercase + string.digits
            return ''.join(random.choices(chars, k=8))
        else:
            # Format standard XXX000
            letters = ''.join(random.choices(string.ascii_uppercase, k=3))
            numbers = ''.join(random.choices(string.digits, k=3))
            return f"{letters}{numbers}"
    
    def get_channel_title(self, channel_id):
        """Renvoie le titre personnalisé pour un canal spécifique"""
        return self.special_channels.get(channel_id, "Nouvelle partie")
    
    def get_voice_channel_name(self, voice_channel):
        """Renvoie le nom personnalisé pour un salon vocal"""
        if voice_channel:
            if voice_channel.id in self.voice_channels:
                return self.voice_channels[voice_channel.id]
            else:
                return voice_channel.name
        return "Nouvelle partie"
    
    @commands.Cog.listener()
    async def on_message(self, message):
        """Détecte automatiquement les party-codes dans les messages"""
        # Ignorer les messages du bot
        if message.author.bot:
            return
            
        # Ignorer les messages privés
        if not message.guild:
            return
            
        # Ignorer les messages de commande
        if message.content.startswith('!'):
            return
        
        # Ne traiter que les messages dans le canal spécifique
        if message.channel.id != 1362499174418874609:
            return
            
        # Vérifier si la détection automatique est activée
        if not await self.config.guild(message.guild).auto_detection():
            return
        
        # Récupérer le salon vocal de l'auteur si présent
        voice_channel = None
        if message.author.voice and message.author.voice.channel:
            voice_channel = message.author.voice.channel
        
        # Rechercher des party-codes dans le message
        content = message.content.strip()
        
        # Extraire tous les codes potentiels
        matches = self.party_code_pattern.findall(content.upper())
        
        # Vérifier si le message contient principalement des codes
        if matches:
            # Extraire tous les codes uniques
            unique_codes = list(set(matches))
            
            # Créer une chaîne avec tous les codes
            codes_str = " & ".join(unique_codes)
            
            # Si la chaîne obtenue est assez similaire au message original, c'est probablement un code de partie
            clean_content = re.sub(r'[&\s,]+', '', content.upper())
            clean_codes = re.sub(r'[&\s,]+', '', codes_str)
            
            # Si au moins 80% du message est constitué de codes, on le considère comme un party-code
            similarity = len(clean_codes) / len(clean_content) if clean_content else 0
            
            if similarity >= 0.8:
                # Supprimer le message original si possible
                try:
                    await message.delete()
                except:
                    pass
                
                # Déterminer le titre du salon en fonction du salon vocal de l'utilisateur
                channel_title = "Nouvelle partie"
                if voice_channel:
                    channel_title = self.get_voice_channel_name(voice_channel)
                
                # Créer l'embed
                embed = await create_party_embed(message.guild, message.author, channel_title, voice_channel or message.channel)
                
                # Créer la vue avec le bouton
                view = PartyCodeView(self.bot, codes_str, message.author, voice_channel)
                
                # Envoyer l'embed
                msg = await message.channel.send(embed=embed, view=view)
                
                # Stocker le message dans la vue pour pouvoir le mettre à jour plus tard
                view.message = msg
                
                # Démarrer la tâche de mise à jour du compteur
                self.bot.loop.create_task(update_countdown(view))
    
    @commands.group()
    @commands.guild_only()
    async def partycode(self, ctx):
        """Commandes pour gérer les codes de partie"""
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)
    
    @partycode.command(name="create")
    async def partycode_create(self, ctx, format: str = None, *, codes: str = None):
        """Crée une annonce de code de partie
        
        Format (optionnel): 6 ou 8 pour spécifier la longueur du code
        Codes (optionnel): codes personnalisés
        
        Exemples:
        - !partycode create (génère un code de 6 caractères)
        - !partycode create 8 (génère un code de 8 caractères)
        - !partycode create ZOR170 & FDI794 (utilise des codes personnalisés)
        """
        # Vérifier si le canal est autorisé
        allowed_channels = await self.config.guild(ctx.guild).allowed_channels()
        if allowed_channels and ctx.channel.id not in allowed_channels:
            allowed_channels_mentions = [f"<#{channel_id}>" for channel_id in allowed_channels]
            return await ctx.send(
                f"❌ Cette commande n'est pas autorisée dans ce canal. "
                f"Canaux autorisés: {', '.join(allowed_channels_mentions)}",
                delete_after=10
            )
        
        # Récupérer le salon vocal de l'auteur si présent
        voice_channel = None
        if ctx.author.voice and ctx.author.voice.channel:
            voice_channel = ctx.author.voice.channel
        
        # Déterminer le format et les codes
        code_length = 6  # Format par défaut
        
        # Si le premier argument est 6 ou 8, l'utiliser comme format
        if format in ["6", "8"]:
            code_length = int(format)
            # Dans ce cas, format est utilisé pour la longueur et pas pour les codes
            codes_to_use = codes
        else:
            # Sinon, utiliser format comme début des codes
            codes_to_use = f"{format} {codes}" if codes else format
        
        # Supprimer la commande originale si possible
        try:
            await ctx.message.delete()
        except:
            pass
        
        # Créer ou utiliser les codes fournis
        party_code = codes_to_use if codes_to_use else self.generate_party_code(code_length)
        
        # Obtenir le titre personnalisé en fonction du canal
        channel_title = self.get_channel_title(ctx.channel.id)
        
        # Créer l'embed
        embed = await create_party_embed(ctx.guild, ctx.author, channel_title, voice_channel or ctx.channel)
        
        # Créer la vue avec le bouton
        view = PartyCodeView(self.bot, party_code, ctx.author, voice_channel)
        
        # Envoyer l'embed
        message = await ctx.send(embed=embed, view=view)
        
        # Stocker le message dans la vue pour pouvoir le mettre à jour plus tard
        view.message = message
        
        # Démarrer la tâche de mise à jour du compteur
        self.bot.loop.create_task(update_countdown(view))
    
    @partycode.command(name="auto")
    @commands.admin_or_permissions(administrator=True)
    async def partycode_auto(self, ctx, state: str = None):
        """Active ou désactive la détection automatique des party-codes
        
        États:
        - on: Activer
        - off: Désactiver
        Sans argument: Affiche l'état actuel
        """
        current = await self.config.guild(ctx.guild).auto_detection()
        
        if state is None:
            return await ctx.send(
                f"📊 La détection automatique des party-codes est actuellement "
                f"**{'activée' if current else 'désactivée'}**."
            )
        
        if state.lower() not in ["on", "off"]:
            return await ctx.send("❌ État invalide. Utilisez 'on' ou 'off'.")
        
        new_state = state.lower() == "on"
        await self.config.guild(ctx.guild).auto_detection.set(new_state)
        
        await ctx.send(
            f"✅ La détection automatique des party-codes est maintenant "
            f"**{'activée' if new_state else 'désactivée'}**."
        )
    
    @partycode.command(name="channel")
    @commands.admin_or_permissions(administrator=True)
    async def partycode_channel(self, ctx, channel: discord.TextChannel = None):
        """Ajoute ou retire un canal de la liste des canaux autorisés"""
        if not channel:
            channel = ctx.channel
        
        async with self.config.guild(ctx.guild).allowed_channels() as channels:
            if channel.id in channels:
                channels.remove(channel.id)
                await ctx.send(f"❌ Le canal {channel.mention} n'est plus autorisé pour les codes de partie.")
            else:
                channels.append(channel.id)
                await ctx.send(f"✅ Le canal {channel.mention} est maintenant autorisé pour les codes de partie.")
    
    @partycode.command(name="list")
    @commands.admin_or_permissions(administrator=True)
    async def partycode_list(self, ctx):
        """Liste les canaux autorisés pour les codes de partie"""
        channels = await self.config.guild(ctx.guild).allowed_channels()
        
        if not channels:
            return await ctx.send("Aucun canal n'est configuré. Par défaut, la commande est autorisée partout.")
        
        channel_mentions = [f"<#{channel_id}>" for channel_id in channels]
        
        embed = discord.Embed(
            title="📋 Canaux autorisés pour les codes de partie",
            description="\n".join(channel_mentions) if channel_mentions else "Aucun canal configuré",
            color=0x3498db
        )
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(PartyCode(bot))
