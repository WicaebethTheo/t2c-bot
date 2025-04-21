import discord
from discord.ext import commands
import yt_dlp
import asyncio

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queue = []
        self.is_playing = False
        # Liste des IDs des salons vocaux permanents autorisés
        self.allowed_channels = [
            1353000421035216916 
        ]
        # ID du salon vocal qui crée les salons temporaires
        self.creation_channel_id = 1352995736803086366  # Remplacez par l'ID du salon qui crée les salons temporaires
        self.ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
        self.ffmpeg_options = {
            'options': '-vn',
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'
        }

    def is_channel_allowed(self, channel):
        # Vérifie si le salon est dans la liste des salons autorisés
        # OU si c'est le salon de création
        # OU si c'est un salon temporaire
        return (channel.id in self.allowed_channels or 
                channel.id == self.creation_channel_id or 
                channel.category_id is not None)

    @commands.command(name='play', help='Joue une musique depuis YouTube')
    async def play(self, ctx, *, url):
        if not ctx.author.voice:
            await ctx.send("Vous devez être dans un canal vocal pour utiliser cette commande!")
            return

        voice_channel = ctx.author.voice.channel
        if not self.is_channel_allowed(voice_channel):
            await ctx.send("❌ La musique n'est pas autorisée dans ce salon vocal!")
            return

        if ctx.voice_client is None:
            await voice_channel.connect()
        elif ctx.voice_client.channel != voice_channel:
            await ctx.voice_client.move_to(voice_channel)

        with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
            try:
                info = ydl.extract_info(url, download=False)
                url2 = info['url']
                title = info['title']
                self.queue.append({'url': url2, 'title': title})
                
                if not self.is_playing:
                    await self.play_next(ctx)
                else:
                    await ctx.send(f"🎵 {title} a été ajouté à la file d'attente!")
            except Exception as e:
                await ctx.send(f"Une erreur est survenue: {str(e)}")

    @commands.command(name='setcreation', help='Définit le salon qui crée les salons temporaires')
    @commands.has_permissions(administrator=True)
    async def set_creation_channel(self, ctx, channel_id: int):
        self.creation_channel_id = channel_id
        await ctx.send(f"✅ Le salon <#{channel_id}> a été défini comme salon de création!")

    @commands.command(name='setchannel', help='Ajoute un salon vocal permanent à la liste des salons autorisés')
    @commands.has_permissions(administrator=True)
    async def set_channel(self, ctx, channel_id: int):
        if channel_id not in self.allowed_channels:
            self.allowed_channels.append(channel_id)
            await ctx.send(f"✅ Le salon vocal <#{channel_id}> a été ajouté à la liste des salons autorisés!")
        else:
            await ctx.send("❌ Ce salon vocal est déjà dans la liste des salons autorisés!")

    @commands.command(name='removechannel', help='Retire un salon vocal permanent de la liste des salons autorisés')
    @commands.has_permissions(administrator=True)
    async def remove_channel(self, ctx, channel_id: int):
        if channel_id in self.allowed_channels:
            self.allowed_channels.remove(channel_id)
            await ctx.send(f"✅ Le salon vocal <#{channel_id}> a été retiré de la liste des salons autorisés!")
        else:
            await ctx.send("❌ Ce salon vocal n'est pas dans la liste des salons autorisés!")

    @commands.command(name='listchannels', help='Affiche la liste des salons vocaux autorisés')
    async def list_channels(self, ctx):
        if not self.allowed_channels and not self.creation_channel_id:
            await ctx.send("Aucun salon vocal n'est autorisé pour la musique.")
            return
        
        message = "🎵 Salons vocaux autorisés pour la musique:\n"
        
        if self.creation_channel_id:
            message += f"• Salon de création: <#{self.creation_channel_id}>\n"
            message += "• Tous les salons temporaires créés à partir de ce salon\n"
        
        if self.allowed_channels:
            message += "\nSalons permanents autorisés:\n"
            message += "\n".join([f"• <#{channel_id}>" for channel_id in self.allowed_channels])
        
        await ctx.send(message)

    async def play_next(self, ctx):
        if len(self.queue) > 0:
            self.is_playing = True
            current = self.queue.pop(0)
            
            ctx.voice_client.play(discord.FFmpegPCMAudio(current['url'], **self.ffmpeg_options),
                                after=lambda e: asyncio.run_coroutine_threadsafe(self.play_next(ctx), self.bot.loop))
            await ctx.send(f"🎵 En train de jouer: {current['title']}")
        else:
            self.is_playing = False

    @commands.command(name='stop', help='Arrête la musique et vide la file d\'attente')
    async def stop(self, ctx):
        if ctx.voice_client:
            self.queue = []
            ctx.voice_client.stop()
            await ctx.voice_client.disconnect()
            await ctx.send("⏹️ La musique a été arrêtée et la file d'attente a été vidée!")

    @commands.command(name='skip', help='Passe à la musique suivante')
    async def skip(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            await ctx.send("⏭️ Musique suivante!")
            await self.play_next(ctx)
        else:
            await ctx.send("Aucune musique n'est en cours de lecture!")

    @commands.command(name='queue', help='Affiche la file d\'attente')
    async def show_queue(self, ctx):
        if not self.queue:
            await ctx.send("La file d'attente est vide!")
            return
        
        queue_list = "\n".join([f"{i+1}. {song['title']}" for i, song in enumerate(self.queue)])
        await ctx.send(f"🎵 File d'attente:\n{queue_list}")

async def setup(bot):
    await bot.add_cog(Music(bot))
