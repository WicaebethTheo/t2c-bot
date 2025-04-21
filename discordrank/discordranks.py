import discord
from redbot.core import commands, Config
import random
import math
import asyncio
import datetime
from datetime import timedelta

class DiscordRanks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=160227016329789440)
        
        # Structure par défaut pour les données
        default_guild = {
            "channel_id": None,  # Canal pour les annonces de niveau
            "enabled": True,     # Système activé par défaut
            "xp_per_message": 15,  # XP par message
            "xp_per_minute_voice": 10,  # XP par minute en vocal
            "cooldown": 60,      # Cooldown entre les gains de XP en secondes
            "level_formula": 100,  # XP nécessaire pour le niveau 1, multiplié par le niveau pour chaque niveau suivant
            "roles_rewards": {
                "20": 1352739404657201175,  # Rôle Actifs au niveau 20
                "30": 1352739400261304463   # Rôle Actif+ au niveau 30
            },
            "last_reset": 0,  # Timestamp du dernier reset
            "reset_interval": 7776000  # 90 jours en secondes
        }
        
        default_member = {
            "xp": 0,
            "level": 0,
            "last_message": 0,  # Timestamp du dernier message (pour le cooldown)
            "voice_time": 0,     # Temps total passé en vocal (en minutes)
            "voice_join_time": 0,  # Timestamp de la dernière connexion vocale
            "messages": 0,       # Nombre total de messages
        }
        
        self.config.register_guild(**default_guild)
        self.config.register_member(**default_member)
        
        # Dictionnaire pour suivre les utilisateurs en vocal
        self.voice_users = {}
        
        # Démarrer les tâches
        self.voice_xp_task = self.bot.loop.create_task(self.check_voice_time())
        self.reset_check_task = self.bot.loop.create_task(self.check_reset_time())
    
    def cog_unload(self):
        # S'assurer que les tâches sont annulées quand le cog est déchargé
        if self.voice_xp_task:
            self.voice_xp_task.cancel()
        if self.reset_check_task:
            self.reset_check_task.cancel()
    
    async def check_voice_time(self):
        """Tâche qui vérifie et attribue des XP aux utilisateurs en vocal"""
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            try:
                # Pour chaque serveur
                for guild in self.bot.guilds:
                    # Pour chaque salon vocal
                    for voice_channel in guild.voice_channels:
                        # Pour chaque membre dans le salon vocal
                        for member in voice_channel.members:
                            # Ignorer les bots et les membres en sourdine/muet
                            if member.bot or member.voice.self_deaf or member.voice.self_mute:
                                continue
                            
                            # Attribuer XP si le membre était déjà en vocal
                            if member.id in self.voice_users:
                                # Convertir le temps en vocal en XP
                                async with self.config.guild(guild).all() as guild_data:
                                    xp_per_minute = guild_data["xp_per_minute_voice"]
                                
                                # Ajouter l'XP
                                await self.add_xp(member, xp_per_minute)
                            
                            # Ajouter l'utilisateur au suivi
                            self.voice_users[member.id] = datetime.datetime.now()
                
                # Attendre 1 minute avant la prochaine vérification
                await asyncio.sleep(60)
            except Exception as e:
                print(f"Erreur dans la tâche voice_xp: {e}")
                await asyncio.sleep(60)
    
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        """Suivi des connexions et déconnexions vocales"""
        if member.bot:
            return
        
        # Si le membre rejoint un salon vocal
        if before.channel is None and after.channel is not None:
            # On enregistre son heure de connexion
            self.voice_users[member.id] = datetime.datetime.now()
            async with self.config.member(member).all() as member_data:
                member_data["voice_join_time"] = datetime.datetime.now().timestamp()
        
        # Si le membre quitte un salon vocal
        elif before.channel is not None and after.channel is None:
            # On calcule le temps passé en vocal
            if member.id in self.voice_users:
                join_time = self.voice_users[member.id]
                now = datetime.datetime.now()
                time_spent = (now - join_time).total_seconds() / 60  # Convertir en minutes
                
                # Mettre à jour les statistiques
                async with self.config.member(member).all() as member_data:
                    member_data["voice_time"] += time_spent
                
                # Supprimer l'utilisateur du suivi
                del self.voice_users[member.id]
    
    @commands.Cog.listener()
    async def on_message(self, message):
        """Attribution d'XP à chaque message envoyé"""
        # Ignorer les bots et les commandes
        if message.author.bot or message.content.startswith("!"):
            return
        
        # Ignorer les messages privés
        if not message.guild:
            return
        
        # Vérifier si le système est activé
        if not await self.config.guild(message.guild).enabled():
            return
        
        # Vérifier le cooldown
        async with self.config.member(message.author).all() as member_data:
            now = datetime.datetime.now().timestamp()
            if now - member_data["last_message"] < await self.config.guild(message.guild).cooldown():
                return
            
            # Mettre à jour le timestamp et le compteur de messages
            member_data["last_message"] = now
            member_data["messages"] += 1
        
        # Attribuer l'XP
        guild_data = await self.config.guild(message.guild).all()
        xp_to_add = random.randint(
            int(guild_data["xp_per_message"] * 0.8),
            int(guild_data["xp_per_message"] * 1.2)
        )
        await self.add_xp(message.author, xp_to_add)
    
    async def add_xp(self, member, xp_amount):
        """Ajoute de l'XP à un membre et gère les level ups"""
        if member.bot:
            return
        
        old_level = 0
        guild_data = await self.config.guild(member.guild).all()
        level_formula = guild_data["level_formula"]
        
        async with self.config.member(member).all() as member_data:
            old_level = member_data["level"]
            member_data["xp"] += int(xp_amount)
            
            # Calcul du nouveau niveau
            # Formule: level = racine carrée(xp / base)
            # où base est l'XP nécessaire pour le niveau 1
            new_level = int(math.sqrt(member_data["xp"] / level_formula))
            
            if new_level > old_level:
                member_data["level"] = new_level
        
        # Vérifier s'il y a eu un level up
        if new_level > old_level:
            # Annoncer le level up si un canal est configuré
            channel_id = guild_data["channel_id"]
            if channel_id:
                channel = member.guild.get_channel(channel_id)
                if channel:
                    embed = discord.Embed(
                        title="🎉 Level up!",
                        description=f"{member.mention} a atteint le niveau **{new_level}** !",
                        color=0x2b2d31
                    )
                    embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
                    await channel.send(embed=embed)
            
            # Vérifier les récompenses de rôle
            role_rewards = guild_data["roles_rewards"]
            for level_str, role_id in role_rewards.items():
                if int(level_str) <= new_level:
                    role = member.guild.get_role(role_id)
                    if role and role not in member.roles:
                        try:
                            await member.add_roles(role, reason=f"Récompense de niveau {level_str}")
                        except discord.Forbidden:
                            pass
    
    async def check_reset_time(self):
        """Vérifie si un reset est nécessaire"""
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            try:
                for guild in self.bot.guilds:
                    guild_data = await self.config.guild(guild).all()
                    current_time = datetime.datetime.now().timestamp()
                    
                    # Vérifier si 90 jours se sont écoulés depuis le dernier reset
                    if current_time - guild_data["last_reset"] >= guild_data["reset_interval"]:
                        # Effectuer le reset
                        await self.reset_levels(guild)
                        
                        # Mettre à jour le timestamp du dernier reset
                        await self.config.guild(guild).last_reset.set(current_time)
                        
                        # Annoncer le reset
                        if guild_data["channel_id"]:
                            channel = guild.get_channel(guild_data["channel_id"])
                            if channel:
                                embed = discord.Embed(
                                    title="🔄 Reset des niveaux",
                                    description="Les niveaux ont été réinitialisés pour la nouvelle saison !",
                                    color=0x2b2d31
                                )
                                embed.add_field(
                                    name="ℹ️ Information",
                                    value="Les niveaux sont réinitialisés tous les 90 jours. Continuez à participer pour gagner de nouveaux rôles !",
                                    inline=False
                                )
                                await channel.send(embed=embed)
                
                # Vérifier toutes les heures
                await asyncio.sleep(3600)
                
            except Exception as e:
                print(f"Erreur dans la tâche check_reset_time: {e}")
                await asyncio.sleep(3600)

    async def reset_levels(self, guild):
        """Réinitialise les niveaux de tous les membres"""
        # Récupérer tous les membres
        all_members = await self.config.all_members(guild)
        
        # Retirer les rôles de récompense
        guild_data = await self.config.guild(guild).all()
        role_rewards = guild_data["roles_rewards"]
        
        for member_id in all_members:
            member = guild.get_member(member_id)
            if member:
                # Retirer les rôles de récompense
                for role_id in role_rewards.values():
                    role = guild.get_role(role_id)
                    if role and role in member.roles:
                        try:
                            await member.remove_roles(role, reason="Reset des niveaux")
                        except discord.Forbidden:
                            pass
        
        # Réinitialiser les données de tous les membres
        await self.config.clear_all_members(guild)

    @commands.command()
    @commands.admin_or_permissions(administrator=True)
    async def announce(self, ctx):
        """Crée une annonce pour présenter le système de niveaux"""
        # Canal d'annonce fixe
        channel_id = 1352736703688740944
        announcement_channel = ctx.guild.get_channel(channel_id)
        
        if not announcement_channel:
            return await ctx.send(f"❌ Le canal d'annonce (ID: {channel_id}) n'a pas été trouvé.")
        
        # Créer l'embed principal d'annonce
        embed = discord.Embed(
            title="🏆 Nouveau système de niveaux !",
            description="Un système de niveaux est maintenant disponible sur ce serveur ! Gagnez de l'XP en participant activement et débloquez des récompenses exclusives.",
            color=0x2b2d31
        )
        
        # Comment gagner de l'XP
        embed.add_field(
            name="💬 Comment gagner de l'XP ?",
            value="• Envoyer des messages dans les salons textuels\n• Passer du temps dans les salons vocaux\n\nPlus vous êtes actif, plus vous gagnez d'XP rapidement !",
            inline=False
        )
        
        # Commandes disponibles
        embed.add_field(
            name="📋 Commandes disponibles",
            value="• `!level` ou `!rank` - Voir votre niveau actuel\n• `!level @membre` - Voir le niveau d'un autre membre\n• `!top` - Afficher le classement des membres\n• `!leaderboard` - Alias pour la commande top",
            inline=False
        )
        
        # Récompenses
        guild_data = await self.config.guild(ctx.guild).all()
        rewards_text = ""
        
        role_rewards = guild_data["roles_rewards"]
        if role_rewards:
            rewards_text = "Voici les rôles que vous pouvez débloquer :\n\n"
            for level, role_id in sorted(role_rewards.items(), key=lambda x: int(x[0])):
                role = ctx.guild.get_role(role_id)
                if role:
                    rewards_text += f"• Niveau {level} : {role.mention}\n"
        else:
            rewards_text = "Les administrateurs configureront bientôt des récompenses de rôles exclusives !"
        
        embed.add_field(
            name="🎁 Récompenses",
            value=rewards_text,
            inline=False
        )
        
        # Pied de page
        embed.set_footer(text="Commencez dès maintenant à interagir pour gagner de l'XP !")
        
        # Image
        embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else None)
        
        # Envoi du message d'annonce
        try:
            # Créer un exemple de profil
            example_member = ctx.guild.get_member(ctx.author.id)
            
            await announcement_channel.send(embed=embed)
            await ctx.send(f"✅ Annonce du système de niveaux créée avec succès dans {announcement_channel.mention} !")
            
            # Exemple de profil
            await asyncio.sleep(1)
            example_embed = await self.create_level_embed(
                example_member,
                {
                    "level": 5,
                    "xp": 3500,
                    "messages": 120,
                    "voice_time": 185  # en minutes
                },
                {
                    "level_formula": guild_data["level_formula"]
                },
                rank=1
            )
            example_embed.set_author(name="Exemple de profil")
            await announcement_channel.send("Voici à quoi ressemble un profil de niveau :", embed=example_embed)
            
        except discord.Forbidden:
            await ctx.send(f"❌ Je n'ai pas la permission d'envoyer des messages dans {announcement_channel.mention}.")
        except Exception as e:
            await ctx.send(f"❌ Une erreur s'est produite : {str(e)}")
    
    async def create_level_embed(self, member, member_data, guild_data, rank=0):
        """Crée un embed de niveau pour un membre"""
        # Calcul de l'XP nécessaire pour le prochain niveau
        current_level = member_data["level"]
        current_xp = member_data["xp"]
        next_level_xp = (current_level + 1) ** 2 * guild_data["level_formula"]
        
        # Calcul du pourcentage vers le prochain niveau
        level_xp = current_level ** 2 * guild_data["level_formula"]
        next_level_total_xp = next_level_xp - level_xp
        current_level_progress = current_xp - level_xp
        progress_percentage = min(100, int((current_level_progress / next_level_total_xp) * 100))
        
        # Créer une barre de progression
        progress_bar = ""
        for i in range(0, 100, 5):
            if i < progress_percentage:
                progress_bar += "█"
            else:
                progress_bar += "░"
        
        # Créer l'embed
        embed = discord.Embed(
            title=f"Profil de {member.display_name}",
            color=0x2b2d31
        )
        
        embed.add_field(name="Rang", value=f"#{rank}" if rank > 0 else "N/A", inline=True)
        embed.add_field(name="Niveau", value=str(current_level), inline=True)
        embed.add_field(name="XP", value=f"{current_xp} / {next_level_xp}", inline=True)
        
        embed.add_field(name=f"Progression ({progress_percentage}%)", value=progress_bar, inline=False)
        embed.add_field(name="Messages envoyés", value=str(member_data["messages"]), inline=True)
        
        # Convertir le temps en vocal en heures/minutes
        voice_hours = int(member_data["voice_time"] // 60)
        voice_minutes = int(member_data["voice_time"] % 60)
        embed.add_field(name="Temps en vocal", value=f"{voice_hours}h {voice_minutes}m", inline=True)
        
        embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
        embed.set_footer(text="Un niveau supérieur est atteint en participant régulièrement sur le serveur!")
        
        return embed
    
    @commands.command()
    async def level(self, ctx, member: discord.Member = None):
        """Affiche le niveau et l'XP d'un membre"""
        if member is None:
            member = ctx.author
        
        data = await self.config.member(member).all()
        guild_data = await self.config.guild(ctx.guild).all()
        
        # Calculer le rang du membre
        all_members = await self.config.all_members(ctx.guild)
        sorted_members = sorted(all_members.items(), key=lambda x: (x[1]["level"], x[1]["xp"]), reverse=True)
        
        rank = 0
        for i, (member_id, member_data) in enumerate(sorted_members, 1):
            if member_id == member.id:
                rank = i
                break
        
        # Créer et envoyer l'embed
        embed = await self.create_level_embed(member, data, guild_data, rank)
        await ctx.send(embed=embed)
    
    @commands.command()
    async def rank(self, ctx):
        """Alias pour la commande level"""
        await ctx.invoke(self.level)
    
    @commands.command()
    async def top(self, ctx, page: int = 1):
        """Affiche le classement des membres par niveau et XP"""
        if page < 1:
            page = 1
        
        per_page = 10
        all_members = await self.config.all_members(ctx.guild)
        
        if not all_members:
            return await ctx.send("Aucun membre n'a encore gagné d'XP.")
        
        sorted_members = sorted(all_members.items(), key=lambda x: (x[1]["level"], x[1]["xp"]), reverse=True)
        
        pages = math.ceil(len(sorted_members) / per_page)
        if page > pages:
            page = pages
        
        start_idx = (page - 1) * per_page
        end_idx = min(start_idx + per_page, len(sorted_members))
        
        embed = discord.Embed(
            title="Classement des membres",
            description=f"Page {page}/{pages}",
            color=0x2b2d31
        )
        
        for i, (member_id, data) in enumerate(sorted_members[start_idx:end_idx], start_idx + 1):
            member = ctx.guild.get_member(member_id)
            if member:
                embed.add_field(
                    name=f"#{i}: {member.display_name}",
                    value=f"Niveau {data['level']} - {data['xp']} XP",
                    inline=False
                )
            else:
                # Membre plus sur le serveur
                continue
        
        embed.set_footer(text=f"Utilisez !top [page] pour voir d'autres classements")
        
        await ctx.send(embed=embed)
    
    @commands.command()
    async def leaderboard(self, ctx, page: int = 1):
        """Alias pour la commande top"""
        await ctx.invoke(self.top, page=page)
    
    @commands.group()
    @commands.admin_or_permissions(administrator=True)
    async def levelset(self, ctx):
        """Commandes pour configurer le système de niveaux"""
        if ctx.invoked_subcommand is None:
            guild_data = await self.config.guild(ctx.guild).all()
            
            embed = discord.Embed(
                title="Configuration du système de niveaux",
                color=0x2b2d31
            )
            
            channel = ctx.guild.get_channel(guild_data["channel_id"]) if guild_data["channel_id"] else None
            embed.add_field(name="Canal d'annonce", value=channel.mention if channel else "Non configuré", inline=True)
            embed.add_field(name="Statut", value="Activé" if guild_data["enabled"] else "Désactivé", inline=True)
            embed.add_field(name="Cooldown", value=f"{guild_data['cooldown']} secondes", inline=True)
            
            embed.add_field(name="XP par message", value=str(guild_data["xp_per_message"]), inline=True)
            embed.add_field(name="XP par minute en vocal", value=str(guild_data["xp_per_minute_voice"]), inline=True)
            embed.add_field(name="Formule de niveau", value=f"Base: {guild_data['level_formula']}", inline=True)
            
            # Rôles récompenses
            role_rewards = guild_data["roles_rewards"]
            if role_rewards:
                rewards_text = ""
                for level, role_id in role_rewards.items():
                    role = ctx.guild.get_role(role_id)
                    rewards_text += f"Niveau {level}: {role.mention if role else 'Rôle inconnu'}\n"
                embed.add_field(name="Récompenses de rôles", value=rewards_text, inline=False)
            else:
                embed.add_field(name="Récompenses de rôles", value="Aucune récompense configurée", inline=False)
            
            # Informations sur le reset
            last_reset = datetime.datetime.fromtimestamp(guild_data["last_reset"])
            next_reset = last_reset + timedelta(seconds=guild_data["reset_interval"])
            embed.add_field(
                name="🔄 Reset automatique",
                value=f"Dernier reset: {last_reset.strftime('%d/%m/%Y')}\nProchain reset: {next_reset.strftime('%d/%m/%Y')}",
                inline=False
            )
            
            await ctx.send(embed=embed)
    
    @levelset.command(name="channel")
    async def levelset_channel(self, ctx, channel: discord.TextChannel = None):
        """Définit le canal pour les annonces de level up"""
        if channel:
            await self.config.guild(ctx.guild).channel_id.set(channel.id)
            await ctx.send(f"Les annonces de level up seront envoyées dans {channel.mention}.")
        else:
            await self.config.guild(ctx.guild).channel_id.set(None)
            await ctx.send("Les annonces de level up sont désactivées.")
    
    @levelset.command(name="toggle")
    async def levelset_toggle(self, ctx):
        """Active ou désactive le système de niveaux"""
        current = await self.config.guild(ctx.guild).enabled()
        await self.config.guild(ctx.guild).enabled.set(not current)
        await ctx.send(f"Le système de niveaux est maintenant {'activé' if not current else 'désactivé'}.")
    
    @levelset.command(name="xpmessage")
    async def levelset_xpmessage(self, ctx, amount: int):
        """Définit l'XP gagné par message"""
        if amount < 1:
            return await ctx.send("L'XP doit être supérieur à 0.")
        
        await self.config.guild(ctx.guild).xp_per_message.set(amount)
        await ctx.send(f"Les membres gagneront désormais environ {amount} XP par message.")
    
    @levelset.command(name="xpvoice")
    async def levelset_xpvoice(self, ctx, amount: int):
        """Définit l'XP gagné par minute en vocal"""
        if amount < 0:
            return await ctx.send("L'XP ne peut pas être négatif.")
        
        await self.config.guild(ctx.guild).xp_per_minute_voice.set(amount)
        await ctx.send(f"Les membres gagneront désormais {amount} XP par minute passée en vocal.")
    
    @levelset.command(name="cooldown")
    async def levelset_cooldown(self, ctx, seconds: int):
        """Définit le cooldown entre les gains d'XP (en secondes)"""
        if seconds < 0:
            return await ctx.send("Le cooldown ne peut pas être négatif.")
        
        await self.config.guild(ctx.guild).cooldown.set(seconds)
        await ctx.send(f"Le cooldown est maintenant de {seconds} secondes.")
    
    @levelset.command(name="formula")
    async def levelset_formula(self, ctx, base: int):
        """Définit la formule de calcul des niveaux (XP nécessaire)"""
        if base < 1:
            return await ctx.send("La base doit être supérieure à 0.")
        
        await self.config.guild(ctx.guild).level_formula.set(base)
        await ctx.send(f"La formule de niveau a été mise à jour. XP pour niveau N = {base} × N²")
    
    @levelset.command(name="addrole")
    async def levelset_addrole(self, ctx, level: int, role: discord.Role):
        """Ajoute une récompense de rôle pour un niveau spécifique"""
        if level < 1:
            return await ctx.send("Le niveau doit être supérieur à 0.")
        
        async with self.config.guild(ctx.guild).roles_rewards() as roles_rewards:
            roles_rewards[str(level)] = role.id
        
        await ctx.send(f"Les membres recevront le rôle {role.mention} en atteignant le niveau {level}.")
    
    @levelset.command(name="removerole")
    async def levelset_removerole(self, ctx, level: int):
        """Supprime une récompense de rôle pour un niveau spécifique"""
        async with self.config.guild(ctx.guild).roles_rewards() as roles_rewards:
            if str(level) in roles_rewards:
                del roles_rewards[str(level)]
                await ctx.send(f"La récompense de rôle pour le niveau {level} a été supprimée.")
            else:
                await ctx.send(f"Il n'y a pas de récompense de rôle pour le niveau {level}.")
    
    @levelset.command(name="reset")
    async def levelset_reset(self, ctx, member: discord.Member = None):
        """Réinitialise les statistiques d'un membre ou de tous les membres"""
        if member:
            # Réinitialiser un seul membre
            await self.config.member(member).clear()
            await ctx.send(f"Les statistiques de {member.mention} ont été réinitialisées.")
        else:
            # Demander confirmation pour réinitialiser tout le monde
            confirm_msg = await ctx.send("Voulez-vous vraiment réinitialiser les statistiques de TOUS les membres ? Répondez par 'oui' pour confirmer.")
            
            def check(m):
                return m.author == ctx.author and m.channel == ctx.channel and m.content.lower() == "oui"
            
            try:
                await self.bot.wait_for("message", check=check, timeout=30.0)
                # Réinitialiser tous les membres
                await self.config.clear_all_members(ctx.guild)
                await ctx.send("Toutes les statistiques ont été réinitialisées.")
            except asyncio.TimeoutError:
                await confirm_msg.edit(content="Opération annulée.")

    @levelset.command(name="forcereset")
    @commands.admin_or_permissions(administrator=True)
    async def levelset_forcereset(self, ctx):
        """Force un reset des niveaux"""
        # Demander confirmation
        confirm_msg = await ctx.send("⚠️ Voulez-vous vraiment réinitialiser tous les niveaux maintenant ? Cette action est irréversible. Répondez par 'oui' pour confirmer.")
        
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel and m.content.lower() == "oui"
        
        try:
            await self.bot.wait_for("message", check=check, timeout=30.0)
            # Effectuer le reset
            await self.reset_levels(ctx.guild)
            # Mettre à jour le timestamp du dernier reset
            await self.config.guild(ctx.guild).last_reset.set(datetime.datetime.now().timestamp())
            await ctx.send("✅ Les niveaux ont été réinitialisés avec succès.")
        except asyncio.TimeoutError:
            await confirm_msg.edit(content="❌ Opération annulée.")

    @levelset.command(name="checkroles")
    @commands.admin_or_permissions(administrator=True)
    async def levelset_checkroles(self, ctx):
        """Vérifie et attribue les rôles manquants en fonction des niveaux"""
        # Récupérer les données du serveur
        guild_data = await self.config.guild(ctx.guild).all()
        role_rewards = guild_data["roles_rewards"]
        
        if not role_rewards:
            return await ctx.send("❌ Aucune récompense de rôle n'est configurée.")
        
        # Message de statut initial
        status_msg = await ctx.send("🔍 Vérification des rôles en cours...")
        
        # Compteurs pour le rapport
        total_members = 0
        roles_added = 0
        roles_removed = 0
        errors = 0
        
        # Récupérer tous les membres
        all_members = await self.config.all_members(ctx.guild)
        
        for member_id, member_data in all_members.items():
            member = ctx.guild.get_member(member_id)
            if not member:  # Ignorer les membres qui ne sont plus sur le serveur
                continue
                
            total_members += 1
            
            try:
                # Vérifier chaque niveau de récompense
                for level_str, role_id in role_rewards.items():
                    role = ctx.guild.get_role(role_id)
                    if not role:
                        continue
                        
                    should_have_role = member_data["level"] >= int(level_str)
                    has_role = role in member.roles
                    
                    if should_have_role and not has_role:
                        # Ajouter le rôle manquant
                        await member.add_roles(role, reason=f"Attribution automatique - Niveau {level_str}")
                        roles_added += 1
                    elif not should_have_role and has_role:
                        # Retirer le rôle si le niveau est insuffisant
                        await member.remove_roles(role, reason="Retrait automatique - Niveau insuffisant")
                        roles_removed += 1
                        
            except discord.Forbidden:
                errors += 1
                continue
            except Exception as e:
                errors += 1
                print(f"Erreur lors de la vérification des rôles pour {member}: {str(e)}")
                continue
        
        # Créer l'embed de rapport
        embed = discord.Embed(
            title="📊 Rapport de vérification des rôles",
            color=0x2b2d31,
            timestamp=datetime.datetime.now()
        )
        
        embed.add_field(name="Membres vérifiés", value=str(total_members), inline=True)
        embed.add_field(name="Rôles ajoutés", value=str(roles_added), inline=True)
        embed.add_field(name="Rôles retirés", value=str(roles_removed), inline=True)
        
        if errors > 0:
            embed.add_field(
                name="⚠️ Erreurs",
                value=f"{errors} erreur(s) se sont produites lors de la vérification",
                inline=False
            )
        
        # Afficher les récompenses actuelles
        rewards_text = "**Récompenses configurées :**\n"
        for level, role_id in sorted(role_rewards.items(), key=lambda x: int(x[0])):
            role = ctx.guild.get_role(role_id)
            rewards_text += f"Niveau {level}: {role.mention if role else 'Rôle inconnu'}\n"
        
        embed.add_field(name="ℹ️ Informations", value=rewards_text, inline=False)
        embed.set_footer(text=f"Demandé par {ctx.author.display_name}")
        
        # Mettre à jour le message de statut avec le rapport
        await status_msg.edit(content=None, embed=embed)

    @commands.command(name="checklevels")
    @commands.admin_or_permissions(administrator=True)
    async def check_levels(self, ctx):
        """Vérifie les niveaux de tous les membres et attribue les rôles manquellement"""
        # Définition manuelle des rôles et niveaux
        role_levels = {
            20: 1352739404657201175,  # Actifs
            30: 1352739400261304463   # Actif+
        }
        
        # Message de statut initial
        status_msg = await ctx.send("🔍 Vérification des niveaux en cours...")
        
        # Compteurs pour le rapport
        total_members = 0
        roles_added = 0
        errors = 0
        members_with_roles = []
        
        # Récupérer tous les membres du serveur
        for member in ctx.guild.members:
            if member.bot:  # Ignorer les bots
                continue
                
            total_members += 1
            
            # Récupérer les données du membre (s'il en a)
            member_data = await self.config.member(member).all()
            member_level = member_data.get("level", 0)
            
            try:
                # Vérifier chaque niveau de récompense
                for required_level, role_id in role_levels.items():
                    role = ctx.guild.get_role(role_id)
                    if not role:
                        continue
                        
                    if member_level >= required_level and role not in member.roles:
                        # Ajouter le rôle manquant
                        await member.add_roles(role, reason=f"Attribution manuelle - Niveau {required_level}")
                        roles_added += 1
                        members_with_roles.append((member.name, member_level, role.name))
                        
            except discord.Forbidden:
                errors += 1
                continue
            except Exception as e:
                errors += 1
                print(f"Erreur lors de la vérification des rôles pour {member}: {str(e)}")
                continue
        
        # Créer l'embed de rapport
        embed = discord.Embed(
            title="📊 Rapport d'attribution des rôles",
            description="Attribution des rôles en fonction des niveaux",
            color=0x2b2d31,
            timestamp=datetime.datetime.now()
        )
        
        embed.add_field(name="Membres vérifiés", value=str(total_members), inline=True)
        embed.add_field(name="Rôles attribués", value=str(roles_added), inline=True)
        
        if errors > 0:
            embed.add_field(
                name="⚠️ Erreurs",
                value=f"{errors} erreur(s) se sont produites lors de la vérification",
                inline=False
            )
        
        # Afficher les membres qui ont reçu des rôles
        if members_with_roles:
            details = "**Rôles attribués aux membres :**\n"
            for member_name, level, role_name in members_with_roles:
                details += f"• {member_name} (Niveau {level}) → {role_name}\n"
            if len(details) > 1024:  # Limite Discord pour un field
                details = details[:1021] + "..."
            embed.add_field(name="📝 Détails", value=details, inline=False)
        else:
            embed.add_field(name="📝 Détails", value="Aucun rôle n'a été attribué.", inline=False)
        
        embed.set_footer(text=f"Demandé par {ctx.author.display_name}")
        
        # Mettre à jour le message de statut avec le rapport
        await status_msg.edit(content=None, embed=embed)

async def setup(bot):
    await bot.add_cog(DiscordRanks(bot))
