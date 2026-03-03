#!/bin/bash
# System Health Check Script for DBT Platform
# Usage: ./check_system_health.sh

set -e

echo "╔════════════════════════════════════════════════════════════╗"
echo "║        DBT Platform - System Health Check                 ║"
echo "║        Version 1.1.0 - February 23, 2026                   ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check functions
check_docker() {
    echo -n "🐳 Checking Docker installation... "
    if command -v docker &> /dev/null; then
        echo -e "${GREEN}✅ Docker found ($(docker --version | cut -d' ' -f3 | tr -d ','))${NC}"
        return 0
    else
        echo -e "${RED}❌ Docker not installed${NC}"
        return 1
    fi
}

check_docker_compose() {
    echo -n "🐳 Checking Docker Compose... "
    if docker compose version &> /dev/null; then
        echo -e "${GREEN}✅ Docker Compose found ($(docker compose version --short))${NC}"
        return 0
    else
        echo -e "${RED}❌ Docker Compose not available${NC}"
        return 1
    fi
}

check_containers() {
    echo -n "📦 Checking Docker containers... "
    RUNNING=$(docker compose ps --filter "status=running" -q | wc -l | tr -d ' ')
    TOTAL=$(docker compose ps -q | wc -l | tr -d ' ')
    
    if [ "$RUNNING" -eq "$TOTAL" ] && [ "$RUNNING" -gt 0 ]; then
        echo -e "${GREEN}✅ All containers running ($RUNNING/$TOTAL)${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️  Some containers not running ($RUNNING/$TOTAL)${NC}"
        return 1
    fi
}

check_streamlit() {
    echo -n "🎨 Checking Streamlit service... "
    if curl -s -f http://localhost:8501/healthz > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Streamlit healthy${NC}"
        return 0
    else
        echo -e "${RED}❌ Streamlit not responding${NC}"
        return 1
    fi
}

check_postgres() {
    echo -n "🗄️  Checking PostgreSQL... "
    if docker compose exec -T postgres psql -U postgres -d dbt_db -c "SELECT 1;" &> /dev/null; then
        echo -e "${GREEN}✅ Database connected${NC}"
        return 0
    else
        echo -e "${RED}❌ Database not accessible${NC}"
        return 1
    fi
}

check_dbt_models() {
    echo -n "📊 Checking DBT models... "
    COUNT=$(docker compose exec -T postgres psql -U postgres -d dbt_db -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='dbt_marts';" 2>/dev/null | tr -d ' ')
    
    if [ "$COUNT" == "4" ]; then
        echo -e "${GREEN}✅ All 4 marts tables exist${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️  Expected 4 marts tables, found: $COUNT${NC}"
        return 1
    fi
}

check_data_integrity() {
    echo -n "🔍 Checking data integrity... "
    ORDERS=$(docker compose exec -T postgres psql -U postgres -d dbt_db -t -c "SELECT SUM(total_orders)::INT FROM dbt_marts.sales_summary;" 2>/dev/null | tr -d ' ')
    
    if [ "$ORDERS" == "830" ]; then
        echo -e "${GREEN}✅ Data validated (830 orders)${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️  Order count unexpected: $ORDERS (expected 830)${NC}"
        return 1
    fi
}

check_logs_for_errors() {
    echo -n "📋 Checking for errors in logs... "
    ERROR_COUNT=$(docker compose logs streamlit --tail=100 2>/dev/null | grep -i "error" | grep -v "ERROR_LOG" | grep -v "error_handler" | wc -l | tr -d ' ')
    
    if [ "$ERROR_COUNT" -eq 0 ]; then
        echo -e "${GREEN}✅ No errors in logs${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️  Found $ERROR_COUNT error lines${NC}"
        return 1
    fi
}

check_ports() {
    echo "🔌 Checking required ports..."
    PORTS=(8501 8000 5432 6379 8080)
    PORT_NAMES=("Streamlit" "FastAPI" "PostgreSQL" "Redis" "Weaviate")
    
    for i in "${!PORTS[@]}"; do
        PORT=${PORTS[$i]}
        NAME=${PORT_NAMES[$i]}
        
        if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
            echo -e "   ${GREEN}✅ Port $PORT ($NAME) is in use${NC}"
        else
            echo -e "   ${YELLOW}⚠️  Port $PORT ($NAME) not in use${NC}"
        fi
    done
}

check_git_status() {
    echo -n "📝 Checking git status... "
    CURRENT_COMMIT=$(git rev-parse --short HEAD 2>/dev/null)
    CURRENT_BRANCH=$(git branch --show-current 2>/dev/null)
    
    if [ "$CURRENT_BRANCH" == "nosa_clean" ]; then
        echo -e "${GREEN}✅ On branch: $CURRENT_BRANCH (commit: $CURRENT_COMMIT)${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️  On branch: $CURRENT_BRANCH (expected: nosa_clean)${NC}"
        return 1
    fi
}

check_disk_space() {
    echo -n "💾 Checking disk space... "
    AVAILABLE=$(df -h . | awk 'NR==2 {print $4}')
    echo -e "${GREEN}✅ Available: $AVAILABLE${NC}"
}

# Run all checks
echo "Starting comprehensive health check..."
echo ""

FAILED_CHECKS=0

check_docker || ((FAILED_CHECKS++))
check_docker_compose || ((FAILED_CHECKS++))
check_git_status || ((FAILED_CHECKS++))
check_disk_space
echo ""

check_containers || ((FAILED_CHECKS++))
check_streamlit || ((FAILED_CHECKS++))
check_postgres || ((FAILED_CHECKS++))
echo ""

check_dbt_models || ((FAILED_CHECKS++))
check_data_integrity || ((FAILED_CHECKS++))
check_logs_for_errors || ((FAILED_CHECKS++))
echo ""

check_ports
echo ""

# Summary
echo "╔════════════════════════════════════════════════════════════╗"
if [ $FAILED_CHECKS -eq 0 ]; then
    echo -e "║  ${GREEN}✅ ALL CHECKS PASSED - SYSTEM HEALTHY${NC}                  ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo ""
    echo "✨ Your DBT Platform is ready for use!"
    echo "🌐 Access at: http://localhost:8501"
    exit 0
else
    echo -e "║  ${YELLOW}⚠️  $FAILED_CHECKS CHECK(S) FAILED${NC}                              ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo ""
    echo "❗ Some issues detected. Please review the output above."
    echo "📚 See docs/DEPLOYMENT_CHECKLIST.md for troubleshooting."
    exit 1
fi
