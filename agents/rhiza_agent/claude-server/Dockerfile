FROM ubuntu:22.04

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Install dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    python3 \
    python3-pip \
    python3-venv \
    nodejs \
    npm \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user
RUN useradd -m -s /bin/bash claude

# Switch to claude user
USER claude
WORKDIR /home/claude

# Install Claude CLI (as user)
RUN curl -fsSL https://console.anthropic.com/install.sh | sh

# Add claude to PATH
ENV PATH="/home/claude/.local/bin:${PATH}"

# Copy entrypoint script
COPY --chown=claude:claude entrypoint.sh /home/claude/
RUN chmod +x /home/claude/entrypoint.sh

# Set working directory for the project mount
WORKDIR /app/project

ENTRYPOINT ["/home/claude/entrypoint.sh"]
CMD ["claude", "mcp", "serve", "--port", "8090"]