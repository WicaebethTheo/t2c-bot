import discord
from redbot.core import commands
import asyncio

class Construction(commands.Cog):
    """Affiche une page "En construction" élégante."""

    def __init__(self, bot):
        self.bot = bot

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

    @commands.command(name="construction")
    @has_required_role()
    async def construction(self, ctx, *, message="Cette section est en cours de construction."):
        """
        Affiche un message "En construction" élégant.
        
        Le message par défaut peut être remplacé en ajoutant du texte après la commande.
        Exemple: !construction Le salon des événements sera disponible bientôt!
        """
        # Supprimer le message de commande
        try:
            await ctx.message.delete()
        except (discord.Forbidden, discord.HTTPException):
            # Si le bot n'a pas la permission de supprimer ou autre erreur, continuez quand même
            pass
        
        # Créer l'embed pour la page en construction
        embed = discord.Embed(
            title="🚧 En construction 🚧",
            description=message,
            color=discord.Color.gold()
        )
        
        # Ajouter des détails à l'embed
        embed.add_field(
            name="Statut",
            value="⚙️ Travaux en cours",
            inline=True
        )
        embed.add_field(
            name="Revenir plus tard",
            value="Merci de votre patience!",
            inline=True
        )
        
        # Image de construction (image qui fonctionne bien sur Discord)
        construction_image = "https://media.istockphoto.com/id/1182622704/fr/vectoriel/signe-davertissement-de-travaux-en-cours-isol%C3%A9-sur-fond-transparent-concept-en.jpg?s=612x612&w=0&k=20&c=Q6KwGJL2FwUl6Fk-SvG00DXm2I8gHO3AFMnTRFB_QR0="
        embed.set_image(url=construction_image)
        
        # Ajouter un footer avec le nom de l'utilisateur qui a lancé la commande
        embed.set_footer(text=f"Message placé par {ctx.author.name}", icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
        
        # Envoyer l'embed
        await ctx.send(embed=embed)
        
    @commands.command(name="construction2")
    @has_required_role()
    async def construction2(self, ctx, *, message="Cette section est en cours de construction."):
        """
        Affiche un message "En construction" avec une animation de progression.
        
        Le message par défaut peut être remplacé en ajoutant du texte après la commande.
        Exemple: !construction2 Le salon des événements sera bientôt prêt!
        """
        # Supprimer le message de commande
        try:
            await ctx.message.delete()
        except (discord.Forbidden, discord.HTTPException):
            # Si le bot n'a pas la permission de supprimer ou autre erreur, continuez quand même
            pass
        
        # Créer l'embed initial
        embed = discord.Embed(
            title="🚧 En construction 🚧",
            description=message,
            color=discord.Color.gold()
        )
        
        # Séquence d'animation pour la barre de progression
        progress_bars = [
            "⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜ 0%",
            "🟨⬜⬜⬜⬜⬜⬜⬜⬜⬜ 10%",
            "🟨🟨⬜⬜⬜⬜⬜⬜⬜⬜ 20%",
            "🟨🟨🟨⬜⬜⬜⬜⬜⬜⬜ 30%",
            "🟨🟨🟨🟨⬜⬜⬜⬜⬜⬜ 40%",
            "🟨🟨🟨🟨🟨⬜⬜⬜⬜⬜ 50%",
            "🟨🟨🟨🟨🟨🟨⬜⬜⬜⬜ 60%",
            "🟨🟨🟨🟨🟨🟨🟨⬜⬜⬜ 70%",
            "🟨🟨🟨🟨🟨🟨🟨🟨⬜⬜ 80%",
            "🟨🟨🟨🟨🟨🟨🟨🟨🟨⬜ 90%",
            "🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨 100%",
            "🚧 Construction en cours... 🚧"
        ]
        
        embed.add_field(
            name="Progression",
            value=progress_bars[0],
            inline=False
        )
        
        # Ajouter un footer avec le nom de l'utilisateur qui a lancé la commande
        embed.set_footer(text=f"Message placé par {ctx.author.name}", icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
        
        # Envoyer l'embed initial
        message_obj = await ctx.send(embed=embed)
        
        # Animer la barre de progression
        for i in range(1, len(progress_bars)):
            embed.set_field_at(
                0,
                name="Progression",
                value=progress_bars[i],
                inline=False
            )
            
            await message_obj.edit(embed=embed)
            await asyncio.sleep(0.7)  # Délai entre les animations
            
        # Embed final avec message de conclusion
        final_embed = discord.Embed(
            title="🚧 En construction 🚧",
            description=message,
            color=discord.Color.gold()
        )
        
        final_embed.add_field(
            name="Statut",
            value="⚙️ Travaux en cours",
            inline=True
        )
        final_embed.add_field(
            name="Revenir plus tard",
            value="Merci de votre patience!",
            inline=True
        )
        
        # Image de construction fiable
        construction_image = "https://media.istockphoto.com/id/1182622704/fr/vectoriel/signe-davertissement-de-travaux-en-cours-isol%C3%A9-sur-fond-transparent-concept-en.jpg?s=612x612&w=0&k=20&c=Q6KwGJL2FwUl6Fk-SvG00DXm2I8gHO3AFMnTRFB_QR0="
        final_embed.set_image(url=construction_image)
        
        # Ajouter un footer avec le nom de l'utilisateur qui a lancé la commande
        final_embed.set_footer(text=f"Message placé par {ctx.author.name}", icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
        
        # Mise à jour du message avec l'embed final
        await message_obj.edit(embed=final_embed)
        
    @commands.command(name="construction3")
    @has_required_role()
    async def construction3(self, ctx, *, message="Cette section est en cours de construction."):
        """
        Affiche un message "En construction" plus détaillé avec des informations de projet.
        
        Le message par défaut peut être remplacé en ajoutant du texte après la commande.
        """
        # Supprimer le message de commande
        try:
            await ctx.message.delete()
        except (discord.Forbidden, discord.HTTPException):
            # Si le bot n'a pas la permission de supprimer ou autre erreur, continuez quand même
            pass
        
        # Créer l'embed pour la page en construction
        embed = discord.Embed(
            title="🚧 Projet en développement 🚧",
            description=message,
            color=discord.Color.orange()
        )
        
        # Ajouter des détails à l'embed
        embed.add_field(
            name="📅 Date de début",
            value=f"{discord.utils.format_dt(discord.utils.utcnow(), style='D')}",
            inline=True
        )
        embed.add_field(
            name="⏰ Estimation",
            value="Bientôt disponible",
            inline=True
        )
        
        embed.add_field(
            name="📊 Avancement",
            value="`■■■□□□□□□□` 30%",
            inline=False
        )
        
        embed.add_field(
            name="🧰 Tâches en cours",
            value="• Configuration des systèmes\n• Mise en place des fonctionnalités\n• Tests et optimisations",
            inline=False
        )
        
        # Image de construction fiable
        construction_image = "https://media.istockphoto.com/id/1182622704/fr/vectoriel/signe-davertissement-de-travaux-en-cours-isol%C3%A9-sur-fond-transparent-concept-en.jpg?s=612x612&w=0&k=20&c=Q6KwGJL2FwUl6Fk-SvG00DXm2I8gHO3AFMnTRFB_QR0="
        embed.set_thumbnail(url=construction_image)
        
        # Ajouter un footer avec le nom de l'utilisateur qui a lancé la commande
        embed.set_footer(text=f"Projet initié par {ctx.author.name}", icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
        
        # Envoyer l'embed
        await ctx.send(embed=embed)

    @construction.error
    async def construction_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            error_msg = await ctx.send("❌ Tu n'as pas le rôle requis pour utiliser cette commande.")
            await asyncio.sleep(5)
            try:
                await error_msg.delete()
            except (discord.Forbidden, discord.NotFound):
                pass

    @construction2.error
    async def construction2_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            error_msg = await ctx.send("❌ Tu n'as pas le rôle requis pour utiliser cette commande.")
            await asyncio.sleep(5)
            try:
                await error_msg.delete()
            except (discord.Forbidden, discord.NotFound):
                pass

    @construction3.error
    async def construction3_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            error_msg = await ctx.send("❌ Tu n'as pas le rôle requis pour utiliser cette commande.")
            await asyncio.sleep(5)
            try:
                await error_msg.delete()
            except (discord.Forbidden, discord.NotFound):
                pass

async def setup(bot):
    await bot.add_cog(Construction(bot))
