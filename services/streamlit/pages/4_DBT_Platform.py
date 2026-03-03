"""
DBT Platform - Complete Data Transformation Interface
Combines: Welcome, Northwind Demo, Documentation
"""

import streamlit as st
import pandas as pd
import psycopg2
import plotly.express as px
import plotly.graph_objects as go
from io import StringIO
import re
import json
from pathlib import Path
import time
import os
import requests

# Page config
st.set_page_config(
    page_title="DBT Analytics Platform",
    page_icon="🏗️",
    layout="wide"
)

# Navigation sidebar
st.sidebar.title("Navigation")
st.sidebar.page_link("Home.py", label="🏠 Home")
st.sidebar.page_link("pages/1_Chat.py", label="📝 Chat")
st.sidebar.page_link("pages/2_System_Health.py", label="💚 System Health")
st.sidebar.page_link("pages/3_LangChain_Demo.py", label="🔗 LangChain Demo")
st.sidebar.page_link("pages/4_DBT_Platform.py", label="📊 DBT Platform")
st.sidebar.page_link("pages/5_FastAPI_Docs.py", label="⚡ FastAPI Docs")
st.sidebar.divider()

# Helper functions for SQL queries
def get_db_connection():
    """Create database connection"""
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "postgres"),
        port=5432,
        database=os.getenv("DBT_DB", "dbt_db"),
        user=os.getenv("POSTGRES_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD", "change_me_please"),
    )

@st.cache_data(ttl=300)
def run_query(query: str) -> pd.DataFrame:
    """Execute SQL query and return DataFrame"""
    conn = None
    try:
        conn = get_db_connection()
        df = pd.read_sql(query, conn)
        return df
    except Exception as e:
        st.error(f"Query failed: {str(e)}")
        return pd.DataFrame()
    finally:
        if conn:
            conn.close()

def load_readme(file_path: str) -> str:
    """Load README markdown content"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error loading README: {str(e)}"

# ==================== DEMO SETUP FUNCTIONS ====================

def check_northwind_installed() -> bool:
    """Check if Northwind data is already loaded"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'customers');")
        exists = cur.fetchone()[0]
        cur.close()
        conn.close()
        return exists
    except:
        return False

def check_dbt_models_ready() -> bool:
    """Check if DBT models are built"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        # Check if marts schema and tables exist
        cur.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'dbt_marts' 
                AND table_name = 'customer_analytics'
            );
        """)
        exists = cur.fetchone()[0]
        cur.close()
        conn.close()
        return exists
    except:
        return False

NORTHWIND_SQL_URL = "https://raw.githubusercontent.com/pthom/northwind_psql/master/northwind.sql"
NORTHWIND_SQL_PATH = "/data/northwind/northwind.sql"

def download_northwind_sql(progress_callback=None) -> bool:
    """Download the Northwind SQL file from GitHub into /data/northwind/"""
    try:
        data_dir = Path(NORTHWIND_SQL_PATH).parent
        data_dir.mkdir(parents=True, exist_ok=True)

        if progress_callback:
            progress_callback(f"⬇️ Downloading Northwind SQL from GitHub...")

        response = requests.get(NORTHWIND_SQL_URL, timeout=60)
        response.raise_for_status()

        with open(NORTHWIND_SQL_PATH, "w", encoding="utf-8") as f:
            f.write(response.text)

        size_kb = len(response.content) // 1024
        if progress_callback:
            progress_callback(f"✅ Downloaded {size_kb} KB → {NORTHWIND_SQL_PATH}")
        return True
    except Exception as e:
        if progress_callback:
            progress_callback(f"❌ Download failed: {str(e)}")
        return False


