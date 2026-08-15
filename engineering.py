"""
engineering.py
----------------
Core object-oriented engineering classes for the Fluid Flow & Heat Transfer
Engineering Suite (PE 262 Capstone Project).

This module keeps all the "engineering science" (fluid properties, pipe flow
hydraulics, and heat transfer calculations) separate from the Streamlit UI
code. The Streamlit pages simply import these classes, feed them user
inputs, and display the results.

Classes
-------
Fluid          : holds density and viscosity for a fluid, with a small
                 built-in library of common fluids (water, air, crude oil).
Pipe           : represents a circular pipe and calculates flow hydraulics
                 (velocity, Reynolds number, friction factor, pressure drop).
HeatExchanger  : performs steady-state conduction and transient (Newton's
                 Law of Cooling) heat transfer calculations.
"""

import math


class Fluid:
    """
    Represents a fluid with the physical properties needed for pipe-flow
    and heat-transfer calculations.

    Attributes
    ----------
    name : str
        Name of the fluid (e.g. "Water", "Air", "Crude Oil").
    density : float
        Fluid density in kg/m^3.
    viscosity : float
        Dynamic viscosity in Pa.s (kg/m.s).

    A small built-in library (`Fluid.LIBRARY`) provides typical property
    values for water, air, and crude oil at roughly room temperature, so a
    user can pick a fluid by name and have density/viscosity auto-populated.
    Users can also supply their own custom values.
    """

    # Typical properties at ~20 C, 1 atm (approximate, for teaching use).
    LIBRARY = {
        "Water":     {"density": 998.0,  "viscosity": 0.001002},
        "Air":       {"density": 1.204,  "viscosity": 1.825e-5},
        "Crude Oil": {"density": 850.0,  "viscosity": 0.01},
    }

    def __init__(self, name, density=None, viscosity=None):
        """
        Create a Fluid.

        Parameters
        ----------
        name : str
            Fluid name. If it matches a key in Fluid.LIBRARY (e.g. "Water"),
            density/viscosity are auto-populated unless explicitly overridden.
        density : float, optional
            Density in kg/m^3. Required if `name` is not in the library.
        viscosity : float, optional
            Dynamic viscosity in Pa.s. Required if `name` is not in the library.

        Raises
        ------
        ValueError
            If the fluid is not in the library and density/viscosity are not
            both supplied, or if supplied values are not positive numbers.
        """
        self.name = name

        if name in Fluid.LIBRARY:
            defaults = Fluid.LIBRARY[name]
            self.density = density if density is not None else defaults["density"]
            self.viscosity = viscosity if viscosity is not None else defaults["viscosity"]
        else:
            if density is None or viscosity is None:
                raise ValueError(
                    f"'{name}' is not a built-in fluid. Please provide both "
                    "density (kg/m^3) and viscosity (Pa.s) for a custom fluid."
                )
            self.density = density
            self.viscosity = viscosity

        if self.density <= 0 or self.viscosity <= 0:
            raise ValueError("Density and viscosity must both be positive numbers.")

    def __repr__(self):
        return f"Fluid(name={self.name!r}, density={self.density} kg/m^3, viscosity={self.viscosity} Pa.s)"


