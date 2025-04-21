import discord
from redbot.core import commands, Config
import asyncio
from discord.ui import Button, View
from typing import List

class ServerChannels(commands.Cog):
    """Création automatique des salons pour le serveur T2C Staff"""

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=1355616275233247382)
        self.target_server_id = 1355616275233247382  # ID du serveur cible
        
        # Définition des catégories et leurs salons
        self.categories = [
            {
                "name": "-------| Général |-------",
                "channels": [
                    {"name": "join-leave", "emoji": "🏆", "type": "text"},
                    {"name": "présentations", "emoji": None, "type": "text"},
                    {"name": "avertissement", "emoji": "🚩", "type": "text"},
                    {"name": "annonce", "emoji": "🔔", "type": "text"},
                    {"name": "compte-rendu-réunion", "emoji": "📝", "type": "text"},
                    {"name": "général", "emoji": "💬", "type": "text"},
                    {"name": "absence", "emoji": "✍️", "type": "text"},
                    {"name": "Réunion", "emoji": None, "type": "voice"}
                ]
            },
            {
                "name": "-------| Orga Event |-------",
                "channels": [
                    {"name": "information", "emoji": "📄", "type": "text"},
                    {"name": "annonce", "emoji": "🔔", "type": "text"},
                    {"name": "compte-rendu-réunion", "emoji": "📝", "type": "text"},
                    {"name": "absence", "emoji": "✍️", "type": "text"},
                    {"name": "tchat", "emoji": "💬", "type": "text"},
                    {"name": "Réunion", "emoji": None, "type": "voice"}
                ]
            },
            {
                "name": "-------| Animation |-------",
                "channels": [
                    {"name": "annonce", "emoji": "🔔", "type": "text"},
                    {"name": "planning-animation", "emoji": "🎮", "type": "text"},
                    {"name": "compte-rendu-réunion", "emoji": "📝", "type": "text"},
                    {"name": "absence", "emoji": "✍️", "type": "text"},
                    {"name": "tchat", "emoji": "💬", "type": "text"},
                    {"name": "Réunion", "emoji": None, "type": "voice"}
                ]
            },
            {
                "name": "--------| Stream |---------",
                "channels": [
                    {"name": "annonce", "emoji": "🔔", "type": "text"},
                    {"name": "planning-live", "emoji": "🎥", "type": "text"},
                    {"name": "compte-rendu-réunion", "emoji": "📝", "type": "text"},
                    {"name": "absence", "emoji": "✍️", "type": "text"},
                    {"name": "tchat", "emoji": "💬", "type": "text"},
                    {"name": "Réunion", "emoji": None, "type": "voice"}
                ]
            },
            {
                "name": "-------| Communication |-------",
                "channels": [
                    {"name": "annonce", "emoji": "🔔", "type": "text"},
                    {"name": "absence", "emoji": "✍️", "type": "text"},
                    {"name": "compte-rendu-réunion", "emoji": "📝", "type": "text"},
                    {"name": "tchat", "emoji": "💬", "type": "text"},
                    {"name": "Réunion", "emoji": None, "type": "voice"}
                ]
            },
            {
                "name": "----------| Design |---------",
                "channels": [
                    {"name": "annonce", "emoji": "🔔", "type": "text"},
                    {"name": "compte-rendu-réunion", "emoji": "📝", "type": "text"},
                    {"name": "planning-stream", "emoji": "🎥", "type": "text"},
                    {"name": "planning-animation", "emoji": "🎮", "type": "text"},
                    {"name": "montage", "emoji": "🎬", "type": "text"},
                    {"name": "création", "emoji": "🎨", "type": "text"},
                    {"name": "absence", "emoji": "✍️", "type": "text"},
                    {"name": "tchat", "emoji": "💬", "type": "text"},
                    {"name": "Réunion", "emoji": None, "type": "voice"}
                ]
            },
            {
                "name": "-------| Maintenance |-------",
                "channels": [
                    {"name": "annonce", "emoji": "🔔", "type": "text"},
                    {"name": "compte-rendu-réunion", "emoji": "📝", "type": "text"},
                    {"name": "absence", "emoji": "✍️", "type": "text"},
                    {"name": "tchat", "emoji": "💬", "type": "text"},
                    {"name": "test-bot", "emoji": None, "type": "text"},
                    {"name": "Réunion", "emoji": None, "type": "voice"}
                ]
            },
            {
                "name": "-------| Modération |-------",
                "channels": [
                    {"name": "annonce", "emoji": "🔔", "type": "text"},
                    {"name": "compte-rendu-réunion", "emoji": "📝", "type": "text"},
                    {"name": "absence", "emoji": "✍️", "type": "text"},
                    {"name": "tchat", "emoji": "💬", "type": "text"},
                    {"name": "Réunion", "emoji": None, "type": "voice"}
                ]
            },
            {
                "name": "-------| eSport |-------",
                "channels": [
                    {"name": "annonce", "emoji": "🔔", "type": "text"},
                    {"name": "discussion", "emoji": "💬", "type": "text"},
                    {"name": "Voc 1", "emoji": None, "type": "voice"},
                    {"name": "Voc 2", "emoji": None, "type": "voice"},
                    {"name": "Voc 3", "emoji": None, "type": "voice"}
                ]
            },
            {
                "name": "-------| HeadStaff |-------",
                "channels": [
                    {"name": "objectif", "emoji": "📈", "type": "text"},
                    {"name": "information", "emoji": "📄", "type": "text"},
                    {"name": "compte-rendu-réunion", "emoji": "📝", "type": "text"},
                    {"name": "annonce", "emoji": "🔔", "type": "text"},
                    {"name": "discussion", "emoji": "💬", "type": "text"},
                    {"name": "login", "emoji": None, "type": "text"},
                    {"name": "a-faire", "emoji": None, "type": "text"},
                    {"name": "first-clutch", "emoji": None, "type": "text"},
                    {"name": "Réunion", "emoji": None, "type": "voice"}
                ]
            }
        ]

    @commands.command()
    @commands.admin_or_permissions(administrator=True)
    async def createserver(self, ctx):
        """Crée automatiquement les salons pour le serveur T2C Staff"""
        
        # Vérifier si la commande est exécutée dans le serveur cible
        if ctx.guild.id != self.target_server_id:
            await ctx.send(f"❌ Cette commande ne peut être utilisée que sur le serveur avec ID {self.target_server_id}.")
            return
        
        # Message de confirmation avant de procéder
        message = await ctx.send("⚠️ Cette commande va créer toutes les catégories et salons pour le serveur T2C Staff. Continuer? (oui/non)")
        
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel and m.content.lower() in ["oui", "non"]
            
        try:
            # Attendre la confirmation
            response = await self.bot.wait_for('message', check=check, timeout=30.0)
            
            if response.content.lower() == "non":
                await ctx.send("❌ Opération annulée.")
                return
                
            # Commencer la création
            status_message = await ctx.send("🔄 Création en cours...")
            
            # Créer les catégories et les salons
            for category_data in self.categories:
                # Créer la catégorie
                category_name = category_data["name"]
                
                # Vérifier si la catégorie existe déjà
                existing_category = discord.utils.get(ctx.guild.categories, name=category_name)
                if existing_category:
                    category = existing_category
                    await status_message.edit(content=f"ℹ️ Catégorie `{category_name}` existe déjà, utilisation de celle-ci.")
                else:
                    category = await ctx.guild.create_category(category_name)
                    await status_message.edit(content=f"✅ Catégorie `{category_name}` créée avec succès.")
                
                # Attendre un peu pour éviter les rate limits
                await asyncio.sleep(0.5)
                
                # Créer les salons dans cette catégorie
                for channel_data in category_data["channels"]:
                    channel_name = channel_data["name"]
                    channel_emoji = channel_data["emoji"]
                    channel_type = channel_data["type"]
                    
                    # Formater le nom du salon avec l'emoji si présent
                    formatted_name = f"{channel_emoji} • {channel_name}" if channel_emoji else channel_name
                    
                    # Vérifier si le salon existe déjà dans cette catégorie
                    if channel_type == "text":
                        existing_channel = discord.utils.get(category.text_channels, name=formatted_name.lower().replace(" ", "-"))
                        if existing_channel:
                            await status_message.edit(content=f"ℹ️ Salon texte `{formatted_name}` existe déjà, ignoré.")
                            continue
                            
                        # Créer le salon texte
                        await ctx.guild.create_text_channel(name=formatted_name, category=category)
                        await status_message.edit(content=f"✅ Salon texte `{formatted_name}` créé avec succès.")
                    
                    elif channel_type == "voice":
                        existing_channel = discord.utils.get(category.voice_channels, name=channel_name)
                        if existing_channel:
                            await status_message.edit(content=f"ℹ️ Salon vocal `{channel_name}` existe déjà, ignoré.")
                            continue
                            
                        # Créer le salon vocal
                        await ctx.guild.create_voice_channel(name=channel_name, category=category)
                        await status_message.edit(content=f"✅ Salon vocal `{channel_name}` créé avec succès.")
                    
                    # Attendre un peu pour éviter les rate limits
                    await asyncio.sleep(0.5)
            
            # Message final de confirmation
            await ctx.send("✅ Configuration terminée! Tous les salons ont été créés avec succès.")
            
        except asyncio.TimeoutError:
            await ctx.send("❌ Temps écoulé. Opération annulée.")
        except discord.Forbidden:
            await ctx.send("❌ Je n'ai pas les permissions nécessaires pour créer des salons.")
        except Exception as e:
            await ctx.send(f"❌ Une erreur s'est produite: {str(e)}")

    @commands.command()
    @commands.admin_or_permissions(administrator=True)
    async def deleteallchannels(self, ctx):
        """Supprime tous les salons du serveur T2C Staff (ATTENTION: DANGEREUX)"""
        
        # Vérifier si la commande est exécutée dans le serveur cible
        if ctx.guild.id != self.target_server_id:
            await ctx.send(f"❌ Cette commande ne peut être utilisée que sur le serveur avec ID {self.target_server_id}.")
            return
        
        # Message d'avertissement sérieux
        await ctx.send("⚠️ **ATTENTION**: Cette commande va **SUPPRIMER TOUS LES SALONS** du serveur! Cette action est **IRRÉVERSIBLE**.")
        await ctx.send("⚠️ Pour confirmer, veuillez taper `JE CONFIRME LA SUPPRESSION DE TOUS LES SALONS`")
        
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel and m.content == "JE CONFIRME LA SUPPRESSION DE TOUS LES SALONS"
            
        try:
            # Attendre la confirmation
            await self.bot.wait_for('message', check=check, timeout=30.0)
            
            # Commencer la suppression
            status_message = await ctx.send("🔄 Suppression en cours...")
            
            # Supprimer tous les salons textuels
            for channel in ctx.guild.text_channels:
                if channel != ctx.channel:  # Ne pas supprimer le salon où la commande est exécutée
                    await channel.delete()
                    await asyncio.sleep(0.5)  # Attendre pour éviter les rate limits
            
            # Supprimer tous les salons vocaux
            for channel in ctx.guild.voice_channels:
                await channel.delete()
                await asyncio.sleep(0.5)  # Attendre pour éviter les rate limits
            
            # Supprimer toutes les catégories
            for category in ctx.guild.categories:
                await category.delete()
                await asyncio.sleep(0.5)  # Attendre pour éviter les rate limits
            
            await ctx.send("✅ Tous les salons ont été supprimés. Utilisez `!createserver` pour recréer les salons.")
            
        except asyncio.TimeoutError:
            await ctx.send("❌ Temps écoulé. Opération annulée.")
        except discord.Forbidden:
            await ctx.send("❌ Je n'ai pas les permissions nécessaires pour supprimer des salons.")
        except Exception as e:
            await ctx.send(f"❌ Une erreur s'est produite: {str(e)}")

async def setup(bot):
    await bot.add_cog(ServerChannels(bot))
