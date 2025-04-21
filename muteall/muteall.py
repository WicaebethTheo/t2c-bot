import discord
from redbot.core import commands

class MuteAll(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Liste des IDs des rôles autorisés
        self.authorized_roles = [
            974387257630933083,  # Administrateur
            1352739267499003935,
            1352739255817867345,
            1352739281327751210, 
            1352739299036237917, 
            1353003538380357652, 
            1352739356623896648, 
            1352739366874779750
        ]
        self.owner_id = 257152912776495104  # ID de Wicaebeth
    
    def has_required_role():
        async def predicate(ctx):
            # Si c'est Wicaebeth, autoriser
            if ctx.author.id == 257152912776495104:
                return True
            
            # Vérifier si l'utilisateur a l'un des rôles autorisés
            for role_id in [
                974387257630933083,  # Administrateur
                1352739267499003935,
                1352739255817867345,
                1352739281327751210, 
                1352739299036237917, 
                1353003538380357652, 
                1352739356623896648, 
                1352739366874779750
            ]:
                role = ctx.guild.get_role(role_id)
                if role and role in ctx.author.roles:
                    return True
            
            raise commands.CheckFailure("Tu n'as pas les rôles requis pour utiliser cette commande.")
            
        return commands.check(predicate)
    
    @commands.command()
    @has_required_role()
    async def mute(self, ctx):
        """Mute tous les utilisateurs dans le salon vocal où vous êtes, sauf vous-même"""
        # Vérifier si l'auteur est dans un salon vocal
        if not ctx.author.voice:
            return await ctx.send("❌ Vous devez être dans un salon vocal pour utiliser cette commande.")
        
        voice_channel = ctx.author.voice.channel
        # Exclure l'auteur de la commande et les bots
        members_to_mute = [member for member in voice_channel.members if not member.bot and member.id != ctx.author.id]
        
        if not members_to_mute:
            return await ctx.send("❌ Il n'y a personne d'autre à muter dans ce salon vocal.")
        
        # Muter tous les membres sélectionnés
        success_count = 0
        failed_count = 0
        
        for member in members_to_mute:
            try:
                await member.edit(mute=True)
                success_count += 1
            except discord.Forbidden:
                failed_count += 1
        
        # Construire le message de réponse
        response = f"✅ **{success_count}** membres ont été mutes avec succès (vous avez été exclu)."
        if failed_count > 0:
            response += f"\n❌ Impossible de muter **{failed_count}** membres (permissions insuffisantes)."
        
        await ctx.send(response)
    
    @commands.command()
    @has_required_role()
    async def unmute(self, ctx):
        """Démute tous les utilisateurs dans le salon vocal où vous êtes"""
        # Vérifier si l'auteur est dans un salon vocal
        if not ctx.author.voice:
            return await ctx.send("❌ Vous devez être dans un salon vocal pour utiliser cette commande.")
        
        voice_channel = ctx.author.voice.channel
        # Exclure les bots mais inclure tout le monde (l'auteur pourrait vouloir se démuter aussi)
        members_to_unmute = [member for member in voice_channel.members if not member.bot]
        
        if not members_to_unmute:
            return await ctx.send("❌ Il n'y a personne à démuter dans ce salon vocal.")
        
        # Démuter tous les membres
        success_count = 0
        failed_count = 0
        
        for member in members_to_unmute:
            try:
                await member.edit(mute=False)
                success_count += 1
            except discord.Forbidden:
                failed_count += 1
        
        # Construire le message de réponse
        response = f"✅ **{success_count}** membres ont été démutés avec succès."
        if failed_count > 0:
            response += f"\n❌ Impossible de démuter **{failed_count}** membres (permissions insuffisantes)."
        
        await ctx.send(response)
    
    @mute.error
    @unmute.error
    async def mute_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send("❌ Tu n'as pas le rôle requis pour utiliser cette commande.")
        else:
            await ctx.send(f"❌ Une erreur s'est produite : {str(error)}")

async def setup(bot):
    await bot.add_cog(MuteAll(bot))
