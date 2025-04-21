import asyncio
import discord
from redbot.core import commands, checks, Config
from datetime import datetime
import html
import io
import traceback

class Support(commands.Cog):
    """Module de gestion des tickets pour le support et le recrutement"""

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=1234567890)
        default_guild = {
            "ticket_counter": 0,
            "active_tickets": {}
        }
        self.config.register_guild(**default_guild)

        # IDs des salons et catégories
        self.CHANNELS = {
            "support": 1352736661989228544,
            "recrutement": 1352736663515693188,
            "tickets_category": 1352777439834800298,
            "logs": 1353013226870149190
        }

    class CloseTicketButton(discord.ui.Button):
        def __init__(self):
            super().__init__(
                style=discord.ButtonStyle.danger,
                label="Fermer le ticket",
                emoji="🔒",
                custom_id="close_ticket"
            )

    @commands.command()
    @checks.admin_or_permissions(administrator=True)
    async def setuptickets(self, ctx):
        """Configure les messages de tickets dans les salons appropriés"""
        await ctx.send("⚙️ Configuration des messages de tickets...")

        # Configuration du salon support
        support_channel = ctx.guild.get_channel(self.CHANNELS["support"])
        if support_channel:
            try:
                await support_channel.purge()
                embed = discord.Embed(
                    title="🎫 Support",
                    description="Cliquez sur le bouton ci-dessous pour ouvrir un ticket de support",
                    color=discord.Color.blue()
                )
                view = discord.ui.View(timeout=None)
                view.add_item(
                    discord.ui.Button(
                        style=discord.ButtonStyle.primary,
                        label="Ouvrir un ticket",
                        emoji="🎫",
                        custom_id="ticket_support"
                    )
                )
                await support_channel.send(embed=embed, view=view)
            except Exception as e:
                await ctx.send(f"❌ Erreur pour le salon support: {str(e)}")

        # Configuration du salon recrutement
        recruit_channel = ctx.guild.get_channel(self.CHANNELS["recrutement"])
        if recruit_channel:
            try:
                await recruit_channel.purge()
                embed = discord.Embed(
                    title="📝 Recrutement",
                    description="Cliquez sur le bouton ci-dessous pour postuler",
                    color=discord.Color.green()
                )
                view = discord.ui.View(timeout=None)
                view.add_item(
                    discord.ui.Button(
                        style=discord.ButtonStyle.primary,
                        label="Postuler",
                        emoji="📝",
                        custom_id="ticket_recruit"
                    )
                )
                await recruit_channel.send(embed=embed, view=view)
            except Exception as e:
                await ctx.send(f"❌ Erreur pour le salon recrutement: {str(e)}")

        await ctx.send("✅ Configuration terminée")

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        if not interaction.type == discord.InteractionType.component:
            return

        custom_id = interaction.data.get("custom_id", "")
        
        try:
            if custom_id.startswith("ticket_"):
                # Différer la réponse immédiatement pour éviter l'expiration
                await interaction.response.defer(ephemeral=True)
                ticket_type = custom_id.split("_")[1]
                await self.create_ticket(interaction, ticket_type)
            elif custom_id == "close_ticket":
                # Différer la réponse immédiatement pour éviter l'expiration
                await interaction.response.defer(ephemeral=True)
                await self.close_ticket(interaction)
        except discord.NotFound:
            # L'interaction a expiré, on ignore
            pass
        except Exception as e:
            print(f"Erreur dans on_interaction: {str(e)}")
            traceback.print_exc()
            try:
                if interaction.response.is_done():
                    await interaction.followup.send(f"Une erreur est survenue : {str(e)}", ephemeral=True)
                else:
                    await interaction.response.send_message(f"Une erreur est survenue : {str(e)}", ephemeral=True)
            except:
                pass

    async def create_ticket(self, interaction: discord.Interaction, ticket_type: str):
        """Crée un nouveau ticket"""
        guild = interaction.guild
        user = interaction.user

        # Vérification des tickets existants
        async with self.config.guild(guild).active_tickets() as active_tickets:
            user_tickets = [
                channel_id for channel_id, data in active_tickets.items()
                if str(data["user_id"]) == str(user.id) and data["type"] == ticket_type
            ]
            
            if user_tickets:
                await interaction.followup.send(
                    "Vous avez déjà un ticket ouvert !",
                    ephemeral=True
                )
                return

            try:
                # Mise à jour du compteur
                counter = await self.config.guild(guild).ticket_counter()
                await self.config.guild(guild).ticket_counter.set(counter + 1)

                # Création du salon
                category = guild.get_channel(self.CHANNELS["tickets_category"])
                
                # Liste des rôles autorisés à voir les tickets
                authorized_roles = [
                    1352739255817867345,  # Rôle 1
                    1352739267499003935,  # Rôle 2
                    974387257630933083,   # Rôle 3
                    1352735317735637174,  # Rôle 4
                    1352739299036237917,  # Rôle 5
                    1352739281327751210,  # Rôle 6
                    1353003538380357652,  # Rôle 7
                    1352739356623896648,  # Rôle 8
                    1352739360885178440,  # Rôle 9
                    1361460353933770893,
                    1360970016614387903
                ]

                # Configuration des permissions
                overwrites = {
                    guild.default_role: discord.PermissionOverwrite(read_messages=False),
                    user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                    guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_channels=True)
                }

                # Ajouter les permissions pour les rôles autorisés
                for role_id in authorized_roles:
                    role = guild.get_role(role_id)
                    if role:
                        overwrites[role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)

                channel_name = f"{ticket_type}-{counter + 1:04d}"
                channel = await category.create_text_channel(
                    name=channel_name,
                    overwrites=overwrites
                )

                # Enregistrement du ticket
                active_tickets[str(channel.id)] = {
                    "user_id": str(user.id),
                    "type": ticket_type
                }

                # Message de bienvenue
                title = "🎫 Ticket de Support" if ticket_type == "support" else "📝 Candidature Staff"
                description = (
                    "Décrivez votre problème en détail."
                    if ticket_type == "support"
                    else "Afin de pouvoir vous orienter de la manière la plus précise possible, nous aimerions en savoir un peu plus sur vous :\n\n"
                    "**Votre âge**\n\n"
                    "**Votre parcours professionnel : études ou expérience de travail**\n\n"
                    "**Ce que vous aimeriez faire, par exemple :**\n"
                    "• Organiser des parties personnalisées de manière autonome\n"
                    "• Être informé des futurs projets et pouvoir les communiquer aux membres\n"
                    "• Faire partie de la modération, prévenir d'éventuels comportements toxiques et aider à la résolution de conflits\n"
                    "• Autres merci de développer\n\n"
                    "**Vos disponibilités (nuit / soir / journée)**"
                )
                color = discord.Color.blue() if ticket_type == "support" else discord.Color.green()

                embed = discord.Embed(
                    title=title,
                    description=description,
                    color=color
                )
                embed.add_field(name="Créé par", value=user.mention)
                embed.add_field(name="ID du ticket", value=f"#{counter + 1:04d}")

                # Vue avec le bouton de fermeture
                view = discord.ui.View(timeout=None)
                close_button = self.CloseTicketButton()
                view.add_item(close_button)
                
                await channel.send(content=user.mention, embed=embed, view=view)
                await interaction.followup.send(
                    f"Votre ticket a été créé : {channel.mention}",
                    ephemeral=True
                )

            except Exception as e:
                print(f"Erreur dans create_ticket: {str(e)}")
                traceback.print_exc()
                await interaction.followup.send(
                    f"Une erreur est survenue lors de la création du ticket : {str(e)}",
                    ephemeral=True
                )

    async def close_ticket(self, interaction: discord.Interaction):
        """Ferme un ticket"""
        if not interaction.channel:
            return

        try:
            channel = interaction.channel
            guild = interaction.guild
            closer = interaction.user

            # Vérifier si le canal est un ticket actif
            active_tickets = await self.config.guild(guild).active_tickets()
            if str(channel.id) not in active_tickets:
                await interaction.followup.send(
                    "Ce n'est pas un ticket actif.",
                    ephemeral=True
                )
                return

            ticket_data = active_tickets[str(channel.id)]
            await interaction.followup.send("🔒 Fermeture du ticket...")

            # Générer la transcription
            transcript = await self.generate_transcript(channel)
            
            # Créer le fichier de transcription
            transcript_filename = f"ticket-{channel.name}-{datetime.now().strftime('%Y%m%d-%H%M%S')}.html"
            
            # Obtenir le salon de logs
            logs_channel = guild.get_channel(self.CHANNELS["logs"])
            print(f"Salon de logs ID: {self.CHANNELS['logs']}, objet: {logs_channel}")
            
            if logs_channel:
                try:
                    user = guild.get_member(int(ticket_data["user_id"]))
                    user_mention = user.mention if user else "Utilisateur inconnu"
                    
                    embed = discord.Embed(
                        title="🔒 Ticket Fermé",
                        description=f"**Ticket:** {channel.name}\n"
                                  f"**Type:** {ticket_data['type']}\n"
                                  f"**Créé par:** {user_mention}\n"
                                  f"**Fermé par:** {closer.mention}",
                        color=discord.Color.red(),
                        timestamp=datetime.now()
                    )
                    
                    # Créer l'objet fichier
                    file_bytes = io.BytesIO(transcript.encode('utf-8'))
                    transcript_file = discord.File(
                        fp=file_bytes,
                        filename=transcript_filename
                    )
                    
                    # Envoyer l'embed et le fichier transcription
                    await logs_channel.send(content=f"Ticket fermé: {channel.name}", embed=embed, file=transcript_file)
                    print(f"Notification envoyée au salon de logs")
                except Exception as e:
                    print(f"Erreur lors de l'envoi au salon de logs: {str(e)}")
                    traceback.print_exc()
            else:
                print(f"Salon de logs introuvable! ID: {self.CHANNELS['logs']}")

            # Supprimer le ticket des tickets actifs
            async with self.config.guild(guild).active_tickets() as tickets:
                if str(channel.id) in tickets:
                    del tickets[str(channel.id)]

            # Message de fermeture et suppression du canal
            embed = discord.Embed(
                title="🔒 Fermeture du ticket",
                description="Ce ticket va être fermé dans 5 secondes.",
                color=discord.Color.red()
            )
            await channel.send(embed=embed)
            await asyncio.sleep(5)
            await channel.delete(reason=f"Ticket fermé par {closer.name}")

        except discord.NotFound:
            pass
        except discord.Forbidden:
            await interaction.followup.send(
                "Je n'ai pas la permission de fermer ce ticket.",
                ephemeral=True
            )
        except Exception as e:
            print(f"Erreur dans close_ticket: {str(e)}")
            traceback.print_exc()
            try:
                await interaction.followup.send(
                    f"Une erreur est survenue lors de la fermeture du ticket : {str(e)}",
                    ephemeral=True
                )
            except:
                pass

    async def generate_transcript(self, channel):
        """Génère une transcription HTML des messages du ticket"""
        messages = []
        try:
            async for message in channel.history(limit=None, oldest_first=True):
                timestamp = message.created_at.strftime("%d/%m/%Y %H:%M:%S")
                content = html.escape(message.content) if message.content else ""
                
                # Traitement des embeds
                embeds_content = []
                for embed in message.embeds:
                    embed_text = []
                    if embed.title:
                        embed_text.append(f"<strong>{html.escape(embed.title)}</strong>")
                    if embed.description:
                        embed_text.append(html.escape(embed.description))
                    for field in embed.fields:
                        embed_text.append(f"<strong>{html.escape(field.name)}:</strong> {html.escape(field.value)}")
                    if embed_text:
                        embeds_content.append("<br>".join(embed_text))

                # Construction du message HTML
                message_html = f"""
                <div class="message">
                    <div class="message-info">
                        <img src="{message.author.display_avatar.url}" class="avatar">
                        <span class="author">{html.escape(message.author.display_name)}</span>
                        <span class="timestamp">{timestamp}</span>
                    </div>
                    <div class="content">
                        {content}
                        {"<br>" + "<br>".join(embeds_content) if embeds_content else ""}
                    </div>
                </div>
                """
                messages.append(message_html)
        except Exception as e:
            print(f"Erreur lors de la génération de la transcription: {str(e)}")
            traceback.print_exc()
            messages.append(f"<div class='error'>Erreur lors de la récupération des messages: {html.escape(str(e))}</div>")

        # Template HTML complet
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #36393f; color: #dcddde; }}
                .message {{ background: #2f3136; margin: 10px 0; padding: 15px; border-radius: 5px; }}
                .message-info {{ display: flex; align-items: center; margin-bottom: 10px; }}
                .avatar {{ width: 40px; height: 40px; border-radius: 50%; margin-right: 10px; }}
                .author {{ color: #fff; font-weight: bold; margin-right: 10px; }}
                .timestamp {{ color: #72767d; font-size: 0.8em; }}
                .content {{ margin-left: 50px; }}
                .error {{ background: #f04747; color: white; padding: 10px; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <h1>Transcription du ticket {channel.name}</h1>
            {"".join(messages)}
        </body>
        </html>
        """
        return html_content

    @commands.command()
    @checks.admin_or_permissions(administrator=True)
    async def forceclose(self, ctx, channel_id: int = None):
        """Force la fermeture d'un ticket avec envoi du log"""
        if not channel_id:
            if not isinstance(ctx.channel, discord.TextChannel):
                await ctx.send("❌ Veuillez spécifier un ID de canal à fermer.")
                return
            channel = ctx.channel
        else:
            channel = ctx.guild.get_channel(channel_id)
            if not channel:
                await ctx.send(f"❌ Canal {channel_id} introuvable.")
                return
                
        guild = ctx.guild
        closer = ctx.author
        
        await ctx.send("🔒 Fermeture forcée du ticket...")
        
        # Générer un transcript minimal
        transcript = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #36393f; color: #dcddde; }}
            </style>
        </head>
        <body>
            <h1>Ticket fermé de force par {closer.name}</h1>
            <p>Canal: {channel.name}</p>
            <p>Date: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}</p>
        </body>
        </html>
        """
        
        # Créer le fichier de transcription
        transcript_filename = f"ticket-{channel.name}-force-{datetime.now().strftime('%Y%m%d-%H%M%S')}.html"
        
        # Obtenir le salon de logs
        logs_channel = guild.get_channel(self.CHANNELS["logs"])
        
        if logs_channel:
            try:
                # Créer l'embed
                embed = discord.Embed(
                    title="🔒 Ticket Fermé (Forcé)",
                    description=f"**Ticket:** {channel.name}\n**Fermé par:** {closer.mention}",
                    color=discord.Color.red(),
                    timestamp=datetime.now()
                )
                
                # Créer le fichier
                file_bytes = io.BytesIO(transcript.encode('utf-8'))
                transcript_file = discord.File(
                    fp=file_bytes,
                    filename=transcript_filename
                )
                
                # Envoyer le message
                await logs_channel.send(content=f"Ticket fermé de force: {channel.name}", embed=embed, file=transcript_file)
                await ctx.send(f"✅ Log envoyé à {logs_channel.mention}")
                
            except Exception as e:
                await ctx.send(f"❌ Erreur lors de l'envoi du log: {str(e)}")
        else:
            await ctx.send(f"❌ Salon de logs introuvable! ID: {self.CHANNELS['logs']}")
        
        # Message de fermeture et suppression du canal
        embed = discord.Embed(
            title="🔒 Fermeture du ticket",
            description="Ce ticket va être fermé dans 5 secondes.",
            color=discord.Color.red()
        )
        await channel.send(embed=embed)
        
        # Supprimer le ticket des tickets actifs
        async with self.config.guild(guild).active_tickets() as tickets:
            if str(channel.id) in tickets:
                del tickets[str(channel.id)]
                
        await asyncio.sleep(5)
        if channel != ctx.channel:  # Ne pas supprimer le canal si c'est celui où la commande a été exécutée
            try:
                await channel.delete(reason=f"Ticket fermé de force par {closer.name}")
            except Exception as e:
                await ctx.send(f"❌ Erreur lors de la suppression du canal: {str(e)}")

async def setup(bot):
    await bot.add_cog(Support(bot))