def load_northwind_data(progress_callback=None) -> bool:
    """Download (if needed) and load the Northwind dataset into PostgreSQL.
    Skips loading if all key tables already exist and contain rows.
    """
    conn = None
    try:
        if progress_callback:
            progress_callback("📂 Checking for Northwind SQL file...")

        sql_file = NORTHWIND_SQL_PATH

        # Download from GitHub if the file is not present on the shared volume
        if not os.path.exists(sql_file):
            ok = download_northwind_sql(progress_callback)
            if not ok:
                return False

        if progress_callback:
            progress_callback("🔌 Connecting to PostgreSQL database...")

        conn = get_db_connection()
        # autocommit=True makes psycopg2 use PQexec() instead of PQexecParams(),
        # which is the only way to execute a SQL file with multiple statements.
        conn.autocommit = True
        cur = conn.cursor()

        key_tables = ["customers", "orders", "products", "order_details", "employees"]

        # ------------------------------------------------------------
        # ✅ NEW: Skip loading if all key tables exist and have rows
        # ------------------------------------------------------------
        if progress_callback:
            progress_callback("🔎 Checking if Northwind is already loaded...")

        all_exist_and_filled = True
        for tbl in key_tables:
            # Check table exists (current schema search_path)
            cur.execute(
                """
                SELECT EXISTS (
                    SELECT 1
                    FROM information_schema.tables
                    WHERE table_schema = current_schema()
                      AND table_name = %s
                );
                """,
                (tbl,),
            )
            exists = cur.fetchone()[0]
            if not exists:
                all_exist_and_filled = False
                break

            # If it exists, check it has rows
            cur.execute(f"SELECT COUNT(*) FROM {tbl};")
            cnt = cur.fetchone()[0]
            if cnt == 0:
                all_exist_and_filled = False
                break

        if all_exist_and_filled:
            if progress_callback:
                progress_callback("✅ Northwind tables already exist and contain data. Skipping load.")
            cur.close()
            return True

        # ------------------------------------------------------------
        # 📊 Load if missing / empty
        # ------------------------------------------------------------
        if progress_callback:
            progress_callback("📊 Loading Northwind tables into database...")

        # Read and execute SQL
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()

        # Execute the entire SQL file in one call.
        # autocommit + PQexec supports multiple statements in a single execute().
        cur.execute(sql_content)

        if progress_callback:
            progress_callback("🔍 Verifying data in key tables...")

        # Verify that all essential tables exist AND have rows
        all_ok = True
        for tbl in key_tables:
            cur.execute(f"SELECT COUNT(*) FROM {tbl};")
            cnt = cur.fetchone()[0]
            if cnt > 0:
                if progress_callback:
                    progress_callback(f"  ✅ {tbl}: {cnt} rows")
            else:
                if progress_callback:
                    progress_callback(f"  ❌ {tbl}: 0 rows — data did not load!")
                all_ok = False

        cur.close()

        if not all_ok:
            if progress_callback:
                progress_callback("❌ Some tables are empty. Please delete the SQL file and try again.")
            return False

        if progress_callback:
            progress_callback("✅ All Northwind tables loaded successfully!")

        return True
    except Exception as e:
        if progress_callback:
            progress_callback(f"❌ Error loading data: {str(e)}")
        return False
    finally:
        if conn:
            conn.close()

DOCKER_SOCKET = "/var/run/docker.sock"
DBT_CONTAINER = "dbt-transform"

def run_dbt_via_docker(cmd=None, progress_callback=None, timeout=300) -> bool:
    """Run a dbt command inside the dbt-transform container via the Docker socket.
    Uses curl (available in the Streamlit image) to talk to the Docker Engine API.
    Returns True on success, False on failure (caller can then show a manual fallback).
    """
    import subprocess

    cmd = cmd or ["dbt", "run"]
    cmd_str = " ".join(cmd)

    try:
        if not os.path.exists(DOCKER_SOCKET):
            if progress_callback:
                progress_callback(f"⚠️ Docker socket not found at {DOCKER_SOCKET}")
            return False

        if progress_callback:
            progress_callback("🐳 Connecting to Docker API via socket...")

        # ── Step 1: Create exec instance ────────────────────────────────
        exec_payload = json.dumps({
            "AttachStdout": True,
            "AttachStderr": True,
            "Cmd": cmd,
            "WorkingDir": "/dbt",
        })

        create = subprocess.run(
            [
                "curl", "-s", "-X", "POST",
                "--unix-socket", DOCKER_SOCKET,
                f"http://localhost/containers/{DBT_CONTAINER}/exec",
                "-H", "Content-Type: application/json",
                "-d", exec_payload,
            ],
            capture_output=True, text=True, timeout=10,
        )

        if create.returncode != 0 or not create.stdout.strip():
            if progress_callback:
                progress_callback(f"❌ Docker API unreachable: {create.stderr[:200]}")
            return False

        resp = json.loads(create.stdout)
        if "message" in resp:
            if progress_callback:
                progress_callback(f"❌ Docker error: {resp['message']}")
            return False

        exec_id = resp["Id"]
        if progress_callback:
            progress_callback(f"⚙️ Running {cmd_str}...")

        # ── Step 2: Start exec — blocking, streams output via Tty ───────
        start = subprocess.run(
            [
                "curl", "-s", "-X", "POST",
                "--unix-socket", DOCKER_SOCKET,
                f"http://localhost/exec/{exec_id}/start",
                "-H", "Content-Type: application/json",
                "-d", json.dumps({"Detach": False, "Tty": True}),
            ],
            capture_output=True, text=True, timeout=timeout,
        )

        # Display cleaned-up dbt output
        if start.stdout:
            clean = re.sub(r"\x1b\[[0-9;]*[a-zA-Z]", "", start.stdout)  # strip ANSI
            for line in clean.split("\n"):
                line = line.strip()
                if line and progress_callback:
                    progress_callback(f"  {line}")

        # ── Step 3: Inspect exec to get exit code ───────────────────────
        inspect = subprocess.run(
            [
                "curl", "-s",
                "--unix-socket", DOCKER_SOCKET,
                f"http://localhost/exec/{exec_id}/json",
            ],
            capture_output=True, text=True, timeout=10,
        )

        exit_code = json.loads(inspect.stdout).get("ExitCode", -1)

        if exit_code == 0:
            if progress_callback:
                progress_callback(f"✅ {cmd_str} completed successfully!")
            return True
        else:
            if progress_callback:
                progress_callback(f"❌ {cmd_str} exited with code {exit_code}")
            return False

    except subprocess.TimeoutExpired:
        if progress_callback:
            progress_callback(f"❌ {cmd_str} timed out after {timeout}s")
        return False
    except Exception as e:
        if progress_callback:
            progress_callback(f"❌ Docker exec error: {str(e)}")
        return False

