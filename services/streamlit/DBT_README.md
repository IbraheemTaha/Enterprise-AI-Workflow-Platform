# DBT: The Heart of Your Data Workflow 📊

> **"Without clean, modular, well-structured data, even the most advanced AI agents and models will fail to deliver value."**

---

## 🎯 Why DBT is Critical to This Platform

In the world of AI and machine learning, **data is everything**. But raw data alone isn't enough—it must be:
- **Clean** - Free from errors and inconsistencies
- **Structured** - Organized for efficient querying
- **Documented** - Understandable by both humans and AI
- **Tested** - Validated for quality and integrity
- **Versioned** - Trackable through changes

**This is where DBT becomes the beating heart of your AI workflow.**

---

## 🔄 The Data-to-AI Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│  RAW DATA (User Uploads, CSV, Documents, APIs)                 │
│  • Messy, unstructured, inconsistent                           │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│  🫀 DBT - DATA TRANSFORMATION ENGINE (THE HEART)                │
│  ════════════════════════════════════════════════════════════  │
│  1. STAGING: Clean & standardize raw data                      │
│  2. TRANSFORMATION: Apply business logic & joins               │
│  3. MARTS: Create analytics-ready datasets                     │
│  4. TESTING: Validate data quality automatically               │
│  5. DOCUMENTATION: Generate lineage & schema docs              │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│  CLEAN, STRUCTURED DATA (PostgreSQL, Weaviate)                 │
│  • Ready for AI/ML models                                      │
│  • Quality-assured and tested                                  │
│  • Fully documented and traceable                              │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ├──────►  LLMs (OpenAI, Claude, Gemini)
                     ├──────►  RAG Systems (via Weaviate)
                     ├──────►  AI Agents (LangChain)
                     ├──────►  Analytics (Grafana, Streamlit)
                     └──────►  ML Models (MLflow)
```

---

## 💡 The Problem DBT Solves

### Without DBT:
❌ Data scattered across multiple sources  
❌ Inconsistent formats and naming  
❌ No data quality checks  
❌ Manual, error-prone transformations  
❌ No visibility into data lineage  
❌ AI models working with dirty data = **Poor Results**  

### With DBT:
✅ Single source of truth for all transformed data  
✅ Standardized, tested data transformations  
✅ Automated data quality validation  
✅ SQL-based, version-controlled transformations  
✅ Visual data lineage and documentation  
✅ AI models working with clean data = **Excellent Results**  

---

## 🏗️ DBT Architecture in This Platform

### 1. **Data Ingestion**
Source data is loaded into PostgreSQL via the Northwind Demo wizard in Streamlit:
- **Northwind Dataset** → 8 source tables loaded into the `public` schema of `dbt_db`
- **Custom data** → Any tables pre-loaded into the `public` schema can be modelled with dbt

### 2. **Staging Layer** (Silver Tables)
Clean and standardize raw data:
```sql
-- Example: Clean customer data
SELECT
    customer_id,
    UPPER(TRIM(company_name)) AS company_name,
    clean_phone(phone) AS phone_standardized,
    CURRENT_TIMESTAMP AS loaded_at
FROM raw.customers
WHERE customer_id IS NOT NULL
```

### 3. **Transformation Layer** (Gold Tables)
Apply business logic and create analytics-ready datasets:
```sql
-- Example: Customer lifetime value
SELECT
    c.customer_id,
    c.company_name,
    SUM(o.total_amount) AS lifetime_value,
    COUNT(o.order_id) AS total_orders,
    AVG(o.total_amount) AS avg_order_value
FROM staging.customers c
LEFT JOIN staging.orders o ON c.customer_id = o.customer_id
GROUP BY 1, 2
```

### 4. **Marts Layer** (Analytics)
Purpose-built datasets for specific use cases:
- **Analytics Marts** → Streamlit dashboards  
- **AI Marts** → Vector embeddings for Weaviate  
- **ML Marts** → Features for MLflow models  

### 5. **Data Quality Testing**
Automatic validation on every run:
```yaml
tests:
  - unique
  - not_null
  - relationships
  - accepted_values
  - custom_business_rules
