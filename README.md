# 🛢️ Fluid Flow & Heat Transfer Engineering Suite

**PE 262 — Computer Programming for Petroleum Engineers**
Capstone Project — Full Engineering Application
Department of Petroleum Engineering, KNUST

## What this app does

A multi-page Streamlit web app with three engineering tools built on a
shared object-oriented Python library:

| Module | Description |
|---|---|
| **A — Pipe Flow Analyser** | Enter a fluid (water, air, crude oil, or custom), pipe geometry, and flow rate to get velocity, Reynolds number, friction factor, and pressure drop (Darcy-Weisbach). Plots pressure drop vs. flow rate and exports results to CSV. |
| **B — Heat Transfer Calculator** | Calculates steady-state conduction through a flat wall (Fourier's Law) and the time for an object to cool using Newton's Law of Cooling, with an interactive cooling-curve plot. |
| **C — Rock & Fluid Data Dashboard** | Upload a CSV of rock/fluid core-analysis data (porosity, permeability, etc.), view summary statistics, filter interactively, view a histogram and a crossplot, and download the filtered data. |

## 🔗 Live app

**Live Streamlit app:** _[PASTE YOUR STREAMLIT COMMUNITY CLOUD URL HERE AFTER DEPLOYING]_

## Project structure

```
.
├── Home.py                                 # Landing page
├── engineering.py                          # Fluid, Pipe, HeatExchanger classes (OOP core)
├── pages/
│   ├── 1_Pipe_Flow_Analyser.py             # Module A
│   ├── 2_Heat_Transfer_Calculator.py       # Module B
│   └── 3_Rock_Fluid_Data_Dashboard.py      # Module C
├── sample_rock_fluid_data.csv              # Sample dataset for Module C
├── requirements.txt
├── AI_USAGE.md                             # Documented AI assistance (Module D)
└── README.md
```

## Running locally

```bash
pip install -r requirements.txt
streamlit run Home.py
```

The app will open at `http://localhost:8501`.

## Design notes (OOP)

All engineering calculations live in `engineering.py`, separate from the
Streamlit UI code:

- **`Fluid`** — holds density and viscosity, with a small built-in library
  (water, air, crude oil) plus support for custom fluids.
- **`Pipe`** — takes a `Fluid` and pipe geometry, and calculates velocity,
  Reynolds number, Darcy friction factor (laminar or Swamee-Jain
  turbulent), and pressure drop.
- **`HeatExchanger`** — performs steady-state flat-wall conduction and
  Newton's Law of Cooling calculations.

Every function has a docstring, and all three classes raise `ValueError`
with a clear message on invalid input (e.g. negative diameter, zero
thermal conductivity) so the app can catch these and show a friendly
error instead of crashing.

## Deployment (Streamlit Community Cloud)

1. Push this repository to GitHub (see steps below).
2. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub.
3. Click **"New app"**, select this repository, branch `main`, and set
   **Main file path** to `Home.py`.
4. Click **Deploy**. The app will build and go live at a
   `https://<your-app-name>.streamlit.app` URL.
5. Paste that URL into the **Live app** section above and into your
   submission.

## Author

Built as part of the PE 262 Capstone Project, KNUST.
