FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml README.md ./
COPY src/ src/
RUN pip install --no-cache-dir -e . \
    && addgroup --system mcp && adduser --system --ingroup mcp mcp
USER mcp
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/')" || exit 1
CMD ["python", "-m", "src.server"]
