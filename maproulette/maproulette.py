from redbot.core import commands
import discord
import asyncio
import random

class AcceptButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.success, label="Accepter la map", emoji="✅", custom_id="accept_map")
        
    async def callback(self, interaction: discord.Interaction):
        view: MapVoteView = self.view
        await view.process_vote(interaction, True)

class RejectButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.danger, label="Refuser la map", emoji="❌", custom_id="reject_map")
        
    async def callback(self, interaction: discord.Interaction):
        view: MapVoteView = self.view
        await view.process_vote(interaction, False)

class MapVoteView(discord.ui.View):
    def __init__(self, parent, map_choice, min_votes_required, timeout):
        super().__init__(timeout=timeout)
        self.parent = parent
        self.map_choice = map_choice
        self.min_votes_required = min_votes_required
        self.accept_voters = set()
        self.reject_voters = set()
        self.all_voters = set()  # Ensemble pour suivre tous les utilisateurs qui ont voté
        self.message = None
        self.ended = False
        
        # Ajouter les boutons
        self.add_item(AcceptButton())
        self.add_item(RejectButton())
    
    async def process_vote(self, interaction: discord.Interaction, is_accept: bool):
        if self.ended:
            await interaction.response.send_message("Le vote est terminé.", ephemeral=True)
            return
            
        user_id = interaction.user.id
        
        # Vérifier si l'utilisateur a déjà voté
        if user_id in self.all_voters:
            await interaction.response.send_message("Vous avez déjà voté et ne pouvez pas changer votre vote.", ephemeral=True)
            return
        
        # Enregistrer le vote
        self.all_voters.add(user_id)
        
        if is_accept:
            self.accept_voters.add(user_id)
        else:
            self.reject_voters.add(user_id)
        
        # Mettre à jour l'affichage
        accept_count = len(self.accept_voters)
        reject_count = len(self.reject_voters)
        
        embed = discord.Embed(
            title="🎲 Roulette MAP",
            description=(
                f"MAP → {self.map_choice['name']}\n\n"
                f"✅ Accepter cette map: **{accept_count}** votes\n"
                f"❌ Refuser et relancer: **{reject_count}** votes\n\n"
                f"Minimum {self.min_votes_required} votes nécessaires pour accepter ou refuser.\n\n"
                f"⚠️ Attention: Vous ne pouvez voter qu'une seule fois!"
            ),
            color=0x00B0F4
        )
        embed.set_image(url=self.map_choice['image'])
        remaining = max(0, (self.timeout - (asyncio.get_event_loop().time() - self.start_time)))
        embed.set_footer(text=f"Temps restant: {int(remaining)} secondes")
        
        await interaction.response.defer(ephemeral=True)
        
        # Message de confirmation avec le choix fait
        vote_type = "ACCEPTER" if is_accept else "REFUSER"
        await interaction.followup.send(f"Votre vote pour {vote_type} la map a été enregistré! Vous ne pouvez plus changer votre vote.", ephemeral=True)
        
        # Mettre à jour le message
        await self.message.edit(embed=embed)
        
        # Vérifier si on a atteint le seuil de votes
        if accept_count >= self.min_votes_required or reject_count >= self.min_votes_required:
            self.ended = True
            self.stop()
    
    async def on_timeout(self):
        self.ended = True
        # S'assurer que les boutons sont désactivés après le timeout
        try:
            if self.message:
                # Récupérer le dernier embed
                current_embed = self.message.embeds[0]
                # Mettre à jour le footer pour indiquer que le temps est écoulé
                current_embed.set_footer(text="Temps écoulé! Le vote est terminé.")
                # Désactiver les boutons en mettant view=None
                await self.message.edit(embed=current_embed, view=None)
        except Exception as e:
            print(f"Erreur lors de la désactivation des boutons après timeout: {e}")
    
    async def start(self, channel):
        embed = discord.Embed(
            title="🎲 Roulette MAP",
            description=(
                f"MAP → {self.map_choice['name']}\n\n"
                f"✅ Accepter cette map: **0** votes\n"
                f"❌ Refuser et relancer: **0** votes\n\n"
                f"Minimum {self.min_votes_required} votes nécessaires pour accepter ou refuser.\n\n"
                f"⚠️ Attention: Vous ne pouvez voter qu'une seule fois!"
            ),
            color=0x00B0F4
        )
        embed.set_image(url=self.map_choice['image'])
        embed.set_footer(text=f"Temps restant: {int(self.timeout)} secondes")
        
        self.message = await channel.send(embed=embed, view=self)
        self.start_time = asyncio.get_event_loop().time()
        return self.message

