import discord
from redbot.core import commands, checks
import os

class Bot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cogs_folder = "/home/ubuntu/cogs"
        self.admin_role_id = 974387257630933083
        self.bot_role_id = 1360599785622474783
        self.authorized_users = [257152912776495104, 160227016329789440]

    async def bot_or_admin_check(self, ctx):
        # Vérifier si l'utilisateur est dans la liste des autorisés
        if ctx.author.id in self.authorized_users:
            return True
            
        # Vérifier si l'utilisateur a le rôle Bot
        if any(role.id == self.bot_role_id for role in ctx.author.roles):
            return True
            
        # Vérifier si l'utilisateur a le rôle Admin
        if any(role.id == self.admin_role_id for role in ctx.author.roles):
            return True
            
        return False

    @commands.command()
    async def bot(self, ctx):
        """Liste tous les modules disponibles dans le bot"""
        if not await self.bot_or_admin_check(ctx):
            await ctx.send("❌ Tu n'as pas la permission d'utiliser cette commande. Il faut avoir le rôle Bot ou Admin.")
            return
            
        await ctx.send("🔍 **Recherche des modules disponibles...**")
        
        try:
            # Récupérer les cogs chargés
            loaded_modules = [cog.lower() for cog in self.bot.cogs.keys()]
            
            # Récupérer tous les modules disponibles
            available_modules = []
            for item in os.listdir(self.cogs_folder):
                module_path = os.path.join(self.cogs_folder, item)
                if os.path.isdir(module_path):
                    module_file = os.path.join(module_path, f"{item}.py")
                    if os.path.isfile(module_file):
                        status = "✅" if item.lower() in loaded_modules else "❌"
                        available_modules.append((item, status))
            
            # Trier les modules par nom
            available_modules.sort(key=lambda x: x[0])
            
            # Créer l'embed
            embed = discord.Embed(
                title="Modules du bot",
                description="Liste de tous les modules disponibles\n✅ = chargé | ❌ = non chargé",
                color=0x2b2d31
            )
            
            # Ajouter les modules à l'embed
            for i in range(0, len(available_modules), 10):
                field_modules = available_modules[i:i+10]
                field_value = "\n".join([f"{status} **{name}**" for name, status in field_modules])
                embed.add_field(name="\u200b", value=field_value, inline=True)
            
            embed.set_footer(text="Pour charger : !load nom | Pour décharger : !unload nom")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Une erreur s'est produite : {str(e)}")

async def setup(bot):
    cog = Bot(bot)
    await bot.add_cog(cog)
    
    # Récupérer les commandes Core
    core_commands = ["load", "unload", "reload"]
    
    # Remplacer les checks des commandes Core
    for cmd_name in core_commands:
        cmd = bot.get_command(cmd_name)
        if cmd:
            # Supprimer tous les checks existants
            cmd.checks = []
            
            # Ajouter notre check personnalisé
            async def core_check(ctx):
                return await cog.bot_or_admin_check(ctx)
                
            cmd.add_check(core_check)
            print(f"Check personnalisé appliqué à la commande {cmd_name}")
            
    # Ajouter un gestionnaire d'erreur global pour les commandes
    @bot.event
    async def on_command_error(ctx, error):
        if isinstance(error, (commands.CheckFailure, commands.MissingPermissions)):
            await ctx.send("❌ Tu n'as pas la permission d'utiliser cette commande. Il faut avoir le rôle Bot ou Admin.")
