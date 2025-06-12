# 🧠 Logistics Optimization Platform

This platform provides two containerized services for:
- Optimizing a cooperative's logistics via a REST API
- Visualizing the results through an interactive Streamlit UI

---

## Services

### 1. `logistic-optimization` (REST API)

- Exposes a `POST /optimize` endpoint
- Accepts a `data.json` file describing sites, flows, and constraints
- Runs a Gurobi optimization model and produces:
  - `data/flows.csv`
  - `data/cells.csv`

### 2. `logistic-ui` (Streamlit)

- Reads `flows.csv` and `cells.csv`
- Displays **interactive dashboards**:
  - Flow volume and distribution
  - Storage cell usage over time

---

## Launching the Platform

```bash
cd deploy && docker-compose up
```

## Triggering an Optimization (API Call)
```bash
curl -X POST http://localhost:8080/optimize \
  -H "Content-Type: application/json" \
  -d @data/data.json
```

Results will be saved to the data/ folder:
- `flows.csv`
- `cells.csv`