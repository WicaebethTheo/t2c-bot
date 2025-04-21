import discord
from redbot.core import commands, Config
import asyncio
import datetime
import logging
from datetime import datetime, timedelta

class Stats(commands.Cog):
    """Module de statistiques pour suivre l'utilisation des commandes"""

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=12345678905)
        
        # Configuration par défaut
        default_guild = {
            "roulette_stats": {},  # {user_id: count}
            "stats_channel_id": 1360579826523705456,  # Canal où envoyer le récapitulatif
            "last_reset": None,  # Date de la dernière réinitialisation des stats
        }
        
        self.config.register_guild(**default_guild)
        
        # Démarrer la tâche d'envoi du récapitulatif quotidien
        self.daily_recap_task = self.bot.loop.create_task(self.schedule_daily_recap())
        self.logger = logging.getLogger("red.stats-staff")
    
    def cog_unload(self):
        # Annuler la tâche planifiée lors du déchargement du cog
        if self.daily_recap_task:
            self.daily_recap_task.cancel()
    
    async def schedule_daily_recap(self):
        """Planifie l'envoi du récapitulatif quotidien à 20h"""
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            try:
                # Obtenir l'heure actuelle
                now = datetime.now()
                
                # Calculer le temps restant jusqu'à 20h aujourd'hui
                target_time = now.replace(hour=20, minute=0, second=0, microsecond=0)
                if now >= target_time:
                    # Si nous avons déjà dépassé 20h, attendre jusqu'à demain 20h
                    target_time = target_time + timedelta(days=1)
                
                # Calculer le délai en secondes
                seconds_until_target = (target_time - now).total_seconds()
                
                self.logger.info(f"Prochain récapitulatif des statistiques dans {seconds_until_target:.2f} secondes")
                
                # Attendre jusqu'à l'heure cible
                await asyncio.sleep(seconds_until_target)
                
                # Envoyer le récapitulatif pour chaque serveur
                for guild in self.bot.guilds:
                    await self.send_daily_recap(guild)
                
                # Attendre 24 heures avant la prochaine vérification (pour éviter les doublons)
                await asyncio.sleep(60)  # Attendre 1 minute pour éviter de relancer immédiatement
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Erreur dans la tâche de récapitulatif quotidien: {e}")
                await asyncio.sleep(3600)  # Attendre 1 heure en cas d'erreur
    
    async def send_daily_recap(self, guild):
        """Envoie le récapitulatif quotidien des statistiques"""
        try:
            # Récupérer les statistiques et l'ID du canal
            stats_channel_id = await self.config.guild(guild).stats_channel_id()
            roulette_stats = await self.config.guild(guild).roulette_stats()
            
            # Vérifier si nous avons des statistiques à afficher
            if not roulette_stats:
                return
            
            # Récupérer le canal
            stats_channel = guild.get_channel(stats_channel_id)
            if not stats_channel:
                self.logger.warning(f"Canal de statistiques {stats_channel_id} non trouvé pour le serveur {guild.name}")
                return
            
            # Créer l'embed pour le récapitulatif
            embed = discord.Embed(
                title="📊 Récapitulatif d'utilisation de !roulette",
                description=f"Voici le récapitulatif des utilisations de la commande !roulette pour aujourd'hui",
                color=0x3498DB,
                timestamp=datetime.now()
            )
            
            # Ajouter les statistiques à l'embed
            users_info = []
            
            for user_id, count in roulette_stats.items():
                # Récupérer l'utilisateur
                user = guild.get_member(int(user_id))
                if not user:
                    continue
                
                # Récupérer le rôle le plus haut de l'utilisateur (ignorant le rôle @everyone)
                highest_role = None
                for role in user.roles:
                    if role.name != "@everyone":
                        if highest_role is None or role.position > highest_role.position:
                            highest_role = role
                
                highest_role_name = highest_role.name if highest_role else "Aucun rôle"
                
                # Ajouter l'utilisateur à la liste
                users_info.append({
                    "name": user.display_name,
                    "count": count,
                    "role": highest_role_name,
                    "role_color": highest_role.color.value if highest_role else 0xFFFFFF,
                    "avatar": user.display_avatar.url,
                    "user": user
                })
            
            # Trier par nombre d'utilisations
            users_info.sort(key=lambda x: x["count"], reverse=True)
            
            # Ajouter chaque utilisateur au récapitulatif
            if users_info:
                for i, user_info in enumerate(users_info, 1):
                    embed.add_field(
                        name=f"{i}. {user_info['name']}",
                        value=f"📢 **Utilisations**: {user_info['count']}\n👑 **Rang**: {user_info['role']}",
                        inline=False
                    )
                
                # Ajouter le plus grand utilisateur comme thumbnail
                if users_info:
                    embed.set_thumbnail(url=users_info[0]["avatar"])
            else:
                embed.description = "Aucune utilisation de la commande !roulette aujourd'hui."
            
            # Ajouter un footer
            embed.set_footer(text="Les statistiques seront réinitialisées demain à 20h")
            
            # Envoyer l'embed
            await stats_channel.send(embed=embed)
            
            # Réinitialiser les statistiques
            await self.config.guild(guild).roulette_stats.clear()
            await self.config.guild(guild).last_reset.set(datetime.now().isoformat())
            
            self.logger.info(f"Récapitulatif des statistiques envoyé pour {guild.name}")
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'envoi du récapitulatif quotidien: {e}")
    
    @commands.Cog.listener()
    async def on_command(self, ctx):
        """Écoute toutes les commandes exécutées"""
        if not ctx.guild:
            return
        
        # Vérifier si c'est la commande roulette
        if ctx.command.name == "roulette":
            # Récupérer les statistiques actuelles
            async with self.config.guild(ctx.guild).roulette_stats() as roulette_stats:
                user_id = str(ctx.author.id)
                roulette_stats[user_id] = roulette_stats.get(user_id, 0) + 1
            
            self.logger.debug(f"Utilisation de !roulette enregistrée pour {ctx.author.name} ({ctx.author.id})")
    
    @commands.group(name="statscog")
    @commands.admin_or_permissions(administrator=True)
    async def stats_commands(self, ctx):
        """Commandes pour gérer les statistiques"""
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)
    
    @stats_commands.command(name="channel")
    async def set_stats_channel(self, ctx, channel: discord.TextChannel = None):
        """Définir le canal pour les récapitulatifs de statistiques
        
        Exemple:
        - `!statscog channel #statistiques` - Définit le canal #statistiques pour les récapitulatifs
        - `!statscog channel` - Affiche le canal actuellement défini
        """
        if channel:
            await self.config.guild(ctx.guild).stats_channel_id.set(channel.id)
            await ctx.send(f"✅ Canal de statistiques défini sur {channel.mention}")
        else:
            channel_id = await self.config.guild(ctx.guild).stats_channel_id()
            channel = ctx.guild.get_channel(channel_id)
            if channel:
                await ctx.send(f"📊 Canal de statistiques actuel: {channel.mention}")
            else:
                await ctx.send("⚠️ Aucun canal de statistiques défini.")
    
    @stats_commands.command(name="view")
    async def view_stats(self, ctx):
        """Affiche les statistiques actuelles d'utilisation de !roulette"""
        roulette_stats = await self.config.guild(ctx.guild).roulette_stats()
        
        if not roulette_stats:
            await ctx.send("📊 Aucune statistique disponible. Personne n'a utilisé la commande !roulette depuis la dernière réinitialisation.")
            return
        
        embed = discord.Embed(
            title="📊 Statistiques d'utilisation de !roulette",
            description="Utilisations depuis la dernière réinitialisation",
            color=0x3498DB
        )
        
        # Trier les utilisateurs par nombre d'utilisations
        sorted_stats = sorted(roulette_stats.items(), key=lambda x: x[1], reverse=True)
        
        for user_id, count in sorted_stats:
            user = ctx.guild.get_member(int(user_id))
            name = user.display_name if user else f"Utilisateur {user_id}"
            embed.add_field(name=name, value=f"📢 **Utilisations**: {count}", inline=True)
        
        last_reset = await self.config.guild(ctx.guild).last_reset()
        if last_reset:
            reset_time = datetime.fromisoformat(last_reset)
            embed.set_footer(text=f"Dernière réinitialisation: {reset_time.strftime('%d/%m/%Y %H:%M')}")
        
        await ctx.send(embed=embed)
    
    @stats_commands.command(name="reset")
    async def reset_stats(self, ctx):
        """Réinitialise les statistiques d'utilisation de !roulette"""
        await self.config.guild(ctx.guild).roulette_stats.clear()
        await self.config.guild(ctx.guild).last_reset.set(datetime.now().isoformat())
        await ctx.send("✅ Les statistiques de !roulette ont été réinitialisées.")
    
    @stats_commands.command(name="forcedaily")
    async def force_daily_recap(self, ctx):
        """Force l'envoi du récapitulatif quotidien"""
        await ctx.send("⏳ Génération du récapitulatif quotidien...")
        await self.send_daily_recap(ctx.guild)
        await ctx.send("✅ Récapitulatif quotidien envoyé!")

async def setup(bot):
    await bot.add_cog(Stats(bot))
