import discord
from redbot.core import commands, checks, Config
import asyncio

class RankMenu(discord.ui.Select):
    def __init__(self, ranks):
        self.ranks = ranks
        options = []
        for rank in ranks:
            options.append(discord.SelectOption(
                label=rank["name"],
                value=str(rank["id"])
            ))
        
        super().__init__(
            placeholder="Sélectionnez votre rang",
            min_values=1,
            max_values=1,
            options=options,
            custom_id="rank_select"
        )

    async def callback(self, interaction: discord.Interaction):
        # Récupérer le rôle sélectionné
        selected_role_id = int(self.values[0])
        member = interaction.user
        
        # Liste des IDs de tous les rôles de rang
        rank_role_ids = [rank["id"] for rank in self.ranks]
        
        # Retirer tous les rôles de rang existants
        roles_to_remove = []
        for role_id in rank_role_ids:
            role = interaction.guild.get_role(role_id)
            if role and role in member.roles:
                roles_to_remove.append(role)
        if roles_to_remove:
            await member.remove_roles(*roles_to_remove)
        
        # Ajouter le nouveau rôle
        new_role = interaction.guild.get_role(selected_role_id)
        if new_role:
            await member.add_roles(new_role)
            await interaction.response.send_message(f"Votre rang a été mis à jour : {new_role.name}", ephemeral=True)
        else:
            await interaction.response.send_message("Une erreur s'est produite.", ephemeral=True)

class RankView(discord.ui.View):
    def __init__(self, ranks):
        super().__init__(timeout=None)
        self.add_item(RankMenu(ranks))

class Ranks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=1234567890)
        self.roles_channel_id = 1352736659799670884
        
        default_guild = {
            "ranks": [
                {"name": "Fer", "id": 1352739476006502440, "emoji": "<:rankiron:1353094973557309521>"},
                {"name": "Bronze", "id": 1352739471770255483, "emoji": "<:rankbronze:1353095944282837124>"},
                {"name": "Argent", "id": 1352739467164647525, "emoji": "<:ranksilver:1353095904869089373>"},
                {"name": "Or", "id": 1352739462920142879, "emoji": "<:rankgold:1353094971795968092>"},
                {"name": "Platine", "id": 1352739458516127866, "emoji": "<:rankplatine:1353094968117563623>"},
                {"name": "Diamant", "id": 1352739454758158356, "emoji": "<:rankdiamond:1353095038476877988>"},
                {"name": "Ascendant", "id": 1352739450605535232, "emoji": "<:rankascendant:1353094963725996102>"},
                {"name": "Immortel", "id": 1352739446327345235, "emoji": "<:rankimmortal:1353095978680324271>"}
            ]
        }
        self.config.register_guild(**default_guild)

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
    async def setuproles(self, ctx):
        """Configure les messages de rôles dans le salon dédié"""
        # Vérifier le salon
        channel = self.bot.get_channel(self.roles_channel_id)
        if not channel:
            await ctx.send(f"Erreur: Le salon avec l'ID {self.roles_channel_id} n'a pas été trouvé.")
            return

        # Nettoyer le salon en supprimant les messages existants
        await ctx.send("Nettoyage du salon en cours...")
        try:
            # Supprimer les messages existants (limité à 100 messages)
            await channel.purge(limit=100)
            await ctx.send("✅ Salon nettoyé avec succès.")
        except discord.Forbidden:
            await ctx.send("❌ Je n'ai pas la permission de supprimer des messages dans ce salon.")
            return
        except Exception as e:
            await ctx.send(f"❌ Une erreur s'est produite lors du nettoyage : {str(e)}")
            return

        # Récupérer les données
        guild_data = await self.config.guild(ctx.guild).all()

        # Créer l'embed
        embed = discord.Embed(
            title="Rank",
            description="**Voici la liste des différents rôles :**\n\n",
            color=0x2b2d31
        )

        # Ajouter les rangs à l'embed
        for rank in guild_data["ranks"]:
            role = ctx.guild.get_role(rank["id"])
            if role:
                embed.description += f"{rank['emoji']} ➜ {role.mention}\n"

        # Créer le bouton "Choisir les rôles"
        class RoleButton(discord.ui.Button):
            def __init__(self):
                super().__init__(
                    style=discord.ButtonStyle.secondary,
                    label="Choisir les rôles",
                    custom_id="choose_roles"
                )

            async def callback(self, interaction: discord.Interaction):
                view = RankView(guild_data["ranks"])
                await interaction.response.send_message(
                    "Sélectionnez votre rang :",
                    view=view,
                    ephemeral=True
                )

        # Créer la vue avec le bouton
        view = discord.ui.View(timeout=None)
        view.add_item(RoleButton())

        # Envoyer le message
        await channel.send(embed=embed, view=view)
        await ctx.send("Configuration des rôles terminée !")

    @setuproles.error
    async def setuproles_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            error_msg = await ctx.send("❌ Tu n'as pas le rôle requis pour utiliser cette commande.")
            await asyncio.sleep(5)
            try:
                await error_msg.delete()
            except (discord.Forbidden, discord.NotFound):
                pass

async def setup(bot):
    await bot.add_cog(Ranks(bot))