class Pipe:
    """
    Represents a circular pipe carrying a Fluid, and calculates single-phase
    incompressible flow hydraulics: velocity, Reynolds number, Darcy
    friction factor, and frictional pressure drop (Darcy-Weisbach equation).

    Attributes
    ----------
    diameter : float
        Internal pipe diameter, D, in metres.
    length : float
        Pipe length, L, in metres.
    roughness : float
        Absolute pipe wall roughness, epsilon, in metres.
    fluid : Fluid
        The Fluid object flowing through the pipe.
    """

    def __init__(self, diameter, length, roughness, fluid):
        """
        Create a Pipe.

        Parameters
        ----------
        diameter : float
            Internal diameter in metres. Must be positive.
        length : float
            Pipe length in metres. Must be positive.
        roughness : float
            Absolute roughness in metres. Must be non-negative.
        fluid : Fluid
            A Fluid instance describing the flowing fluid.

        Raises
        ------
        ValueError
            If diameter/length are not positive, roughness is negative, or
            fluid is not a Fluid instance.
        """
        if diameter <= 0:
            raise ValueError("Pipe diameter must be a positive number (m).")
        if length <= 0:
            raise ValueError("Pipe length must be a positive number (m).")
        if roughness < 0:
            raise ValueError("Pipe roughness cannot be negative (m).")
        if not isinstance(fluid, Fluid):
            raise ValueError("fluid must be a Fluid object.")

        self.diameter = diameter
        self.length = length
        self.roughness = roughness
        self.fluid = fluid

    def area(self):
        """Return the pipe's internal cross-sectional area in m^2."""
        return math.pi * (self.diameter ** 2) / 4.0

    def velocity(self, flow_rate):
        """
        Calculate the mean flow velocity for a given volumetric flow rate.

        Parameters
        ----------
        flow_rate : float
            Volumetric flow rate, Q, in m^3/s. Must be non-negative.

        Returns
        -------
        float
            Mean velocity, v = Q / A, in m/s.
        """
        if flow_rate < 0:
            raise ValueError("Flow rate cannot be negative.")
        return flow_rate / self.area()

    def reynolds_number(self, flow_rate):
        """
        Calculate the Reynolds number, Re = (rho * v * D) / mu.

        Parameters
        ----------
        flow_rate : float
            Volumetric flow rate in m^3/s.

        Returns
        -------
        float
            Dimensionless Reynolds number.
        """
        v = self.velocity(flow_rate)
        return (self.fluid.density * v * self.diameter) / self.fluid.viscosity

    def friction_factor(self, flow_rate):
        """
        Calculate the Darcy friction factor, f.

        Uses the laminar formula f = 64/Re for Re < 2300, and the
        Swamee-Jain explicit approximation to the Colebrook equation for
        turbulent flow (Re >= 2300):

            f = 0.25 / [ log10( eps/(3.7 D) + 5.74/Re^0.9 ) ]^2

        Parameters
        ----------
        flow_rate : float
            Volumetric flow rate in m^3/s.

        Returns
        -------
        float
            Dimensionless Darcy friction factor.
        """
        re = self.reynolds_number(flow_rate)
        if re <= 0:
            return 0.0
        if re < 2300:
            return 64.0 / re
        rel_rough = self.roughness / self.diameter
        denom = math.log10(rel_rough / 3.7 + 5.74 / (re ** 0.9))
        return 0.25 / (denom ** 2)

    def pressure_drop(self, flow_rate):
        """
        Calculate the frictional pressure drop using the Darcy-Weisbach
        equation:

            dP = f * (L/D) * (rho * v^2) / 2

        Parameters
        ----------
        flow_rate : float
            Volumetric flow rate in m^3/s.

        Returns
        -------
        float
            Pressure drop in Pascals (Pa).
        """
        v = self.velocity(flow_rate)
        f = self.friction_factor(flow_rate)
        return f * (self.length / self.diameter) * (self.fluid.density * v ** 2) / 2.0

    def summary(self, flow_rate):
        """
        Convenience method returning all key flow results as a dictionary.

        Parameters
        ----------
        flow_rate : float
            Volumetric flow rate in m^3/s.

        Returns
        -------
        dict
            Keys: velocity_m_s, reynolds_number, flow_regime, friction_factor,
            pressure_drop_Pa, pressure_drop_kPa.
        """
        v = self.velocity(flow_rate)
        re = self.reynolds_number(flow_rate)
        f = self.friction_factor(flow_rate)
        dp = self.pressure_drop(flow_rate)
        regime = "Laminar" if re < 2300 else ("Transitional" if re < 4000 else "Turbulent")
        return {
            "velocity_m_s": v,
            "reynolds_number": re,
            "flow_regime": regime,
            "friction_factor": f,
            "pressure_drop_Pa": dp,
            "pressure_drop_kPa": dp / 1000.0,
        }

    def __repr__(self):
        return f"Pipe(D={self.diameter} m, L={self.length} m, roughness={self.roughness} m, fluid={self.fluid.name})"


