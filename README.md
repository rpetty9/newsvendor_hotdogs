# Monte Carlo Simulation of the Newsvendor Problem

## Overview
This project was completed for ISYE 6644 in the Master of Science in Analytics program at Georgia Tech.

The goal is to build an interactive Monte Carlo simulation for the newsvendor problem and use it to study hot dog inventory decisions for a game-day setting.

The app lets the user adjust scenario inputs, simulate demand, compare order quantities, and estimate the order quantity that gives the highest average profit.

---

## Project Context
The project follows the standard simulation-study flow:

- define the decision problem
- build a demand model
- run repeated simulation
- compare decisions under uncertainty

The focus is on showing how uncertainty in attendance and demand affects the recommended order quantity.

---

## Background: The Newsvendor Problem
The newsvendor problem is a classic inventory model for a product that must be ordered before uncertain demand is realized.

In this project:

- the selling period is one game
- demand is random
- leftover hot dogs have limited salvage value
- unmet demand becomes lost sales

The main tradeoff is ordering too much versus ordering too little.

---

## Problem Formulation

### Objective
Choose the hot dog order quantity `Q` that maximizes expected profit under uncertain demand.

Profit formula:

`Profit = p * min(Q, D) - c * Q + s * max(Q - D, 0)`

### Decision Variable
- `Q`: order quantity

### Random Variable
- `D`: demand, modeled as `D = A * r * epsilon`
- `A`: attendance
- `r`: baseline hot dogs per attendee
- `epsilon`: residual multiplicative noise

### Scenario Inputs
The model allows the user to change inputs such as:

- playoff vs regular season
- team and opponent records
- weather
- promotion
- stadium type and capacity

In the current implementation, these inputs mainly affect attendance. The purchase rate `r` is held fixed.

### Cost Parameters
- `p`: selling price
- `c`: unit cost
- `s`: salvage value

### Performance Measures
- average profit
- stockout rate
- sellout rate
- leftover inventory

---

## Modeling Approach

### Demand Modeling
Attendance is modeled with a Normal distribution whose mean is adjusted by the selected scenario.

Demand is then computed from:

- attendance
- a fixed baseline purchase rate
- a lognormal noise term

### Simulation Logic
For each simulated game:

1. sample attendance
2. sample demand
3. compute sales and leftovers
4. compute profit
5. store the results

Repeating this many times gives Monte Carlo estimates for profit and other metrics.

---

## Implementation

### Tools Used
- Python
- NumPy
- Pandas
- Streamlit
- Altair

### Project Structure
```text
sim_project/
|- app.py
|- src/
|  |- config.py
|  |- scenario.py
|  |- game.py
|  `- run_sim.py
|- pics/
|- .streamlit/
|- requirements.txt
`- README.md
```

---

## Results and Analysis
The app is designed to help answer questions like:

- how sensitive is the best `Q` to demand uncertainty?
- how much stockout risk comes with a higher-profit choice?
- how close are the top two `Q` values?

The dashboard includes point estimates, confidence intervals, and a comparison between the best grid value and the runner-up.

---

## Limitations
- single-period model
- one-product focus
- no mid-game replenishment
- no dynamic pricing
- simplified demand assumptions
- fixed baseline per-fan purchase rate

---

## How to Run
1. Clone the repository
2. Create a virtual environment
3. Install the requirements
4. Run `streamlit run app.py`

---

## Author
Richard James Petty Jr.  
M.S. Analytics, Georgia Tech
