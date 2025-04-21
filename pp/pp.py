from redbot.core import commands
import discord
import asyncio
from discord.ui import Button, View

class JoinVoiceButton(Button):
    def __init__(self, channel_id: int):
        super().__init__(
            style=discord.ButtonStyle.success,
            label="Rejoindre la préparation",
            emoji="🎮"
        )
        self.channel_id = channel_id

    async def callback(self, interaction: discord.Interaction):
        channel = interaction.guild.get_channel(self.channel_id)
        if channel:
            try:
                await interaction.response.send_message(f"Clique sur le salon pour le rejoindre: {channel.mention}", ephemeral=True)
            except discord.HTTPException:
                await interaction.response.send_message("Une erreur est survenue.", ephemeral=True)
        else:
            await interaction.response.send_message("Le salon vocal n'a pas été trouvé.", ephemeral=True)

class PartiesPersonnalisees(commands.Cog):
    """Cog pour gérer les parties personnalisées"""

    def __init__(self, bot):
        self.bot = bot
        self.pp_channel_id = 1352768726524498101
        self.pp_role_id = 1352971285725970503
        # Mapping des salons vocaux de préparation
        self.prep_channels = {
            1352768734904979517: "🔊 Préparation n°1",
            1360965851502874865: "🔊 Préparation n°2",
            1360968736940625982: "🔊 Préparation n°3",
            1360968699535687720: "🔊 Préparation n°4"
        }

    def has_required_role():
        async def predicate(ctx):
            # Liste des IDs des utilisateurs autorisés
            authorized_user_ids = [
                257152912776495104,  # Wicaebeth
                # Ajoutez ici les autres IDs d'utilisateurs autorisés
            ]
            
            # Vérifier si l'utilisateur est dans la liste des autorisés
            if ctx.author.id in authorized_user_ids:
                return True
            
            # Liste des IDs des rôles autorisés
            authorized_role_ids = [
                974387257630933083,  # Rôle original
                1352739281327751210,
                1352739299036237917,
                1353003538380357652,
                1352739356623896648,
                1352739360885178440,
                1352739366874779750,
                1352739267499003935,
                1352739255817867345,
                1352739281327751210,
                1360970016614387903,
                1361460353933770893,
            ]
            
            # Vérifier si l'utilisateur a l'un des rôles autorisés
            for role_id in authorized_role_ids:
                role = ctx.guild.get_role(role_id)
                if role and role in ctx.author.roles:
                    return True
                    
            raise commands.CheckFailure("Tu n'as pas les rôles requis ou n'es pas autorisé à utiliser cette commande.")
            return False
        return commands.check(predicate)

    @commands.command(name="pp")
    @has_required_role()
    async def partie_personnalisee(self, ctx):
        """Annonce une partie personnalisée avec un format précis"""
        # Supprimer la commande de l'utilisateur
        try:
            await ctx.message.delete()
        except (discord.Forbidden, discord.NotFound):
            # Ignorer si le bot n'a pas les permissions ou si le message a déjà été supprimé
            pass
        
        # Vérifier si l'utilisateur est dans un salon vocal
        if not ctx.author.voice or not ctx.author.voice.channel:
            error_msg = await ctx.send("⚠️ Tu dois être dans un salon vocal de préparation pour lancer une PP !")
            await asyncio.sleep(10)
            try:
                await error_msg.delete()
            except (discord.Forbidden, discord.NotFound):
                pass
            return

        # Vérifier si l'utilisateur est dans un salon de préparation valide
        current_voice_channel = ctx.author.voice.channel.id
        if current_voice_channel not in self.prep_channels:
            error_msg = await ctx.send("⚠️ Tu dois être dans un salon de préparation valide pour lancer une PP !")
            await asyncio.sleep(10)
            try:
                await error_msg.delete()
            except (discord.Forbidden, discord.NotFound):
                pass
            return
        
        # Vérifier si la commande est utilisée dans le bon canal
        target_channel = self.bot.get_channel(self.pp_channel_id)
        if not target_channel:
            # Si le canal n'existe pas, envoyer un message d'erreur et le supprimer après 10 secondes
            error_msg = await ctx.send("⚠️ Le canal des parties personnalisées n'a pas été trouvé.")
            await asyncio.sleep(10)
            try:
                await error_msg.delete()
            except (discord.Forbidden, discord.NotFound):
                pass
            return
        
        # Récupérer le rôle par ID
        role = ctx.guild.get_role(self.pp_role_id)
        
        if not role:
            # Si le rôle n'existe pas, envoyer un message d'erreur et le supprimer après 10 secondes
            error_msg = await ctx.send("⚠️ Le rôle pour les parties personnalisées n'a pas été trouvé.")
            await asyncio.sleep(10)
            try:
                await error_msg.delete()
            except (discord.Forbidden, discord.NotFound):
                pass
            return
        
        # Créer l'embed pour l'annonce avec le format exact
        embed = discord.Embed(
            title="✨ Nouvelle PP",
            description=(
                "Mode → 5vs5\n"
                "Type → Chill\n"
                "Ranks → Tous\n"
                "Map → Roulette\n"
                f"Staff → {ctx.author.mention} ✨"
            ),
            color=0x9B59B6  # Couleur violette
        )
        
        # Ajouter l'avatar de l'auteur
        avatar_url = ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url
        embed.set_thumbnail(url=avatar_url)
        
        # Ajouter le footer correspondant au salon vocal
        embed.set_footer(text=self.prep_channels[current_voice_channel])
        
        # Créer le bouton et la vue
        view = View(timeout=None)  # Le bouton reste actif indéfiniment
        join_button = JoinVoiceButton(current_voice_channel)
        view.add_item(join_button)
        
        # Envoyer le message dans le canal spécifique avec le bouton
        await target_channel.send(
            content=f"{role.mention}",
            embed=embed,
            view=view,
            allowed_mentions=discord.AllowedMentions(roles=True)
        )
        
        # Si la commande n'a pas été utilisée dans le bon canal, envoyer une confirmation
        if ctx.channel.id != self.pp_channel_id:
            confirm_msg = await ctx.send("✅ Partie personnalisée annoncée dans le canal approprié !")
            await asyncio.sleep(5)
            try:
                await confirm_msg.delete()
            except (discord.Forbidden, discord.NotFound):
                pass

    @partie_personnalisee.error
    async def partie_personnalisee_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            error_msg = await ctx.send("❌ Tu n'es pas autorisé à utiliser cette commande.")
            await asyncio.sleep(5)
            try:
                await error_msg.delete()
            except (discord.Forbidden, discord.NotFound):
                pass

async def setup(bot):
    await bot.add_cog(PartiesPersonnalisees(bot))
