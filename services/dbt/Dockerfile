# Use official dbt PostgreSQL image
FROM ghcr.io/dbt-labs/dbt-postgres:1.9.latest

# Set working directory
WORKDIR /dbt

# Install additional dependencies
RUN apt-get update && apt-get install -y \
    curl \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy dbt project files
COPY dbt_project.yml .
COPY profiles.yml /root/.dbt/profiles.yml
COPY models/ models/
COPY tests/ tests/
#COPY macros/ macros/
COPY seeds/ seeds/
COPY snapshots/ snapshots/
COPY analyses/ analyses/

# Copy entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Expose port for dbt docs
EXPOSE 8002

# Set entrypoint
ENTRYPOINT ["/entrypoint.sh"]
