import discord
from discord.ext import commands
import wikipedia
import requests

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
