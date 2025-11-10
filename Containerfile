# Use Fedora 43 as base image
FROM docker.io/library/fedora:43

# Set labels
LABEL maintainer="Your Name <your.email@example.com>"
LABEL description="MCP Server for Ansible Automation Platform"
LABEL version="1.0"

# Install Python and pip
RUN dnf install -y \
    python3 \
    python3-pip \
    && dnf clean all

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy application files
COPY server.py .
COPY aap_client.py .

# Create a non-root user to run the application
RUN useradd -m -u 1000 mcpuser && \
    chown -R mcpuser:mcpuser /app

# Switch to non-root user
USER mcpuser

# Expose the port the app runs on
EXPOSE 8000

# Set environment variables (can be overridden at runtime)
ENV AAP_URL="" \
    AAP_TOKEN="" \
    AAP_PROJECT_ID="" \
    AAP_VERIFY_SSL="True" \
    AAP_TIMEOUT="30" \
    AAP_MAX_RETRIES="3"

# Health check - verify port is listening
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python3 -c "import socket; s=socket.socket(); s.settimeout(5); s.connect(('localhost', 8000)); s.close()" || exit 1

# Run the server
CMD ["python3", "server.py"]