class MapRoulette(commands.Cog):
    """Cog pour la roulette de maps Valorant"""

    def __init__(self, bot):
        self.bot = bot
        self.roulette_channel_id = 1352768729452384417
        self.maps = [
            {"name": "ASCENT", "image": "https://beebom.com/wp-content/uploads/2023/09/Ascent-Valorant-Cover.jpg"},
            {"name": "BIND", "image": "https://static.wikia.nocookie.net/valorant/images/2/23/Loading_Screen_Bind.png"},
            {"name": "BREEZE", "image": "https://cmsassets.rgpub.io/sanity/images/dsfx7636/news_live/b79528c1c15525072a138c2648be78a4b7fa3fd9-1920x1080.jpg?auto=format&fit=fill&q=80&w=956"},
            {"name": "FRACTURE", "image": "https://static.wikia.nocookie.net/valorant/images/f/fc/Loading_Screen_Fracture.png"},
            {"name": "HAVEN", "image": "https://files.bo3.gg/uploads/image/64582/image/webp-aaaa475629b10d73cbe5de879e7033c2.webp"},
            {"name": "ICEBOX", "image": "https://www.mandatory.gg/wp-content/uploads/mandatory-news-valorant-retrait-icebox-avril-2023.jpg"},
            {"name": "LOTUS", "image": "https://cmsassets.rgpub.io/sanity/images/dsfx7636/news_live/df5c6e7629733f801b7059f7d0ed8d286cbdbc1e-1920x1080.jpg?auto=format&fit=fill&q=80&w=956"},
            {"name": "PEARL", "image": "https://www.pcgamesn.com/wp-content/sites/pcgamesn/2022/09/valorant-map-pearl-players-divided.jpg"},
            {"name": "SPLIT", "image": "https://cmsassets.rgpub.io/sanity/images/dsfx7636/news_live/fe3ff195d072643e1cc1e07801152d2e2ab96cd6-1920x1080.jpg"},
            {"name": "SUNSET", "image": "https://cdn.ome.lt/C8HZ7SYxtIeBVR8RAcn5tTtfhc8=/970x360/smart/uploads/conteudo/fotos/sunset-valorant-novo-mapa.jpg"},
            {"name": "ABYSS", "image": "https://static.wikia.nocookie.net/valorant/images/6/61/Loading_Screen_Abyss.png"}
        ]
        self.loading_emojis = ["🔄", "⏳", "⌛"]
        self.min_votes_required = 6
        self.vote_timeout = 60.0  # secondes

    def has_required_role():
        async def predicate(ctx):
            # ID de Wicaebeth
            wicaebeth_id = 257152912776495104
            # Si c'est Wicaebeth, autoriser
            if ctx.author.id == wicaebeth_id:
                return True
            
            # Liste des IDs des rôles autorisés
            authorized_role_ids = [
                974387257630933083,  # Rôle original
                1352739281327751210,
                1352739299036237917,
                1353003538380357652,
                1352739356623896648,
                1352739360885178440,
                1352739366874779750,
                1352739267499003935,
                1352739255817867345,
                1352739281327751210,
                1360970016614387903,
                1360965009269588028,
                1361460353933770893
                
            ]
            
            # Vérifier si l'utilisateur a l'un des rôles autorisés
            for role_id in authorized_role_ids:
                role = ctx.guild.get_role(role_id)
                if role and role in ctx.author.roles:
                    return True
                    
            raise commands.CheckFailure("Tu n'as pas les rôles requis pour utiliser cette commande.")
            return False
        return commands.check(predicate)

    @commands.command(name="roulette")
    @has_required_role()
    async def roulette(self, ctx):
        """Choisit aléatoirement une map avec système de vote en groupe"""
        # Supprimer la commande de l'utilisateur
        try:
            await ctx.message.delete()
        except (discord.Forbidden, discord.NotFound):
            pass

        # Vérifier si la commande est utilisée dans le bon canal
        target_channel = self.bot.get_channel(self.roulette_channel_id)
        if not target_channel:
            error_msg = await ctx.send("⚠️ Le canal de la roulette n'a pas été trouvé.")
            await asyncio.sleep(10)
            try:
                await error_msg.delete()
            except (discord.Forbidden, discord.NotFound):
                pass
            return
        
        # Récupérer le nom d'affichage de l'auteur et le logo du serveur
        author_name = ctx.author.display_name
        author_avatar = ctx.author.display_avatar.url
        guild_icon = ctx.guild.icon.url if ctx.guild.icon else None
        
        # Créer l'embed de chargement initial
        loading_embed = discord.Embed(
            title="🎲 Roulette MAP",
            description="Tirage de la map en cours...",
            color=0x00B0F4
        )
        loading_embed.set_image(url="https://i.imgur.com/jhEvEJJ.gif")
        loading_embed.set_footer(text=f"Roulette lancée par {author_name}", icon_url=author_avatar)
        if guild_icon:
            loading_embed.set_thumbnail(url=guild_icon)
        
        # Envoyer le message initial dans le canal cible
        loading_message = await target_channel.send(content=ctx.author.mention, embed=loading_embed)
        
        # Si la commande n'a pas été utilisée dans le bon canal, envoyer une confirmation
        if ctx.channel.id != self.roulette_channel_id:
            confirm_msg = await ctx.send("✅ Roulette lancée dans le canal approprié !")
            await asyncio.sleep(5)
            try:
                await confirm_msg.delete()
            except (discord.Forbidden, discord.NotFound):
                pass
        
        # Animation avancée avec les cartes qui défilent
        animation_steps = [
            {"text": "🎯 Recherche des maps disponibles...", "color": 0x3498DB},
            {"text": "🔄 Mélange des maps...", "color": 0x9B59B6},
            {"text": "✨ Tirage au sort...", "color": 0xE91E63},
            {"text": "🔎 Analyse des statistiques...", "color": 0x2ECC71},
            {"text": "🎮 Préparation du résultat...", "color": 0xF1C40F},
        ]
        
        # Afficher les maps qui "défilent" pendant l'animation
        random_maps = random.sample(self.maps, min(6, len(self.maps)))
        
        for i, step in enumerate(animation_steps):
            loading_embed.description = step["text"]
            loading_embed.color = step["color"]
            
            # Changer l'image pour montrer différentes maps pendant le "défilement"
            if i < len(random_maps):
                loading_embed.set_image(url=random_maps[i]["image"])
                loading_embed.set_footer(text=f"Sélection en cours... | Lancée par {author_name}", icon_url=author_avatar)
            
            await loading_message.edit(embed=loading_embed)
            await asyncio.sleep(1.2)  # Durée légèrement plus longue pour avoir le temps de voir l'image
        
        # Effet de "ralentissement" sur les dernières maps
        slowing_maps = random.sample(self.maps, 3)  # Prendre 3 maps au hasard 
        
        for i, map_data in enumerate(slowing_maps):
            loading_embed.description = "⏳ Finalisation du choix..."
            loading_embed.color = 0xFF9500
            loading_embed.set_image(url=map_data["image"])
            loading_embed.set_footer(text=f"Presque terminé... | Lancée par {author_name}", icon_url=author_avatar)
            
            await loading_message.edit(embed=loading_embed)
            # Augmenter progressivement le délai pour l'effet de ralentissement
            await asyncio.sleep(0.8 + (i * 0.4))
        
        # Choisir une map aléatoire pour le résultat final
        map_choice = random.choice(self.maps)
        
        # Supprimer le message d'animation (sans la fenêtre de compte à rebours)
        await loading_message.delete()
        
        # Créer et démarrer la vue de vote
        vote_view = MapVoteView(self, map_choice, self.min_votes_required, self.vote_timeout)
        vote_message = await vote_view.start(target_channel)
        
        # Ajouter le nom de l'auteur dans le footer de l'embed initial du vote
        updated_embed = vote_message.embeds[0]
        updated_embed.set_footer(text=f"Roulette lancée par {author_name}", icon_url=author_avatar)
        if guild_icon:
            updated_embed.set_thumbnail(url=guild_icon)
        await vote_message.edit(embed=updated_embed)
        
        # Attendre que le vote soit terminé
        try:
            await asyncio.wait_for(vote_view.wait(), timeout=self.vote_timeout + 1)
        except asyncio.TimeoutError:
            # En cas de timeout, s'assurer que le vote est marqué comme terminé
            vote_view.ended = True
        
        # Récupérer les compteurs de vote
        accept_count = len(vote_view.accept_voters)
        reject_count = len(vote_view.reject_voters)
        
        # Déterminer le résultat du vote
        if accept_count >= self.min_votes_required:
            # La map est acceptée
            result_embed = discord.Embed(
                title="🎲 Roulette MAP",
                description=(
                    f"MAP → {map_choice['name']}\n\n"
                    f"**MAP ACCEPTÉE** avec {accept_count} votes pour et {reject_count} votes contre."
                ),
                color=0x2ECC71  # Vert
            )
            result_embed.set_image(url=map_choice['image'])
            result_embed.set_footer(text=f"Roulette lancée par {author_name}", icon_url=author_avatar)
            if guild_icon:
                result_embed.set_thumbnail(url=guild_icon)
            # Utiliser None à la place de la vue pour désactiver les boutons
            await vote_message.edit(embed=result_embed, view=None)
            
        elif reject_count >= self.min_votes_required:
            # La map est refusée, relancer la roulette
            result_embed = discord.Embed(
                title="🎲 Roulette MAP",
                description=(
                    f"MAP → {map_choice['name']}\n\n"
                    f"**MAP REFUSÉE** avec {reject_count} votes contre et {accept_count} votes pour.\n\n"
                    f"Relance de la roulette..."
                ),
                color=0xE74C3C  # Rouge
            )
            result_embed.set_image(url=map_choice['https://as1.ftcdn.net/jpg/00/08/37/08/1000_F_8370831_pjgOukKlNV27vADLsCCCqh4ij8esWqfB.jpg'])
            result_embed.set_footer(text=f"Roulette lancée par {author_name}", icon_url=author_avatar)
            if guild_icon:
                result_embed.set_thumbnail(url=guild_icon)
            # Utiliser None à la place de la vue pour désactiver les boutons
            await vote_message.edit(embed=result_embed, view=None)
            await asyncio.sleep(3)  # Pause dramatique
            await vote_message.delete()
            await self.roulette(ctx)  # Relancer la roulette
            
        else:
            # Pas assez de votes, garder la map par défaut
            result_embed = discord.Embed(
                title="🎲 Roulette MAP",
                description=(
                    f"MAP → {map_choice['name']}\n\n"
                    f"⏰ **TEMPS ÉCOULÉ**\n"
                    f"Votes: {accept_count} pour, {reject_count} contre.\n"
                    f"Pas assez de votes ({self.min_votes_required} nécessaires), la map est gardée par défaut."
                ),
                color=0xF1C40F  # Jaune
            )
            result_embed.set_image(url=map_choice['image'])
            result_embed.set_footer(text=f"Roulette lancée par {author_name}", icon_url=author_avatar)
            if guild_icon:
                result_embed.set_thumbnail(url=guild_icon)
            # Utiliser None à la place de la vue pour désactiver les boutons
            await vote_message.edit(embed=result_embed, view=None)

    @roulette.error
    async def roulette_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            error_msg = await ctx.send("❌ Tu n'as pas le rôle requis pour utiliser cette commande.")
            await asyncio.sleep(5)
            try:
                await error_msg.delete()
            except (discord.Forbidden, discord.NotFound):
                pass

async def setup(bot):
    await bot.add_cog(MapRoulette(bot))
