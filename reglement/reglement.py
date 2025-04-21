import discord
from redbot.core import commands, Config, checks
from redbot.core.utils.menus import menu, DEFAULT_CONTROLS
import asyncio
import datetime

class AccepterReglementView(discord.ui.View):
    def __init__(self, cog):
        super().__init__(timeout=None)  # Le bouton reste actif indéfiniment
        self.cog = cog
        
    @discord.ui.button(label="J'accepte le règlement", style=discord.ButtonStyle.success, custom_id="accepter_reglement")
    async def accepter_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Réagit quand un utilisateur clique sur le bouton d'acceptation"""
        await self.cog.handle_reglement_accept(interaction)

class Reglement(commands.Cog):
    """Système de règlement pour serveur communautaire Discord"""

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=156465489412, force_registration=True)
        
        default_guild = {
            "reglement": {
                "introduction": "Bienvenue sur Time 2 Clutch ! Afin de garantir une expérience agréable pour tous et toutes, nous vous demandons de respecter les règles suivantes (tout manquement pourra entraîner des sanctions allant du simple avertissement au bannissement définitif ⚠️)",
                "sections": {
                    "1": {
                        "titre": "Respect et bonne conduite",
                        "contenu": "• Le respect entre membres est primordial. Aucune forme d'insulte, harcèlement, discrimination ou discours haineux ne sera tolérée.\n• Les débats sont autorisés tant qu'ils restent courtois et respectueux.\n• L'usage excessif de majuscules, spam ou flood est interdit."
                    },
                    "2": {
                        "titre": "Contenus et comportements interdits",
                        "contenu": "• Tout contenu NSFW (pornographique, gore, choquant) est strictement interdit.\n• La promotion de cheats, hacks ou toute autre pratique illégale est interdite.\n• Les discussions sur des sujets sensibles (politique, religion, etc.) doivent être abordées avec précaution ou évitées."
                    },
                    "3": {
                        "titre": "Organisation des salons",
                        "contenu": "• Veuillez respecter les catégories et utiliser les salons appropriés pour vos discussions.\n• L'utilisation des salons vocaux doit se faire dans le respect des autres utilisateurs (pas de cris, bruits de fond excessifs, etc.).\n• Les pseudos et avatars offensants ou inappropriés ne sont pas autorisés."
                    },
                    "4": {
                        "titre": "Publicité et autopromotion",
                        "contenu": "• La publicité pour d'autres serveurs Discord est interdite sauf autorisation de l'administration.\n• L'autopromotion (chaînes YouTube, Twitch, etc.) est tolérée uniquement dans les salons dédiés."
                    },
                    "5": {
                        "titre": "Comportement en jeu",
                        "contenu": "• Jouez de manière fair-play, toute triche ou comportement toxique en jeu pourra entraîner des sanctions sur le serveur.\n• Évitez le rage-quit ou les comportements nuisibles envers votre équipe."
                    },
                    "6": {
                        "titre": "Rôle et responsabilités du staff",
                        "contenu": "• Le staff est là pour garantir le bon fonctionnement du serveur. Leurs décisions doivent être respectées.\n• En cas de problème, contactez le support en créant un ticket.\n• Tout abus ou contournement des règles sera sanctionné."
                    }
                },
                "conclusion": "En rejoignant ce serveur, vous acceptez ce règlement.\n\nL'équipe de modération se réserve le droit de modifier ce règlement à tout moment.\n\nMerci de votre compréhension et bon jeu à tous ! 🎮",
            },
            "reglement_channel_id": None,
            "reglement_message_id": None,
            "role_acceptation_id": None,
            "logs_channel_id": None,
            "derniere_maj": None,
        }
        
        self.config.register_guild(**default_guild)
        self.accept_view = AccepterReglementView(self)
        
    async def handle_reglement_accept(self, interaction):
        """Traite l'interaction lorsqu'un utilisateur accepte le règlement"""
        guild = interaction.guild
        guild_config = self.config.guild(guild)
        role_id = await guild_config.role_acceptation_id()
        logs_id = await guild_config.logs_channel_id()
        
        if not role_id:
            return await interaction.response.send_message("⚠️ Aucun rôle n'est configuré pour l'acceptation du règlement.", ephemeral=True)
            
        role = guild.get_role(role_id)
        if not role:
            return await interaction.response.send_message("⚠️ Le rôle configuré est introuvable. Veuillez contacter un administrateur.", ephemeral=True)
            
        # Attribuer le rôle
        try:
            await interaction.user.add_roles(role, reason="Acceptation du règlement")
            await interaction.response.send_message("✅ Merci d'avoir accepté le règlement! Vous avez maintenant accès au serveur.", ephemeral=True)
            
            # Envoyer un log
            if logs_id:
                logs_channel = guild.get_channel(logs_id)
                if logs_channel:
                    log_embed = discord.Embed(
                        title="📝 Acceptation du règlement",
                        description=f"{interaction.user.mention} a accepté le règlement.",
                        color=discord.Color.green(),
                        timestamp=datetime.datetime.now()
                    )
                    log_embed.set_author(name=str(interaction.user), icon_url=interaction.user.display_avatar.url if interaction.user.display_avatar else None)
                    log_embed.set_footer(text=f"ID: {interaction.user.id}")
                    await logs_channel.send(embed=log_embed)
                    
        except discord.Forbidden:
            await interaction.response.send_message("❌ Je n'ai pas la permission d'attribuer ce rôle. Veuillez contacter un administrateur.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Une erreur est survenue: {str(e)}", ephemeral=True)

    def cog_unload(self):
        """Nettoyage lors du déchargement du cog"""
        self.bot.loop.create_task(self.accept_view.stop())

    @commands.group(name="reglement")
    async def reglement(self, ctx):
        """Commandes liées au règlement du serveur"""
        pass

    @reglement.command(name="afficher")
    async def afficher_reglement(self, ctx):
        """Affiche le règlement complet du serveur"""
        reglement_data = await self.config.guild(ctx.guild).reglement()
        
        embeds = []
        
        # Embed d'introduction
        intro_embed = discord.Embed(
            title="📜 Règlement du serveur",
            description=reglement_data["introduction"],
            color=discord.Color.blue()
        )
        intro_embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else None)
        intro_embed.set_footer(text=f"Serveur {ctx.guild.name}", icon_url=ctx.guild.icon.url if ctx.guild.icon else None)
        embeds.append(intro_embed)
        
        # Embeds pour chaque section
        for num, section in reglement_data["sections"].items():
            section_embed = discord.Embed(
                title=f"Section {num}: {section['titre']}",
                description=section["contenu"],
                color=discord.Color.blue()
            )
            embeds.append(section_embed)
        
        # Embed de conclusion
        conclusion_embed = discord.Embed(
            title="Conclusion et acceptation",
            description=reglement_data["conclusion"],
            color=discord.Color.blue()
        )
        
        derniere_maj = await self.config.guild(ctx.guild).derniere_maj()
        if derniere_maj:
            conclusion_embed.set_footer(text=f"Dernière mise à jour: {derniere_maj}")
            
        embeds.append(conclusion_embed)
        
        await menu(ctx, embeds, DEFAULT_CONTROLS)
        
    @reglement.command(name="section")
    async def afficher_section(self, ctx, numero: str):
        """Affiche une section spécifique du règlement
        
        Exemple: !reglement section 2
        """
        reglement_data = await self.config.guild(ctx.guild).reglement()
        
        if numero not in reglement_data["sections"]:
            return await ctx.send("❌ Cette section n'existe pas dans le règlement.")
        
        section = reglement_data["sections"][numero]
        
        embed = discord.Embed(
            title=f"Section {numero}: {section['titre']}",
            description=section["contenu"],
            color=discord.Color.blue()
        )
        embed.set_footer(text=f"Règlement de {ctx.guild.name}")
        
        await ctx.send(embed=embed)
        
    @reglement.command(name="recherche")
    async def recherche_reglement(self, ctx, *, terme: str):
        """Recherche un terme dans le règlement
        
        Exemple: !reglement recherche spam
        """
        reglement_data = await self.config.guild(ctx.guild).reglement()
        resultats = []
        
        # Recherche dans l'introduction
        if terme.lower() in reglement_data["introduction"].lower():
            resultats.append(("Introduction", reglement_data["introduction"]))
            
        # Recherche dans les sections
        for num, section in reglement_data["sections"].items():
            if terme.lower() in section["titre"].lower() or terme.lower() in section["contenu"].lower():
                resultats.append((f"Section {num}: {section['titre']}", section["contenu"]))
                
        # Recherche dans la conclusion
        if terme.lower() in reglement_data["conclusion"].lower():
            resultats.append(("Conclusion", reglement_data["conclusion"]))
            
        if not resultats:
            return await ctx.send(f"❌ Aucun résultat trouvé pour '{terme}'.")
            
        embeds = []
        for titre, contenu in resultats:
            embed = discord.Embed(
                title=titre,
                description=contenu,
                color=discord.Color.green()
            )
            # On surligne le terme recherché
            embed.set_footer(text=f"Recherche: '{terme}'")
            embeds.append(embed)
            
        await menu(ctx, embeds, DEFAULT_CONTROLS)

    @checks.admin_or_permissions(manage_guild=True)
    @reglement.command(name="configurer")
    async def configurer_reglement(self, ctx):
        """Configure les paramètres du règlement (Admin uniquement)"""
        # Configuration interactive du règlement
        await ctx.send("⚙️ **Configuration du système de règlement**\n"
                       "Veuillez répondre aux questions suivantes pour configurer le règlement.\n"
                       "Vous pouvez répondre `annuler` à tout moment pour annuler le processus.")

        # Fonction vérification réponse
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        # Canal du règlement
        await ctx.send("📝 Dans quel canal voulez-vous publier le règlement ? Mentionnez le canal ou indiquez son ID.")
        try:
            reponse = await self.bot.wait_for("message", check=check, timeout=60.0)
            if reponse.content.lower() == "annuler":
                return await ctx.send("❌ Configuration annulée.")
                
            # Extraction du canal
            if reponse.channel_mentions:
                channel = reponse.channel_mentions[0]
            else:
                try:
                    channel_id = int(reponse.content.strip())
                    channel = ctx.guild.get_channel(channel_id)
                    if not channel:
                        return await ctx.send("❌ Canal introuvable. Configuration annulée.")
                except ValueError:
                    return await ctx.send("❌ Canal invalide. Configuration annulée.")
                    
            await self.config.guild(ctx.guild).reglement_channel_id.set(channel.id)
            
            # Rôle d'acceptation
            await ctx.send("🔑 Quel rôle souhaitez-vous attribuer aux membres qui acceptent le règlement ? "
                           "Mentionnez le rôle ou indiquez son ID. Répondez `aucun` si vous ne voulez pas utiliser cette fonction.")
            reponse = await self.bot.wait_for("message", check=check, timeout=60.0)
            if reponse.content.lower() == "annuler":
                return await ctx.send("❌ Configuration annulée.")
                
            if reponse.content.lower() != "aucun":
                # Extraction du rôle
                if reponse.role_mentions:
                    role = reponse.role_mentions[0]
                    await self.config.guild(ctx.guild).role_acceptation_id.set(role.id)
                else:
                    try:
                        role_id = int(reponse.content.strip())
                        role = ctx.guild.get_role(role_id)
                        if not role:
                            await ctx.send("⚠️ Rôle introuvable. La fonction d'acceptation sera désactivée.")
                            await self.config.guild(ctx.guild).role_acceptation_id.set(None)
                        else:
                            await self.config.guild(ctx.guild).role_acceptation_id.set(role.id)
                    except ValueError:
                        await ctx.send("⚠️ ID de rôle invalide. La fonction d'acceptation sera désactivée.")
                        await self.config.guild(ctx.guild).role_acceptation_id.set(None)
            else:
                await self.config.guild(ctx.guild).role_acceptation_id.set(None)
                
            # Canal de logs
            await ctx.send("📋 Dans quel canal voulez-vous envoyer les logs d'acceptation du règlement ? "
                           "Mentionnez le canal ou indiquez son ID. Répondez `aucun` si vous ne voulez pas utiliser cette fonction.")
            reponse = await self.bot.wait_for("message", check=check, timeout=60.0)
            if reponse.content.lower() == "annuler":
                return await ctx.send("❌ Configuration annulée.")
                
            if reponse.content.lower() != "aucun":
                # Extraction du canal
                if reponse.channel_mentions:
                    logs_channel = reponse.channel_mentions[0]
                    await self.config.guild(ctx.guild).logs_channel_id.set(logs_channel.id)
                else:
                    try:
                        channel_id = int(reponse.content.strip())
                        logs_channel = ctx.guild.get_channel(channel_id)
                        if not logs_channel:
                            await ctx.send("⚠️ Canal de logs introuvable. La fonction de logs sera désactivée.")
                            await self.config.guild(ctx.guild).logs_channel_id.set(None)
                        else:
                            await self.config.guild(ctx.guild).logs_channel_id.set(logs_channel.id)
                    except ValueError:
                        await ctx.send("⚠️ ID de canal invalide. La fonction de logs sera désactivée.")
                        await self.config.guild(ctx.guild).logs_channel_id.set(None)
            else:
                await self.config.guild(ctx.guild).logs_channel_id.set(None)
                
            await ctx.send("✅ Configuration de base terminée! Utilisez `!reglement modifier` pour modifier le contenu du règlement.")
            
        except asyncio.TimeoutError:
            await ctx.send("❌ Temps écoulé. Configuration annulée.")

    @checks.admin_or_permissions(manage_guild=True)
    @reglement.command(name="modifier")
    async def modifier_reglement(self, ctx):
        """Modifie le contenu du règlement (Admin uniquement)"""
        reglement_data = await self.config.guild(ctx.guild).reglement()
        
        await ctx.send("📝 **Modification du règlement**\n"
                       "Que souhaitez-vous modifier ?\n"
                       "1️⃣ Introduction\n"
                       "2️⃣ Ajouter une section\n"
                       "3️⃣ Modifier une section existante\n"
                       "4️⃣ Supprimer une section\n"
                       "5️⃣ Conclusion\n"
                       "❌ Annuler")
                       
        # Fonction de vérification
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel
            
        # Attente de la réponse
        try:
            reponse = await self.bot.wait_for("message", check=check, timeout=60.0)
            if reponse.content.lower() == "annuler" or reponse.content == "❌":
                return await ctx.send("❌ Modification annulée.")
                
            choix = reponse.content
            
            # Introduction
            if choix == "1" or choix == "1️⃣":
                await ctx.send("📝 Veuillez entrer la nouvelle introduction:")
                reponse = await self.bot.wait_for("message", check=check, timeout=300.0)
                if reponse.content.lower() == "annuler":
                    return await ctx.send("❌ Modification annulée.")
                    
                reglement_data["introduction"] = reponse.content
                await self.config.guild(ctx.guild).reglement.set(reglement_data)
                await ctx.send("✅ Introduction modifiée avec succès!")
                
            # Ajouter section
            elif choix == "2" or choix == "2️⃣":
                # Déterminer le numéro de section
                section_nums = [int(k) for k in reglement_data["sections"].keys() if k.isdigit()]
                next_section = str(max(section_nums) + 1 if section_nums else 1)
                
                await ctx.send(f"📝 Création de la section {next_section}")
                
                await ctx.send("📝 Entrez le titre de cette section:")
                reponse = await self.bot.wait_for("message", check=check, timeout=300.0)
                if reponse.content.lower() == "annuler":
                    return await ctx.send("❌ Création annulée.")
                    
                titre = reponse.content
                
                await ctx.send("📝 Entrez le contenu de cette section:")
                reponse = await self.bot.wait_for("message", check=check, timeout=300.0)
                if reponse.content.lower() == "annuler":
                    return await ctx.send("❌ Création annulée.")
                    
                contenu = reponse.content
                
                # Ajout de la section
                reglement_data["sections"][next_section] = {
                    "titre": titre,
                    "contenu": contenu
                }
                
                await self.config.guild(ctx.guild).reglement.set(reglement_data)
                await ctx.send(f"✅ Section {next_section} ajoutée avec succès!")
                
            # Modifier section
            elif choix == "3" or choix == "3️⃣":
                # Afficher les sections disponibles
                sections = "\n".join([f"{num}. {section['titre']}" for num, section in reglement_data["sections"].items()])
                await ctx.send(f"📝 Quelle section souhaitez-vous modifier ?\n{sections}")
                
                reponse = await self.bot.wait_for("message", check=check, timeout=60.0)
                if reponse.content.lower() == "annuler":
                    return await ctx.send("❌ Modification annulée.")
                    
                num_section = reponse.content
                if num_section not in reglement_data["sections"]:
                    return await ctx.send("❌ Section introuvable. Modification annulée.")
                    
                await ctx.send(f"📝 Modification de la section {num_section}: {reglement_data['sections'][num_section]['titre']}")
                
                await ctx.send("📝 Entrez le nouveau titre (ou `garder` pour conserver l'actuel):")
                reponse = await self.bot.wait_for("message", check=check, timeout=300.0)
                if reponse.content.lower() == "annuler":
                    return await ctx.send("❌ Modification annulée.")
                    
                if reponse.content.lower() != "garder":
                    reglement_data["sections"][num_section]["titre"] = reponse.content
                
                await ctx.send("📝 Entrez le nouveau contenu (ou `garder` pour conserver l'actuel):")
                reponse = await self.bot.wait_for("message", check=check, timeout=300.0)
                if reponse.content.lower() == "annuler":
                    return await ctx.send("❌ Modification annulée.")
                    
                if reponse.content.lower() != "garder":
                    reglement_data["sections"][num_section]["contenu"] = reponse.content
                
                await self.config.guild(ctx.guild).reglement.set(reglement_data)
                await ctx.send(f"✅ Section {num_section} modifiée avec succès!")
                
            # Supprimer section
            elif choix == "4" or choix == "4️⃣":
                # Afficher les sections disponibles
                sections = "\n".join([f"{num}. {section['titre']}" for num, section in reglement_data["sections"].items()])
                await ctx.send(f"📝 Quelle section souhaitez-vous supprimer ?\n{sections}")
                
                reponse = await self.bot.wait_for("message", check=check, timeout=60.0)
                if reponse.content.lower() == "annuler":
                    return await ctx.send("❌ Suppression annulée.")
                    
                num_section = reponse.content
                if num_section not in reglement_data["sections"]:
                    return await ctx.send("❌ Section introuvable. Suppression annulée.")
                    
                # Confirmation
                await ctx.send(f"⚠️ Êtes-vous sûr de vouloir supprimer la section {num_section}: {reglement_data['sections'][num_section]['titre']} ? (oui/non)")
                
                reponse = await self.bot.wait_for("message", check=check, timeout=60.0)
                if reponse.content.lower() != "oui":
                    return await ctx.send("❌ Suppression annulée.")
                    
                # Suppression
                del reglement_data["sections"][num_section]
                
                await self.config.guild(ctx.guild).reglement.set(reglement_data)
                await ctx.send(f"✅ Section {num_section} supprimée avec succès!")
                
            # Conclusion
            elif choix == "5" or choix == "5️⃣":
                await ctx.send("📝 Veuillez entrer la nouvelle conclusion:")
                reponse = await self.bot.wait_for("message", check=check, timeout=300.0)
                if reponse.content.lower() == "annuler":
                    return await ctx.send("❌ Modification annulée.")
                    
                reglement_data["conclusion"] = reponse.content
                await self.config.guild(ctx.guild).reglement.set(reglement_data)
                await ctx.send("✅ Conclusion modifiée avec succès!")
            
            else:
                await ctx.send("❌ Option invalide. Modification annulée.")
                return
                
            # Mise à jour de la date
            await self.config.guild(ctx.guild).derniere_maj.set(datetime.datetime.now().strftime("%d/%m/%Y"))
                
        except asyncio.TimeoutError:
            await ctx.send("❌ Temps écoulé. Modification annulée.")

    @checks.admin_or_permissions(manage_guild=True)
    @reglement.command(name="publier")
    async def publier_reglement(self, ctx):
        """Publie ou met à jour le règlement dans le canal configuré (Admin uniquement)"""
        reglement_data = await self.config.guild(ctx.guild).reglement()
        channel_id = await self.config.guild(ctx.guild).reglement_channel_id()
        role_id = await self.config.guild(ctx.guild).role_acceptation_id()
        message_id = await self.config.guild(ctx.guild).reglement_message_id()
        
        if not channel_id:
            return await ctx.send("❌ Aucun canal n'a été configuré pour le règlement. Utilisez `!reglement configurer` d'abord.")
            
        channel = ctx.guild.get_channel(channel_id)
        if not channel:
            return await ctx.send("❌ Le canal configuré est introuvable. Veuillez reconfigurer le règlement.")
            
        # Nettoyer le salon en supprimant tous les messages
        await ctx.send("🧹 Nettoyage du salon de règlement en cours...")
        try:
            # Supprimer tous les messages du salon
            await channel.purge(limit=100)
            await ctx.send("✅ Salon nettoyé avec succès.")
        except discord.Forbidden:
            await ctx.send("❌ Je n'ai pas la permission de supprimer des messages dans ce salon.")
            return
        except Exception as e:
            await ctx.send(f"❌ Une erreur s'est produite lors du nettoyage du salon : {str(e)}")
            return
            
        # Création des embeds
        embeds = []
        
        # Embed d'introduction
        intro_embed = discord.Embed(
            title="📜 Règlement du serveur",
            description=reglement_data["introduction"],
            color=discord.Color.blue()
        )
        intro_embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else None)
        
        # Ajouter les sections à l'embed principal
        for num, section in reglement_data["sections"].items():
            intro_embed.add_field(
                name=f"📌 Section {num}: {section['titre']}",
                value=section["contenu"][:1024],  # Limite de Discord pour les champs d'embed
                inline=False
            )
        
        # Embed de conclusion avec bouton d'acceptation
        conclusion_embed = discord.Embed(
            description=reglement_data["conclusion"],
            color=discord.Color.blue()
        )
        
        derniere_maj = await self.config.guild(ctx.guild).derniere_maj()
        if derniere_maj:
            conclusion_embed.set_footer(text=f"Dernière mise à jour: {derniere_maj}")
            
        embeds = [intro_embed, conclusion_embed]
        
        # Publier le nouveau règlement
        try:
            # Envoyer le premier embed (introduction)
            await channel.send(embed=intro_embed)
            
            # Envoyer le dernier embed (conclusion) avec le bouton d'acceptation si un rôle est configuré
            if role_id:
                message = await channel.send(embed=conclusion_embed, view=self.accept_view)
            else:
                message = await channel.send(embed=conclusion_embed)
                
            # Enregistrer l'ID du nouveau message
            await self.config.guild(ctx.guild).reglement_message_id.set(message.id)
            await ctx.send(f"✅ Règlement publié avec succès dans {channel.mention}!")
            
        except Exception as e:
            await ctx.send(f"❌ Erreur lors de la publication du règlement: {str(e)}")

    @checks.admin_or_permissions(manage_guild=True)
    @reglement.command(name="reboot")
    async def reboot_reglement(self, ctx):
        """Réinitialise le règlement aux valeurs par défaut (Admin uniquement)"""
        # Demande de confirmation
        await ctx.send("⚠️ **ATTENTION** ⚠️\nCette commande va réinitialiser l'intégralité du règlement aux valeurs par défaut.\n"
                      "Toutes vos modifications seront perdues.\n\n"
                      "Tapez `confirmer` pour continuer ou toute autre réponse pour annuler.")
                      
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel
            
        try:
            reponse = await self.bot.wait_for("message", check=check, timeout=30.0)
            if reponse.content.lower() != "confirmer":
                return await ctx.send("❌ Réinitialisation annulée.")
                
            # Réinitialiser les données
            await self.config.guild(ctx.guild).clear()
            await ctx.send("✅ Le règlement a été réinitialisé aux valeurs par défaut.")
            
        except asyncio.TimeoutError:
            await ctx.send("❌ Temps écoulé. Réinitialisation annulée.")

    @reglement.command(name="stats")
    @checks.admin_or_permissions(manage_guild=True)
    async def stats_reglement(self, ctx):
        """Affiche les statistiques du règlement (Admin uniquement)"""
        guild_config = self.config.guild(ctx.guild)
        reglement_data = await guild_config.reglement()
        channel_id = await guild_config.reglement_channel_id()
        role_id = await guild_config.role_acceptation_id()
        logs_id = await guild_config.logs_channel_id()
        message_id = await guild_config.reglement_message_id()
        derniere_maj = await guild_config.derniere_maj()
        
        embed = discord.Embed(
            title="📊 Statistiques du règlement",
            color=discord.Color.blue(),
            timestamp=datetime.datetime.now()
        )
        
        # Informations générales
        embed.add_field(
            name="📝 Contenu",
            value=f"Sections: {len(reglement_data['sections'])}\n"
                  f"Dernière mise à jour: {derniere_maj or 'Jamais'}", 
            inline=False
        )
        
        # Informations de configuration
        channel = ctx.guild.get_channel(channel_id) if channel_id else None
        role = ctx.guild.get_role(role_id) if role_id else None
        logs_channel = ctx.guild.get_channel(logs_id) if logs_id else None
        
        embed.add_field(
            name="⚙️ Configuration",
            value=f"Canal de publication: {channel.mention if channel else 'Non configuré'}\n"
                  f"Rôle d'acceptation: {role.mention if role else 'Non configuré'}\n"
                  f"Canal de logs: {logs_channel.mention if logs_channel else 'Non configuré'}\n"
                  f"Message ID: {message_id or 'Non publié'}",
            inline=False
        )
        
        # Stats du rôle
        if role:
            membres_avec_role = len(role.members)
            membres_totaux = ctx.guild.member_count
            pourcentage = (membres_avec_role / membres_totaux) * 100 if membres_totaux > 0 else 0
            
            embed.add_field(
                name="👥 Acceptation",
                value=f"Membres ayant accepté: {membres_avec_role}/{membres_totaux} ({pourcentage:.1f}%)",
                inline=False
            )
            
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Reglement(bot))

