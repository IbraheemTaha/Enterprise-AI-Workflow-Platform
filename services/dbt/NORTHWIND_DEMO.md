# Northwind DBT Demo Guide 🫀

This guide walks you through the complete Northwind demo - demonstrating how DBT transforms raw data into production-ready analytics.

---

## 📚 Table of Contents

1. [Overview](#overview)
2. [What is Northwind?](#what-is-northwind)
3. [Data Architecture](#data-architecture)
4. [Exploring the Demo](#exploring-the-demo)
5. [Understanding the Models](#understanding-the-models)
6. [Running Queries](#running-queries)
7. [Creating Your Own Models](#creating-your-own-models)
8. [Best Practices](#best-practices)

---

## Overview

The Northwind demo showcases a complete DBT pipeline:

- **Source Data**: Classic Northwind database (orders, customers, products)
- **Staging Layer**: 6 cleaned and standardized views
- **Marts Layer**: 4 analytics-ready tables
- **Data Tests**: 51 automated quality checks
- **Documentation**: Full lineage graphs and catalog

### Quick Access

- **DBT Platform**: http://localhost:8501 → sidebar → **DBT Platform**
- **DBT Documentation**: http://localhost:8002

---

## What is Northwind?

Northwind is a sample database originally created by Microsoft to demonstrate database features. It represents a small import/export company with:

- **Customers**: 91 companies from 21 countries
- **Orders**: 830 orders over ~2 years
- **Products**: 77 products across 8 categories
- **Employees**: 9 employees managing sales

**Why we use it:**
- ✅ Realistic business data with complex relationships
- ✅ Perfect size for learning (not too big, not too simple)
- ✅ Widely recognized in data engineering tutorials
- ✅ Demonstrates common analytics patterns

---

## Data Architecture

### 3-Layer Architecture

```
┌─────────────────────────────────────────────────────────┐
│  RAW LAYER (public schema)                              │
│  ─────────────────────────────────────────────────────  │
│  • customers, orders, order_details                     │
│  • products, categories, suppliers                      │
│  • employees, shippers, territories                     │
│                                                          │
│  Status: As-is from source (messy, inconsistent)        │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼ DBT Transformation
┌─────────────────────────────────────────────────────────┐
│  STAGING LAYER (dbt_staging schema)                     │
│  ─────────────────────────────────────────────────────  │
│  • stg_customers     → Cleaned, standardized names      │
│  • stg_orders        → Added shipping metrics           │
│  • stg_order_details → Calculated amounts               │
│  • stg_products      → Inventory flags                  │
│  • stg_employees     → Tenure calculations              │
│  • stg_categories    → Standardized text                │
│                                                          │
│  Status: Clean, tested, documented views                │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼ DBT Transformation
┌─────────────────────────────────────────────────────────┐
│  MARTS LAYER (dbt_marts schema)                         │
│  ─────────────────────────────────────────────────────  │
│  • customer_analytics    → LTV, segments, status        │
│  • sales_summary         → Daily/monthly trends         │
│  • product_performance   → Revenue ranks, lifecycle     │
│  • employee_performance  → Sales metrics, quality       │
│                                                          │
│  Status: Analytics-ready, business-focused tables       │
└─────────────────────────────────────────────────────────┘
```

### Data Flow

1. **Ingestion**: Northwind SQL loaded into `public` schema
2. **Staging**: DBT creates clean views in `dbt_staging`
3. **Marts**: DBT builds aggregated tables in `dbt_marts`
4. **Consumption**: Streamlit, LangChain, APIs query marts

---

## Initializing the Demo

The first time you open the **📊 Northwind Demo** tab, a 3-step setup wizard appears. Each step shows a description of what will happen and a button to confirm before execution.

### Step 0 — Introduction
Read the overview (91 customers, 830 orders, 10 DBT models, 51 tests) and click **🚀 Start Demo Setup**.

### Step 1 — Load Dataset
- Click **▶️ Load Dataset**
- The SQL file (~400 KB) is automatically downloaded from GitHub into `./data/northwind/` if not already cached
- All Northwind tables are loaded into the `public` schema in PostgreSQL
- A log shows progress and row counts for `customers`, `orders`, `products`, `order_details`, `employees`
- On success, click **▶️ Next Step →**

### Step 2 — Run DBT Transformation
- Click **▶️ Run DBT Transformation**
- The UI automatically triggers `dbt run` inside the `dbt-transform` container via the Docker socket — **no terminal command is needed**
- Live DBT output is displayed in the log area
- On success (PASS=10), click **▶️ Next Step →**
- If the Docker socket is unavailable, a fallback manual command is shown: `docker exec dbt-transform dbt run`

### Step 3 — Verify & Finish
- Click **▶️ Verify Tables**
- The UI queries `dbt_marts` to confirm all 4 mart tables exist and contain data
- A balloon animation confirms success — click **🚀 Start Exploring Analytics**

### Resetting the Demo
To start over from scratch, use the **🗑️ Reset Demo** expander (top-right of the Northwind Demo tab). It drops all Northwind raw tables and DBT schemas. You can optionally delete the cached SQL file to force a re-download.

---

## Exploring the Demo

### 1. DBT Platform — Northwind Demo

Navigate to **http://localhost:8501**, click **DBT Platform** in the sidebar, then select the **📊 Northwind Demo** tab.

If the demo has not been initialized yet, a setup wizard will appear. Follow the 3-step wizard (see [Initializing the Demo](#initializing-the-demo)) before the analytics tabs become available.

#### Tab 1: Dashboard Overview
- Real-time KPIs (revenue, orders, customers)
- Top customers by revenue chart
- Revenue trend over time
- Product performance rankings
- Employee sales metrics

**Try this:**
1. Identify the top customer by lifetime value
2. Find which product category generates the most revenue
3. See if there are seasonal revenue patterns

#### Tab 2: Data Explorer
- Browse all DBT models (staging + marts)
- Preview data with adjustable row limits
- Download as CSV
- View column types and stats

**Try this:**
1. Select "Customer Analytics"
2. Set limit to 100 rows
3. Download the data
4. Open in Excel/Google Sheets

#### Tab 3: SQL Query
- Write custom SQL queries against any schema
- Use pre-built templates
- Export results instantly

**Try this:**
1. Select "Top customers by revenue" template
2. Click "▶️ Execute Query"
3. Modify the LIMIT to see more results
4. Download query results

#### Tab 4: Advanced Analytics
- Customer cohort analysis (sunburst chart)
- Product category performance (treemap)
- Geographic distribution (maps & charts)
- Time series analysis

**Try this:**
1. Select "Customer Cohort Analysis"
2. Examine the sunburst chart layers
3. Identify which segment has the highest average LTV

### 2. DBT Documentation Server

Navigate to **http://localhost:8002**

#### Lineage Graph (DAG)
- Visual representation of all model dependencies
- Click nodes to see model details
- Trace data flow from sources to marts

**Try this:**
1. Click "View DAG" or navigate to Graph
2. Find `customer_analytics` node
3. Trace backwards to see all dependencies
4. Notice how it uses `stg_customers`, `stg_orders`, `stg_order_details`

#### Model Details
- SQL source code for each model
- Column descriptions
- Test results
- Relationships

**Try this:**
1. Search for `customer_analytics`
2. View the "Details" tab
3. Read column descriptions
4. Check "Tests" tab to see all passed tests

---

## Understanding the Models

### Staging Models

#### stg_customers.sql
**Purpose**: Clean and standardize customer data

```sql
-- Key transformations:
- UPPER(TRIM(company_name)) → Standardized company names
- regexp_replace(phone) → Cleaned phone numbers
- current_timestamp as loaded_at → Audit trail
```

**Use cases:**
- Customer lookup by ID
- Geographic analysis by city/country
- Contact information retrieval

#### stg_orders.sql
**Purpose**: Enrich orders with calculated shipping metrics

```sql
-- Key transformations:
- is_shipped → Boolean flag for shipped orders
- is_late_shipment → Identifies late deliveries
- days_to_ship → Shipping duration calculation
```

**Use cases:**
- Order tracking
- Shipping performance analysis
- Late shipment identification

#### stg_order_details.sql
**Purpose**: Calculate line-item amounts

```sql
-- Key transformations:
- gross_amount = unit_price * quantity
- net_amount = gross_amount * (1 - discount)
- discount_amount = gross_amount * discount
```

**Use cases:**
- Revenue calculations
- Discount analysis
- Order profitability

#### stg_products.sql
**Purpose**: Add inventory management flags

```sql
-- Key transformations:
- is_discontinued → Product status flag
- needs_reorder → Stock below threshold
- is_out_of_stock → Zero stock alert
- total_available_units → Current + on_order
```

**Use cases:**
- Inventory monitoring
- Reorder automation
- Product catalog filtering

### Marts Models

#### customer_analytics.sql
**Purpose**: Customer 360° view with lifetime value

**Key metrics:**
- `lifetime_revenue` - Total spent by customer
- `total_orders` - Order count
- `customer_segment` - High/Medium/Low value
- `customer_status` - Active/At Risk/Churned
- `late_shipment_rate_pct` - Service quality metric

**Business questions answered:**
- Who are our top customers?
- Which customers are at risk of churning?
- What's the average customer lifetime value?
- Which geographic regions generate most revenue?

**Sample query:**
```sql
SELECT 
    company_name,
    lifetime_revenue,
    customer_segment,
    customer_status
FROM dbt_marts.customer_analytics
WHERE customer_segment = 'High Value'
AND customer_status = 'Active'
ORDER BY lifetime_revenue DESC;
```

#### sales_summary.sql
**Purpose**: Daily sales trends and time-series analysis

**Key metrics:**
- `net_revenue` - Daily revenue after discounts
- `total_orders` - Orders per day
- `unique_customers` - Customer count per day
- `month_to_date_revenue` - Running MTD total
- `year_to_date_revenue` - Running YTD total

**Business questions answered:**
- What's our daily revenue trend?
- Are we seeing seasonal patterns?
- How does this month compare to last month?
- What's the revenue growth rate?

**Sample query:**
```sql
SELECT 
    TO_CHAR(order_date, 'YYYY-MM') as month,
    SUM(net_revenue) as monthly_revenue,
    COUNT(DISTINCT order_date) as active_days
FROM dbt_marts.sales_summary
GROUP BY TO_CHAR(order_date, 'YYYY-MM')
ORDER BY month DESC;
```

#### product_performance.sql
**Purpose**: Product-level sales and inventory analytics

**Key metrics:**
- `net_revenue` - Total product revenue
- `total_units_sold` - Quantity sold
- `revenue_rank` - Performance ranking
- `revenue_contribution_pct` - % of total revenue
- `product_lifecycle_stage` - Active/Declining/Inactive

**Business questions answered:**
- What are our best-selling products?
- Which products contribute most to revenue?
- Are there products that need promotion?
- What's the product lifecycle distribution?

**Sample query:**
```sql
SELECT 
    product_name,
    category_name,
    net_revenue,
    revenue_rank,
    product_lifecycle_stage
FROM dbt_marts.product_performance
WHERE revenue_rank <= 20
ORDER BY revenue_rank;
```

#### employee_performance.sql
**Purpose**: Sales rep performance and accountability

**Key metrics:**
- `total_revenue` - Revenue generated by employee
- `total_orders` - Orders processed
- `unique_customers` - Customer count served
- `revenue_per_year_employed` - Productivity metric
- `late_shipment_rate_pct` - Service quality

**Business questions answered:**
- Who are our top-performing sales reps?
- Which employees need additional training?
- What's the correlation between tenure and performance?
- Are there service quality issues?

**Sample query:**
```sql
SELECT 
    full_name,
    title,
    total_revenue,
    revenue_rank,
    late_shipment_rate_pct
FROM dbt_marts.employee_performance
ORDER BY revenue_rank;
```

---

## Running Queries

### Via DBT Platform (Recommended)

1. Go to http://localhost:8501 and click **DBT Platform** in the sidebar
2. Navigate to the **📊 Northwind Demo** tab → **💬 SQL Query** sub-tab
3. Choose a template or write custom SQL
4. Click **▶️ Execute Query**
5. Download results as needed

### Via PostgreSQL CLI

```bash
# Connect to database
docker exec -it postgres psql -U postgres -d dbt_db

# Run query
SELECT * FROM dbt_marts.customer_analytics LIMIT 10;

# Exit
\q
```

### Via Python/Pandas

```python
import os
import psycopg2
import pandas as pd

conn = psycopg2.connect(
    host=os.getenv("POSTGRES_HOST", "localhost"),
    port=int(os.getenv("POSTGRES_PORT", "5432")),
    database=os.getenv("DBT_DB", "dbt_db"),
    user=os.getenv("POSTGRES_USER", "postgres"),
    password=os.getenv("POSTGRES_PASSWORD"),
)

df = pd.read_sql("""
    SELECT * FROM dbt_marts.customer_analytics
    ORDER BY lifetime_revenue DESC
    LIMIT 10
""", conn)

print(df)
```

---

## Creating Your Own Models

### Example: Create a "Top Products" Mart

**Step 1: Create staging model** (if needed)

You already have `stg_products.sql`, so skip to Step 2.

**Step 2: Create marts model**

Create file: `services/dbt/models/marts/top_products_by_category.sql`

```sql
{{
    config(
        materialized='table',
        tags=['northwind', 'marts', 'custom']
    )
}}

with products as (
    select * from {{ ref('stg_products') }}
),

categories as (
    select * from {{ ref('stg_categories') }}
),

order_details as (
    select * from {{ ref('stg_order_details') }}
),

product_sales as (
    select
        od.product_id,
        sum(od.net_amount) as total_revenue,
        sum(od.quantity) as total_units_sold
    from order_details od
    group by od.product_id
),

final as (
    select
        c.category_name,
        p.product_name,
        ps.total_revenue,
        ps.total_units_sold,
        row_number() over (
            partition by c.category_name 
            order by ps.total_revenue desc
        ) as rank_in_category
    from products p
    join categories c on p.category_id = c.category_id
    left join product_sales ps on p.product_id = ps.product_id
)

select * from final
where rank_in_category <= 3
order by category_name, rank_in_category
```

**Step 3: Document the model**

Add to `services/dbt/models/marts/schema.yml`:

```yaml
  - name: top_products_by_category
    description: Top 3 products by revenue for each category
    columns:
      - name: category_name
        description: Product category
      - name: product_name
        description: Product name
      - name: rank_in_category
        description: Revenue rank within category (1 = highest)
```

**Step 4: Run DBT**

```bash
docker compose exec dbt dbt run --select top_products_by_category
docker compose exec dbt dbt test --select top_products_by_category
docker compose exec dbt dbt docs generate
```

**Step 5: Query the new model**

```sql
SELECT * FROM dbt_marts.top_products_by_category;
```

---

## Best Practices

### 1. Naming Conventions

- **Staging**: `stg_<source_table>`
- **Marts**: `<business_concept>` (e.g., `customer_analytics`, `sales_summary`)
- **Intermediate**: `int_<description>` (rarely used in this demo)

### 2. Model Organization

```
models/
├── sources.yml          # Source definitions
├── staging/
│   ├── stg_*.sql       # One file per source table
│   └── schema.yml      # Staging model docs
└── marts/
    ├── *_analytics.sql # Business-focused models
    └── schema.yml      # Marts model docs
```

### 3. Testing Strategy

**Staging layer:**
- `unique` on primary keys
- `not_null` on required fields
- `relationships` for foreign keys

**Marts layer:**
- `unique` on grain fields
- `not_null` on critical metrics
- Custom tests for business logic

### 4. Documentation

- Always add column descriptions
- Explain business logic in model descriptions
- Use YAML for tests and schema
- Keep README files updated

### 5. Materialization Strategy

- **Staging**: `view` (always fresh, no storage)
- **Marts**: `table` (fast queries, scheduled refresh)
- **Large data**: `incremental` (process only new rows)

---

## Troubleshooting

### Models not appearing?

```bash
# Check compilation
docker compose exec dbt dbt compile

# Run specific model
docker compose exec dbt dbt run --select stg_customers

# Check logs
docker compose logs dbt
```

### Tests failing?

```bash
# Run tests with details
docker compose exec dbt dbt test --store-failures

# Check specific test
docker compose exec dbt dbt test --select stg_customers
```

### Data quality issues?

```sql
-- Check for NULLs
SELECT COUNT(*) FROM dbt_staging.stg_customers WHERE customer_id IS NULL;

-- Check for duplicates
SELECT customer_id, COUNT(*) 
FROM dbt_staging.stg_customers 
GROUP BY customer_id 
HAVING COUNT(*) > 1;
```

---

## Next Steps

1. **Explore More**: Try all query templates in the DBT Platform's **💬 SQL Query** tab
2. **Create Custom Models**: Follow the guide above to build your own marts
3. **Integrate with AI**: Connect these models to LangChain agents or RAG systems
4. **Read the Full README**: Check [services/dbt/README.md](./README.md) for architecture details

---

## Resources

- **DBT Official Docs**: https://docs.getdbt.com/
- **DBT Best Practices**: https://docs.getdbt.com/guides/best-practices
- **Northwind Database Schema**: https://github.com/pthom/northwind_psql
- **PostgreSQL Documentation**: https://www.postgresql.org/docs/

---

**Questions?** Check the [DBT Platform](http://localhost:8501) or explore [DBT Documentation](http://localhost:8002).

**Happy Data Transforming!** 🫀
