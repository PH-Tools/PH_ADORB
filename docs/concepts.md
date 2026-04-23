---
title: ADORB Concepts
---

# ADORB Concepts

The **A.D.O.R.B. cost** (Annualized De-carbonization Of Retrofitted Buildings) is a
lifecycle cost metric that captures the true cost of building ownership by including
externalities that conventional cost analyses ignore — primarily carbon emissions and
grid infrastructure investment.

## The Five Cost Components

Each year of the analysis period produces five cost categories. All are discounted to
present value (PV) before summing.

### 1. Direct Energy Cost (`pv_direct_energy`)

Annual electricity and gas purchase costs, including:
- Purchased electricity (kWh x purchase price)
- Sold electricity / net metering credits (kWh x sale price)
- Annual base / connection charges for each fuel

**Discount rate:** 2%

### 2. Operational Carbon Cost (`pv_operational_CO2`)

The cost of CO2 emissions from building operations:
- **Electricity CO2** — hourly purchased electricity multiplied by hourly grid emissions
  factors from NREL Cambium data, projected forward for each future year. This captures
  grid decarbonization over time.
- **Gas CO2** — total gas consumption converted to therms, multiplied by a fixed emission
  factor (12.7 tons CO2 per therm).
- Both are multiplied by the **price of carbon** (default: $0.25/kgCO2).

**Discount rate:** 7.5%

### 3. Maintenance & Replacement Cost (`pv_direct_MR`)

The direct dollar cost of installing and periodically replacing:
- **Constructions** (walls, floors, roofs, windows) — replaced at their `lifetime_years` interval
- **Equipment** (HVAC, lighting, appliances, PV) — replaced at their `lifetime_years` interval
- **CO2 reduction measures** — one-time costs at their specified year

Each item's full cost (labor + material) is charged at year 0 and again at each
replacement cycle within the analysis duration.

**Discount rate:** 2%

### 4. Embodied Carbon Cost (`pv_embodied_CO2`)

The carbon cost of manufacturing the materials used in constructions, equipment, and
CO2 measures:
- Material cost (total cost x material fraction) is converted to kgCO2 using the
  national emissions intensity factor (`kg_CO2_per_USD` from `PhAdorbNationalEmissions`).
- The resulting kgCO2 is multiplied by the price of carbon.
- A 0.75 adjustment factor is applied.
- Like direct costs, embodied CO2 recurs at each replacement cycle.

**Discount rate:** 0% (no discounting — embodied carbon is treated at face value)

### 5. Grid Transition Cost (`pv_e_trans`)

The building's share of national renewable energy infrastructure investment:
- The USA national transition cost ($4.5 trillion) is spread over 1,600 GW of new
  nameplate capacity, yielding a cost per Watt.
- This is amortized linearly over 30 years.
- Each year, the building's peak electrical demand (W) is multiplied by the annual
  per-Watt transition cost.
- After year 30, the transition cost drops to zero.

**Discount rate:** 2%

## Present Value Discounting

All costs are converted to present value using:

```
PV = nominal_cost / (1 + discount_rate)^(year + 1)
```

Different cost categories use different discount rates (see above) to reflect different
risk profiles and time preferences.

## Analysis Duration

The analysis duration (typically 50–100 years) determines how many years of costs are
computed. Longer durations capture more replacement cycles and show the long-term
benefit of durable, low-carbon designs.

## Grid Region (Cambium Data)

The `PhAdorbGridRegion` holds hourly CO2 emissions factors for each year from 2023
through 2111 (89 years), sourced from [NREL Cambium](https://www.nrel.gov/analysis/cambium.html).
These factors reflect projected grid decarbonization and vary by region (27 US regions).

The hourly granularity matters: a building that consumes electricity during peak-carbon
hours will have higher operational CO2 costs than one that shifts load to cleaner hours.

## National Emissions Intensity

The `PhAdorbNationalEmissions` factor (`kg_CO2_per_USD`) converts material dollar costs
to embodied kgCO2 using a country-level economic input-output approach. This is a
simplified proxy for full lifecycle assessment (LCA) of each material.

## Labor vs. Material Fractions

Each construction and equipment item has a `labor_fraction` (0.0–1.0). Only the
**material fraction** (1 - labor_fraction) contributes to embodied CO2, since labor
does not carry upstream manufacturing emissions.
