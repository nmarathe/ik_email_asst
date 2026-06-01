# Stage 1: Build & Dependencies
FROM python:3.11-slim as builder
WORKDIR /app

# Install system dependencies if required for compiling certain wheels
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements to leverage Docker caching
COPY requirements.txt .

# Install dependencies into a wheels cache or directly
RUN pip install --no-cache-dir --user -r requirements.txt


# Stage 2: Final Runtime
FROM python:3.11-slim as runner
WORKDIR /app

# 1. Create the system user AND explicitly build the home directory
RUN groupadd -g 10001 appuser && \
    useradd -u 10001 -g appuser -m -s /bin/sh appuser && \
    mkdir -p /home/appuser/.streamlit

# 2. Copy dependencies and application files, granting ownership during the copy
COPY --from=builder --chown=appuser:appuser /root/.local /home/appuser/.local
COPY --chown=appuser:appuser . .

# 3. Ensure full directory ownership for safety
RUN chown -R appuser:appuser /app /home/appuser

# Switch to the non-root user
USER appuser

# Expose Streamlit's default port
EXPOSE 8501

# Update PATH to use packages installed by the builder
ENV PATH=/home/appuser/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1

# Configure Streamlit behavior inside Docker
ENTRYPOINT ["streamlit", "run", "src/ui/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
