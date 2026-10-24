# Optimization Engine
# Genetic Algorithm based intervention planner
# Given a budget, finds the OPTIMAL combination of interventions
# that maximizes cooling, instead of a human guessing allocations

import numpy as np
from pymoo.core.problem import Problem
from pymoo.algorithms.soo.nonconvex.ga import GA
from pymoo.optimize import minimize
from pymoo.operators.sampling.rnd import FloatRandomSampling


COST_PER_UNIT = {
    'trees': 1500,
    'cool_roofs_sqm': 400,
    'green_roofs_sqm': 900,
    'water_bodies': 2000000,
}

COOLING_WEIGHT = {
    'trees': 0.0012,
    'cool_roofs_sqm': 0.00006,
    'green_roofs_sqm': 0.00010,
    'water_bodies': 0.35,
}


class CoolingOptimizationProblem(Problem):
    """
    Decision variables: how many units of each intervention type
    Objective: maximize total cooling effect
    Constraint: total cost must not exceed budget
    """

    def __init__(self, budget_inr, max_trees=10000, max_cool_roof=50000,
                 max_green_roof=20000, max_water_bodies=5):
        self.budget = budget_inr

        super().__init__(
            n_var=4,
            n_obj=1,
            n_constr=1,
            xl=np.array([0, 0, 0, 0]),
            xu=np.array([max_trees, max_cool_roof, max_green_roof, max_water_bodies]),
            sampling=FloatRandomSampling()
        )

    def _evaluate(self, x, out, *args, **kwargs):
        trees = x[:, 0]
        cool_roofs = x[:, 1]
        green_roofs = x[:, 2]
        water_bodies = x[:, 3]

        cooling = (
            trees * COOLING_WEIGHT['trees'] +
            cool_roofs * COOLING_WEIGHT['cool_roofs_sqm'] +
            green_roofs * COOLING_WEIGHT['green_roofs_sqm'] +
            water_bodies * COOLING_WEIGHT['water_bodies']
        )

        cost = (
            trees * COST_PER_UNIT['trees'] +
            cool_roofs * COST_PER_UNIT['cool_roofs_sqm'] +
            green_roofs * COST_PER_UNIT['green_roofs_sqm'] +
            water_bodies * COST_PER_UNIT['water_bodies']
        )

        out["F"] = -cooling
        out["G"] = cost - self.budget


def optimize_intervention_plan(budget_inr, generations=100, population_size=50):
    """
    Genetic Algorithm chalao optimal intervention mix dhundne ke liye

    budget_inr: total available budget in rupees
    Returns: optimal allocation + expected cooling
    """
    problem = CoolingOptimizationProblem(budget_inr=budget_inr)

    algorithm = GA(pop_size=population_size, eliminate_duplicates=True)

    result = minimize(
        problem,
        algorithm,
        ('n_gen', generations),
        seed=42,
        verbose=False
    )

    if result.X is None:
        return {
            'feasible': False,
            'message': 'No feasible solution found within budget constraints'
        }

    best = result.X
    trees, cool_roofs, green_roofs, water_bodies = best

    total_cooling = -result.F[0]
    total_cost = (
        trees * COST_PER_UNIT['trees'] +
        cool_roofs * COST_PER_UNIT['cool_roofs_sqm'] +
        green_roofs * COST_PER_UNIT['green_roofs_sqm'] +
        water_bodies * COST_PER_UNIT['water_bodies']
    )

    return {
        'feasible': True,
        'allocation': {
            'trees': int(trees),
            'cool_roofs_sqm': int(cool_roofs),
            'green_roofs_sqm': int(green_roofs),
            'water_bodies': int(water_bodies)
        },
        'budget_used': round(total_cost, 0),
        'budget_total': budget_inr,
        'expected_cooling': round(total_cooling, 2)
    }


if __name__ == "__main__":
    print("Running genetic algorithm optimization...")
    print("Budget: Rs 50 lakh (5,000,000)\n")

    result = optimize_intervention_plan(budget_inr=5000000, generations=100)

    if result['feasible']:
        print("Optimal allocation found:")
        for item, qty in result['allocation'].items():
            print(f"  {item}: {qty}")
        print(f"\nBudget used: Rs {result['budget_used']:,.0f} of Rs {result['budget_total']:,.0f}")
        print(f"Expected cooling: {result['expected_cooling']}°C")
    else:
        print(result['message'])