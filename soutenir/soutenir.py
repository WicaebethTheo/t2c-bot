import discord
from redbot.core import commands, checks, Config
import asyncio
from discord.ui import View, Button

class WebsiteButton(Button):
    def __init__(self):
        super().__init__(
            style=discord.ButtonStyle.link,
            url="https://wicaebeth.com/lafinequipe/",
            label="🌐 Visiter notre site web",
            row=1
        )

class SupportView(View):
    def __init__(self):
        super().__init__(timeout=None)  # Le bouton reste actif indéfiniment
        self.add_item(WebsiteButton())

class Soutenir(commands.Cog):
    """Système de support du serveur"""

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=1234567890)
        
        # IDs des salons
        self.SUPPORT_CHANNEL = 1352736665432625182
        
    def has_required_role():
        async def predicate(ctx):
            # ID de Wicaebeth
            wicaebeth_id = 257152912776495104
            # Si c'est Wicaebeth, autoriser
            if ctx.author.id == wicaebeth_id:
                return True
            
            # Sinon vérifier le rôle
            required_role_id = 974387257630933083
            role = ctx.guild.get_role(required_role_id)
            if not role:
                raise commands.CheckFailure("Le rôle requis n'existe pas sur ce serveur.")
            if role not in ctx.author.roles:
                raise commands.CheckFailure("Tu n'as pas le rôle requis pour utiliser cette commande.")
            return True
        return commands.check(predicate)

    @commands.command()
    @has_required_role()
    async def createsupport(self, ctx):
        """Crée le message de support dans le salon dédié"""
        support_channel = self.bot.get_channel(self.SUPPORT_CHANNEL)
        if not support_channel:
            await ctx.send("❌ Le salon de support n'a pas été trouvé.")
            return

        # Supprimer les messages existants dans le salon
        try:
            await support_channel.purge(limit=None)
        except discord.Forbidden:
            await ctx.send("❌ Je n'ai pas la permission de supprimer les messages dans le salon de support.")
            return

        # Créer l'embed principal
        embed = discord.Embed(
            title="💫 Comment soutenir le serveur ?",
            description="```md\n# Contribuez au développement de notre communauté !\n```\n"
                       "Bonjour à tous,\n"
                       "Si vous appréciez notre serveur et souhaitez nous aider à le faire évoluer, "
                       "voici plusieurs façons d'apporter votre soutien :",
            color=0x2b2d31  # Couleur Discord moderne
        )

        # Ajouter les sections
        embed.add_field(
            name="╭・📣 Inviter de nouveaux membres",
            value="> Le meilleur moyen d'agrandir et dynamiser la communauté\n"
                  "> est tout simplement d'en parler autour de vous !\n"
                  "> \n"
                  "> Partagez le lien du serveur avec vos amis, votre équipe\n"
                  "> de jeu ou toute personne susceptible d'être intéressée.",
            inline=False
        )

        embed.add_field(
            name="┊・🚀 Booster le serveur",
            value="> Les boosts Discord nous permettent d'accéder à des\n"
                  "> fonctionnalités améliorées :\n"
                  "> • Meilleure qualité audio\n"
                  "> • Davantage d'emojis\n"
                  "> • Des salons exclusifs\n"
                  "> • Et bien plus encore !\n"
                  "> \n"
                  "> Si vous avez un boost disponible, il sera grandement apprécié.",
            inline=False
        )

        embed.add_field(
            name="╰・💎 Soutien financier",
            value="> Pour ceux qui souhaitent aller plus loin, il est possible\n"
                  "> d'aider financièrement via des dons.\n"
                  "> \n"
                  "> Cela nous permet de :\n"
                  "> • Maintenir et améliorer le serveur\n"
                  "> • Organiser des événements\n"
                  "> • Ajouter des fonctionnalités supplémentaires\n"
                  "> \n"
                  "> Si vous êtes intéressé, contactez <@Wika> pour plus de détails.",
            inline=False
        )

        # Ajouter le footer avec une ligne de séparation
        embed.add_field(
            name="",
            value="```md\n# Merci pour votre soutien !\n```",
            inline=False
        )
        embed.set_footer(text="Chaque contribution aide à faire grandir notre communauté et à offrir un espace toujours plus agréable pour tout le monde.")

        # Envoyer l'embed avec le bouton
        view = SupportView()
        await support_channel.send(embed=embed, view=view)
        
        # Confirmer l'envoi
        await ctx.send("✅ Message de support créé avec succès !")

    @createsupport.error
    async def createsupport_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            error_msg = await ctx.send("❌ Tu n'as pas le rôle requis pour utiliser cette commande.")
            await asyncio.sleep(5)
            try:
                await error_msg.delete()
            except (discord.Forbidden, discord.NotFound):
                pass

async def setup(bot):
    """Fonction de configuration requise par Red-Bot"""
    cog = Soutenir(bot)
    await bot.add_cog(cog)
    return cog
