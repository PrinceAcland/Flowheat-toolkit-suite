"""
2_Heat_Transfer_Calculator.py
-------------------------------
Module B of the Capstone app: Heat Transfer Calculator.

Two calculations, using the HeatExchanger class from engineering.py:
  1. Steady-state conduction through a single-layer flat wall (Fourier's Law)
  2. Newton's Law of Cooling: time to cool from T0 to a target temperature
     in a given ambient temperature, plus an interactive cooling curve plot.
"""

import matplotlib.pyplot as plt
import streamlit as st

from engineering import HeatExchanger

st.set_page_config(page_title="Heat Transfer Calculator", page_icon="🌡️", layout="wide")

st.title("🌡️ Module B — Heat Transfer Calculator")
st.caption(
    "Steady-state flat-wall conduction (Fourier's Law) and transient "
    "cooling (Newton's Law of Cooling)."
)

he = HeatExchanger()

tab1, tab2 = st.tabs(["1. Conduction through a flat wall", "2. Newton's Law of Cooling"])

# ==========================================================================
# TAB 1: Steady-state conduction
# ==========================================================================
with tab1:
    st.subheader("Steady-state conduction through a flat wall")
    st.markdown(
        "Calculates the heat flow, $Q$, that steadily passes through a "
        "single flat layer of material once temperatures on both faces "
        "have stabilised (Fourier's Law)."
    )

    colA, colB = st.columns(2)
    with colA:
        k = st.number_input(
            "Thermal conductivity, k (W/m·K)", min_value=0.001, value=0.8, step=0.05,
            help="How well the wall material conducts heat. Example: "
            "concrete ≈ 0.8–1.4 W/m·K, steel ≈ 45–60 W/m·K, glass wool "
            "insulation ≈ 0.04 W/m·K.",
        )
        area = st.number_input(
            "Wall area, A (m²)", min_value=0.01, value=10.0, step=0.5,
            help="Surface area of the wall, measured face-on (length × height).",
        )
        thickness_mm = st.number_input(
            "Wall thickness, L (mm)", min_value=1.0, value=200.0, step=10.0,
            help="Thickness of the wall in the direction heat is flowing, "
            "in millimetres.",
        )
    with colB:
        t_hot = st.number_input(
            "Hot-face temperature (°C)", value=80.0, step=1.0,
            help="Temperature on the warmer side of the wall.",
        )
        t_cold = st.number_input(
            "Cold-face temperature (°C)", value=20.0, step=1.0,
            help="Temperature on the cooler side of the wall.",
        )

    try:
        Q_cond = he.conduction_flat_wall(
            k=k, area=area, thickness=thickness_mm / 1000.0, t_hot=t_hot, t_cold=t_cold
        )
        st.metric("Steady-state heat transfer rate, Q", f"{Q_cond:,.2f} W")
        st.caption(
            f"Heat flux (Q/A) = {Q_cond / area:,.2f} W/m² — the rate of heat "
            "flow per square metre of wall."
        )
    except ValueError as e:
        st.error(f"Input error: {e}")

    with st.expander("ℹ️ How this is calculated"):
        st.markdown(
            r"""
            Fourier's Law for steady 1-D conduction through a single layer:

            $$Q = k \, A \, \dfrac{T_{hot} - T_{cold}}{L}$$

            where $k$ is thermal conductivity, $A$ is area, $L$ is thickness,
            and $T_{hot}$, $T_{cold}$ are the face temperatures.
            """
        )

# ==========================================================================
# TAB 2: Newton's Law of Cooling
# ==========================================================================
with tab2:
    st.subheader("Newton's Law of Cooling")
    st.markdown(
        "Calculates how long a hot object takes to cool to a target "
        "temperature in a cooler surrounding environment, and plots the "
        "full cooling curve."
    )

    colC, colD = st.columns(2)
    with colC:
        t0 = st.number_input(
            "Initial temperature, T₀ (°C)", value=90.0, step=1.0,
            help="Starting temperature of the object being cooled.",
        )
        t_inf = st.number_input(
            "Ambient temperature, T∞ (°C)", value=20.0, step=1.0,
            help="Temperature of the surrounding air/fluid, which the "
            "object cools toward but never passes.",
        )
    with colD:
        t_target = st.slider(
            "Target temperature (°C)",
            min_value=float(min(t0, t_inf) + 0.5),
            max_value=float(max(t0, t_inf) - 0.5),
            value=float((t0 + t_inf) / 2),
            help="The temperature you want to know the cooling time for. "
            "Must lie between the ambient and initial temperatures.",
        )
        k_cool = st.slider(
            "Cooling rate constant, k (1/min)",
            min_value=0.001, max_value=0.5, value=0.05, step=0.001,
            help="How quickly the object loses heat. Larger k = faster "
            "cooling (depends on the object's size, material, and "
            "surface heat-transfer coefficient).",
        )

    try:
        t_cool = he.cooling_time(t0=t0, t_target=t_target, t_inf=t_inf, k_cool=k_cool)
        st.metric("Time to reach target temperature", f"{t_cool:,.2f} min")

        # Plot the cooling curve out to a bit past the target time
        t_max_plot = max(t_cool * 1.3, 1.0)
        times, temps = he.cooling_curve(t0=t0, t_inf=t_inf, k_cool=k_cool, t_max=t_max_plot)

        fig, ax = plt.subplots(figsize=(8, 4.5))
        ax.plot(times, temps, color="#d62728", linewidth=2, label="Object temperature")
        ax.axhline(t_inf, color="gray", linestyle="--", linewidth=1, label="Ambient temperature")
        ax.axhline(t_target, color="green", linestyle=":", linewidth=1, label="Target temperature")
        ax.scatter([t_cool], [t_target], color="black", zorder=5)
        ax.set_xlabel("Time (min)")
        ax.set_ylabel("Temperature (°C)")
        ax.set_title("Cooling Curve — Newton's Law of Cooling")
        ax.grid(True, alpha=0.3)
        ax.legend()
        st.pyplot(fig)

    except ValueError as e:
        st.error(f"Input error: {e}")

    with st.expander("ℹ️ How this is calculated"):
        st.markdown(
            r"""
            Newton's Law of Cooling:

            $$T(t) = T_\infty + (T_0 - T_\infty)\, e^{-kt}$$

            Solving for the time to reach a target temperature $T_{target}$:

            $$t = -\dfrac{1}{k}\ln\!\left(\dfrac{T_{target}-T_\infty}{T_0-T_\infty}\right)$$
            """
        )
