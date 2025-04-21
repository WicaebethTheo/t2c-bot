import discord
from redbot.core import commands, Config
import asyncio

class Publication(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=1234567890)
        self.config.register_global(
            publication_in_progress={}
        )
        self.authorized_id = 257152912776495104  # Votre ID

    @commands.command()
    async def publication(self, ctx):
        """Lance le processus de création d'une publication"""
        # Vérifier si l'utilisateur est autorisé
        if ctx.author.id != self.authorized_id:
            error_msg = await ctx.send("❌ Vous n'êtes pas autorisé à utiliser cette commande.")
            await asyncio.sleep(5)
            try:
                await error_msg.delete()
            except:
                pass
            return

        await ctx.send("Pour créer une publication, utilisez la commande suivante:\n`!pubchan [ID du salon]`\nPar exemple: `!pubchan 123456789012345678`")

    @commands.command()
    async def pubchan(self, ctx, channel_id: int):
        """Spécifie le salon pour la publication"""
        # Vérifier si l'utilisateur est autorisé
        if ctx.author.id != self.authorized_id:
            error_msg = await ctx.send("❌ Vous n'êtes pas autorisé à utiliser cette commande.")
            await asyncio.sleep(5)
            try:
                await error_msg.delete()
            except:
                pass
            return

        # Vérifier si le salon existe
        channel = ctx.guild.get_channel(channel_id)
        if not channel:
            await ctx.send(f"❌ Salon non trouvé avec l'ID {channel_id}.")
            return

        # Enregistrer les informations de la publication en cours
        await self.config.publication_in_progress.set({
            "author_id": ctx.author.id,
            "channel_id": channel_id,
            "guild_id": ctx.guild.id
        })

        await ctx.send(f"✅ Salon sélectionné : {channel.mention}\nUtilisez maintenant `!pubtitle [Votre titre]` pour définir le titre de votre annonce.")

    @commands.command()
    async def pubtitle(self, ctx, *, title: str):
        """Définit le titre de la publication"""
        # Vérifier si l'utilisateur est autorisé
        if ctx.author.id != self.authorized_id:
            error_msg = await ctx.send("❌ Vous n'êtes pas autorisé à utiliser cette commande.")
            await asyncio.sleep(5)
            try:
                await error_msg.delete()
            except:
                pass
            return

        # Vérifier si une publication est en cours
        pub_data = await self.config.publication_in_progress()
        if not pub_data or pub_data.get("author_id") != ctx.author.id:
            await ctx.send("❌ Aucune publication en cours. Utilisez d'abord `!pubchan [ID du salon]`.")
            return

        # Mettre à jour les données
        pub_data["title"] = title
        await self.config.publication_in_progress.set(pub_data)

        await ctx.send(f"✅ Titre défini : **{title}**\nUtilisez maintenant `!pubcontent [Votre contenu]` pour définir le contenu de votre annonce.")

    @commands.command()
    async def pubcontent(self, ctx, *, content: str):
        """Définit le contenu de la publication"""
        # Vérifier si l'utilisateur est autorisé
        if ctx.author.id != self.authorized_id:
            error_msg = await ctx.send("❌ Vous n'êtes pas autorisé à utiliser cette commande.")
            await asyncio.sleep(5)
            try:
                await error_msg.delete()
            except:
                pass
            return

        # Vérifier si une publication est en cours
        pub_data = await self.config.publication_in_progress()
        if not pub_data or pub_data.get("author_id") != ctx.author.id:
            await ctx.send("❌ Aucune publication en cours. Utilisez d'abord `!pubchan [ID du salon]` puis `!pubtitle [Votre titre]`.")
            return

        if "title" not in pub_data:
            await ctx.send("❌ Vous devez d'abord définir un titre avec `!pubtitle [Votre titre]`.")
            return

        # Mettre à jour les données
        pub_data["content"] = content
        await self.config.publication_in_progress.set(pub_data)

        # Créer un aperçu
        embed = discord.Embed(
            title=pub_data["title"],
            description=content,
            color=0x2b2d31
        )
        embed.set_footer(text=f"Annonce préparée par {ctx.author.name}", 
                      icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
        embed.timestamp = discord.utils.utcnow()

        preview_msg = await ctx.send("📝 **Aperçu de votre annonce :**", embed=embed)
        await ctx.send("Pour publier cette annonce, utilisez `!pubsend`. Pour annuler, utilisez `!pubcancel`.")

    @commands.command()
    async def pubsend(self, ctx):
        """Envoie la publication dans le salon spécifié"""
        # Vérifier si l'utilisateur est autorisé
        if ctx.author.id != self.authorized_id:
            error_msg = await ctx.send("❌ Vous n'êtes pas autorisé à utiliser cette commande.")
            await asyncio.sleep(5)
            try:
                await error_msg.delete()
            except:
                pass
            return

        # Vérifier si une publication est prête
        pub_data = await self.config.publication_in_progress()
        if not pub_data or pub_data.get("author_id") != ctx.author.id:
            await ctx.send("❌ Aucune publication en cours.")
            return

        if "title" not in pub_data or "content" not in pub_data:
            await ctx.send("❌ La publication n'est pas complète. Vous devez définir un titre et un contenu.")
            return

        # Récupérer le salon
        guild = self.bot.get_guild(pub_data["guild_id"])
        if not guild:
            await ctx.send("❌ Impossible de trouver le serveur.")
            await self.config.publication_in_progress.clear()
            return

        channel = guild.get_channel(pub_data["channel_id"])
        if not channel:
            await ctx.send("❌ Impossible de trouver le salon spécifié.")
            await self.config.publication_in_progress.clear()
            return

        # Créer et envoyer l'embed
        embed = discord.Embed(
            title=pub_data["title"],
            description=pub_data["content"],
            color=0x2b2d31
        )
        embed.set_footer(text=f"Annonce publiée par {ctx.author.name}", 
                      icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
        embed.timestamp = discord.utils.utcnow()

        try:
            await channel.send(embed=embed)
            await ctx.send(f"✅ L'annonce a été publiée avec succès dans {channel.mention} !")
        except discord.Forbidden:
            await ctx.send("❌ Je n'ai pas la permission d'envoyer des messages dans ce salon.")
        except Exception as e:
            await ctx.send(f"❌ Une erreur s'est produite : {str(e)}")

        # Réinitialiser les données
        await self.config.publication_in_progress.clear()

    @commands.command()
    async def pubcancel(self, ctx):
        """Annule la publication en cours"""
        # Vérifier si l'utilisateur est autorisé
        if ctx.author.id != self.authorized_id:
            error_msg = await ctx.send("❌ Vous n'êtes pas autorisé à utiliser cette commande.")
            await asyncio.sleep(5)
            try:
                await error_msg.delete()
            except:
                pass
            return

        # Vérifier si une publication est en cours
        pub_data = await self.config.publication_in_progress()
        if not pub_data or pub_data.get("author_id") != ctx.author.id:
            await ctx.send("❌ Aucune publication en cours à annuler.")
            return

        # Réinitialiser les données
        await self.config.publication_in_progress.clear()
        await ctx.send("✅ La publication a été annulée.")

    @commands.command()
    async def publist(self, ctx):
        """Affiche la liste des salons disponibles"""
        # Vérifier si l'utilisateur est autorisé
        if ctx.author.id != self.authorized_id:
            error_msg = await ctx.send("❌ Vous n'êtes pas autorisé à utiliser cette commande.")
            await asyncio.sleep(5)
            try:
                await error_msg.delete()
            except:
                pass
            return

        # Récupérer tous les salons textuels du serveur
        channels = ctx.guild.text_channels
        
        if not channels:
            await ctx.send("❌ Aucun salon textuel trouvé sur ce serveur.")
            return
        
        # Créer et envoyer la liste des salons
        embed = discord.Embed(
            title="Liste des salons disponibles",
            description="Utilisez l'ID d'un salon avec la commande `!pubchan [ID]`",
            color=0x2b2d31
        )
        
        for channel in channels:
            embed.add_field(
                name=channel.name, 
                value=f"ID: {channel.id}", 
                inline=False
            )
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Publication(bot))
