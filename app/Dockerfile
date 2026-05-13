# Dockerfile for the SACU Liquid Fuels Model documentation app.
#
# Build:
#   docker build -f app/Dockerfile -t lfm-docs:latest .
#
# Run:
#   docker run --rm -p 8501:8501 lfm-docs:latest
#
# The image bundles the docs, the package, and Streamlit. No assumption
# extraction or model runs happen inside the container — this is a viewer.

FROM python:3.11-slim AS runtime

# Streamlit runs as non-root by convention.
RUN useradd --create-home --shell /bin/bash streamlit
WORKDIR /home/streamlit/app

# Install build prerequisites for the few wheels Streamlit needs to compile.
RUN apt-get update \
    && apt-get install --no-install-recommends -y \
        build-essential \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Install the package + the app extra so the markdown loader can import
# the lfm namespace (not strictly needed for v1 but cheap and avoids
# surprises if a page later wants to import lfm).
COPY pyproject.toml ./
COPY src ./src
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -e ".[app]"

# Application + docs.
COPY app ./app
COPY docs ./docs
COPY README.md CLAUDE.md ./

RUN chown -R streamlit:streamlit /home/streamlit
USER streamlit

EXPOSE 8501

# Streamlit reads STREAMLIT_SERVER_* env vars; defaults are fine for internal hosting.
# Healthcheck pings the built-in liveness endpoint.
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl --fail http://localhost:8501/_stcore/health || exit 1

ENTRYPOINT ["streamlit", "run", "app/streamlit_app.py", \
            "--server.address=0.0.0.0", \
            "--server.port=8501", \
            "--server.headless=true", \
            "--browser.gatherUsageStats=false"]
