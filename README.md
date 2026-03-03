# Monte Carlo Simulation of the Newsvendor Problem

## Overview
This project was completed as part of the ISYE 6644 Simulation course in the Master of Science in Analytics program at Georgia Tech.

The project has two primary objectives:
- To develop an interactive Monte Carlo simulation for analyzing the classic Newsvendor inventory optimization problem.
- To design a professional, user-friendly, and visually engaging analytical application.

The application allows users to explore how demand uncertainty, cost parameters, and service levels impact optimal ordering decisions.

---

## Project Context
This project follows a structured simulation study framework,
including problem formulation, model development, experimentation,
and analysis.

The focus is on translating theoretical inventory models into
practical, data-driven decision tools.

---

## Background: The Newsvendor Problem
The Newsvendor problem is a foundational model in operations
management and supply chain analytics.

It addresses the challenge of determining the optimal order quantity
for a perishable or single-period product under uncertain demand.

Key characteristics include:
- Single selling period
- Random demand
- Unsold inventory has limited salvage value
- Unmet demand results in lost sales

The optimal solution balances:
- Over-ordering costs
- Under-ordering costs

---

## Problem Formulation

### Objective
Determine the order quantity of hotdogs Q that maximizes expected profit
under stochastic demand.

Formula used:
Profit = Selling Price * min(Quantity, Demand) - Purchase Cost * Quantity + Salvage Value * max(Quantity - Demand, 0)

#### Subobjectives
- Simulate profits across many demand realizations
- choose Q* under different scenarios
- visualize tradeoffs



### Decision Variable
- Q: Order quantity

### Random Variable
- D: Demand -> D = A * r * ϵ
- A = Atttendance
    - Distribution = Normal(μ,σ^2)
    - stylized scenario generator taking in outside parameters that intuittivelly affect attendance such as weather (for outdoor stadiums), team record, opponent record, and any special promotions for the game.
    - only exists to create realistic demand distributions
- r = hotdogs per attendee
    - fixed for simplicity and explainability with final number at r = .3
    - weather will have small multiplicative 
    - letting ϵ handle slight variations of this variable
- ϵ = Residual Noise
    - Distribution = 
    - represents randomness that happens day-today including concessions traffic patterns, rain delays, game being a blowout, etc.

### Parameters that influence our formula
- Playoff game?
    - Playoff games usually trump any other factors that come into play. If it's a playoff game, people are coming.
- Team record
    - If teams are doing good, the fans will come
- Opponent record
    - Fans of the opposing team are more likely to come/travel if there team is performing well
- Weather
    - Weather is a big driver in attendance
    - Weather is also a small driver in hot dogs per attendee as for cold games, fans are more likely to buy warm foods, and vice versa
        - NOTE: this is only an affect if the stadium is outdoors

### Cost Parameters
- c: Unit purchase cost
- p: Unit selling price
- s: Salvage value

### Performance Metric
- Expected profit
- Service level
- Stockout probability

---

## Modeling Approach

### Demand Modeling
Demand is modeled using probabilistic distributions estimated
from historical or assumed data.

Monte Carlo sampling is used to generate demand scenarios.

### Simulation Logic
For each simulated period:
1. Sample demand
2. Compute sales and leftover inventory
3. Calculate profit
4. Record outcomes

Thousands of iterations are performed to estimate expected
performance.

---

## Implementation

### Tools Used
- Python
- NumPy
- Pandas
- Matplotlib
- Jupyter

### Project Structure
sim_project/
├── notebooks/
├── src/
├── data/
└── outputs/


---

## Results and Analysis
Key findings include:
- Sensitivity of optimal Q to demand variance
- Trade-offs between service level and profitability
- Impact of cost structure on ordering decisions

(See notebooks for detailed analysis.)

---

## Limitations
- Assumes independent demand
- Single-period model
- Simplified cost structure

Future work may incorporate multi-period inventory systems
and demand learning.

---

## How to Run
1. Clone repository
2. Create virtual environment
3. Install requirements
4. Run notebooks

---

## Author
Richard James Petty Jr.  
M.S. Analytics, Georgia Tech