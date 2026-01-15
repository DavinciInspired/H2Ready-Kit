# H2Ready – Hydrogen Readiness Assessment Toolkit

H2Ready is a hybrid physics–domain software toolkit for evaluating the hydrogen readiness
of natural gas transmission pipelines. It implements a seven‑pillar Hydrogen Readiness Index (HRI)
with deterministic engineering logic, fracture mechanics gating (K_I / K_TH), and portfolio‑level
visualisation.

This repository underpins a broader research and innovation programme on hydrogen‑ready gas networks
and is intended to serve as technical evidence for advanced engineering and digital innovation, including
use in Global Talent / similar endorsement pathways.

## 🔍 Problem

Existing pipeline integrity frameworks focus on natural gas service and do not provide a unified,
quantitative readiness score for hydrogen repurposing. Hydrogen introduces:

- Hydrogen embrittlement / hydrogen‑assisted cracking
- Hydrogen‑enhanced fatigue crack growth
- Coating disbondment and CP overprotection effects
- Increased leakage propensity and uncertainty in legacy data

H2Ready addresses this by:

- Encoding a seven‑pillar hydrogen readiness framework (M, D, I, C, E, Q, O)
- Implementing fracture mechanics and data‑quality gating
- Providing a portfolio dashboard for segment‑by‑segment screening
- Offering a future‑ready path to ML‑enhanced scoring

## 🧠 Key Features

- Seven‑pillar HRI model (Metallurgy, Design, Integrity, Coating/CP, Environment, Data Quality, Operations)
- Deterministic Level‑1 scoring with transparent penalties and YAML‑based configuration
- Fracture toughness gate (K_I > K_TH → Metallurgy cap + HRI cap)
- Integrity and data‑quality gates enforcing conservative decisions
- Streamlit UI for engineers (no ML expertise required)
- FastAPI backend with documented REST endpoints
- PostgreSQL persistence for pipelines, segments, inputs and scores
- Segment heatmap and narrative “key driver” explanations

## 🏗 Architecture

```text
+---------------------+        +---------------------+        +----------------------+
|  Streamlit Frontend | <----> |  FastAPI Backend    | <----> |   PostgreSQL DB      |
|  (HRI UI & Charts)  |        |  (Scoring Engine)   |        |  (Pipelines/Segments)|
+---------------------+        +---------------------+        +----------------------+
                ^                         |
                |                         |
                +-------------------------+
                      Docker Compose
```

- `frontend/` – Streamlit application (tabs: Setup, Inputs, Score & Dashboard)
- `backend/`  – FastAPI app, scoring engine and persistence layer
- `docs/`     – White paper, Recommended Practice (RP), software specification and supporting docs

## 🚀 Quickstart

```bash
git clone https://github.com/<your-username>/h2ready.git
cd h2ready
docker compose up --build
```

- UI: http://localhost:8501
- API docs (OpenAPI): http://localhost:8000/docs

## 📂 Repository Layout

```text
backend/      FastAPI scoring engine & ORM models
frontend/     Streamlit UI (HRI forms, charts, heatmaps)
docs/         White paper, Recommended Practice, software spec, and GT‑oriented docs
.github/      Issue templates and (optionally) CI workflows
```

## 📚 Documentation

Key documents are located under `docs/`:

- `H2Ready_Software_Prototype_Specification_Full.docx` – full software spec (architecture, requirements, APIs)
- `Hydrogen_Readiness_RP_Overview.md` – overview of the Recommended Practice
- `Hydrogen_Readiness_WhitePaper.md` – summary of the white paper for quick reference
- `GLOBAL_TALENT_IMPACT.md` – role of H2Ready in demonstrating technical leadership and innovation
- `ARCHITECTURE.md` – deeper architectural notes
- `ROADMAP.md` – R&D and product roadmap (including ML Levels 2–3)
- `VALIDATION_PLAN.md` – proposed validation / benchmarking strategy

## 🤝 Contributing

Contributions are welcome in the following areas:

- Extending penalty rules as new hydrogen test data become available
- Implementing Level‑2 and Level‑3 ML scoring modes
- Adding importers for ILI, CP and SCADA datasets
- Enhancing visualisations and portfolio analytics

See `CONTRIBUTING.md` for guidance.

## 🧾 Citation

If you use H2Ready in academic or industrial work, please cite the associated white paper and/or RP.
A `CITATION.cff` file is included to support automated citation managers.

## 🛡 License

This project is released under the MIT License (see `LICENSE`).

Where documents are marked © the author, they are shared for review and personal research use but are not
licensed for commercial reuse without permission.
