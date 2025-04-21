import discord
from redbot.core import commands
import asyncio

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

class Clear(commands.Cog):
    """Cog pour nettoyer les messages d'un canal"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="clear")
    @has_required_role()
    async def clear(self, ctx, amount: int = None):
        """Supprime tous les messages du canal actuel"""
        # Supprimer la commande
        try:
            await ctx.message.delete()
        except (discord.Forbidden, discord.NotFound):
            pass

        # Demander confirmation
        confirm_msg = await ctx.send("⚠️ **ATTENTION** ⚠️\nTu es sur le point de supprimer **TOUS** les messages de ce canal.\n"
                                   "Es-tu sûr de vouloir continuer ? (oui/non)")

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel and m.content.lower() in ['oui', 'non']

        try:
            response = await self.bot.wait_for('message', check=check, timeout=30.0)
            
            # Supprimer le message de réponse
            try:
                await response.delete()
            except (discord.Forbidden, discord.NotFound):
                pass

            if response.content.lower() == 'oui':
                # Supprimer le message de confirmation
                try:
                    await confirm_msg.delete()
                except (discord.Forbidden, discord.NotFound):
                    pass

                # Message de démarrage
                status_msg = await ctx.send("🗑️ Suppression des messages en cours...")

                try:
                    # Supprimer tous les messages
                    deleted = await ctx.channel.purge(limit=None, check=lambda m: True)
                    
                    # Envoyer un message de confirmation qui s'auto-détruit
                    complete_msg = await ctx.send(f"✅ {len(deleted)} messages ont été supprimés.")
                    await asyncio.sleep(5)
                    try:
                        await complete_msg.delete()
                    except (discord.Forbidden, discord.NotFound):
                        pass

                except discord.Forbidden:
                    error_msg = await ctx.send("❌ Je n'ai pas la permission de supprimer les messages dans ce canal.")
                    await asyncio.sleep(5)
                    try:
                        await error_msg.delete()
                    except (discord.Forbidden, discord.NotFound):
                        pass
                    return

            else:
                # Si l'utilisateur répond non
                cancel_msg = await ctx.send("❌ Suppression annulée.")
                await asyncio.sleep(5)
                try:
                    await cancel_msg.delete()
                    await confirm_msg.delete()
                except (discord.Forbidden, discord.NotFound):
                    pass

        except asyncio.TimeoutError:
            # Si l'utilisateur ne répond pas dans les 30 secondes
            timeout_msg = await ctx.send("⏰ Temps écoulé. Suppression annulée.")
            await asyncio.sleep(5)
            try:
                await timeout_msg.delete()
                await confirm_msg.delete()
            except (discord.Forbidden, discord.NotFound):
                pass

    @clear.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            error_msg = await ctx.send("❌ Tu n'as pas le rôle requis pour utiliser cette commande.")
            await asyncio.sleep(5)
            try:
                await error_msg.delete()
            except (discord.Forbidden, discord.NotFound):
                pass

async def setup(bot):
    await bot.add_cog(Clear(bot))
