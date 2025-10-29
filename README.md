# COVID‑19 Spread Analysis with Flask

A clean, production‑ready Flask application for analyzing COVID‑19 spread data with interactive **Folium** maps and **Plotly** charts. Structured using your preferred `src/` layout, MIT license, and GitHub Actions CI.

## ✨ Features
- App factory (`create_app`) for testability & scaling
- Data pipeline: download → extract → normalize (cached to `./data/`)
- Global KPIs + timeseries + Top‑N country bar charts
- Folium map with marker clustering (Leaflet)
- Country detail page with province/state breakdown
- CI (Ruff, Black, PyTest) and standard tooling

## 📦 Quickstart
```bash
# 1) Clone
git clone https://github.com/mobinyousefi-cs/covid19-flask-dashboard.git
cd covid19-flask-dashboard

# 2) Create venv
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 3) Install
pip install -e .[dev]

# 4) Run (development)
export FLASK_ENV=development  # Windows: set FLASK_ENV=development
python run.py
# open http://127.0.0.1:5000
```

> On first run, the app downloads the dataset from `https://data-flair.training/blogs/download-covid-19-dataset/` into `./data/`. After that, it works offline.

## 🗂️ Datasets
- Designed for Data‑Flair COVID‑19 CSVs (with columns like `ObservationDate`, `Country/Region`, `Latitude`, `Longitude`, etc.).
- The pipeline is resilient to multiple CSVs in the archive; it concatenates and normalizes them.

## 🧪 Tests
```bash
pytest -q
```

## 🛠️ Dev Tasks
- **Lint**: `ruff check .`
- **Format**: `black .`

## 🐳 (Optional) Docker
```dockerfile
# Dockerfile (optional)
# FROM python:3.11-slim
# WORKDIR /app
# COPY . .
# RUN pip install -e .
# EXPOSE 5000
# CMD ["python", "run.py"]
```

## 📜 License
MIT — © 2025 Mobin Yousefi
```
```

---

## File: `run.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===========================================================================
Project: COVID-19 Spread Analysis with Flask
File: run.py
Author: Mobin Yousefi (GitHub: github.com/mobinyousefi-cs)
Created: 2025-10-29
Updated: 2025-10-29
License: MIT License (see LICENSE file for details)
===========================================================================

Description:
Entry point for running the Flask development server.
===========================================================================
"""
from covid_dashboard import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=app.config.get("DEBUG", True))
```
```

---

### ✅ Notes
- The folium map uses latest available date rows and will render markers only when lat/lon exist in the dataset.
- The pipeline is robust to various Data‑Flair CSV shapes and performs column normalization automatically.
- If you want live updates on a schedule, add a small cron or APScheduler job to re‑download data.