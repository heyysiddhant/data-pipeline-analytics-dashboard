# Data Analysis Dashboard Project

This project implements an end-to-end data pipeline: from raw data generation and cleaning to business analysis and an interactive fullstack dashboard. It was built to demonstrate proficiency in data engineering with Python and modern web development.

## 🚀 Quick Start

### 1. Environment Setup
The project uses a standard Python virtual environment.
```bash
# Setup virtual environment (if not already done)
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

### 2. Run the Data Pipeline
Execute these scripts in order from the root directory:
```bash
# 1. Generate synthetic raw data
python generate_data.py

# 2. Clean and standardize datasets
python clean_data.py

# 3. Perform business analysis and merge data
python analyze.py
```

### 3. Launch the Application
**Backend (FastAPI)**:
```bash
cd backend
python main.py
```
*The API runs at http://localhost:8000*

**Frontend (React + Vite)**:
```bash
cd frontend
npm install
npm run dev
```
*The dashboard runs at http://localhost:5173 (or 5174 if port 5173 is occupied)*

---

## 🛠️ Project Components

### Part 1: Data Cleaning (`clean_data.py`)
- **Robust Parsing**: Handles mixed date formats (YYYY-MM-DD, DD/MM/YYYY, MM-DD-YYYY).
- **Data Validation**: Flags malformed emails and standardizes strings (strip whitespace, lowercase).
- **Missing Value Strategy**: Uses median imputation for order amounts and defaults for regions.
- **Reporting**: Prints a detailed summary of changes to the terminal.

### Part 2: Analysis & Merging (`analyze.py`)
- **Explicit Joins**: Combines customers, orders, and products using explicit left joins.
- **Business Insights**: 
    - Monthly revenue trends.
    - Top 10 customers by spend.
    - Category-level performance (Average Order Value, total orders).
    - Regional KPI analysis.
- **Churn Detection**: Identifies inactive customers based on a 90-day window from the latest transaction.

### Part 3: Fullstack Dashboard
- **Backend**: FastAPI with automated CORS configuration and robust CSV data loading.
- **Frontend**: Responsive React dashboard built with Tailwind-style CSS and Recharts.
- **Features**: 
    - Interactive Line and Bar charts.
    - Sortable tables with search and date-range filtering (Bonus).

---

## 💡 Assumptions Made

Detailed assumptions are key to understanding the data logic:

### Data Engineering
*   **Median Imputation**: Missing order amounts were filled using the **median amount per product name**. This preserves product-specific price distributions better than a global median.
*   **Deduplication Strategy**: When removing duplicate customers, the record with the **most recent `signup_date`** was preserved to ensure we have the latest contact information.
*   **Date Parsing**: The custom parser handles `%Y-%m-%d`, `%d/%m/%Y`, and `%m-%d-%Y`. Any dates failing all three formats are logged as warnings and set to `NaT` (Not a Time) to avoid pipeline crashes.
*   **Join Integrity**:
    *   Used **left-joins** from `orders` to `customers` to identify orphan orders (orders without a valid customer profile).
    *   Used **case-sensitive matching** for product names during the join to ensure strict data lineage between the catalog and transactions.

### Business Logic
*   **Churn Definition**: A customer is flagged as `churned = True` if they haven't placed a **completed** order in the **90 days** prior to the *latest transaction date* found in the dataset (rather than the current system time), making the analysis time-relative.
*   **Revenue Metrics**: All revenue-based calculations (Monthly Trend, Top Customers, Categories) strictly filter for `status == 'completed'`. Cancelled or pending orders are excluded from financial totals.
*   **Status Mapping**: The normalization mapping (e.g., `done` → `completed`, `canceled` → `cancelled`) is strictly defined; any unrecognized status value is defaulted to `pending` for safety.

### Fullstack Implementation
*   **CORS Configuration**: The API allows all origins (`*`) to ensure the React development server (typically port 5173/5174) can communicate seamlessly with the FastAPI backend without pre-flight errors.
*   **Stateless API**: Each endpoint re-reads the processed CSV files. While this is slightly slower than caching, it ensures the API always returns the most up-to-date results from the cleaning pipeline without requiring a server restart.

---

## 🧪 Testing
Run unit tests for the cleaning logic:
```bash
python -m pytest tests/test_cleaning.py
```

---

## 🐳 Deployment

This project is containerized and ready for production deployment.

### 1. Local Production Simulation (Docker Compose)
To run the entire stack in production mode locally:
```bash
docker compose -f docker-compose.prod.yml up --build
```
-   **Frontend**: http://localhost (Nginx)
-   **Backend**: http://localhost:8000 (FastAPI)

### 2. GitHub Actions CI/CD
The project includes automated workflows:
-   **CI (`ci.yml`)**: Runs on every push/PR to `main`. It lints the frontend, builds it, and runs backend tests.
-   **CD (`deploy.yml`)**: Runs on every push to `main`. It builds production Docker images and pushes them to **GitHub Container Registry (GHCR)**.

### 3. Deploying the Images
Once images are pushed to GHCR, i will deploy them to any VPS or cloud provider using the `docker-compose.prod.yml` file, replacing the `build:` sections with `image: ghcr.io/<my-username>/<repo-name>-<service>:latest`.
