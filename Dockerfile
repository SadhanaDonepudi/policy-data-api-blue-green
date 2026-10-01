
FROM python:3.12-slim
WORKDIR /code
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
COPY scripts ./scripts
RUN python -c "import sys; sys.path.insert(0,'.'); from app.store import init_db; init_db()"
EXPOSE 8000
HEALTHCHECK --interval=10s CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health')"
CMD ["uvicorn","app.main:app","--host","0.0.0.0","--port","8000"]
