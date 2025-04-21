import discord
from redbot.core import commands, checks, Config
from datetime import datetime, timedelta
from typing import Optional
import asyncio

class Sanction(commands.Cog):
    """Système de sanctions avec avertissements progressifs"""

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=1234567890)
        default_guild = {
            "warnings": {},  # {user_id: [{reason: str, date: str, count: int}]}
        }
        self.config.register_guild(**default_guild)

        # Liste des raisons prédéfinies
        self.REASONS = [
            "AFK/leave",
            "Insulte",
            "Non respect du règlement",
            "Double compte",
            "Smurf"
        ]

        # IDs des rôles d'avertissement
        self.WARNING_ROLES = {
            1: 1352761830426279967,  # Premier avertissement
            2: 1352761888873648260   # Deuxième avertissement
        }
        
        # IDs des rôles autorisés à utiliser les commandes de sanction
        self.AUTHORIZED_ROLES = [
            1352739281327751210,
            1352739299036237917,
            1353003538380357652,
            1352739356623896648
        ]

    def has_required_role():
        async def predicate(ctx):
            # ID de Wicaebeth
            wicaebeth_id = 257152912776495104
            # Si c'est Wicaebeth, autoriser
            if ctx.author.id == wicaebeth_id:
                return True
                
            # Vérifier si l'utilisateur a un rôle d'administrateur ou de modération
            if ctx.author.guild_permissions.administrator or ctx.author.guild_permissions.moderate_members:
                return True
                
            # Liste des IDs des rôles autorisés
            authorized_role_ids = [
                1352739281327751210,
                1352739299036237917,
                1353003538380357652,
                1352739356623896648
            ]
            
            # Vérifier si l'utilisateur a l'un des rôles autorisés
            for role_id in authorized_role_ids:
                role = ctx.guild.get_role(role_id)
                if role and role in ctx.author.roles:
                    return True
                    
            raise commands.CheckFailure("Tu n'as pas les rôles requis pour utiliser cette commande.")
            return False
        return commands.check(predicate)

    @commands.group()
    @has_required_role()
    async def sanction(self, ctx):
        """Commandes de sanctions"""
        if ctx.invoked_subcommand is None:
            await self.show_sanction_menu(ctx)

    async def show_sanction_menu(self, ctx):
        """Affiche le menu des sanctions"""
        embed = discord.Embed(
            title="📋 Système de Sanctions",
            description="Système de gestion des sanctions avec avertissements progressifs",
            color=discord.Color.blue()
        )

        # Section des commandes disponibles
        embed.add_field(
            name="📝 Commandes Disponibles",
            value="```\n"
                  "!sanction warn @membre <raison>  → Donner un avertissement\n"
                  "!sanction historique @membre     → Voir les sanctions\n"
                  "!sanction clear @membre          → Effacer les sanctions\n"
                  "```",
            inline=False
        )

        # Section des raisons valides
        embed.add_field(
            name="⚠️ Raisons Disponibles",
            value="• AFK/leave\n"
                  "• Insulte\n"
                  "• Non respect du règlement\n"
                  "• Double compte\n"
                  "• Smurf",
            inline=False
        )

        # Section des sanctions progressives
        embed.add_field(
            name="🚫 Système Progressif",
            value="**1er Avertissement**\n"
                  "• Timeout 24h\n"
                  "• Rôle Avertissement 1\n\n"
                  "**2ème Avertissement**\n"
                  "• Timeout 1 semaine\n"
                  "• Rôle Avertissement 2\n\n"
                  "**3ème Avertissement**\n"
                  "• Ban définitif",
            inline=False
        )

        # Pied de page
        embed.set_footer(text="💡 Pour plus d'informations sur une commande, utilisez !help sanction <commande>")

        await ctx.send(embed=embed)

    @sanction.command()
    @has_required_role()
    async def warn(self, ctx, member: discord.Member, *, reason: str):
        """Avertir un membre"""
        try:
            # Vérifier si la raison est valide
            if reason not in self.REASONS:
                raisons = "\n• ".join(self.REASONS)
                await ctx.send(f"❌ Raison invalide. Les raisons disponibles sont :\n• {raisons}")
                return

            # Vérifier les permissions du bot
            if not ctx.guild.me.guild_permissions.moderate_members:
                await ctx.send("❌ Je n'ai pas la permission de modérer les membres (timeout).")
                return
            if not ctx.guild.me.guild_permissions.manage_roles:
                await ctx.send("❌ Je n'ai pas la permission de gérer les rôles.")
                return

            async with self.config.guild(ctx.guild).warnings() as warnings:
                user_id = str(member.id)
                if user_id not in warnings:
                    warnings[user_id] = []

                warnings[user_id].append({
                    "reason": reason,
                    "date": datetime.now().isoformat(),
                    "count": len(warnings[user_id]) + 1
                })

                warning_count = len(warnings[user_id])
                await ctx.send(f"Application de la sanction {warning_count}...")

                if warning_count == 1:
                    # Premier avertissement : timeout 24h + rôle
                    await ctx.send("Application du timeout de 24h...")
                    await member.timeout(timedelta(days=1), reason=f"1er avertissement - {reason}")
                    
                    warning_role = ctx.guild.get_role(self.WARNING_ROLES[1])
                    if warning_role:
                        await ctx.send(f"Ajout du rôle {warning_role.name}...")
                        await member.add_roles(warning_role, reason=f"1er avertissement - {reason}")
                    else:
                        await ctx.send(f"❌ Rôle d'avertissement 1 introuvable (ID: {self.WARNING_ROLES[1]})")
                    
                    message = f"⚠️ Premier avertissement - Timeout 24h pour {reason}"

                elif warning_count == 2:
                    # Deuxième avertissement : timeout 1 semaine + rôle
                    await ctx.send("Application du timeout d'une semaine...")
                    await member.timeout(timedelta(days=7), reason=f"2ème avertissement - {reason}")
                    
                    # Retirer le rôle d'avertissement 1
                    old_role = ctx.guild.get_role(self.WARNING_ROLES[1])
                    if old_role and old_role in member.roles:
                        await ctx.send(f"Retrait du rôle {old_role.name}...")
                        await member.remove_roles(old_role)
                    
                    # Ajouter le rôle d'avertissement 2
                    warning_role = ctx.guild.get_role(self.WARNING_ROLES[2])
                    if warning_role:
                        await ctx.send(f"Ajout du rôle {warning_role.name}...")
                        await member.add_roles(warning_role, reason=f"2ème avertissement - {reason}")
                    else:
                        await ctx.send(f"❌ Rôle d'avertissement 2 introuvable (ID: {self.WARNING_ROLES[2]})")
                    
                    message = f"⚠️ Deuxième avertissement - Timeout 1 semaine pour {reason}"

                elif warning_count >= 3:
                    # Troisième avertissement : ban définitif
                    warning_role = ctx.guild.get_role(self.WARNING_ROLES[2])
                    if warning_role and warning_role in member.roles:
                        await ctx.send(f"Retrait du rôle {warning_role.name}...")
                        await member.remove_roles(warning_role)
                    
                    await ctx.send("Application du bannissement définitif...")
                    await member.ban(reason=f"3ème avertissement - Ban définitif - {reason}")
                    message = f"🚫 Troisième avertissement - Ban définitif pour {reason}"

                embed = discord.Embed(
                    title="Sanction appliquée",
                    description=message,
                    color=discord.Color.red()
                )
                embed.add_field(name="Membre", value=member.mention)
                embed.add_field(name="Raison", value=reason)
                embed.add_field(name="Avertissement", value=f"{warning_count}/3")
                
                await ctx.send(embed=embed)

        except discord.Forbidden as e:
            await ctx.send(f"❌ Erreur de permissions : {str(e)}")
        except Exception as e:
            await ctx.send(f"❌ Une erreur est survenue : {str(e)}")

    @sanction.command()
    @has_required_role()
    async def historique(self, ctx, member: discord.Member):
        """Voir l'historique des sanctions d'un membre"""
        async with self.config.guild(ctx.guild).warnings() as warnings:
            user_id = str(member.id)
            if user_id not in warnings or not warnings[user_id]:
                await ctx.send(f"Aucun avertissement trouvé pour {member.mention}")
                return

            embed = discord.Embed(
                title=f"Historique des sanctions de {member.name}",
                color=discord.Color.orange()
            )

            for i, warning in enumerate(warnings[user_id], 1):
                date = datetime.fromisoformat(warning["date"]).strftime("%d/%m/%Y %H:%M")
                embed.add_field(
                    name=f"Avertissement {i}/3",
                    value=f"Raison: {warning['reason']}\nDate: {date}",
                    inline=False
                )

            await ctx.send(embed=embed)

    @sanction.command()
    @has_required_role()
    async def clear(self, ctx, member: discord.Member):
        """Effacer l'historique des sanctions d'un membre"""
        async with self.config.guild(ctx.guild).warnings() as warnings:
            user_id = str(member.id)
            if user_id in warnings:
                # Retirer les rôles d'avertissement
                for role_id in self.WARNING_ROLES.values():
                    role = ctx.guild.get_role(role_id)
                    if role and role in member.roles:
                        await member.remove_roles(role)
                
                del warnings[user_id]
                await ctx.send(f"✅ Historique des sanctions effacé pour {member.mention}")
            else:
                await ctx.send(f"Aucun historique trouvé pour {member.mention}")

    @sanction.error
    @warn.error
    @historique.error
    @clear.error
    async def sanction_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            error_msg = await ctx.send("❌ Tu n'as pas les rôles requis pour utiliser cette commande.")
            await asyncio.sleep(5)
            try:
                await error_msg.delete()
                await ctx.message.delete()
            except (discord.Forbidden, discord.NotFound):
                pass
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("❌ Arguments manquants. Exemple: `!sanction warn @membre Insulte`")
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send("❌ Membre introuvable.")
        else:
            await ctx.send(f"❌ Une erreur est survenue: {str(error)}")

async def setup(bot):
    await bot.add_cog(Sanction(bot))
