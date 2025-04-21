import discord
from redbot.core import commands, Config
import datetime
import asyncio

class Track(commands.Cog):
    """Module de suivi des activités du serveur"""
    
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=160227016329789449)
        
        default_guild = {
            "channel_id": 1353090812442968104,  # Canal où envoyer les logs
            "enabled": True,                    # Suivi activé par défaut
            "track_messages": True,             # Suivre les messages
            "track_edits": True,                # Suivre les éditions de messages
            "track_deletes": True,              # Suivre les suppressions de messages
            "track_voice": True,                # Suivre les activités vocales
            "track_joins": True,                # Suivre les arrivées
            "track_leaves": True,               # Suivre les départs
            "track_roles": True,                # Suivre les changements de rôles
            "track_bans": True,                 # Suivre les bannissements
            "track_reactions": False            # Suivre les réactions (désactivé par défaut)
        }
        
        self.config.register_guild(**default_guild)
    
    @commands.Cog.listener()
    async def on_message(self, message):
        """Suivi des messages envoyés"""
        # Ignorer les messages du bot
        if message.author.bot:
            return
            
        # Ignorer les messages privés
        if not message.guild:
            return
            
        # Vérifier si le suivi est activé
        if not await self._is_enabled(message.guild, "track_messages"):
            return
        
        # Préparer l'embed de suivi
        embed = discord.Embed(
            title="✉️ Message envoyé",
            description=message.content if message.content else "*Aucun contenu textuel*",
            color=0x3498db,
            timestamp=datetime.datetime.now()
        )
        
        # Ajouter les informations sur l'auteur
        embed.set_author(
            name=f"{message.author.display_name} ({message.author.id})",
            icon_url=message.author.avatar.url if message.author.avatar else message.author.default_avatar.url
        )
        
        # Ajouter des informations sur le canal
        embed.add_field(name="Canal", value=f"{message.channel.mention} ({message.channel.id})", inline=True)
        
        # Ajouter des informations sur les pièces jointes
        if message.attachments:
            attachments_text = "\n".join([f"[{a.filename}]({a.url})" for a in message.attachments])
            embed.add_field(name="Pièces jointes", value=attachments_text, inline=False)
        
        # Envoyer l'embed
        await self._send_log(message.guild, embed)
    
    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        """Suivi des éditions de messages"""
        # Ignorer les messages du bot
        if before.author.bot:
            return
            
        # Ignorer les messages privés
        if not before.guild:
            return
            
        # Ignorer si le contenu n'a pas changé
        if before.content == after.content:
            return
            
        # Vérifier si le suivi est activé
        if not await self._is_enabled(before.guild, "track_edits"):
            return
        
        # Préparer l'embed de suivi
        embed = discord.Embed(
            title="✏️ Message modifié",
            color=0xf1c40f,
            timestamp=datetime.datetime.now()
        )
        
        # Ajouter les informations sur l'auteur
        embed.set_author(
            name=f"{before.author.display_name} ({before.author.id})",
            icon_url=before.author.avatar.url if before.author.avatar else before.author.default_avatar.url
        )
        
        # Ajouter le contenu avant/après
        embed.add_field(name="Avant", value=before.content if before.content else "*Aucun contenu textuel*", inline=False)
        embed.add_field(name="Après", value=after.content if after.content else "*Aucun contenu textuel*", inline=False)
        
        # Ajouter des informations sur le canal
        embed.add_field(name="Canal", value=f"{before.channel.mention} ({before.channel.id})", inline=True)
        embed.add_field(name="Lien", value=f"[Aller au message]({before.jump_url})", inline=True)
        
        # Envoyer l'embed
        await self._send_log(before.guild, embed)
    
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        """Suivi des suppressions de messages"""
        # Ignorer les messages du bot
        if message.author.bot:
            return
            
        # Ignorer les messages privés
        if not message.guild:
            return
            
        # Vérifier si le suivi est activé
        if not await self._is_enabled(message.guild, "track_deletes"):
            return
        
        # Préparer l'embed de suivi
        embed = discord.Embed(
            title="🗑️ Message supprimé",
            description=message.content if message.content else "*Aucun contenu textuel*",
            color=0xe74c3c,
            timestamp=datetime.datetime.now()
        )
        
        # Ajouter les informations sur l'auteur
        embed.set_author(
            name=f"{message.author.display_name} ({message.author.id})",
            icon_url=message.author.avatar.url if message.author.avatar else message.author.default_avatar.url
        )
        
        # Ajouter des informations sur le canal
        embed.add_field(name="Canal", value=f"{message.channel.mention} ({message.channel.id})", inline=True)
        
        # Ajouter des informations sur les pièces jointes
        if message.attachments:
            attachments_text = "\n".join([f"{a.filename}" for a in message.attachments])
            embed.add_field(name="Pièces jointes perdues", value=attachments_text, inline=False)
        
        # Envoyer l'embed
        await self._send_log(message.guild, embed)
    
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        """Suivi des activités vocales"""
        # Ignorer les bots
        if member.bot:
            return
            
        # Vérifier si le suivi est activé
        if not await self._is_enabled(member.guild, "track_voice"):
            return
        
        # Cas : Rejoindre un salon vocal
        if before.channel is None and after.channel is not None:
            embed = discord.Embed(
                title="🎙️ A rejoint un salon vocal",
                description=f"{member.mention} a rejoint {after.channel.mention}",
                color=0x2ecc71,
                timestamp=datetime.datetime.now()
            )
            embed.set_author(
                name=f"{member.display_name} ({member.id})",
                icon_url=member.avatar.url if member.avatar else member.default_avatar.url
            )
            await self._send_log(member.guild, embed)
            
        # Cas : Quitter un salon vocal
        elif before.channel is not None and after.channel is None:
            embed = discord.Embed(
                title="🎙️ A quitté un salon vocal",
                description=f"{member.mention} a quitté {before.channel.mention}",
                color=0xe74c3c,
                timestamp=datetime.datetime.now()
            )
            embed.set_author(
                name=f"{member.display_name} ({member.id})",
                icon_url=member.avatar.url if member.avatar else member.default_avatar.url
            )
            await self._send_log(member.guild, embed)
            
        # Cas : Changer de salon vocal
        elif before.channel is not None and after.channel is not None and before.channel.id != after.channel.id:
            embed = discord.Embed(
                title="🎙️ A changé de salon vocal",
                description=f"{member.mention} est passé de {before.channel.mention} à {after.channel.mention}",
                color=0xf1c40f,
                timestamp=datetime.datetime.now()
            )
            embed.set_author(
                name=f"{member.display_name} ({member.id})",
                icon_url=member.avatar.url if member.avatar else member.default_avatar.url
            )
            await self._send_log(member.guild, embed)
    
    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Suivi des arrivées de membres"""
        # Ignorer les bots
        if member.bot:
            return
            
        # Vérifier si le suivi est activé
        if not await self._is_enabled(member.guild, "track_joins"):
            return
        
        # Calculer l'âge du compte
        account_age = datetime.datetime.now(datetime.timezone.utc) - member.created_at
        
        # Préparer l'embed de suivi
        embed = discord.Embed(
            title="👋 Membre rejoint",
            description=f"{member.mention} a rejoint le serveur",
            color=0x2ecc71,
            timestamp=datetime.datetime.now()
        )
        
        # Ajouter des informations sur le membre
        embed.set_author(
            name=f"{member.display_name} ({member.id})",
            icon_url=member.avatar.url if member.avatar else member.default_avatar.url
        )
        
        # Ajouter la date de création du compte
        embed.add_field(name="Compte créé le", value=f"<t:{int(member.created_at.timestamp())}:F>", inline=True)
        embed.add_field(name="Âge du compte", value=f"{account_age.days} jours", inline=True)
        
        # Ajouter le nombre total de membres
        embed.add_field(name="Nombre de membres", value=str(member.guild.member_count), inline=True)
        
        # Envoyer l'embed
        await self._send_log(member.guild, embed)
    
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        """Suivi des départs de membres"""
        # Ignorer les bots
        if member.bot:
            return
            
        # Vérifier si le suivi est activé
        if not await self._is_enabled(member.guild, "track_leaves"):
            return
        
        # Calculer la durée de présence
        join_duration = datetime.datetime.now(datetime.timezone.utc) - member.joined_at if member.joined_at else None
        
        # Préparer l'embed de suivi
        embed = discord.Embed(
            title="👋 Membre parti",
            description=f"{member.mention} a quitté le serveur",
            color=0xe74c3c,
            timestamp=datetime.datetime.now()
        )
        
        # Ajouter des informations sur le membre
        embed.set_author(
            name=f"{member.display_name} ({member.id})",
            icon_url=member.avatar.url if member.avatar else member.default_avatar.url
        )
        
        # Ajouter la date d'arrivée sur le serveur
        if member.joined_at:
            embed.add_field(name="Avait rejoint le", value=f"<t:{int(member.joined_at.timestamp())}:F>", inline=True)
            if join_duration:
                embed.add_field(name="Durée de présence", value=f"{join_duration.days} jours", inline=True)
        
        # Ajouter les rôles
        if member.roles and len(member.roles) > 1:  # Ignorer le rôle @everyone
            roles = [role.mention for role in member.roles if role.name != "@everyone"]
            if roles:
                embed.add_field(name="Rôles", value=", ".join(roles), inline=False)
        
        # Ajouter le nombre total de membres
        embed.add_field(name="Nombre de membres", value=str(member.guild.member_count), inline=True)
        
        # Envoyer l'embed
        await self._send_log(member.guild, embed)
    
    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        """Suivi des changements de rôles"""
        # Ignorer les bots
        if before.bot:
            return
            
        # Vérifier si le suivi est activé
        if not await self._is_enabled(before.guild, "track_roles"):
            return
        
        # Vérifier si les rôles ont changé
        if set(before.roles) != set(after.roles):
            # Préparer l'embed de suivi
            embed = discord.Embed(
                title="👑 Rôles modifiés",
                color=0x9b59b6,
                timestamp=datetime.datetime.now()
            )
            
            # Ajouter des informations sur le membre
            embed.set_author(
                name=f"{after.display_name} ({after.id})",
                icon_url=after.avatar.url if after.avatar else after.default_avatar.url
            )
            
            # Trouver les rôles ajoutés et retirés
            added_roles = [role for role in after.roles if role not in before.roles]
            removed_roles = [role for role in before.roles if role not in after.roles]
            
            if added_roles:
                embed.add_field(name="Rôles ajoutés", value=", ".join([role.mention for role in added_roles]), inline=False)
            
            if removed_roles:
                embed.add_field(name="Rôles retirés", value=", ".join([role.mention for role in removed_roles]), inline=False)
            
            # Envoyer l'embed
            await self._send_log(before.guild, embed)
    
    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        """Suivi des bannissements"""
        # Ignorer les bots
        if user.bot:
            return
            
        # Vérifier si le suivi est activé
        if not await self._is_enabled(guild, "track_bans"):
            return
        
        # Préparer l'embed de suivi
        embed = discord.Embed(
            title="🔨 Membre banni",
            description=f"{user.mention} a été banni du serveur",
            color=0xe74c3c,
            timestamp=datetime.datetime.now()
        )
        
        # Ajouter des informations sur l'utilisateur
        embed.set_author(
            name=f"{user.display_name} ({user.id})",
            icon_url=user.avatar.url if user.avatar else user.default_avatar.url
        )
        
        # Envoyer l'embed
        await self._send_log(guild, embed)
    
    @commands.Cog.listener()
    async def on_member_unban(self, guild, user):
        """Suivi des débannissements"""
        # Ignorer les bots
        if user.bot:
            return
            
        # Vérifier si le suivi est activé
        if not await self._is_enabled(guild, "track_bans"):
            return
        
        # Préparer l'embed de suivi
        embed = discord.Embed(
            title="🔓 Membre débanni",
            description=f"{user.mention} a été débanni du serveur",
            color=0x2ecc71,
            timestamp=datetime.datetime.now()
        )
        
        # Ajouter des informations sur l'utilisateur
        embed.set_author(
            name=f"{user.display_name} ({user.id})",
            icon_url=user.avatar.url if user.avatar else user.default_avatar.url
        )
        
        # Envoyer l'embed
        await self._send_log(guild, embed)
    
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        """Suivi des réactions ajoutées"""
        # Ignorer si le suivi des réactions est désactivé
        if not await self._is_enabled(self.bot.get_guild(payload.guild_id), "track_reactions"):
            return
            
        # Récupérer des informations sur la réaction
        guild = self.bot.get_guild(payload.guild_id)
        if not guild:
            return
            
        channel = guild.get_channel(payload.channel_id)
        if not channel:
            return
            
        try:
            message = await channel.fetch_message(payload.message_id)
        except:
            return
            
        user = guild.get_member(payload.user_id)
        if not user or user.bot:
            return
            
        # Créer l'embed
        emoji_str = str(payload.emoji)
        embed = discord.Embed(
            title="👍 Réaction ajoutée",
            description=f"{user.mention} a réagi avec {emoji_str} à [un message]({message.jump_url})",
            color=0x3498db,
            timestamp=datetime.datetime.now()
        )
        
        embed.set_author(
            name=f"{user.display_name} ({user.id})",
            icon_url=user.avatar.url if user.avatar else user.default_avatar.url
        )
        
        embed.add_field(name="Canal", value=channel.mention, inline=True)
        embed.add_field(name="Auteur du message", value=message.author.mention, inline=True)
        
        # Envoyer l'embed
        await self._send_log(guild, embed)
    
    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        """Suivi des réactions retirées"""
        # Ignorer si le suivi des réactions est désactivé
        if not await self._is_enabled(self.bot.get_guild(payload.guild_id), "track_reactions"):
            return
            
        # Récupérer des informations sur la réaction
        guild = self.bot.get_guild(payload.guild_id)
        if not guild:
            return
            
        channel = guild.get_channel(payload.channel_id)
        if not channel:
            return
            
        try:
            message = await channel.fetch_message(payload.message_id)
        except:
            return
            
        user = guild.get_member(payload.user_id)
        if not user or user.bot:
            return
            
        # Créer l'embed
        emoji_str = str(payload.emoji)
        embed = discord.Embed(
            title="👎 Réaction retirée",
            description=f"{user.mention} a retiré sa réaction {emoji_str} d'[un message]({message.jump_url})",
            color=0xe74c3c,
            timestamp=datetime.datetime.now()
        )
        
        embed.set_author(
            name=f"{user.display_name} ({user.id})",
            icon_url=user.avatar.url if user.avatar else user.default_avatar.url
        )
        
        embed.add_field(name="Canal", value=channel.mention, inline=True)
        embed.add_field(name="Auteur du message", value=message.author.mention, inline=True)
        
        # Envoyer l'embed
        await self._send_log(guild, embed)
    
    async def _is_enabled(self, guild, feature=None):
        """Vérifie si le suivi est activé pour une fonctionnalité spécifique"""
        if not guild:
            return False
            
        settings = await self.config.guild(guild).all()
        
        # Vérifier si le suivi est activé globalement
        if not settings["enabled"]:
            return False
            
        # Vérifier si la fonctionnalité spécifique est activée
        if feature and feature in settings:
            return settings[feature]
            
        return True
    
    async def _send_log(self, guild, embed):
        """Envoie un message de log dans le canal configuré"""
        if not guild:
            return
            
        channel_id = await self.config.guild(guild).channel_id()
        channel = guild.get_channel(channel_id)
        
        if not channel:
            return
            
        try:
            await channel.send(embed=embed)
        except discord.HTTPException:
            pass
    
    @commands.group(name="trackset")
    @commands.admin_or_permissions(administrator=True)
    async def trackset(self, ctx):
        """Commandes pour configurer le module de suivi"""
        if ctx.invoked_subcommand is None:
            settings = await self.config.guild(ctx.guild).all()
            
            embed = discord.Embed(
                title="📊 Configuration du module de suivi",
                color=0x3498db
            )
            
            # Status global
            embed.add_field(name="Statut", value="✅ Activé" if settings["enabled"] else "❌ Désactivé", inline=True)
            
            # Canal de log
            channel = ctx.guild.get_channel(settings["channel_id"])
            embed.add_field(name="Canal de logs", value=channel.mention if channel else "Non configuré", inline=True)
            
            # Fonctionnalités activées
            features = []
            if settings["track_messages"]: features.append("✉️ Messages")
            if settings["track_edits"]: features.append("✏️ Éditions")
            if settings["track_deletes"]: features.append("🗑️ Suppressions")
            if settings["track_voice"]: features.append("🎙️ Vocal")
            if settings["track_joins"]: features.append("👋 Arrivées")
            if settings["track_leaves"]: features.append("👋 Départs")
            if settings["track_roles"]: features.append("👑 Rôles")
            if settings["track_bans"]: features.append("🔨 Bannissements")
            if settings["track_reactions"]: features.append("👍 Réactions")
            
            embed.add_field(name="Fonctionnalités activées", value="\n".join(features), inline=False)
            
            # Commandes disponibles
            embed.add_field(
                name="Commandes disponibles",
                value="`!trackset toggle` - Activer/désactiver le suivi\n"
                      "`!trackset channel #canal` - Définir le canal de logs\n"
                      "`!trackset feature [fonctionnalité] [on/off]` - Activer/désactiver une fonctionnalité",
                inline=False
            )
            
            await ctx.send(embed=embed)
    
    @trackset.command(name="toggle")
    @commands.admin_or_permissions(administrator=True)
    async def trackset_toggle(self, ctx):
        """Active ou désactive le suivi des activités"""
        current = await self.config.guild(ctx.guild).enabled()
        await self.config.guild(ctx.guild).enabled.set(not current)
        
        if not current:
            await ctx.send("✅ Le suivi des activités est maintenant activé.")
        else:
            await ctx.send("❌ Le suivi des activités est maintenant désactivé.")
    
    @trackset.command(name="channel")
    @commands.admin_or_permissions(administrator=True)
    async def trackset_channel(self, ctx, channel: discord.TextChannel = None):
        """Définit le canal où envoyer les logs"""
        if channel:
            await self.config.guild(ctx.guild).channel_id.set(channel.id)
            await ctx.send(f"✅ Les logs seront envoyés dans {channel.mention}.")
        else:
            # Par défaut, utiliser le canal ID préconfiguré
            default_channel_id = 1353090812442968104
            channel = ctx.guild.get_channel(default_channel_id)
            
            if channel:
                await self.config.guild(ctx.guild).channel_id.set(default_channel_id)
                await ctx.send(f"✅ Les logs seront envoyés dans {channel.mention}.")
            else:
                await ctx.send("❌ Canal par défaut introuvable. Veuillez spécifier un canal valide.")
    
    @trackset.command(name="feature")
    @commands.admin_or_permissions(administrator=True)
    async def trackset_feature(self, ctx, feature: str, state: str):
        """Active ou désactive une fonctionnalité de suivi spécifique
        
        Fonctionnalités disponibles:
        - messages: Messages envoyés
        - edits: Éditions de messages
        - deletes: Suppressions de messages
        - voice: Activités vocales
        - joins: Arrivées de membres
        - leaves: Départs de membres
        - roles: Changements de rôles
        - bans: Bannissements
        - reactions: Réactions aux messages
        
        États:
        - on: Activer
        - off: Désactiver
        """
        valid_features = [
            "messages", "edits", "deletes", "voice", 
            "joins", "leaves", "roles", "bans", "reactions"
        ]
        
        if feature not in valid_features:
            return await ctx.send(f"❌ Fonctionnalité invalide. Options valides: {', '.join(valid_features)}")
        
        if state.lower() not in ["on", "off"]:
            return await ctx.send("❌ État invalide. Utilisez 'on' ou 'off'.")
        
        config_key = f"track_{feature}"
        new_state = state.lower() == "on"
        
        await self.config.guild(ctx.guild).set_raw(config_key, value=new_state)
        
        if new_state:
            await ctx.send(f"✅ Le suivi des **{feature}** est maintenant activé.")
        else:
            await ctx.send(f"❌ Le suivi des **{feature}** est maintenant désactivé.")

async def setup(bot):
    await bot.add_cog(Track(bot))