```

---


### BigQuery-Like Features:
1. **Serverless Execution** → DBT runs automatically on data changes  
2. **SQL-First** → All transformations in familiar SQL  
3. **Scalable** → Handles datasets from KB to GB  
4. **Interactive Queries** → Query marts directly from Streamlit  
5. **Data Catalog** → Auto-generated docs at http://localhost:8002  
6. **Version Control** → All transformations tracked in Git  
7. **Incremental Updates** → Process only new/changed data  

### Example: Northwind Database Demo
We use the classic **Northwind** dataset (orders, customers, products) to demonstrate:
- How raw sales data becomes actionable insights  
- Real-time data transformations  
- Quality testing and validation  
- Integration with AI/ML workflows  

---

## 📊 Real-World Use Cases

### Use Case 1: Customer Analytics for AI Agents
**Problem**: AI agent needs to recommend products  
**DBT Solution**:
1. **Staging**: Clean customer purchase history  
2. **Transform**: Calculate customer preferences  
3. **Marts**: Create `customer_recommendations` table  
4. **AI Integration**: LangChain agent queries this table  

### Use Case 2: Document RAG Pipeline
**Problem**: Users upload PDFs for Q&A  
**DBT Solution**:
1. **Staging**: Extract text, metadata from documents  
2. **Transform**: Clean, chunk, enrich content  
3. **Marts**: Create searchable document catalog  
4. **AI Integration**: Weaviate indexes these chunks  

### Use Case 3: Real-Time Analytics
**Problem**: Business needs live dashboard  
**DBT Solution**:
1. **Staging**: Ingest streaming data  
2. **Transform**: Aggregate metrics  
3. **Marts**: Create dashboard-ready views  
4. **AI Integration**: Streamlit displays real-time  

---

## 🛠️ How It Works: Step-by-Step

### Step 1: Load Source Data
```
Streamlit → DBT Platform → Northwind Demo → Load Dataset
→ PostgreSQL public schema (orders, customers, products, ...)
```

### Step 2: Run DBT Transformations
```bash
# Via Streamlit wizard (recommended) or directly:
docker exec dbt-transform dbt run    # Build staging views + mart tables
docker exec dbt-transform dbt test   # Run 51 data quality checks
docker exec dbt-transform dbt docs generate  # Rebuild docs
```

### Step 3: AI Consumes Clean Data
```python
import os
import psycopg2, pandas as pd

conn = psycopg2.connect(
    host=os.getenv("POSTGRES_HOST", "postgres"),
    port=int(os.getenv("POSTGRES_PORT", "5432")),
    database=os.getenv("DBT_DB", "dbt_db"),
    user=os.getenv("POSTGRES_USER", "postgres"),
    password=os.getenv("POSTGRES_PASSWORD"),
)
df = pd.read_sql("SELECT * FROM dbt_marts.customer_analytics", conn)
```

---

## 📁 Project Structure

```
services/dbt/
├── README.md                    # ← You are here
├── dbt_project.yml             # Project configuration
├── profiles.yml                # Database connections
├── models/
│   ├── sources.yml             # Define raw data sources
│   ├── staging/                # Layer 1: Clean data
│   │   ├── stg_customers.sql
│   │   ├── stg_orders.sql
│   │   └── schema.yml
│   └── marts/                  # Layer 2: Analytics-ready
│       ├── customer_analytics.sql
│       ├── sales_summary.sql
│       └── schema.yml
├── tests/                      # Custom data quality tests
├── macros/                     # Reusable SQL functions
├── analyses/                   # Ad-hoc queries
└── target/                     # Generated docs & artifacts
```

---

## 🚀 Quick Start

### 1. View Demo (Northwind Dataset)
```bash
# Access DBT documentation
open http://localhost:8002

# Explore:
# - Data lineage graph
# - Model documentation
# - Column descriptions
# - Test results
```

### 2. Query Transformed Data
```python
# From any service (Streamlit, LangChain, FastAPI)
import os
import psycopg2, pandas as pd

