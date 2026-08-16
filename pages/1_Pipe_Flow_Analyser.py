"""
1_Pipe_Flow_Analyser.py
------------------------
Module A of the Capstone app: Pipe Flow Analyser.

Lets the user pick a fluid (with auto-populated properties, or custom
values), enter pipe geometry and a flow rate, and see the resulting
velocity, Reynolds number, friction factor, and pressure drop. Also plots
pressure drop against a range of flow rates, and lets the user export the
range results to a CSV file.

All the underlying physics lives in engineering.py (Fluid and Pipe
classes) - this file only handles the Streamlit UI.
"""

import io

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

from engineering import Fluid, Pipe

st.set_page_config(page_title="Pipe Flow Analyser", page_icon="🔧", layout="wide")

st.title("🔧 Module A — Pipe Flow Analyser")
st.caption(
    "Single-phase incompressible pipe flow: velocity, Reynolds number, "
    "Darcy friction factor, and pressure drop (Darcy-Weisbach equation)."
)

# ----------------------------------------------------------------------
# Sidebar inputs
# ----------------------------------------------------------------------
st.sidebar.header("Inputs")

fluid_choice = st.sidebar.selectbox(
    "Fluid",
    options=list(Fluid.LIBRARY.keys()) + ["User-defined"],
    help="Pick a built-in fluid to auto-populate density and viscosity, "
    "or choose 'User-defined' to enter your own values.",
)

if fluid_choice == "User-defined":
    density = st.sidebar.number_input(
        "Density (kg/m³)", min_value=0.001, value=900.0, step=1.0,
        help="Mass per unit volume of the fluid.",
    )
    viscosity = st.sidebar.number_input(
        "Viscosity (Pa·s)", min_value=1e-6, value=0.01, step=0.001, format="%.5f",
        help="Dynamic (absolute) viscosity of the fluid.",
    )
    fluid_name = "User-defined fluid"
else:
    defaults = Fluid.LIBRARY[fluid_choice]
    density = st.sidebar.number_input(
        "Density (kg/m³)", min_value=0.001, value=float(defaults["density"]), step=1.0,
        help="Auto-populated for the selected fluid — feel free to adjust.",
    )
    viscosity = st.sidebar.number_input(
        "Viscosity (Pa·s)", min_value=1e-6, value=float(defaults["viscosity"]),
        step=0.0001, format="%.6f",
        help="Auto-populated for the selected fluid — feel free to adjust.",
    )
    fluid_name = fluid_choice

st.sidebar.markdown("**Pipe geometry**")
diameter_mm = st.sidebar.number_input(
    "Internal diameter, D (mm)", min_value=1.0, value=100.0, step=1.0,
    help="Internal diameter of the pipe, in millimetres.",
)
length_m = st.sidebar.number_input(
    "Pipe length, L (m)", min_value=0.1, value=100.0, step=1.0,
    help="Total length of straight pipe, in metres.",
)
roughness_mm = st.sidebar.number_input(
    "Absolute roughness, ε (mm)", min_value=0.0, value=0.15, step=0.01, format="%.3f",
    help="Absolute wall roughness. Typical: commercial steel ≈ 0.045 mm, "
    "cast iron ≈ 0.26 mm, PVC ≈ 0.0015 mm.",
)

st.sidebar.markdown("**Flow rate**")
flow_rate_m3h = st.sidebar.number_input(
    "Flow rate, Q (m³/h)", min_value=0.01, value=36.0, step=1.0,
    help="Volumetric flow rate through the pipe, in cubic metres per hour.",
)

# ----------------------------------------------------------------------
# Build engineering objects and calculate
# ----------------------------------------------------------------------
try:
    fluid = Fluid(fluid_name, density=density, viscosity=viscosity)
    pipe = Pipe(
        diameter=diameter_mm / 1000.0,
        length=length_m,
        roughness=roughness_mm / 1000.0,
        fluid=fluid,
    )
    flow_rate_m3s = flow_rate_m3h / 3600.0
    results = pipe.summary(flow_rate_m3s)
    calc_ok = True
except ValueError as e:
    st.error(f"Input error: {e}")
    calc_ok = False

if calc_ok:
    st.subheader("Results")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Velocity", f"{results['velocity_m_s']:.3f} m/s")
    c2.metric("Reynolds number", f"{results['reynolds_number']:,.0f}")
    c3.metric("Flow regime", results["flow_regime"])
    c4.metric("Friction factor", f"{results['friction_factor']:.5f}")

    c5, c6 = st.columns(2)
    c5.metric("Pressure drop", f"{results['pressure_drop_kPa']:.3f} kPa")
    c6.metric("Pressure drop", f"{results['pressure_drop_Pa']:.1f} Pa")

    st.divider()

    # ------------------------------------------------------------------
    # Pressure drop vs flow rate plot
    # ------------------------------------------------------------------
    st.subheader("Pressure drop vs flow rate")

    q_max_m3h = st.slider(
        "Maximum flow rate to plot (m³/h)",
        min_value=flow_rate_m3h,
        max_value=flow_rate_m3h * 5,
        value=flow_rate_m3h * 2,
        help="Sets the upper end of the flow-rate range shown on the plot below.",
    )

    q_range_m3h = np.linspace(0.5, q_max_m3h, 60)
    q_range_m3s = q_range_m3h / 3600.0
    dp_range_kPa = [pipe.pressure_drop(q) / 1000.0 for q in q_range_m3s]

    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.plot(q_range_m3h, dp_range_kPa, color="#1f77b4", linewidth=2)
    ax.scatter([flow_rate_m3h], [results["pressure_drop_kPa"]], color="red", zorder=5,
               label="Current operating point")
    ax.set_xlabel("Flow rate, Q (m³/h)")
    ax.set_ylabel("Pressure drop, ΔP (kPa)")
    ax.set_title(f"Pressure Drop vs Flow Rate — {fluid_name}")
    ax.grid(True, alpha=0.3)
    ax.legend()
    st.pyplot(fig)

    # ------------------------------------------------------------------
    # CSV export
    # ------------------------------------------------------------------
    st.divider()
    st.subheader("Export results")

    export_df = pd.DataFrame({
        "flow_rate_m3_per_h": q_range_m3h,
        "pressure_drop_kPa": dp_range_kPa,
        "pressure_drop_Pa": [v * 1000 for v in dp_range_kPa],
    })

    csv_buffer = io.StringIO()
    export_df.to_csv(csv_buffer, index=False)

    st.download_button(
        label="⬇️ Download pressure-drop-vs-flow-rate CSV",
        data=csv_buffer.getvalue(),
        file_name="pipe_flow_pressure_drop_results.csv",
        mime="text/csv",
    )

    with st.expander("Preview exported data"):
        st.dataframe(export_df, use_container_width=True)

    with st.expander("ℹ️ How this is calculated"):
        st.markdown(
            r"""
            - **Velocity:** $v = Q / A$, where $A = \pi D^2 / 4$.
            - **Reynolds number:** $Re = \rho v D / \mu$.
            - **Friction factor:** laminar ($Re < 2300$): $f = 64/Re$.
              Turbulent: Swamee-Jain approximation to the Colebrook equation.
            - **Pressure drop (Darcy-Weisbach):**
              $\Delta P = f \dfrac{L}{D} \dfrac{\rho v^2}{2}$
            """
        )
