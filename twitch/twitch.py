import discord
from redbot.core import commands, Config
import asyncio
import logging

class TwitchRole(commands.Cog):
    """Module pour gérer automatiquement le rôle 'En live' pour les streamers"""

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=1358812550371)
        
        # Configuration par défaut
        default_guild = {
            "enabled": True,
            "streamer_role_id": 1353010353096626246,  # ID du rôle "Streamer"
            "live_role_id": 1358812550371868943,      # ID du rôle "En live"
            "check_interval": 60,                     # Vérification toutes les 60 secondes
            "log_channel_id": None,                    # Canal pour les logs (optionnel)
            "debug_mode": False  # Nouveau paramètre pour le mode debug
        }
        
        self.config.register_guild(**default_guild)
        self.logger = logging.getLogger("red.twitch")
        self.check_task = None
        
    def cog_unload(self):
        """Nettoyer lorsque le cog est déchargé"""
        if self.check_task:
            self.check_task.cancel()
            
    async def initialize(self):
        """Démarrer la tâche de vérification des streamers"""
        self.check_task = self.bot.loop.create_task(self.check_streamers_loop())
        
    async def is_streaming(self, member: discord.Member) -> bool:
        """Vérifie si un membre est en stream avec une détection améliorée"""
        if not member.activities:
            return False

        for activity in member.activities:
            # Log détaillé pour le débogage
            self.logger.info(f"Activité pour {member.name}:")
            self.logger.info(f"- Type: {activity.type}")
            self.logger.info(f"- Classe: {activity.__class__.__name__}")
            
            # Loguer tous les attributs disponibles de l'activité
            for attr in dir(activity):
                if not attr.startswith('_'):  # Ignorer les attributs privés
                    try:
                        value = getattr(activity, attr)
                        self.logger.info(f"- {attr}: {value}")
                    except Exception:
                        pass

            # Vérification exhaustive des différents types de streaming
            if any([
                # Vérification standard du type d'activité
                activity.type == discord.ActivityType.streaming,
                # Vérification de l'instance
                isinstance(activity, discord.Streaming),
                # Vérification du type en tant que chaîne
                str(activity.type).lower() == 'streaming',
                # Vérification des attributs spécifiques aux streams
                hasattr(activity, 'platform') and activity.platform and 'twitch' in str(activity.platform).lower(),
                # Vérification des attributs de RichPresence
                hasattr(activity, 'application_id') and hasattr(activity, 'name') and 'twitch' in str(activity.name).lower(),
                # Vérification des détails de l'activité
                hasattr(activity, 'details') and activity.details and 'streaming' in str(activity.details).lower(),
                # Vérification du nom de l'activité
                hasattr(activity, 'name') and activity.name and 'twitch' in str(activity.name).lower(),
                # Vérification des assets
                hasattr(activity, 'assets') and activity.assets and any('twitch' in str(asset).lower() for asset in activity.assets.values() if asset)
            ]):
                return True

        return False

    async def check_streamers_loop(self):
        """Boucle principale qui vérifie les streamers en direct"""
        await self.bot.wait_until_ready()
        while True:
            try:
                for guild in self.bot.guilds:
                    # Vérifier si le module est activé dans ce serveur
                    enabled = await self.config.guild(guild).enabled()
                    if not enabled:
                        continue
                        
                    # Récupérer les IDs des rôles depuis la config
                    streamer_role_id = await self.config.guild(guild).streamer_role_id()
                    live_role_id = await self.config.guild(guild).live_role_id()
                    debug_mode = await self.config.guild(guild).debug_mode()
                    
                    # Récupérer les objets de rôle
                    streamer_role = guild.get_role(streamer_role_id)
                    live_role = guild.get_role(live_role_id)
                    
                    if not streamer_role or not live_role:
                        self.logger.warning(f"Rôles introuvables dans le serveur {guild.name}")
                        continue
                        
                    # Récupérer tous les membres avec le rôle Streamer
                    streamers = [member for member in guild.members if streamer_role in member.roles]
                    
                    for streamer in streamers:
                        if debug_mode:
                            self.logger.info(f"Vérification de {streamer.name}...")
                            if streamer.activities:
                                for activity in streamer.activities:
                                    self.logger.info(f"- Activité: {activity.type} - {activity.__class__.__name__}")
                        
                        is_streaming = await self.is_streaming(streamer)
                        
                        # Ajouter ou retirer le rôle en fonction du statut
                        has_live_role = live_role in streamer.roles
                        
                        if is_streaming and not has_live_role:
                            # Ajouter le rôle "En live"
                            await streamer.add_roles(live_role, reason="Détection automatique de stream")
                            await self.log_action(guild, f"🟢 {streamer.display_name} a commencé un stream, ajout du rôle {live_role.name}")
                            
                        elif not is_streaming and has_live_role:
                            # Retirer le rôle "En live"
                            await streamer.remove_roles(live_role, reason="Fin du stream détectée")
                            await self.log_action(guild, f"🔴 {streamer.display_name} a terminé son stream, retrait du rôle {live_role.name}")
                
                # Attendre avant la prochaine vérification
                interval = await self.get_check_interval()
                await asyncio.sleep(interval)
                
            except asyncio.CancelledError:
                # La tâche a été annulée, sortir proprement
                break
            except Exception as e:
                self.logger.error(f"Erreur dans la boucle de vérification des streamers: {str(e)}")
                await asyncio.sleep(30)  # Attente en cas d'erreur
    
    async def get_check_interval(self):
        """Récupérer l'intervalle de vérification (valeur par défaut en cas d'erreur)"""
        try:
            guild = next(iter(self.bot.guilds))
            return await self.config.guild(guild).check_interval()
        except:
            return 60  # Intervalle par défaut en secondes
    
    async def log_action(self, guild, message):
        """Envoyer un message de log dans le canal configuré"""
        try:
            log_channel_id = await self.config.guild(guild).log_channel_id()
            if log_channel_id:
                channel = guild.get_channel(log_channel_id)
                if channel:
                    await channel.send(message)
        except Exception as e:
            self.logger.error(f"Erreur lors de l'envoi du log: {str(e)}")
    
    @commands.group(name="twitch")
    @commands.admin_or_permissions(manage_roles=True)
    async def twitch_commands(self, ctx):
        """Commandes pour gérer le module Twitch"""
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)
    
    @twitch_commands.command(name="toggle")
    async def toggle(self, ctx, enabled: bool = None):
        """Activer ou désactiver le module
        
        Exemples:
        - `!twitch toggle true` - Active le module
        - `!twitch toggle false` - Désactive le module
        - `!twitch toggle` - Inverse l'état actuel
        """
        current = await self.config.guild(ctx.guild).enabled()
        
        if enabled is None:
            enabled = not current
            
        await self.config.guild(ctx.guild).enabled.set(enabled)
        
        if enabled:
            await ctx.send("✅ Module de détection des streamers activé.")
        else:
            await ctx.send("❌ Module de détection des streamers désactivé.")
    
    @twitch_commands.command(name="status")
    async def status(self, ctx):
        """Affiche l'état actuel de la configuration"""
        enabled = await self.config.guild(ctx.guild).enabled()
        streamer_role_id = await self.config.guild(ctx.guild).streamer_role_id()
        live_role_id = await self.config.guild(ctx.guild).live_role_id()
        check_interval = await self.config.guild(ctx.guild).check_interval()
        log_channel_id = await self.config.guild(ctx.guild).log_channel_id()
        
        # Récupérer les objets pour l'affichage
        streamer_role = ctx.guild.get_role(streamer_role_id)
        live_role = ctx.guild.get_role(live_role_id)
        log_channel = ctx.guild.get_channel(log_channel_id) if log_channel_id else None
        
        # Créer l'embed
        embed = discord.Embed(
            title="⚙️ Configuration du module Twitch",
            description=f"État: {'✅ Activé' if enabled else '❌ Désactivé'}",
            color=0x6441a5  # Couleur Twitch
        )
        
        embed.add_field(
            name="Rôles",
            value=f"Rôle Streamer: {streamer_role.mention if streamer_role else 'Non trouvé'}\n"
                  f"Rôle En live: {live_role.mention if live_role else 'Non trouvé'}",
            inline=False
        )
        
        embed.add_field(
            name="Paramètres",
            value=f"Intervalle de vérification: {check_interval} secondes\n"
                  f"Canal de logs: {log_channel.mention if log_channel else 'Non configuré'}",
            inline=False
        )
        
        # Compter les streamers actifs
        streamer_role = ctx.guild.get_role(streamer_role_id)
        live_role = ctx.guild.get_role(live_role_id)
        
        if streamer_role and live_role:
            streamers_count = len([m for m in ctx.guild.members if streamer_role in m.roles])
            live_count = len([m for m in ctx.guild.members if live_role in m.roles])
            
            embed.add_field(
                name="Statistiques",
                value=f"Nombre de streamers: {streamers_count}\n"
                      f"Actuellement en live: {live_count}",
                inline=False
            )
        
        await ctx.send(embed=embed)
    
    @twitch_commands.command(name="setrole")
    async def set_roles(self, ctx, role_type: str, role: discord.Role):
        """Définir les rôles pour le module
        
        Arguments:
        - role_type: 'streamer' ou 'live'
        - role: @mention du rôle ou ID
        
        Exemples:
        - `!twitch setrole streamer @Streamer`
        - `!twitch setrole live @En_live`
        """
        if role_type.lower() not in ["streamer", "live"]:
            return await ctx.send("❌ Type de rôle invalide. Utilisez 'streamer' ou 'live'.")
        
        if role_type.lower() == "streamer":
            await self.config.guild(ctx.guild).streamer_role_id.set(role.id)
            await ctx.send(f"✅ Rôle Streamer défini à {role.name}")
        else:
            await self.config.guild(ctx.guild).live_role_id.set(role.id)
            await ctx.send(f"✅ Rôle En live défini à {role.name}")
    
    @twitch_commands.command(name="setinterval")
    async def set_interval(self, ctx, seconds: int):
        """Définir l'intervalle de vérification en secondes
        
        Argument:
        - seconds: Intervalle en secondes (min: 30, max: 300)
        
        Exemple:
        - `!twitch setinterval 60`
        """
        if seconds < 30:
            return await ctx.send("❌ L'intervalle ne peut pas être inférieur à 30 secondes.")
        
        if seconds > 300:
            return await ctx.send("❌ L'intervalle ne peut pas être supérieur à 300 secondes (5 minutes).")
        
        await self.config.guild(ctx.guild).check_interval.set(seconds)
        await ctx.send(f"✅ Intervalle de vérification défini à {seconds} secondes.")
    
    @twitch_commands.command(name="setlogchannel")
    async def set_log_channel(self, ctx, channel: discord.TextChannel = None):
        """Définir le canal pour les logs
        
        Argument:
        - channel: #mention du canal ou aucun pour désactiver
        
        Exemples:
        - `!twitch setlogchannel #logs-twitch`
        - `!twitch setlogchannel` (pour désactiver)
        """
        if channel:
            await self.config.guild(ctx.guild).log_channel_id.set(channel.id)
            await ctx.send(f"✅ Canal de logs défini à {channel.mention}.")
        else:
            await self.config.guild(ctx.guild).log_channel_id.set(None)
            await ctx.send("✅ Canal de logs désactivé.")
    
    @twitch_commands.command(name="debug")
    async def toggle_debug(self, ctx, enabled: bool = None):
        """Active ou désactive le mode debug
        
        Exemple:
        - `!twitch debug true` - Active le mode debug
        - `!twitch debug false` - Désactive le mode debug
        """
        current = await self.config.guild(ctx.guild).debug_mode()
        
        if enabled is None:
            enabled = not current
            
        await self.config.guild(ctx.guild).debug_mode.set(enabled)
        
        if enabled:
            await ctx.send("🔍 Mode debug activé. Les logs détaillés seront affichés.")
        else:
            await ctx.send("🔍 Mode debug désactivé.")
    
    @twitch_commands.command(name="check")
    async def force_check(self, ctx):
        """Force une vérification immédiate des streamers"""
        await ctx.send("🔍 Vérification des streamers en cours...")
        
        streamer_role_id = await self.config.guild(ctx.guild).streamer_role_id()
        live_role_id = await self.config.guild(ctx.guild).live_role_id()
        debug_mode = await self.config.guild(ctx.guild).debug_mode()
        
        streamer_role = ctx.guild.get_role(streamer_role_id)
        live_role = ctx.guild.get_role(live_role_id)
        
        if not streamer_role or not live_role:
            return await ctx.send("❌ Les rôles configurés n'ont pas été trouvés.")
            
        streamers = [member for member in ctx.guild.members if streamer_role in member.roles]
        
        if not streamers:
            return await ctx.send(f"ℹ️ Aucun membre avec le rôle {streamer_role.name} n'a été trouvé.")
        
        live_streamers = []
        for streamer in streamers:
            if debug_mode:
                await ctx.send(f"🔍 Vérification de {streamer.name}...")
                if streamer.activities:
                    activities_info = []
                    for activity in streamer.activities:
                        activity_details = [
                            f"Type: {activity.type}",
                            f"Nom: {activity.name if hasattr(activity, 'name') else 'N/A'}"
                        ]
                        
                        # Ajouter les détails supplémentaires s'ils existent
                        if hasattr(activity, 'details') and activity.details:
                            activity_details.append(f"Détails: {activity.details}")
                        if hasattr(activity, 'state') and activity.state:
                            activity_details.append(f"État: {activity.state}")
                        if hasattr(activity, 'url') and activity.url:
                            activity_details.append(f"URL: {activity.url}")
                        if hasattr(activity, 'platform') and activity.platform:
                            activity_details.append(f"Plateforme: {activity.platform}")
                            
                        activities_info.append(" | ".join(activity_details))
                    
                    await ctx.send("Activités trouvées:\n" + "\n".join(f"- {info}" for info in activities_info))
            
            is_streaming = await self.is_streaming(streamer)
            has_live_role = live_role in streamer.roles
            
            if debug_mode:
                await ctx.send(f"État du stream pour {streamer.name}: {'✅ En stream' if is_streaming else '❌ Pas en stream'}")
            
            if is_streaming and not has_live_role:
                await streamer.add_roles(live_role, reason="Détection manuelle de stream")
                await ctx.send(f"🟢 {streamer.display_name} est en stream, ajout du rôle {live_role.name}")
                live_streamers.append(streamer.display_name)
                
            elif not is_streaming and has_live_role:
                await streamer.remove_roles(live_role, reason="Fin du stream détectée")
                await ctx.send(f"🔴 {streamer.display_name} n'est pas en stream, retrait du rôle {live_role.name}")
        
        if not live_streamers:
            await ctx.send("✅ Vérification terminée. Aucun nouveau streamer en direct détecté.")
        else:
            await ctx.send(f"✅ Vérification terminée. {len(live_streamers)} streamers en direct : {', '.join(live_streamers)}")

async def setup(bot):
    cog = TwitchRole(bot)
    await bot.add_cog(cog)
    await cog.initialize()
