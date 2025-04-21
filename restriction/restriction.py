import discord
from redbot.core import commands, checks, Config
import re

class Restriction(commands.Cog):
    """Système de restriction des invitations Discord"""

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=1234567890)
        default_guild = {
            "enabled": True,  # État de la restriction
            "whitelist_channels": [],  # Salons exemptés
            "whitelist_roles": []  # Rôles exemptés
        }
        self.config.register_guild(**default_guild)

        # Regex pour détecter les liens d'invitation Discord
        self.invite_regex = re.compile(r"(?:https?://)?(?:www\.)?(?:discord\.(?:gg|io|me|li)|discordapp\.com/invite)/[a-zA-Z0-9]+")

    @commands.group()
    @checks.admin_or_permissions(administrator=True)
    async def antiinvite(self, ctx):
        """Commandes de gestion des restrictions d'invitations"""
        if ctx.invoked_subcommand is None:
            await self.show_status(ctx)

    async def show_status(self, ctx):
        """Affiche l'état actuel des restrictions"""
        settings = await self.config.guild(ctx.guild).all()
        
        embed = discord.Embed(
            title="🛡️ Système Anti-Invitations",
            color=discord.Color.blue()
        )
        
        status = "✅ Activé" if settings["enabled"] else "❌ Désactivé"
        embed.add_field(name="État", value=status, inline=False)
        
        # Liste des salons exemptés
        whitelist_channels = settings["whitelist_channels"]
        channels_text = "Aucun" if not whitelist_channels else ", ".join([f"<#{ch}>" for ch in whitelist_channels])
        embed.add_field(name="Salons Exemptés", value=channels_text, inline=False)
        
        # Liste des rôles exemptés
        whitelist_roles = settings["whitelist_roles"]
        roles_text = "Aucun" if not whitelist_roles else ", ".join([f"<@&{r}>" for r in whitelist_roles])
        embed.add_field(name="Rôles Exemptés", value=roles_text, inline=False)
        
        await ctx.send(embed=embed)

    @antiinvite.command()
    async def toggle(self, ctx):
        """Active/Désactive la restriction des invitations"""
        current = await self.config.guild(ctx.guild).enabled()
        await self.config.guild(ctx.guild).enabled.set(not current)
        status = "activée" if not current else "désactivée"
        await ctx.send(f"✅ La restriction des invitations est maintenant {status}.")

    @antiinvite.command()
    async def addchannel(self, ctx, channel: discord.TextChannel):
        """Ajoute un salon à la liste blanche"""
        async with self.config.guild(ctx.guild).whitelist_channels() as whitelist:
            if channel.id in whitelist:
                await ctx.send("❌ Ce salon est déjà dans la liste blanche.")
                return
            whitelist.append(channel.id)
        await ctx.send(f"✅ Le salon {channel.mention} a été ajouté à la liste blanche.")

    @antiinvite.command()
    async def removechannel(self, ctx, channel: discord.TextChannel):
        """Retire un salon de la liste blanche"""
        async with self.config.guild(ctx.guild).whitelist_channels() as whitelist:
            if channel.id not in whitelist:
                await ctx.send("❌ Ce salon n'est pas dans la liste blanche.")
                return
            whitelist.remove(channel.id)
        await ctx.send(f"✅ Le salon {channel.mention} a été retiré de la liste blanche.")

    @antiinvite.command()
    async def addrole(self, ctx, role: discord.Role):
        """Ajoute un rôle à la liste blanche"""
        async with self.config.guild(ctx.guild).whitelist_roles() as whitelist:
            if role.id in whitelist:
                await ctx.send("❌ Ce rôle est déjà dans la liste blanche.")
                return
            whitelist.append(role.id)
        await ctx.send(f"✅ Le rôle {role.mention} a été ajouté à la liste blanche.")

    @antiinvite.command()
    async def removerole(self, ctx, role: discord.Role):
        """Retire un rôle de la liste blanche"""
        async with self.config.guild(ctx.guild).whitelist_roles() as whitelist:
            if role.id not in whitelist:
                await ctx.send("❌ Ce rôle n'est pas dans la liste blanche.")
                return
            whitelist.remove(role.id)
        await ctx.send(f"✅ Le rôle {role.mention} a été retiré de la liste blanche.")

    @commands.Cog.listener()
    async def on_message(self, message):
        # Ignorer les messages des bots
        if message.author.bot:
            return

        # Vérifier si c'est dans un serveur
        if not message.guild:
            return

        # Vérifier si la restriction est activée
        if not await self.config.guild(message.guild).enabled():
            return

        # Vérifier si l'utilisateur est administrateur
        if message.author.guild_permissions.administrator:
            return

        # Vérifier si le salon est dans la liste blanche
        whitelist_channels = await self.config.guild(message.guild).whitelist_channels()
        if message.channel.id in whitelist_channels:
            return

        # Vérifier si l'utilisateur a un rôle exempté
        whitelist_roles = await self.config.guild(message.guild).whitelist_roles()
        if any(role.id in whitelist_roles for role in message.author.roles):
            return

        # Vérifier si le message contient un lien d'invitation
        if self.invite_regex.search(message.content):
            try:
                await message.delete()
                await message.channel.send(
                    f"{message.author.mention}, les liens d'invitation Discord ne sont pas autorisés dans ce salon.",
                    delete_after=10
                )
            except discord.Forbidden:
                pass

async def setup(bot):
    await bot.add_cog(Restriction(bot))