class HeatExchanger:
    """
    Performs two classic heat-transfer calculations used in the Heat
    Transfer Calculator module:

    1. Steady-state conduction through a single-layer flat wall (Fourier's
       Law).
    2. Transient cooling of a lumped body following Newton's Law of
       Cooling, including the time required to reach a target temperature
       and a full temperature-vs-time cooling curve.
    """

    def __init__(self):
        """Create a HeatExchanger helper (stateless; all methods take their own inputs)."""
        pass

    @staticmethod
    def conduction_flat_wall(k, area, thickness, t_hot, t_cold):
        """
        Steady-state 1-D conduction through a single-layer flat wall
        (Fourier's Law):

            Q = k * A * (T_hot - T_cold) / L

        Parameters
        ----------
        k : float
            Thermal conductivity of the wall material, W/(m.K). Must be positive.
        area : float
            Cross-sectional area normal to heat flow, m^2. Must be positive.
        thickness : float
            Wall thickness, L, in metres. Must be positive.
        t_hot : float
            Hot-face temperature, deg C (or K - units cancel in the difference).
        t_cold : float
            Cold-face temperature, deg C (or K).

        Returns
        -------
        float
            Steady-state heat transfer rate, Q, in Watts.

        Raises
        ------
        ValueError
            If k, area, or thickness are not positive.
        """
        if k <= 0:
            raise ValueError("Thermal conductivity k must be positive (W/m.K).")
        if area <= 0:
            raise ValueError("Area must be positive (m^2).")
        if thickness <= 0:
            raise ValueError("Wall thickness must be positive (m).")

        return k * area * (t_hot - t_cold) / thickness

    @staticmethod
    def cooling_time(t0, t_target, t_inf, k_cool):
        """
        Time required for a lumped body to cool from T0 to T_target in an
        ambient temperature T_inf, using Newton's Law of Cooling:

            T(t) = T_inf + (T0 - T_inf) * exp(-k * t)
            =>  t = -(1/k) * ln[ (T_target - T_inf) / (T0 - T_inf) ]

        Parameters
        ----------
        t0 : float
            Initial body temperature (deg C).
        t_target : float
            Target body temperature (deg C). Must lie strictly between
            t_inf and t0 (the body can only cool toward T_inf, never past it).
        t_inf : float
            Ambient (surrounding) temperature (deg C).
        k_cool : float
            Cooling rate constant, 1/s (or 1/min - matches whatever time
            unit the returned t and the plot use). Must be positive.

        Returns
        -------
        float
            Time required to reach t_target, in the same time unit as 1/k_cool.

        Raises
        ------
        ValueError
            If k_cool is not positive, or if t_target is not strictly
            between t_inf and t0 (i.e. physically unreachable by cooling).
        """
        if k_cool <= 0:
            raise ValueError("Cooling constant k must be positive.")
        if t0 == t_inf:
            raise ValueError("Initial temperature cannot equal ambient temperature.")

        # The body cools monotonically from T0 toward T_inf. T_target must be
        # strictly between them (on the correct side) for a finite, positive time.
        lower, upper = sorted([t_inf, t0])
        if not (lower < t_target < upper) or t_target == t0:
            raise ValueError(
                "Target temperature must be strictly between the ambient "
                "temperature and the initial temperature."
            )

        ratio = (t_target - t_inf) / (t0 - t_inf)
        return -(1.0 / k_cool) * math.log(ratio)

    @staticmethod
    def cooling_curve(t0, t_inf, k_cool, t_max, n_points=100):
        """
        Generate a temperature-vs-time cooling curve using Newton's Law of
        Cooling: T(t) = T_inf + (T0 - T_inf) * exp(-k * t).

        Parameters
        ----------
        t0 : float
            Initial temperature (deg C).
        t_inf : float
            Ambient temperature (deg C).
        k_cool : float
            Cooling rate constant (1/time unit). Must be positive.
        t_max : float
            Maximum time to plot to (same time unit as k_cool). Must be positive.
        n_points : int, optional
            Number of points to generate (default 100).

        Returns
        -------
        tuple(list, list)
            (times, temperatures) - two lists of equal length for plotting.
        """
        if k_cool <= 0:
            raise ValueError("Cooling constant k must be positive.")
        if t_max <= 0:
            raise ValueError("Maximum time must be positive.")

        times = [t_max * i / (n_points - 1) for i in range(n_points)]
        temps = [t_inf + (t0 - t_inf) * math.exp(-k_cool * t) for t in times]
        return times, temps
