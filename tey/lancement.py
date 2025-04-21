from redbot.core import commands
import discord
import asyncio

class TeyLancement(commands.Cog):
    """Cog pour lancer plusieurs commandes à la suite"""

    def __init__(self, bot):
        self.bot = bot
        self.bot_role_id = 1360599785622474783  # ID du rôle "Perm Bot"

    async def has_required_role(self, ctx):
        """Vérifier si l'utilisateur a le rôle Bot ou est administrateur"""
        if ctx.author.guild_permissions.administrator:
            return True
            
        # Vérifier si l'utilisateur a le rôle Bot
        for role in ctx.author.roles:
            if role.id == self.bot_role_id:
                return True
                
        return False

    @commands.command(name='boot')
    async def boot(self, ctx):
        """Lance une série de commandes d'initialisation du serveur"""
        # Vérifier si l'utilisateur a le rôle nécessaire
        if not await self.has_required_role(ctx):
            return await ctx.send("❌ Vous n'avez pas la permission d'utiliser cette commande.")
        
        # Liste des commandes à exécuter
        commands_to_run = [
            "createsupport",
            "setuproles",
            "rulespp",
            "reglement publier",
            "setuptickets"
        ]

        status_message = await ctx.send("⏳ Démarrage de l'initialisation du serveur...")

        # Exécuter chaque commande avec un délai entre elles
        for i, cmd_name in enumerate(commands_to_run):
            try:
                # Mettre à jour le message de statut
                await status_message.edit(content=f"⏳ Exécution de la commande {i+1}/{len(commands_to_run)}: `!{cmd_name}`")
                
                # Traiter les commandes de groupe (comme "reglement publier")
                parts = cmd_name.split()
                
                if len(parts) > 1:
                    # C'est potentiellement une commande de groupe
                    group_name = parts[0]
                    subcommand_name = parts[1]
                    
                    # Récupérer la commande de groupe
                    group_command = self.bot.get_command(group_name)
                    
                    if group_command and hasattr(group_command, "commands"):
                        # Trouver la sous-commande
                        subcommand = None
                        for cmd in group_command.commands:
                            if cmd.name == subcommand_name:
                                subcommand = cmd
                                break
                        
                        if subcommand:
                            # Exécuter la sous-commande avec ses arguments (s'il y en a)
                            remaining_args = parts[2:] if len(parts) > 2 else []
                            await ctx.invoke(subcommand, *remaining_args)
                            await ctx.send(f"✅ Commande `!{cmd_name}` exécutée avec succès.")
                            await asyncio.sleep(3)
                            continue
                        else:
                            await ctx.send(f"⚠️ Sous-commande `{subcommand_name}` du groupe `{group_name}` introuvable.")
                            await asyncio.sleep(3)
                            continue
                
                # Si ce n'est pas une commande de groupe ou si le traitement a échoué, essayer comme une commande normale
                command = self.bot.get_command(parts[0])
                if command:
                    # Si c'est une commande simple
                    args = parts[1:] if len(parts) > 1 else []
                    await ctx.invoke(command, *args)
                    await ctx.send(f"✅ Commande `!{cmd_name}` exécutée avec succès.")
                else:
                    await ctx.send(f"⚠️ Commande `!{cmd_name}` introuvable.")
                
                # Attendre un peu entre chaque commande pour éviter les problèmes
                await asyncio.sleep(3)
            
            except Exception as e:
                await ctx.send(f"❌ Erreur lors de l'exécution de `!{cmd_name}`: {str(e)}")
                # Attendre quand même avant de passer à la suivante
                await asyncio.sleep(3)
        
        # Message final
        await status_message.edit(content="✅ Initialisation du serveur terminée !")

async def setup(bot):
    await bot.add_cog(TeyLancement(bot))