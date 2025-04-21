import discord
from redbot.core import commands, checks
import io

class SupportTest(commands.Cog):
    """Test pour les logs de tickets"""

    def __init__(self, bot):
        self.bot = bot
        # ID du salon de logs
        self.LOG_CHANNEL_ID = 1353013226870149190

    @commands.command()
    @checks.admin_or_permissions(administrator=True)
    async def testlog(self, ctx):
        """Teste l'envoi d'un message au salon de logs"""
        guild = ctx.guild
        user = ctx.author
        
        # Obtenir le salon de logs
        logs_channel = guild.get_channel(self.LOG_CHANNEL_ID)
        
        if logs_channel:
            try:
                # Créer un embed de test
                embed = discord.Embed(
                    title="🧪 Test de Log",
                    description="Ceci est un test d'envoi de log",
                    color=discord.Color.blue()
                )
                embed.add_field(name="Auteur", value=user.mention)
                
                # Créer un fichier de test simple
                test_content = "<html><body><h1>Fichier de Test</h1><p>Ceci est un fichier de test.</p></body></html>"
                file_bytes = io.BytesIO(test_content.encode('utf-8'))
                test_file = discord.File(fp=file_bytes, filename="test.html")
                
                # Envoyer le message de test
                await logs_channel.send(content="Message de test", embed=embed, file=test_file)
                await ctx.send(f"✅ Test envoyé au salon {logs_channel.mention}")
                
            except Exception as e:
                await ctx.send(f"❌ Erreur: {str(e)}")
        else:
            await ctx.send(f"❌ Salon de logs introuvable! ID: {self.LOG_CHANNEL_ID}")

async def setup(bot):
    await bot.add_cog(SupportTest(bot)) 