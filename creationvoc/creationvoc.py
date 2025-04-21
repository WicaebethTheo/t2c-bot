import discord
from redbot.core import commands, Config
import asyncio
from discord.ui import Button, View

class VocalControlView(discord.ui.View):
    def __init__(self, owner_id, bot, channel_id):
        super().__init__(timeout=None)
        self.owner_id = owner_id
        self.bot = bot
        self.channel_id = channel_id
        
    @discord.ui.button(label="Rendre Privé", style=discord.ButtonStyle.danger, emoji="🔒", custom_id="make_private")
    async def make_private(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Vérifier si c'est bien le propriétaire du salon
        if interaction.user.id != self.owner_id:
            await interaction.response.send_message("❌ Seul le créateur du salon peut modifier ses paramètres.", ephemeral=True)
            return
            
        # Récupérer le salon
        channel = interaction.guild.get_channel(self.channel_id)
        if not channel:
            await interaction.response.send_message("❌ Ce salon n'existe plus.", ephemeral=True)
            return
            
        try:
            # Mettre à jour les permissions pour rendre le salon privé
            await channel.set_permissions(interaction.guild.default_role, connect=False)
            
            # Mettre à jour le nom du salon pour indiquer qu'il est privé
            current_name = channel.name
            if "🔒" not in current_name:
                await channel.edit(name=f"🔒 {current_name}")
                
            await interaction.response.send_message("✅ Le salon est maintenant privé. Seuls les membres invités peuvent rejoindre.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Une erreur s'est produite: {str(e)}", ephemeral=True)
    
    @discord.ui.button(label="Rendre Public", style=discord.ButtonStyle.success, emoji="🔓", custom_id="make_public")
    async def make_public(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Vérifier si c'est bien le propriétaire du salon
        if interaction.user.id != self.owner_id:
            await interaction.response.send_message("❌ Seul le créateur du salon peut modifier ses paramètres.", ephemeral=True)
            return
            
        # Récupérer le salon
        channel = interaction.guild.get_channel(self.channel_id)
        if not channel:
            await interaction.response.send_message("❌ Ce salon n'existe plus.", ephemeral=True)
            return
            
        try:
            # Mettre à jour les permissions pour rendre le salon public
            await channel.set_permissions(interaction.guild.default_role, connect=True)
            
            # Mettre à jour le nom du salon pour indiquer qu'il est public
            current_name = channel.name
            if "🔒" in current_name:
                await channel.edit(name=current_name.replace("🔒 ", ""))
                
            await interaction.response.send_message("✅ Le salon est maintenant public. Tout le monde peut rejoindre.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Une erreur s'est produite: {str(e)}", ephemeral=True)
    
    @discord.ui.button(label="Limite de Membres", style=discord.ButtonStyle.primary, emoji="👥", custom_id="limit_members")
    async def limit_members(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Vérifier si c'est bien le propriétaire du salon
        if interaction.user.id != self.owner_id:
            await interaction.response.send_message("❌ Seul le créateur du salon peut modifier ses paramètres.", ephemeral=True)
            return
            
        # Récupérer le salon
        channel = interaction.guild.get_channel(self.channel_id)
        if not channel:
            await interaction.response.send_message("❌ Ce salon n'existe plus.", ephemeral=True)
            return
            
        # Demander la limite de membres
        await interaction.response.send_message(
            "Entrez la limite de membres souhaitée (0-99) : \n"
            "- `0` = Aucune limite\n"
            "- `5` = 5 membres maximum\n"
            "- `10` = 10 membres maximum, etc.",
            ephemeral=True
        )
        
        # Fonction pour vérifier si c'est le bon utilisateur et le bon canal
        def check(m):
            return m.author.id == interaction.user.id and m.channel.id == interaction.channel.id
            
        try:
            # Attendre la réponse
            msg = await self.bot.wait_for('message', check=check, timeout=30.0)
            
            # Vérifier que la réponse est un nombre entre 0 et 99
            try:
                limit = int(msg.content)
                if limit < 0 or limit > 99:
                    await interaction.followup.send("❌ La limite doit être entre 0 et 99.", ephemeral=True)
                    return
                    
                # Appliquer la limite
                await channel.edit(user_limit=limit)
                
                # Supprimer le message de réponse de l'utilisateur
                try:
                    await msg.delete()
                except:
                    pass
                
                # Confirmer le changement
                if limit == 0:
                    await interaction.followup.send("✅ Aucune limite de membres n'est maintenant appliquée.", ephemeral=True)
                else:
                    await interaction.followup.send(f"✅ La limite du salon est maintenant de {limit} membres.", ephemeral=True)
                    
            except ValueError:
                await interaction.followup.send("❌ Veuillez entrer un nombre valide.", ephemeral=True)
                
        except asyncio.TimeoutError:
            await interaction.followup.send("❌ Temps écoulé. Aucune limite n'a été définie.", ephemeral=True)

class CreationVoc(commands.Cog):
    """Système de création automatique de salons vocaux"""

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=1234567891)
        self.CREATION_CHANNEL_ID = 1352995736803086366
        self.temp_channels = {}  # Pour stocker les salons temporaires
        self.control_messages = {}  # Pour stocker les messages de contrôle

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        # Si l'utilisateur rejoint le salon de création
        if after.channel and after.channel.id == self.CREATION_CHANNEL_ID:
            # Créer un nouveau salon vocal
            category = after.channel.category
            if category:
                try:
                    # Copier les permissions existantes du salon de création
                    overwrites = after.channel.overwrites.copy()
                    
                    # Modifier les permissions du rôle par défaut pour empêcher de déplacer les membres
                    if member.guild.default_role not in overwrites:
                        overwrites[member.guild.default_role] = discord.PermissionOverwrite()
                    overwrites[member.guild.default_role].move_members = False
                    
                    # Ajouter les permissions spéciales pour le créateur
                    overwrites[member] = discord.PermissionOverwrite(
                        view_channel=True,
                        connect=True,
                        speak=True,
                        stream=True,
                        priority_speaker=True,
                        mute_members=True,
                        deafen_members=True,
                        move_members=True,
                        manage_channels=True
                    )

                    # Créer le salon vocal avec les mêmes propriétés
                    new_channel = await category.create_voice_channel(
                        f"🎮 {member.display_name}",
                        overwrites=overwrites,
                        position=after.channel.position + 1,
                        bitrate=after.channel.bitrate,
                        user_limit=after.channel.user_limit,
                        rtc_region=after.channel.rtc_region,
                        video_quality_mode=after.channel.video_quality_mode
                    )

                    # Déplacer le membre dans son nouveau salon
                    await member.move_to(new_channel)
                    
                    # Stocker le salon dans notre dictionnaire
                    self.temp_channels[new_channel.id] = member.id
                    
                    # Créer un salon textuel temporaire pour les contrôles, visible uniquement par le créateur du salon
                    try:
                        # Créer les permissions pour le salon textuel
                        text_overwrites = {
                            member.guild.default_role: discord.PermissionOverwrite(view_channel=False),
                            member: discord.PermissionOverwrite(
                                view_channel=True,
                                send_messages=True,
                                read_messages=True,
                                read_message_history=True,
                                embed_links=True,
                                attach_files=True
                            ),
                            member.guild.me: discord.PermissionOverwrite(
                                view_channel=True,
                                send_messages=True,
                                read_messages=True,
                                read_message_history=True,
                                embed_links=True,
                                manage_messages=True,
                                manage_channels=True
                            )
                        }
                        
                        # Créer un salon textuel associé au salon vocal
                        control_channel = await category.create_text_channel(
                            name=f"contrôle-{member.name}",
                            topic=f"Contrôles pour le salon vocal de {member.display_name} - Ce salon sera supprimé automatiquement",
                            overwrites=text_overwrites
                        )
                        
                        # Créer l'embed pour les contrôles
                        embed = discord.Embed(
                            title="🎚️ Contrôles du salon vocal",
                            description=(
                                f"{member.mention}, bienvenue dans votre salon vocal personnalisé!\n\n"
                                "Utilisez les boutons ci-dessous pour personnaliser votre salon:\n"
                                "• 🔒 **Rendre Privé** - Seules les personnes invitées peuvent rejoindre\n"
                                "• 🔓 **Rendre Public** - Tout le monde peut rejoindre\n"
                                "• 👥 **Limite de Membres** - Définir un nombre maximum de participants\n\n"
                                "Ce salon de contrôle est visible uniquement par vous et sera supprimé automatiquement quand le salon vocal sera fermé."
                            ),
                            color=discord.Color.blue()
                        )
                        
                        # Créer une vue avec les boutons de contrôle
                        view = VocalControlView(member.id, self.bot, new_channel.id)
                        
                        # Envoyer le message avec les contrôles dans le salon textuel
                        control_message = await control_channel.send(embed=embed, view=view)
                        
                        # Enregistrer les informations pour référence future
                        self.control_messages[new_channel.id] = {
                            "user_id": member.id,
                            "control_message_id": control_message.id,
                            "control_channel_id": control_channel.id
                        }
                        
                        # Envoyer un message système pour indiquer où sont les contrôles
                        try:
                            await control_channel.send(
                                f"{member.mention}, ce salon est uniquement visible par vous et contient les contrôles pour votre salon vocal **{new_channel.name}**.",
                                delete_after=30
                            )
                        except:
                            pass
                            
                    except Exception as e:
                        print(f"Erreur lors de la création du salon de contrôle: {e}")
                        import traceback
                        traceback.print_exc()

                except discord.Forbidden:
                    # Le bot n'a pas les permissions nécessaires
                    pass
                except Exception as e:
                    # Une autre erreur s'est produite
                    print(f"Erreur lors de la création du salon : {e}")
                    import traceback
                    traceback.print_exc()

        # Si l'utilisateur quitte un salon temporaire
        if before.channel and before.channel.id in self.temp_channels:
            # Vérifier si le salon est vide
            if len(before.channel.members) == 0:
                # Récupérer le guild à partir du salon vocal
                guild = before.channel.guild
                
                try:
                    # Supprimer d'abord le salon textuel associé
                    if before.channel.id in self.control_messages:
                        control_info = self.control_messages[before.channel.id]
                        
                        # Récupérer l'ID du salon textuel
                        control_channel_id = control_info.get("control_channel_id")
                        if control_channel_id:
                            control_channel = guild.get_channel(control_channel_id)
                            if control_channel:
                                try:
                                    await control_channel.delete(reason="Salon vocal associé fermé")
                                    print(f"Salon textuel de contrôle supprimé pour le salon vocal {before.channel.id}")
                                except Exception as e:
                                    print(f"Erreur lors de la suppression du salon de contrôle: {e}")
                    
                    # Puis supprimer le salon vocal
                    print(f"Suppression du salon vocal {before.channel.name} (ID: {before.channel.id})")
                    await before.channel.delete(reason="Salon vocal vide")
                    
                    # Retirer les entrées de nos dictionnaires
                    if before.channel.id in self.temp_channels:
                        del self.temp_channels[before.channel.id]
                        print(f"Entrée supprimée du dictionnaire temp_channels pour l'ID {before.channel.id}")
                    
                    if before.channel.id in self.control_messages:
                        del self.control_messages[before.channel.id]
                        print(f"Entrée supprimée du dictionnaire control_messages pour l'ID {before.channel.id}")
                    
                except discord.NotFound:
                    print(f"Canal déjà supprimé : {before.channel.id}")
                    # Si le canal a déjà été supprimé, on supprime quand même les entrées des dictionnaires
                    if before.channel.id in self.temp_channels:
                        del self.temp_channels[before.channel.id]
                    if before.channel.id in self.control_messages:
                        del self.control_messages[before.channel.id]
                
                except discord.Forbidden:
                    print(f"Permission refusée pour supprimer le canal : {before.channel.id}")
                
                except Exception as e:
                    print(f"Erreur lors de la suppression des salons : {e}")
                    import traceback
                    traceback.print_exc()

    @commands.command()
    @commands.admin_or_permissions(administrator=True)
    async def creationvoc(self, ctx):
        """Configure le salon de création vocale avec un message explicatif"""
        
        # Vérifier si le salon de création existe
        creation_channel = ctx.guild.get_channel(self.CREATION_CHANNEL_ID)
        if not creation_channel:
            return await ctx.send(f"❌ Le salon de création vocal (ID: {self.CREATION_CHANNEL_ID}) n'a pas été trouvé.")
            
        # Chercher un salon textuel dans la même catégorie pour y mettre les instructions
        if creation_channel.category:
            text_channels = [c for c in creation_channel.category.channels if isinstance(c, discord.TextChannel)]
            if text_channels:
                instruction_channel = text_channels[0]
                
                # Créer un embed d'instructions
                embed = discord.Embed(
                    title="🎙️ Création de salons vocaux",
                    description=(
                        f"**Pour créer votre propre salon vocal :**\n\n"
                        f"1. Rejoignez le salon **{creation_channel.name}**\n"
                        f"2. Un salon vocal personnel sera automatiquement créé\n"
                        f"3. Vous serez déplacé dans ce nouveau salon\n"
                        f"4. Un salon textuel privé sera créé avec les contrôles de votre salon vocal\n\n"
                        f"En tant que créateur, vous pouvez :\n"
                        f"• Rendre le salon privé ou public\n"
                        f"• Limiter le nombre de membres\n"
                        f"• Gérer les autres membres (déplacer, rendre muet, etc.)\n\n"
                        f"Le salon sera automatiquement supprimé lorsqu'il sera vide."
                    ),
                    color=discord.Color.blue()
                )
                
                # Supprimer les anciens messages
                try:
                    await instruction_channel.purge(limit=10)
                except:
                    pass
                    
                # Envoyer le message d'instructions
                await instruction_channel.send(embed=embed)
                
                await ctx.send(f"✅ Instructions de création de salon vocal envoyées dans {instruction_channel.mention}")
            else:
                await ctx.send("❌ Aucun salon textuel trouvé dans la catégorie du salon de création.")
        else:
            await ctx.send("❌ Le salon de création n'est pas dans une catégorie.")

    @commands.command()
    @commands.admin_or_permissions(administrator=True)
    async def nettoyer_voc(self, ctx):
        """Nettoie tous les salons vocaux temporaires vides"""
        
        nettoyage_status = await ctx.send("🧹 Recherche de salons vocaux temporaires à nettoyer...")
        
        # Compter le nombre de salons nettoyés
        salons_vocaux_nettoyés = 0
        
        # Parcourir nos dictionnaires pour trouver des salons qui pourraient être vides
        temp_ids = list(self.temp_channels.keys())  # Créer une copie pour éviter les erreurs pendant l'itération
        
        for channel_id in temp_ids:
            # Vérifier si le salon existe encore
            channel = ctx.guild.get_channel(channel_id)
            
            # Si le salon n'existe pas ou s'il est vide, le supprimer de nos dictionnaires
            if not channel or len(channel.members) == 0:
                try:
                    # Si le salon existe encore, le supprimer
                    if channel:
                        await channel.delete(reason="Nettoyage manuel des salons vocaux temporaires")
                        salons_vocaux_nettoyés += 1
                    
                    # Supprimer les entrées des dictionnaires
                    if channel_id in self.temp_channels:
                        del self.temp_channels[channel_id]
                    if channel_id in self.control_messages:
                        del self.control_messages[channel_id]
                        
                except Exception as e:
                    await ctx.send(f"⚠️ Erreur lors du nettoyage du salon {channel_id}: {str(e)}")
        
        # Parcourir tous les canaux du serveur à la recherche de salons orphelins
        vocal_count = 0
        
        for channel in ctx.guild.channels:
            # Chercher les salons vocaux qui ressemblent à nos salons temporaires mais ne sont pas dans notre dictionnaire
            if isinstance(channel, discord.VoiceChannel) and channel.name.startswith("🎮 ") and channel.id != self.CREATION_CHANNEL_ID:
                # Vérifier s'il n'est pas dans notre dictionnaire et s'il est vide
                if channel.id not in self.temp_channels and len(channel.members) == 0:
                    try:
                        await channel.delete(reason="Nettoyage de salon vocal orphelin")
                        vocal_count += 1
                    except:
                        pass
        
        # Mettre à jour le message de statut
        await nettoyage_status.edit(content=(
            f"✅ Nettoyage terminé !\n"
            f"• Salons vocaux gérés nettoyés : {salons_vocaux_nettoyés}\n"
            f"• Salons vocaux orphelins nettoyés : {vocal_count}"
        ))

async def setup(bot):
    """Fonction de configuration requise par Red-Bot"""
    cog = CreationVoc(bot)
    await bot.add_cog(cog)
    return cog
