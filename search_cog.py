import discord
from discord.ext import commands
import wikipedia
import requests
import os

class search_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.token_imdb = os.getenv("TOKEN_IMDB")
        self.linkImagem = "https://image.tmdb.org/t/p/w300_and_h450_bestv2"
        self.idioma = "pt-br"
        self.url = f"https://api.themoviedb.org/3/trending/movie/week?api_key={self.token_imdb}&language={self.idioma}"
        self.url_pesquisa = f"https://api.themoviedb.org/3/search/movie?api_key={self.token_imdb}"


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

    @commands.command(name="clima", help="pesquise o cliem em uma cidade")
    async def clima(self, ctx: commands.Context, *,cidade):
        try:
            # Obter coordenadas da cidade via Open-Meteo (geocoding)
            geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={cidade}&count=1&language=pt&format=json"
            geo_response = requests.get(geo_url).json()

            if "results" not in geo_response:
                await ctx.send("❌ Cidade não encontrada. Verifique o nome e tente novamente.")
                return

            latitude = geo_response["results"][0]["latitude"]
            longitude = geo_response["results"][0]["longitude"]
            cidade_nome = geo_response["results"][0]["name"]

            # Obter previsão do tempo
            weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current_weather=true&timezone=America/Sao_Paulo"
            weather_response = requests.get(weather_url).json()

            temperatura = weather_response["current_weather"]["temperature"]
            vento = weather_response["current_weather"]["windspeed"]

            # Enviar resposta formatada
            mensagem = (
                f"🌍 **Clima em {cidade_nome}:**\n"
                f"🌡️ Temperatura: {temperatura}°C\n"
                f"💨 Velocidade do vento: {vento} km/h"
            )
            await ctx.reply(mensagem)

        except Exception as e:
            await ctx.send("❌ Erro ao buscar o clima. Tente novamente mais tarde.")

    @commands.command(name="dolar", help="pesquise cotação do dolar")
    async def dolar(self, ctx: commands.Context):
        try:
            url = "https://economia.awesomeapi.com.br/json/last/USD-BRL"
            response = requests.get(url).json()

            if "USDBRL" not in response:
                await ctx.send("❌ Erro ao buscar a cotação. Tente novamente mais tarde.")
                return

            cotacao = float(response["USDBRL"]["bid"])
            variacao = float(response["USDBRL"]["varBid"])
            data = response["USDBRL"]["create_date"]

            emoji_variacao = "📈" if variacao >= 0 else "📉"

            mensagem = (
                f"💰 **Cotação do Dólar** 💵\n"
                f"💵 1 USD = R$ {cotacao:.2f}\n"
                f"{emoji_variacao} Variação: R$ {variacao:.2f}\n"
                f"🕒 Atualizado em: {data}"
            )
            await ctx.reply(mensagem)

        except Exception as e:
            await ctx.send("❌ Erro ao buscar a cotação. Tente novamente mais tarde.")

    @commands.command(name="filmes", help="retorna uma lista de filmes")
    async def filmes(self, ctx: commands.Context):
        try:
            data = requests.get(self.url).json()
            lista_resultados = data["results"]

            for filme in lista_resultados:
                await ctx.reply(f"""
                Nome: {filme["title"]}
                Sinopse: {filme["overview"]}
                Nota: {filme["vote_average"]}⭐
                {self.linkImagem+"/"+filme["poster_path"]}
                """)
            # await ctx.reply("buscado")
        except Exception as error:
            await ctx.reply(error)

    @commands.command(name="pesquisa_filme", help="pesquisa um filme por nome")
    async def pesquisa_filme(self, ctx: commands.Context, *,nome_filme):
        try:
            # print(self.url + f"&query={nome_filme}")
            data = requests.get(self.url_pesquisa + f"&query={nome_filme}").json()
            lista_resultados = data["results"]

            for filme in lista_resultados:
                if filme:
                    await ctx.reply(f"""
                    Nome: {filme["title"]}
                    Sinopse: {filme["overview"]}
                    Nota: {filme["vote_average"]}⭐
                    {self.linkImagem + "/" + filme["poster_path"]}
                """)
                    filme_id = filme["id"]
                    for tr in self.retorna_lista_trailes(filme_id):
                        await ctx.send(f"https://www.youtube.com/embed/{tr['key']}")
                else:
                    await ctx.reply(f"Sem resultado para a pesquisa: {nome_filme}")

            # await ctx.reply(nome_filme)
        except Exception as error:
            await ctx.reply(error)

    def retorna_lista_trailes(self, filme_id):
        try:
            url_trailer = f"https://api.themoviedb.org/3/movie/{filme_id}/videos?api_key={self.token_imdb}&language={self.idioma}"
            trailers_json = requests.get(url_trailer).json()
            data_tr = trailers_json["results"]
            return data_tr
        except Exception as erro:
            print(erro)
            return [];