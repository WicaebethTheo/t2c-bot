from redbot.core import commands
import discord
from discord.ui import Button, View
import asyncio

class AcceptButton(Button):
    def __init__(self):
        super().__init__(
            label="Accepter le règlement",
            style=discord.ButtonStyle.green,
            custom_id="accept_rules"
        )

    async def callback(self, interaction: discord.Interaction):
        role_id = 1352971285725970503
        role = interaction.guild.get_role(role_id)
        
        if role is None:
            await interaction.response.send_message("❌ Erreur: Le rôle n'a pas été trouvé.", ephemeral=True)
            return
            
        if role in interaction.user.roles:
            await interaction.response.send_message("✅ Tu as déjà accepté le règlement !", ephemeral=True)
            return
            
        await interaction.user.add_roles(role)
        await interaction.response.send_message("✅ Tu as accepté le règlement ! Tu as maintenant accès aux salons.", ephemeral=True)

class RulesPP(commands.Cog):
    """Cog pour gérer le règlement des parties personnalisées"""
    
    def __init__(self, bot):
        self.bot = bot
        self.RULES_CHANNEL = 1352768727971791101

    async def cog_load(self):
        """Called when the cog is loaded"""
        pass

    @staticmethod
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
    async def rulespp(self, ctx):
        """Crée le message de règlement des parties personnalisées"""
        # Supprimer la commande
        try:
            await ctx.message.delete()
        except (discord.Forbidden, discord.NotFound):
            pass

        channel = self.bot.get_channel(self.RULES_CHANNEL)
        if not channel:
            await ctx.send("❌ Le salon de règlement n'a pas été trouvé.")
            return

        # Nettoyer le salon en supprimant tous les messages
        await ctx.send("🧹 Nettoyage du salon de règlement en cours...")
        try:
            # Supprimer tous les messages du salon
            await channel.purge(limit=100)
            await ctx.send("✅ Salon nettoyé avec succès.")
        except discord.Forbidden:
            await ctx.send("❌ Je n'ai pas la permission de supprimer des messages dans ce salon.")
            return
        except Exception as e:
            await ctx.send(f"❌ Une erreur s'est produite lors du nettoyage du salon : {str(e)}")
            return

        # Créer l'embed
        embed = discord.Embed(
            title="📜 Règlement des Parties Personnalisées",
            color=0x2F3136
        )

        # Préparation
        embed.add_field(
            name="⚡ Préparation",
            value=(
                "• Le staff gère le lancement, ne pas déranger et passer en spectateur.\n"
                "• Équipes faites à la main : indiquez votre peak elo dans le chat.\n"
                "• Map tirée au sort (6 refus minimum pour relancer la roulette une fois de plus) ou choisie si tout le monde est d'accord.\n"
                "• Validez le règlement pour accéder aux salons."
            ),
            inline=False
        )

        # Durant la partie
        embed.add_field(
            name="🎮 En jeu",
            value=(
                "**Limites d'armes par équipe :**\n"
                "• 1 Odin, 1 Judge, 1 Operator (ult Chamber exclu)\n\n"
                "• Chat vocal autorisé avant chaque manche (sans abus).\n"
                "• Instalock interdit.\n"
                "• Pas de trashtalk / comportements toxiques.\n"
                "• Smurf interdit (ne mentez pas sur votre rang).\n"
                "• Absence non justifiée = sanction."
            ),
            inline=False
        )

        # Objectif
        embed.add_field(
            name="🎯 Objectif",
            value=(
                "Le but des parties personnalisées est que les joueurs de tous niveaux, du bas elo au haut elo, puissent s'amuser.\n"
                "Toute attitude négative envers un autre joueur sera sanctionnée."
            ),
            inline=False
        )

        # Créer la vue avec le bouton
        view = View(timeout=None)
        view.add_item(AcceptButton())

        # Envoyer l'embed avec le bouton
        await channel.send(embed=embed, view=view)
        await ctx.send("✅ Message de règlement créé avec succès !")

    @rulespp.error
    async def rulespp_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            error_msg = await ctx.send("❌ Tu n'as pas le rôle requis pour utiliser cette commande.")
            await asyncio.sleep(5)
            try:
                await error_msg.delete()
            except (discord.Forbidden, discord.NotFound):
                pass

async def setup(bot):
    await bot.add_cog(RulesPP(bot))
