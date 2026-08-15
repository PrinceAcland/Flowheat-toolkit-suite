# AI Usage Documentation

As required by the capstone rubric (Module D), this document lists the
prompts used to get AI assistance while building this app, what was
verified, and what was corrected.

## Prompt 1

**Prompt:** "Help me design an `engineering.py` module with `Fluid`,
`Pipe`, and `HeatExchanger` classes for a pipe-flow and heat-transfer
Streamlit app. I need velocity, Reynolds number, friction factor, and
Darcy-Weisbach pressure drop for the pipe, and Fourier's Law conduction
plus Newton's Law of Cooling for the heat exchanger."

**What was verified:** I hand-calculated the pipe-flow example (water,
D = 100 mm, L = 100 m, Q = 36 m³/h) using the Darcy-Weisbach equation and
the Swamee-Jain friction-factor approximation, and compared it against the
function output — velocity, Reynolds number, and pressure drop all matched
to 3+ significant figures. I also checked the conduction example
(Q = kA·ΔT/L) and the Newton's Law of Cooling time formula by substituting
numbers by hand.

**What was corrected:** The first version of the friction-factor function
did not branch between laminar and turbulent flow — it always used the
Swamee-Jain (turbulent) formula, which gives a wrong (much higher) friction
factor at low, laminar Reynolds numbers. I corrected it to check
`Re < 2300` and use `f = 64/Re` in that regime.

## Prompt 2

**Prompt:** "Build a Streamlit multi-page app structure for this — a Home
page plus three module pages (Pipe Flow Analyser, Heat Transfer
Calculator, Rock & Fluid Data Dashboard) using Streamlit's `pages/`
folder convention, with sidebar inputs, metric displays, plots, and CSV
export/import."

**What was verified:** I ran the app locally with `streamlit run Home.py`
and clicked through every page and every input to confirm nothing
crashed, the plots updated when sliders moved, and the CSV
download/upload buttons produced valid files that reopened correctly in
Excel.

**What was corrected:** The generated cooling-curve plot originally let
the target-temperature slider go outside the valid range between ambient
and initial temperature, which made `cooling_time()` raise an error. I
fixed this by bounding the slider's min/max to the ambient and initial
temperatures so an invalid target can't be selected in the first place.

## Prompt 3

**Prompt:** "Add error handling to the `Fluid`, `Pipe`, and
`HeatExchanger` classes so bad inputs (negative diameter, zero thermal
conductivity, an unreachable target temperature, etc.) raise clear
`ValueError` messages instead of crashing the app, and add docstrings to
every method."

**What was verified:** I manually tested each class with intentionally
bad inputs (negative pipe diameter, zero conductivity, a target
temperature outside the valid cooling range, an unknown fluid name with
no custom properties supplied) and confirmed each one raised a readable
error message and that the Streamlit page caught it and displayed
`st.error()` instead of crashing.

**What was corrected:** The original error handling for the cooling-time
calculation did not check that the target temperature lies strictly
between the ambient and initial temperatures, so an out-of-range target
caused a `math domain error` from `math.log()` of a negative number
instead of a clear message. I added an explicit range check that raises a
descriptive `ValueError` before the log calculation runs.