def reset_dbt_docs(progress_callback=None) -> bool:
    """Regenerate dbt docs to reflect the reset database state.

    dbt docs generate writes manifest.json / catalog.json in-place inside
    the existing target/ directory, so the already-running dbt docs serve
    picks up the new files automatically — no killing or restart required.
    """
    return run_dbt_via_docker(
        cmd=["dbt", "docs", "generate"],
        progress_callback=progress_callback,
        timeout=120,
    )


def reset_northwind_demo(delete_sql_file: bool = False, progress_callback=None) -> bool:
    """Drop all Northwind raw tables and DBT schemas so the demo can be re-run."""
    conn = None
    try:
        conn = get_db_connection()
        conn.autocommit = True
        cur = conn.cursor()

        # Drop DBT output schemas (CASCADE removes all tables/views inside them)
        for schema in ("dbt_marts", "dbt_staging", "dbt"):
            cur.execute(f"DROP SCHEMA IF EXISTS {schema} CASCADE;")
            if progress_callback:
                progress_callback(f"  ✅ Dropped schema {schema}")

        # Drop the Northwind raw tables from the public schema
        northwind_tables = [
            "customer_customer_demo", "customer_demographics",
            "employee_territories", "order_details", "orders",
            "customers", "products", "suppliers", "categories",
            "employees", "shippers", "territories", "region", "us_states",
        ]
        for tbl in northwind_tables:
            cur.execute(f"DROP TABLE IF EXISTS public.{tbl} CASCADE;")
            if progress_callback:
                progress_callback(f"  ✅ Dropped public.{tbl}")

        cur.close()

        # Optionally remove the cached SQL file so it is re-downloaded next time
        if delete_sql_file and os.path.exists(NORTHWIND_SQL_PATH):
            os.remove(NORTHWIND_SQL_PATH)
            if progress_callback:
                progress_callback(f"  ✅ Deleted cached SQL file")

        if progress_callback:
            progress_callback("✅ Database reset complete — ready for a fresh demo!")
        return True
    except Exception as e:
        if progress_callback:
            progress_callback(f"❌ Reset failed: {str(e)}")
        return False
    finally:
        if conn:
            conn.close()


def wait_for_dbt_models(progress_callback=None, max_wait_seconds=60) -> bool:
    """Wait for DBT models to be available in database"""
    try:
        start_time = time.time()
        check_interval = 2  # Check every 2 seconds
        last_count = -1
        
        while (time.time() - start_time) < max_wait_seconds:
            try:
                conn = get_db_connection()
                cur = conn.cursor()
                
                # Check if DBT has created the marts schema and tables
                cur.execute("""
                    SELECT COUNT(*) 
                    FROM information_schema.tables 
                    WHERE table_schema = 'dbt_marts' 
                    AND table_name IN ('customer_analytics', 'sales_summary', 'product_performance', 'employee_performance')
                """)
                table_count = cur.fetchone()[0]
                
                cur.close()
                conn.close()
                
                if table_count >= 4:  # All 4 mart tables exist
                    if progress_callback:
                        progress_callback(f"✅ All 4 mart tables verified!")
                    return True
                else:
                    # Only log when count changes to reduce spam
                    if table_count != last_count:
                        if progress_callback:
                            progress_callback(f"📊 Tables found: {table_count}/4")
                        last_count = table_count
                
            except Exception:
                # Tables don't exist yet, keep waiting
                pass
            
            time.sleep(check_interval)
        
        # Timeout
        if progress_callback:
            progress_callback(f"⏱️ Still waiting... ({last_count}/4 tables detected)")
        return False
        
    except Exception as e:
        if progress_callback:
            progress_callback(f"❌ Error: {str(e)}")
        return False

