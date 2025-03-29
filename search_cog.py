import discord
from discord.ext import commands
import wikipedia

class search_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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
