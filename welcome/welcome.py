import discord
from redbot.core import commands, checks, Config
import asyncio
import datetime

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.welcome_channel_id = 1352736656113012737
        self.reglement_channel_id = 1352736658146983946
        self.autorole_channel_id = 1352736659799670884

    @commands.Cog.listener()
    async def on_member_join(self, member):
        channel = self.bot.get_channel(self.welcome_channel_id)
        if channel:
            # Création de l'embed principal
            embed = discord.Embed(
                title="🎉 Bienvenue sur Time 2 Clutch !",
                description=f"Hey {member.mention}, bienvenue parmi nous !\nNous sommes ravis de t'accueillir dans notre communauté gaming.",
                color=discord.Color.purple()
            )
            
            # Informations sur le membre
            embed.add_field(
                name="📝 À propos de toi",
                value=f"• Pseudo: **{member.name}**\n• Membre n°**{member.guild.member_count}**\n• Rejoint le: **{discord.utils.format_dt(member.joined_at, 'F')}**",
                inline=False
            )
            
            # Suggestions pour commencer
            embed.add_field(
                name="🎮 Pour commencer",
                value=f"• Lis le <#{self.reglement_channel_id}> pour connaître nos règles\n• Choisis tes rôles dans <#{self.autorole_channel_id}>",
                inline=False
            )
            
            # Footer avec date
            embed.set_footer(
                text=f"T.2.C • {datetime.datetime.now().strftime('%d/%m/%Y')}",
                icon_url=member.guild.icon.url if member.guild.icon else None
            )
            
            # Avatar du membre
            avatar_url = member.avatar.url if member.avatar else member.default_avatar.url
            embed.set_thumbnail(url=avatar_url)
            
            # Image décorative
            embed.set_image(url="https://i.gifer.com/origin/db/db06c14a3148ef1e0764641c2dc1f347_w200.gif")
            
            # Personnalisation de l'auteur
            embed.set_author(
                name="Nouveau membre !",
                icon_url=member.guild.icon.url if member.guild.icon else None
            )
            
            # Envoyer le message de bienvenue
            await channel.send(
                f"🎮 **Une nouvelle personne rejoint l'aventure !** 🎮",
                embed=embed
            )

async def setup(bot):
    await bot.add_cog(Welcome(bot))