# ==================== MAIN APP ====================

# Initialize session state
if 'demo_initialized' not in st.session_state:
    st.session_state.demo_initialized = check_northwind_installed() and check_dbt_models_ready()
if 'setup_step' not in st.session_state:
    # 0 = intro, 1 = loading data, 2 = waiting for dbt run, 3 = verifying tables
    st.session_state.setup_step = 0
if 'reset_armed' not in st.session_state:
    st.session_state.reset_armed = False
if 'step_started' not in st.session_state:
    # False = show step preview + action button; True = execute the step
    st.session_state.step_started = False

st.title("🏗️ DBT Analytics Platform")
st.markdown("**Transform raw data into analytics-ready insights**")

# Create tabs
tab1, tab2, tab3 = st.tabs([
    "🏠 Welcome",
    "📊 Northwind Demo", 
    #"⬆️ Create Project",
    "📚 Documentation"
])

# ==================== TAB 1: WELCOME ====================
with tab1:
    st.header("Welcome to DBT Analytics Platform")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        ### What is DBT?
        
        **DBT (Data Build Tool)** transforms raw data into analytics-ready datasets using:
        - **SQL transformations** - Write modular, reusable SQL
        - **Version control** - Track changes like code
        - **Automated testing** - Validate data quality
        - **Documentation** - Auto-generate lineage graphs
        
        ### What We Offer
        
        This platform provides **two powerful capabilities**:
        
        #### 1. 📊 Northwind Demo
        Explore a **production-ready analytics pipeline** built on the classic Microsoft Northwind database:
        - **91 customers**, 830 orders, $1.3M revenue
        - **10 DBT models** (6 staging views + 4 mart tables)
        - **51 automated tests** ensuring data quality
        - **Interactive dashboards** for exploration
        #### 2. 📚 Comprehensive Documentation        
            
        ### Architecture
        
        ```
        Raw Data → DBT Staging → DBT Marts → Analytics
           ↓           ↓            ↓           ↓
        messy      cleaned    aggregated   insights
        ```
        """)
    
    with col2:
        # Demo status box
        if st.session_state.demo_initialized:
            st.success("**✅ Northwind Demo Ready!**\n\nClick the **📊 Northwind Demo** tab above to explore the analytics.")
            
            st.metric("Demo Customers", "91")
            st.metric("Demo Orders", "830")
            st.metric("Total Models", "10")
            st.metric("Data Tests", "51 ✅")
        else:
            st.info("**🎯 Ready to Start the Demo?**\n\nClick the **📊 Northwind Demo** tab above and press the setup button to get started!")
            
            st.markdown("**What you'll get:**")
            st.markdown("• 91 customers across 21 countries")
            st.markdown("• 830 orders ($1.3M revenue)")
            st.markdown("• 10 DBT models with analytics")
            st.markdown("• Automated quality tests")
        
        #if not st.session_state.demo_initialized:
        #    st.divider()
        #    st.markdown("**Or...**")
        #    st.info("**💡 Pro Tip**\n\nYou can also upload your own CSV in the **⬆️ Create Project** tab!")

# ==================== TAB 3: CREATE PROJECT ====================
# Rendered before tab2 so that st.stop() inside tab2 does not prevent this tab from loading.
#with tab3:
#    st.header("⬆️ Create Your DBT Project")

#    st.markdown("""
#    ### Upload CSV & Generate DBT Models

#    Upload your CSV file and we'll:
#    1. ✅ Automatically detect schema (column types)
#    2. ✅ Create PostgreSQL table in `user_uploads` schema
#    3. ✅ Generate production-ready DBT staging model SQL
#    4. ✅ Provide downloadable `.sql` file
#    """)

#    col1, col2 = st.columns([2, 1])

#    with col1:
#        # File uploader
#        uploaded_file = st.file_uploader(
#            "Choose a CSV file",
#            type=['csv'],
#            help="Upload CSV with column headers"
#        )

#        if uploaded_file is not None:
#            # Read CSV
#            df = pd.read_csv(uploaded_file)

#            st.success(f"✅ File loaded: {len(df)} rows, {len(df.columns)} columns")

#            # Preview
#            st.subheader("Data Preview")
#            st.dataframe(df.head(10), use_container_width=True)

#            # Schema detection
#            st.subheader("Detected Schema")
#            schema_df = pd.DataFrame([
#                {"Column": col, "Type": str(df[col].dtype), "SQL Type": infer_sql_type(df[col].dtype)}
#                for col in df.columns
#            ])
#            st.dataframe(schema_df, use_container_width=True, hide_index=True)

#    with col2:
#        if uploaded_file is not None:
#            st.subheader("Configuration")