conn = psycopg2.connect(
    host=os.getenv("POSTGRES_HOST", "postgres"),
    port=int(os.getenv("POSTGRES_PORT", "5432")),
    database=os.getenv("DBT_DB", "dbt_db"),
    user=os.getenv("POSTGRES_USER", "postgres"),
    password=os.getenv("POSTGRES_PASSWORD"),
)
df = pd.read_sql("SELECT * FROM dbt_marts.customer_analytics", conn)
```

---

## 🧪 Data Quality: The Foundation of AI Success

### Why Data Quality Matters for AI:

**Scenario**: You're building an AI chatbot for customer service.

❌ **Without DBT Testing**:
```
User: "Show my order status"
AI: "Error: Found 3 customers with the same ID"
User: "What did I buy last month?"
AI: "Order total: $-500.00" (negative price!)
```

✅ **With DBT Testing**:
```
User: "Show my order status"
AI: "Your order #12345 shipped yesterday, arrives Friday"
User: "What did I buy last month?"
AI: "3 items totaling $125.50 - Coffee Maker, Mug Set, Beans"
```

### DBT Tests Prevent:
- **Duplicate records** → Confuses AI models  
- **NULL values** → Breaks predictions  
- **Invalid data** → Garbage in = Garbage out  
- **Broken relationships** → Incomplete context  
- **Schema changes** → Model failures  

---

## 📈 DBT + AI: Better Together

```
┌──────────────────────────────────────────────────────────┐
│  Traditional AI Workflow (Without DBT)                   │
├──────────────────────────────────────────────────────────┤
│  Raw Data → Manual Cleaning → Hope for the best → AI    │
│  ⏱️  Slow | 🐛 Error-prone | 📉 Poor Results            │
└──────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────┐
│  Modern AI Workflow (With DBT)                           │
├──────────────────────────────────────────────────────────┤
│  Raw Data → DBT Pipeline → Tested Data → High-Quality AI│
│  ⚡ Fast | ✅ Reliable | 📈 Excellent Results            │
└──────────────────────────────────────────────────────────┘
```

---

## 🎯 Key Takeaways

1. **DBT is not optional** - It's the foundation that makes everything else work  
2. **Clean data = Smart AI** - No amount of fancy models can fix dirty data  
3. **SQL is powerful** - Transform data where it lives (PostgreSQL)  
4. **Testing is automatic** - Catch errors before they reach users  
5. **Documentation is free** - Auto-generated and always up-to-date  
6. **Scalability is built-in** - From demo to production without changes  

---

## 🔗 Integration Points

- ✅ **PostgreSQL** — Central relational database for the platform; dbt writes to `dbt_staging` and `dbt_marts` schemas in `dbt_db`
- ✅ **Streamlit** — Web UI for the platform; DBT Platform page reads mart tables to power the Dashboard, Data Explorer, and SQL Query tabs
- ✅ **DBT Docs** — Auto-generated interactive documentation, lineage graph, and schema reference at `http://localhost:8002`
- ✅ **Weaviate** — Vector database used by LangChain for RAG; clean structured data from dbt marts is available as a source for embedding workflows
- ✅ **LangChain** — RAG and chat service backed by Weaviate and PostgreSQL; mart tables provide structured context for AI queries
- ℹ️ **Airflow** — Workflow orchestration service available in the platform for scheduling and pipeline management
- ℹ️ **MLflow** — Experiment tracking and artifact storage service available in the platform

---

## 📚 Learn More

### Official DBT Resources:
- [DBT Documentation](https://docs.getdbt.com/)  
- [DBT Best Practices](https://docs.getdbt.com/guides/best-practices)  
- [DBT Discourse Community](https://discourse.getdbt.com/)  

### This Project:
- [Architecture Docs](../../docs/ARCHITECTURE.md)
- [Northwind Demo Guide](./NORTHWIND_DEMO.md)

---

## 💬 Philosophy

> **"Data transformation is not just a technical step—it's the bridge between raw information and actionable intelligence. DBT makes this bridge solid, tested, and reliable."**

In this platform:
- **Without DBT**: Raw source tables → Unstructured queries → Inconsistent results
- **With DBT**: Source tables → Tested, documented marts → Reliable AI and analytics outcomes

---

## 🏆 Success Metrics

With DBT as the heart of your workflow, you can expect:

| Metric | Without DBT | With DBT |
|--------|-------------|----------|
| **Data Quality** | ~60% | >95% |
| **AI Accuracy** | Variable | Consistent |
| **Debug Time** | Hours | Minutes |
| **Trust in Data** | Low | High |
| **Scalability** | Limited | Unlimited |
| **Documentation** | Outdated | Real-time |

---

## 🎨 Remember

**DBT isn't just a tool—it's the architectural decision that makes your entire AI platform trustworthy, scalable, and production-ready.**

Every LLM call, every RAG query, every ML prediction depends on the quality of data flowing through DBT. Invest in getting this right, and everything else becomes easier.

---

**Ready to see it in action?** 👉 [Northwind Demo Guide](./NORTHWIND_DEMO.md)
