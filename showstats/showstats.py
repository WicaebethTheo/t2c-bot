import discord
from redbot.core import commands, Config
import asyncio
import logging

class ShowStats(commands.Cog):
    """Module pour afficher automatiquement les statistiques du serveur dans les noms de salons vocaux"""

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=12345678906)
        
        # Configuration par défaut
        default_guild = {
            "enabled": True,
            "members_channel_id": 1352736642045182112,  # Canal pour afficher le nombre de membres
            "boosts_channel_id": 1352976542858481795,   # Canal pour afficher le nombre de boosts
            "members_format": "╭💎・Membres : {count}",  # Format pour le nom du canal des membres
            "boosts_format": "╰🧊・Boosts : {count}",    # Format pour le nom du canal des boosts
            "update_interval": 300                     # Intervalle de mise à jour en secondes (5 minutes)
        }
        
        self.config.register_guild(**default_guild)
        
        # Démarrer la tâche de mise à jour des statistiques
        self.stats_task = self.bot.loop.create_task(self.update_stats_loop())
        self.logger = logging.getLogger("red.showstats")
    
    def cog_unload(self):
        # Annuler la tâche planifiée lors du déchargement du cog
        if self.stats_task:
            self.stats_task.cancel()
    
    async def update_stats_loop(self):
        """Boucle de mise à jour des statistiques dans les noms de salons"""
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            try:
                # Mettre à jour les statistiques pour chaque serveur
                for guild in self.bot.guilds:
                    enabled = await self.config.guild(guild).enabled()
                    if enabled:
                        await self.update_server_stats(guild)
                
                # Attendre l'intervalle configuré
                update_interval = await self.config.guild(guild).update_interval()
                await asyncio.sleep(update_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Erreur dans la tâche de mise à jour des statistiques: {e}")
                await asyncio.sleep(60)  # Attendre 1 minute en cas d'erreur
    
    async def update_server_stats(self, guild):
        """Met à jour les statistiques d'un serveur spécifique"""
        try:
            # Récupérer les IDs des canaux
            members_channel_id = await self.config.guild(guild).members_channel_id()
            boosts_channel_id = await self.config.guild(guild).boosts_channel_id()
            
            # Récupérer les formats de noms
            members_format = await self.config.guild(guild).members_format()
            boosts_format = await self.config.guild(guild).boosts_format()
            
            # Récupérer les canaux
            members_channel = guild.get_channel(members_channel_id)
            boosts_channel = guild.get_channel(boosts_channel_id)
            
            # Mettre à jour le canal des membres
            if members_channel:
                # Obtenir le nombre total de membres (sans les bots)
                member_count = sum(1 for member in guild.members if not member.bot)
                new_name = members_format.format(count=member_count)
                
                # Ne mettre à jour que si le nom a changé
                if members_channel.name != new_name:
                    await members_channel.edit(name=new_name)
                    self.logger.info(f"Canal des membres mis à jour pour {guild.name}: {new_name}")
            else:
                self.logger.warning(f"Canal des membres {members_channel_id} non trouvé pour {guild.name}")
            
            # Mettre à jour le canal des boosts
            if boosts_channel:
                # Obtenir le nombre de boosts
                boost_count = guild.premium_subscription_count
                new_name = boosts_format.format(count=boost_count)
                
                # Ne mettre à jour que si le nom a changé
                if boosts_channel.name != new_name:
                    await boosts_channel.edit(name=new_name)
                    self.logger.info(f"Canal des boosts mis à jour pour {guild.name}: {new_name}")
            else:
                self.logger.warning(f"Canal des boosts {boosts_channel_id} non trouvé pour {guild.name}")
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la mise à jour des statistiques pour {guild.name}: {e}")
    
    @commands.group(name="showstats")
    @commands.admin_or_permissions(administrator=True)
    async def showstats_commands(self, ctx):
        """Commandes pour gérer l'affichage des statistiques dans les salons vocaux"""
        if ctx.invoked_subcommand is None:
            # Afficher les paramètres actuels
            enabled = await self.config.guild(ctx.guild).enabled()
            members_channel_id = await self.config.guild(ctx.guild).members_channel_id()
            boosts_channel_id = await self.config.guild(ctx.guild).boosts_channel_id()
            update_interval = await self.config.guild(ctx.guild).update_interval()
            
            members_channel = ctx.guild.get_channel(members_channel_id)
            boosts_channel = ctx.guild.get_channel(boosts_channel_id)
            
            status = "✅ Activé" if enabled else "❌ Désactivé"
            
            embed = discord.Embed(
                title="📊 Configuration de ShowStats",
                description=f"État: {status}\nIntervalle de mise à jour: {update_interval} secondes",
                color=0x3498DB
            )
            
            embed.add_field(
                name="Canal des membres",
                value=f"ID: {members_channel_id}\nCanal: {members_channel.mention if members_channel else 'Non trouvé'}",
                inline=False
            )
            
            embed.add_field(
                name="Canal des boosts",
                value=f"ID: {boosts_channel_id}\nCanal: {boosts_channel.mention if boosts_channel else 'Non trouvé'}",
                inline=False
            )
            
            await ctx.send(embed=embed)
    
    @showstats_commands.command(name="toggle")
    async def toggle_stats(self, ctx, enabled: bool = None):
        """Active ou désactive la mise à jour automatique des statistiques
        
        Exemples:
        - `!showstats toggle true` - Active les mises à jour
        - `!showstats toggle false` - Désactive les mises à jour
        - `!showstats toggle` - Inverse l'état actuel
        """
        current = await self.config.guild(ctx.guild).enabled()
        
        if enabled is None:
            # Inverser l'état actuel
            enabled = not current
        
        await self.config.guild(ctx.guild).enabled.set(enabled)
        
        if enabled:
            await ctx.send("✅ Les mises à jour automatiques des statistiques sont maintenant activées.")
            # Exécuter une mise à jour immédiate
            await self.update_server_stats(ctx.guild)
        else:
            await ctx.send("❌ Les mises à jour automatiques des statistiques sont maintenant désactivées.")
    
    @showstats_commands.command(name="memberschannel")
    async def set_members_channel(self, ctx, channel: discord.VoiceChannel):
        """Définit le salon vocal pour afficher le nombre de membres
        
        Exemple: `!showstats memberschannel #nombre-de-membres`
        """
        await self.config.guild(ctx.guild).members_channel_id.set(channel.id)
        await ctx.send(f"✅ Le canal {channel.mention} sera utilisé pour afficher le nombre de membres.")
        
        # Mettre à jour immédiatement
        await self.update_server_stats(ctx.guild)
    
    @showstats_commands.command(name="boostschannel")
    async def set_boosts_channel(self, ctx, channel: discord.VoiceChannel):
        """Définit le salon vocal pour afficher le nombre de boosts
        
        Exemple: `!showstats boostschannel #nombre-de-boosts`
        """
        await self.config.guild(ctx.guild).boosts_channel_id.set(channel.id)
        await ctx.send(f"✅ Le canal {channel.mention} sera utilisé pour afficher le nombre de boosts.")
        
        # Mettre à jour immédiatement
        await self.update_server_stats(ctx.guild)
    
    @showstats_commands.command(name="interval")
    async def set_update_interval(self, ctx, seconds: int):
        """Définit l'intervalle de mise à jour en secondes (minimum 60 secondes)
        
        Exemple: `!showstats interval 300` - Met à jour toutes les 5 minutes
        """
        if seconds < 60:
            return await ctx.send("⚠️ L'intervalle minimum est de 60 secondes.")
        
        await self.config.guild(ctx.guild).update_interval.set(seconds)
        await ctx.send(f"✅ L'intervalle de mise à jour a été défini à {seconds} secondes.")
    
    @showstats_commands.command(name="format")
    async def set_format(self, ctx, stat_type: str, *, format_str: str):
        """Définit le format d'affichage pour un type de statistique
        
        Types disponibles: members, boosts
        Utilisez {count} pour l'emplacement du nombre
        
        Exemples:
        - `!showstats format members ╭💎・Membres : {count}`
        - `!showstats format boosts ╰🧊・Boosts : {count}`
        """
        if stat_type.lower() not in ["members", "boosts"]:
            return await ctx.send("⚠️ Type invalide. Utilisez 'members' ou 'boosts'.")
        
        if "{count}" not in format_str:
            return await ctx.send("⚠️ Le format doit contenir {count} pour l'emplacement du nombre.")
        
        if stat_type.lower() == "members":
            await self.config.guild(ctx.guild).members_format.set(format_str)
        else:
            await self.config.guild(ctx.guild).boosts_format.set(format_str)
        
        await ctx.send(f"✅ Format pour {stat_type} défini sur: {format_str}")
        
        # Mettre à jour immédiatement
        await self.update_server_stats(ctx.guild)
    
    @showstats_commands.command(name="update")
    async def force_update(self, ctx):
        """Force la mise à jour immédiate des statistiques"""
        await ctx.send("⏳ Mise à jour des statistiques...")
        await self.update_server_stats(ctx.guild)
        await ctx.send("✅ Statistiques mises à jour!")

async def setup(bot):
    await bot.add_cog(ShowStats(bot))