#            # Table name
#            default_name = re.sub(r'[^a-z0-9_]', '_', uploaded_file.name.lower().replace('.csv', ''))
#            table_name = st.text_input("Table Name:", value=default_name)

#            # Schema selection
#            schema = st.selectbox("PostgreSQL Schema:", ["user_uploads", "public"])

#            # Upload button
#            if st.button("🚀 Upload & Create Table", type="primary"):
#                with st.spinner("Creating table..."):
#                    success = create_table_from_df(df, table_name, schema)
#                    if success:
#                        st.success(f"✅ Table `{schema}.{table_name}` created with {len(df)} rows!")

#                        # Generate DBT model
#                        dbt_sql = generate_dbt_staging_model(table_name, df)

#                        st.subheader("📄 Generated DBT Model")
#                        st.code(dbt_sql, language='sql')

#                        # Download button
#                        st.download_button(
#                            label="📥 Download DBT Model",
#                            data=dbt_sql,
#                            file_name=f"stg_{table_name}.sql",
#                            mime="text/plain"
#                        )

#                        st.info(f"""
#                        **Next Steps:**
#                        1. Save `stg_{table_name}.sql` to `services/dbt/models/staging/`
#                        2. Add source to `models/sources.yml`
#                        3. Run `dbt run` to materialize
#                        """)

# ==================== TAB 4: DOCUMENTATION ====================
# Rendered before tab2 so that st.stop() inside tab2 does not prevent this tab from loading.
with tab3:
    st.header("📚 Documentation")

    doc_tab1, doc_tab2 = st.tabs(["📖 DBT README", "📘 Northwind Guide"])

    with doc_tab1:
        st.subheader("DBT Platform Guide")
        readme_path = "/app/DBT_README.md"
        readme_content = load_readme(readme_path)
        st.markdown(readme_content)

    with doc_tab2:
        st.subheader("Northwind Demo Tutorial")
        guide_path = "/app/NORTHWIND_DEMO.md"
        guide_content = load_readme(guide_path)
        st.markdown(guide_content)

