FROM python:3.13-slim

# Install ffmpeg
RUN apt-get update && apt-get install -y ffmpeg

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

CMD ["python", "bot.py"]