FROM python:3.14-slim

COPY --from=denoland/deno:bin /deno /usr/local/bin/deno
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg ca-certificates

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

ENTRYPOINT ["fastapi", "run", "main.py"]
CMD ["--host", "0.0.0.0"]
