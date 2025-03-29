# Usa uma imagem base do Python
FROM python:3.11

# Instala ffmpeg
RUN apt-get update && apt-get install -y ffmpeg

# Define o diretório de trabalho dentro do contêiner
WORKDIR /app

# Copia os arquivos do bot para o contêiner
COPY . .

# Instala as dependências do projeto
RUN pip install --no-cache-dir -r requirements.txt

# Comando para rodar o bot
CMD ["python", "main.py"]
