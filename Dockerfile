# syntax=docker/dockerfile:1

FROM python:3.12-slim

# 使用 uv 官方镜像中的可执行文件，无需额外 pip 安装
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    HF_ENDPOINT=https://hf-mirror.com \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=0

WORKDIR /app

# 先只拷贝依赖清单：依赖不变时这层走缓存，重建镜像很快
COPY pyproject.toml uv.lock ./
# --no-install-project：本项目是应用而非可安装包，跳过自身构建
# --no-dev：不安装 locust 等开发依赖
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-install-project

# 可选：构建时就把 Embedding 模型下载好，避免容器首次启动时才下载（慢）
# RUN python -c "from huggingface_hub import snapshot_download; snapshot_download('BAAI/bge-small-zh-v1.5')"

# 拷贝应用代码与静态资源
COPY app ./app
COPY scripts ./scripts
COPY frontend ./frontend
COPY data ./data

# 使用 uv 创建的虚拟环境
ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000

# 启动预热检索器需要时间，start-period 给足
HEALTHCHECK --interval=30s --timeout=5s --start-period=180s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/research_assistant/health')" || exit 1

# 容器内必须监听 0.0.0.0，否则宿主机端口映射进不来
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
