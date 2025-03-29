from ast import alias
import discord
from discord.ext import commands
from youtubesearchpython import VideosSearch
from yt_dlp import YoutubeDL
import asyncio
import wikipedia
import subprocess


class music_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # all the music related stuff
        self.is_playing = False
        self.is_paused = False

        # 2d array containing [song, channel]
        self.music_queue = []
        self.YDL_OPTIONS = {'format': 'bestaudio/best'}
        self.FFMPEG_OPTIONS = {'options': '-vn'}

        self.vc = None
        self.ytdl = YoutubeDL(self.YDL_OPTIONS)
        self.caminho = subprocess.check_output(["which", "ffmpeg"], text=True).strip()

    # searching the item on youtube
    def search_yt(self, item):
        if item.startswith("https://"):
            title = self.ytdl.extract_info(item, download=False)["title"]
            return {'source': item, 'title': title}
        search = VideosSearch(item, limit=1)
        return {'source': search.result()["result"][0]["link"], 'title': search.result()["result"][0]["title"]}

    async def play_next(self):
        if len(self.music_queue) > 0:
            self.is_playing = True

            # get the first url
            m_url = self.music_queue[0][0]['source']

            # remove the first element as you are currently playing it
            self.music_queue.pop(0)
            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(None, lambda: self.ytdl.extract_info(m_url, download=False))
            song = data['url']
            self.vc.play(discord.FFmpegPCMAudio(song, executable=self.caminho, **self.FFMPEG_OPTIONS),
                         after=lambda e: asyncio.run_coroutine_threadsafe(self.play_next(), self.bot.loop))
        else:
            self.is_playing = False

    # infinite loop checking
    async def play_music(self, ctx):
        if len(self.music_queue) > 0:
            self.is_playing = True
            m_url = self.music_queue[0][0]['source']

            # try to connect to voice channel if you are not already connected
            if self.vc == None or not self.vc.is_connected():
                self.vc = await self.music_queue[0][1].connect()

                # in case we fail to connect
                if self.vc == None:
                    await ctx.send("```Could not connect to the voice channel```")
                    return
            else:
                await self.vc.move_to(self.music_queue[0][1])
            # remove the first element as you are currently playing it
            self.music_queue.pop(0)
            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(None, lambda: self.ytdl.extract_info(m_url, download=False))
            song = data['url']
            self.vc.play(discord.FFmpegPCMAudio(song, executable=self.caminho, **self.FFMPEG_OPTIONS),
                         after=lambda e: asyncio.run_coroutine_threadsafe(self.play_next(), self.bot.loop))

        else:
            self.is_playing = False

    @commands.command(name="play", aliases=["p", "playing"], help="Plays a selected song from youtube")
    async def play(self, ctx, *args):
        query = " ".join(args)
        try:
            voice_channel = ctx.author.voice.channel
        except:
            await ctx.send("```You need to connect to a voice channel first!```")
            return
        if self.is_paused:
            self.vc.resume()
        else:
            song = self.search_yt(query)
            if type(song) == type(True):
                await ctx.send(
                    "```Could not download the song. Incorrect format try another keyword. This could be due to playlist or a livestream format.```")
            else:
                if self.is_playing:
                    await ctx.send(f"**#{len(self.music_queue) + 2} -'{song['title']}'** added to the queue")
                else:
                    await ctx.send(f"**'{song['title']}'** added to the queue")
                self.music_queue.append([song, voice_channel])
                if self.is_playing == False:
                    await self.play_music(ctx)

    @commands.command(name="pause", help="Pauses the current song being played")
    async def pause(self, ctx, *args):
        if self.is_playing:
            self.is_playing = False
            self.is_paused = True
            self.vc.pause()
        elif self.is_paused:
            self.is_paused = False
            self.is_playing = True
            self.vc.resume()

    @commands.command(name="resume", aliases=["r"], help="Resumes playing with the discord bot")
    async def resume(self, ctx, *args):
        if self.is_paused:
            self.is_paused = False
            self.is_playing = True
            self.vc.resume()

    @commands.command(name="skip", aliases=["s"], help="Skips the current song being played")
    async def skip(self, ctx):
        if self.vc != None and self.vc:
            self.vc.stop()
            # try to play next in the queue if it exists
            await self.play_music(ctx)

    @commands.command(name="queue", aliases=["q"], help="Displays the current songs in queue")
    async def queue(self, ctx):
        retval = ""
        for i in range(0, len(self.music_queue)):
            retval += f"#{i + 1} -" + self.music_queue[i][0]['title'] + "\n"

        if retval != "":
            await ctx.send(f"```queue:\n{retval}```")
        else:
            await ctx.send("```No music in queue```")

    @commands.command(name="clear", aliases=["c", "bin"], help="Stops the music and clears the queue")
    async def clear(self, ctx):
        if self.vc != None and self.is_playing:
            self.vc.stop()
        self.music_queue = []
        await ctx.send("```Music queue cleared```")

    @commands.command(name="stop", aliases=["disconnect", "l", "d"], help="Kick the bot from VC")
    async def dc(self, ctx):
        self.is_playing = False
        self.is_paused = False
        await self.vc.disconnect()

    @commands.command(name="remove", help="Removes last song added to queue")
    async def re(self, ctx):
        self.music_queue.pop()
        await ctx.send("```last song removed```")

    @commands.command(name="wiki", help="pesquise alguma coisa na wikipidia")
    async def wiki(self, ctx: commands.Context, *, pesquisa):
        try:
            wikipedia.set_lang("pt")
            limite_resumo = 1500  # Limite para o resumo
            buscas = wikipedia.search(pesquisa)
            if not buscas:
                await ctx.reply("Nenhum resultado encontrado para essa pesquisa.")
                return

            pagina = wikipedia.page(buscas[0], auto_suggest=False)
            resumo = wikipedia.summary(pagina.title,
                                       sentences=5)  # Obter um resumo (ajuste o número de sentenças conforme necessário)
            link = pagina.url

            mensagem = f"**{pagina.title}**\n\n{resumo[:limite_resumo] + '...' if len(resumo) > limite_resumo else resumo}\n\nLeia mais: {link}"

            if len(mensagem) > 2000:  # Check if the final message exceeds Discord's limit
                partes = [mensagem[i:i + 2000] for i in range(0, len(mensagem), 2000)]
                for parte in partes:
                    await ctx.reply(parte)
            else:
                await ctx.reply(mensagem)

        except wikipedia.exceptions.PageError:
            await ctx.reply(f"Não encontrei a página '{pesquisa}' na Wikipédia em português.")
        except wikipedia.exceptions.DisambiguationError as e:
            await ctx.reply(
                f"Resultado ambíguo para '{pesquisa}'. Por favor, seja mais específico.\nOpções: {', '.join(e.options[:10])}")
        except Exception as erro:
            await ctx.reply(f"Ocorreu um erro ao buscar na Wikipédia: {erro}")