# ==================== TAB 2: NORTHWIND DEMO ====================
with tab2:
    st.header("📊 Northwind Analytics Demo")

    # Re-check demo status on every load (only if not yet initialized)
    if not st.session_state.demo_initialized:
        st.session_state.demo_initialized = check_northwind_installed() and check_dbt_models_ready()

    # Show setup wizard if demo not ready
    if not st.session_state.demo_initialized:
        st.markdown("---")

        col1, col2, col3 = st.columns([1, 2, 1])

        with col2:
            step = st.session_state.setup_step

            # ── STEP 0: Intro ────────────────────────────────────────────
            if step == 0:
                st.markdown("""
                <div style='text-align: center; padding: 2rem;'>
                    <h2>🎯 Initialize Northwind Demo</h2>
                    <p style='font-size: 1.2rem; color: #666;'>
                    One-click setup to experience DBT's power with real data
                    </p>
                </div>
                """, unsafe_allow_html=True)

                st.info("""
                **What you'll get:**

                🏢 **Complete Business Analytics** from the Northwind Trading Company
                - 91 customers across 21 countries
                - 830 orders totaling $1.3M in revenue
                - 77 products across 8 categories

                🏗️ **Production-Grade DBT Project**
                - 6 staging models (cleaned data)
                - 4 analytical marts (business insights)
                - 51 automated data quality tests
                - Full data lineage documentation
                """)

                st.markdown("### 📋 Setup Steps")
                st.markdown("""
                1. **Load Dataset** — Download & import Northwind data into PostgreSQL
                2. **Run DBT** — Build 10 models automatically via Docker
                3. **Verify** — Confirm all tables and data are ready

                Each step shows a preview and a button — you're in control.
                ⏱️ **Total time:** ~1 minute
                """)

                if st.button("🚀 Start Demo Setup", type="primary", use_container_width=True, key="start_setup"):
                    st.session_state.setup_step = 1
                    st.rerun()

            # ── STEP 1 ────────────────────────────────────────────────────
            elif step == 1:
                st.progress(0.15)
                st.subheader("📥 Step 1 of 3 — Load Northwind Dataset")

                if not st.session_state.step_started:
                    # Preview: tell the user what will happen, let them confirm
                    st.info(
                        "This step will **download** the Northwind SQL file from GitHub "
                        "(~400 KB) into `./data/northwind/` and **load all tables** "
                        "into PostgreSQL.\n\n"
                        "Tables created: `customers`, `orders`, `products`, "
                        "`order_details`, `employees`, and more."
                    )
                    if st.button("▶️ Load Dataset", type="primary", use_container_width=True, key="run_step1"):
                        st.session_state.step_started = True
                        st.rerun()

                else:
                    # Execute: run the load, then wait for user to press Next
                    log_lines = []
                    log_box = st.empty()

                    def _log(msg):
                        log_lines.append(msg)
                        log_box.text("\n".join(log_lines))

                    with st.spinner("Loading data into PostgreSQL…"):
                        success = load_northwind_data(_log)

                    if success:
                        st.success("✅ Northwind data loaded successfully!")
                        if st.button("▶️ Next Step →", type="primary", use_container_width=True, key="next_step1"):
                            st.session_state.setup_step = 2
                            st.session_state.step_started = False
                            st.rerun()
                    else:
                        st.error("❌ Data loading failed. Check the log above.")
                        if st.button("🔄 Try Again", key="retry_load"):
                            st.session_state.step_started = False
                            st.rerun()

            # ── STEP 2 ────────────────────────────────────────────────────
            elif step == 2:
                st.success("✅ Step 1/3: Northwind data loaded!")
                st.progress(0.5)
                st.subheader("🏗️ Step 2 of 3 — Run DBT Transformation")

                if not st.session_state.step_started:
                    # Preview
                    st.info(
                        "This step runs **`dbt run`** inside the `dbt-transform` container, "
                        "which builds:\n\n"
                        "- 6 **staging views** (cleaned source data)\n"
                        "- 4 **mart tables** (business analytics)\n\n"
                        "The command is triggered automatically via the Docker socket."
                    )
                    if st.button("▶️ Run DBT Transformation", type="primary", use_container_width=True, key="run_step2"):
                        st.session_state.step_started = True
                        st.rerun()

                else:
                    # Execute
                    log_lines = []
                    log_box = st.empty()

                    def _log_dbt(msg):
                        log_lines.append(msg)
                        log_box.text("\n".join(log_lines))

                    with st.spinner("Running dbt run inside the dbt-transform container…"):
                        dbt_ok = run_dbt_via_docker(cmd=["dbt", "run"], progress_callback=_log_dbt, timeout=300)
                        if dbt_ok:
                            run_dbt_via_docker(cmd=["dbt", "docs", "generate"], progress_callback=_log_dbt, timeout=60)

                    if dbt_ok:
                        st.success("✅ DBT transformation complete!")
                        if st.button("▶️ Next Step →", type="primary", use_container_width=True, key="next_step2"):
                            st.session_state.setup_step = 3
                            st.session_state.step_started = False
                            st.rerun()
                    else:
                        # Fallback: Docker socket unavailable or exec failed
                        st.warning(
                            "⚠️ Auto-run failed. Run the command below manually, "
                            "then click **Verify Tables**."
                        )
                        st.code("docker exec dbt-transform dbt run", language="bash")
                        if st.button("✅ DBT Run Complete — Verify Tables", type="primary", use_container_width=True):
                            st.session_state.setup_step = 3
                            st.session_state.step_started = False
                            st.rerun()

            # ── STEP 3 ────────────────────────────────────────────────────
            elif step == 3:
                st.success("✅ Step 1/3: Northwind data loaded!")
                st.success("✅ Step 2/3: DBT transformation complete!")
                st.progress(0.8)
                st.subheader("✔️ Step 3 of 3 — Verify & Finish")

                if not st.session_state.step_started:
                    # Preview
                    st.info(
                        "This step **queries the database** to confirm that all 4 mart "
                        "tables exist and contain data, then marks the demo as ready."
                    )
                    if st.button("▶️ Verify Tables", type="primary", use_container_width=True, key="run_step3"):
                        st.session_state.step_started = True
                        st.rerun()

                else:
                    # Execute
                    log_lines = []
                    log_box = st.empty()

                    def _log3(msg):
                        log_lines.append(msg)
                        log_box.text("\n".join(log_lines))

                    _log3("Checking for DBT mart tables…")
                    with st.spinner("Verifying…"):
                        verify_success = wait_for_dbt_models(_log3, max_wait_seconds=15)

                    if verify_success:
                        try:
                            conn = get_db_connection()
                            cur = conn.cursor()
                            cur.execute("SELECT COUNT(*) FROM dbt_marts.customer_analytics;")
                            customer_count = cur.fetchone()[0]
                            cur.execute("SELECT COUNT(*) FROM dbt_marts.sales_summary;")
                            sales_count = cur.fetchone()[0]
                            cur.close()
                            conn.close()

                            _log3(f"✅ customer_analytics: {customer_count} records")
                            _log3(f"✅ sales_summary: {sales_count} records")
                            _log3("✅ All tables verified!")

                            st.session_state.demo_initialized = True
                            st.session_state.setup_step = 0
                            st.session_state.step_started = False

                            st.balloons()
                            st.success(
                                "🎉 **Northwind Demo is Ready!**\n\n"
                                "All data has been loaded and DBT models have been built successfully."
                            )
                            if st.button("🚀 Start Exploring Analytics", type="primary", use_container_width=True):
                                st.rerun()

                        except Exception as e:
                            st.error(f"❌ Verification failed: {str(e)}")
                            st.session_state.step_started = False
                            if st.button("🔄 Go Back & Retry", key="retry_verify"):
                                st.session_state.setup_step = 2
                                st.rerun()
                    else:
                        st.warning("⚠️ Tables not found. Make sure `dbt run` completed successfully.")
                        st.session_state.step_started = False
                        if st.button("🔄 Try Again", key="retry_verify2"):
                            st.session_state.setup_step = 2
                            st.rerun()

        st.stop()  # Don't render analytics tabs until demo is ready
    
    # Demo is ready - show analytics tabs
    col_title, col_reset = st.columns([4, 1])
    col_title.markdown("**✅ Demo is ready!** Explore the data using the tabs below.")

    with col_reset.expander("🗑️ Reset Demo"):
        if not st.session_state.reset_armed:
            st.caption("Drop all tables and start fresh.")
            delete_file = st.checkbox("Also delete cached SQL file", key="reset_delete_file")
            if st.button("Reset Demo", key="reset_arm_btn"):
                st.session_state.reset_armed = True
                st.rerun()
        else:
            st.warning("**All data will be deleted.** This cannot be undone.")
            c1, c2 = st.columns(2)
            if c1.button("✅ Confirm", type="primary", key="reset_confirm_btn"):
                log_lines = []
                log_box = st.empty()

                def _reset_log(msg):
                    log_lines.append(msg)
                    log_box.text("\n".join(log_lines))

                with st.spinner("Resetting…"):
                    reset_northwind_demo(
                        delete_sql_file=st.session_state.get("reset_delete_file", False),
                        progress_callback=_reset_log,
                    )
                    # Clean + regenerate dbt docs inside the running container.
                    reset_dbt_docs(progress_callback=_reset_log)
                st.cache_data.clear()
                st.session_state.demo_initialized = False
                st.session_state.setup_step = 0
                st.session_state.reset_armed = False
                st.rerun()
            if c2.button("Cancel", key="reset_cancel_btn"):
                st.session_state.reset_armed = False
                st.rerun()

    demo_tab1, demo_tab2, demo_tab3, demo_tab4 = st.tabs([
        "📈 Dashboard",
        "🔍 Data Explorer", 
        "💬 SQL Query",
        "📊 Analytics"
    ])
    
    # Dashboard Overview
    with demo_tab1:
        st.subheader("Dashboard Overview")
        
        # KPIs
        col1, col2, col3, col4 = st.columns(4)
        
        # Get metrics
        customer_count = run_query("SELECT COUNT(*) as cnt FROM dbt_marts.customer_analytics")
        order_count = run_query("SELECT SUM(total_orders) as cnt FROM dbt_marts.sales_summary")
        total_revenue = run_query("SELECT SUM(net_revenue) as total FROM dbt_marts.sales_summary")
        
        if not customer_count.empty:
            col1.metric("Total Customers", f"{customer_count['cnt'].iloc[0]:,}")
        if not order_count.empty:
            col2.metric("Total Orders", f"{order_count['cnt'].iloc[0]:,}")
        if not total_revenue.empty:
            col3.metric("Total Revenue", f"${total_revenue['total'].iloc[0]:,.2f}")
        col4.metric("DBT Models", "10 ✅")
        
        # Revenue by Customer Segment
        st.subheader("Customer Segmentation")
        segment_data = run_query("""
            SELECT customer_segment, 
                   COUNT(*) as customers,
                   SUM(lifetime_revenue) as total_revenue
            FROM dbt_marts.customer_analytics
            GROUP BY customer_segment
            ORDER BY total_revenue DESC
        """)
        
        if not segment_data.empty:
            col1, col2 = st.columns(2)
            with col1:
                fig = px.pie(segment_data, values='customers', names='customer_segment',
                           title='Customers by Segment')
                st.plotly_chart(fig, use_container_width=True)
            with col2:
                fig = px.bar(segment_data, x='customer_segment', y='total_revenue',
                           title='Revenue by Segment', color='customer_segment')
                st.plotly_chart(fig, use_container_width=True)
        
        # Monthly trends
        st.subheader("Revenue Trends")
        monthly_data = run_query("""
            SELECT DATE_TRUNC('month', order_date) as month,
                   SUM(net_revenue) as monthly_revenue
            FROM dbt_marts.sales_summary
            GROUP BY DATE_TRUNC('month', order_date)
            ORDER BY DATE_TRUNC('month', order_date)
        """)
        
        if not monthly_data.empty:
            fig = px.line(monthly_data, x='month', y='monthly_revenue',
                         title='Monthly Revenue Trend')
            st.plotly_chart(fig, use_container_width=True)
    
    # Data Explorer
    with demo_tab2:
        st.subheader("🔍 Explore DBT Models")
        
        models = {
            "Customer Analytics (Mart)": "SELECT * FROM dbt_marts.customer_analytics LIMIT 100",
            "Sales Summary (Mart)": "SELECT * FROM dbt_marts.sales_summary LIMIT 100",
            "Product Performance (Mart)": "SELECT * FROM dbt_marts.product_performance LIMIT 100",
            "Employee Performance (Mart)": "SELECT * FROM dbt_marts.employee_performance LIMIT 100",
            "Staging: Customers": "SELECT * FROM dbt_staging.stg_customers LIMIT 100",
            "Staging: Orders": "SELECT * FROM dbt_staging.stg_orders LIMIT 100",
            "Staging: Products": "SELECT * FROM dbt_staging.stg_products LIMIT 100"
        }
        
        selected_model = st.selectbox("Select a model to explore:", list(models.keys()))
        
        if st.button("Load Data", type="primary"):
            with st.spinner("Loading..."):
                df = run_query(models[selected_model])
                if not df.empty:
                    st.success(f"✅ Loaded {len(df)} rows")
                    st.dataframe(df, use_container_width=True, height=400)
                    
                    # Download button
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download CSV",
                        data=csv,
                        file_name=f"{selected_model.lower().replace(' ', '_')}.csv",
                        mime="text/csv"
                    )
    
    # SQL Query
    with demo_tab3:
        st.subheader("💬 Run Custom SQL")
        
        st.markdown("""
        Execute custom SQL queries against the Northwind database. 
        Available schemas: `dbt_staging`, `dbt_marts`, `public`
        """)
        
        # Sample queries
        sample_queries = {
            "Top 10 Customers": """SELECT contact_name, lifetime_revenue, customer_segment
FROM dbt_marts.customer_analytics
ORDER BY lifetime_revenue DESC
LIMIT 10;""",
            "Products to Reorder": """SELECT product_name, units_in_stock, reorder_level
FROM dbt_staging.stg_products
WHERE needs_reorder = TRUE;""",
            "Employee Leaderboard": """SELECT full_name, total_revenue, total_orders
FROM dbt_marts.employee_performance
ORDER BY total_orders DESC;"""
        }
        
        selected_sample = st.selectbox("Or choose a sample query:", ["Custom"] + list(sample_queries.keys()))
        
        if selected_sample != "Custom":
            default_query = sample_queries[selected_sample]
        else:
            default_query = "SELECT * FROM dbt_marts.customer_analytics LIMIT 10;"
        
        user_query = st.text_area("SQL Query:", value=default_query, height=150)
        
        if st.button("▶️ Execute Query", type="primary"):
            with st.spinner("Executing..."):
                result = run_query(user_query)
                if not result.empty:
                    st.success(f"✅ Query returned {len(result)} rows")
                    st.dataframe(result, use_container_width=True)
    
    # Advanced Analytics
    with demo_tab4:
        st.subheader("📊 Advanced Analytics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Top Products")
            top_products = run_query("""
                SELECT product_name, net_revenue, total_units_sold
                FROM dbt_marts.product_performance
                ORDER BY net_revenue DESC
                LIMIT 10
            """)
            if not top_products.empty:
                fig = px.bar(top_products, x='product_name', y='net_revenue',
                           title='Top 10 Products by Revenue')
                fig.update_xaxes(tickangle=-45)
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### Employee Performance")
            emp_perf = run_query("""
                SELECT full_name, total_revenue, total_orders
                FROM dbt_marts.employee_performance
                ORDER BY total_revenue DESC
            """)
            if not emp_perf.empty:
                fig = px.scatter(emp_perf, x='total_orders', y='total_revenue',
                               text='full_name', title='Sales vs Order Count')
                st.plotly_chart(fig, use_container_width=True)





# Footer
st.divider()
_dbt_port = os.getenv("DBT_PORT", "8002")
st.markdown(f"""
<div style='text-align: center; color: #666;'>
    <p>🏗️ <strong>DBT Analytics Platform</strong> | Built with Streamlit & PostgreSQL</p>
    <p>View lineage: <a href='http://localhost:{_dbt_port}' target='_blank'>DBT Docs Server</a></p>
</div>
""", unsafe_allow_html=True)


# Side Footer
st.sidebar.caption(f"Last updated: {time.strftime('%Y-%m-%d %H:%M:%S')}")