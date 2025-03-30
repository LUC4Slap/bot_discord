import discord
from discord.ext import commands


class help_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.help_message = ""
        self.text_channel_list = []
        self.set_message()

    def set_message(self):
        self.help_message = f"""
            ```
General commands:
{self.bot.command_prefix}help - exibe todos os comandos disponíveis
{self.bot.command_prefix}q - exibe a fila de músicas atual
{self.bot.command_prefix}p - encontra a música no youtube e a reproduz no seu canal atual. Retoma a reprodução da música atual se ela foi pausada
{self.bot.command_prefix}skip - pula a música atual que está sendo tocada
{self.bot.command_prefix}clear - Para a música e limpa a fila
{self.bot.command_prefix}stop - Desconectou o bot do canal de voz
{self.bot.command_prefix}pause - pausa a música atual que está sendo tocada ou retoma se já estiver pausada
{self.bot.command_prefix}resume - retoma a reprodução da música atual
{self.bot.command_prefix}prefix - alterar prefixo de comando
{self.bot.command_prefix}remove - remove a última música da fila
{self.bot.command_prefix}wiki - faz uma busca na wikipidia - ex: [!wiki brasil]
{self.bot.command_prefix}clima - faz uma busca do clime em uma cidade
{self.bot.command_prefix}dolar - traz a cotação atual do dolar
{self.bot.command_prefix}filmes - traz os top 10 filmes do imdb
{self.bot.command_prefix}pesquisa_filme - permite fazer uma busca de um filme no imdb
            ```
            """

    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.change_presence(activity=discord.Game(f"type {self.bot.command_prefix}help"))

    @commands.command(name="help", help="Displays all the available commands")
    async def help(self, ctx):
        await ctx.send(self.help_message)

    @commands.command(name="prefix", help="Change bot prefix")
    async def prefix(self, ctx, *args):
        self.bot.command_prefix = " ".join(args)
        self.set_message()
        await ctx.send(f"prefix set to **'{self.bot.command_prefix}'**")
        await self.bot.change_presence(activity=discord.Game(f"type {self.bot.command_prefix}help"))

    @commands.command(name="send_to_all", help="send a message to all members")
    async def send_to_all(self, msg):
        for text_channel in self.text_channel_list:
            await text_channel.send(msg)