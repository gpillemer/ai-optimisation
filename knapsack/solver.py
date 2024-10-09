import gurobipy as gp
from gurobipy import GRB 
from typing import List, Dict, Tuple, Optional

class Solver:
    STATUS_MESSAGES = {
        GRB.LOADED: 'LOADED',
        GRB.OPTIMAL: 'OPTIMAL',
        GRB.INFEASIBLE: 'INFEASIBLE',
        GRB.INF_OR_UNBD: 'INF_OR_UNBD',
        GRB.UNBOUNDED: 'UNBOUNDED',
        GRB.CUTOFF: 'CUTOFF',
        GRB.ITERATION_LIMIT: 'ITERATION_LIMIT',
        GRB.NODE_LIMIT: 'NODE_LIMIT',
        GRB.TIME_LIMIT: 'TIME_LIMIT',
        GRB.SOLUTION_LIMIT: 'SOLUTION_LIMIT',
        GRB.INTERRUPTED: 'INTERRUPTED',
        GRB.NUMERIC: 'NUMERIC',
        GRB.SUBOPTIMAL: 'SUBOPTIMAL',
        GRB.INPROGRESS: 'IN_PROGRESS'
    }

    def __init__(self, items: List[Dict[str, float]], max_weight: float, user_constraints: List[str]) -> None:
        self.items = items
        self.max_weight = max_weight
        self.user_constraints = user_constraints
        self.model = gp.Model('knapsack')
        self.var_x: Dict[int, gp.Var] = {}
        self.constr_weight: gp.Constr = None
        
    def solve(self) -> None:
        self._create_model()
        self.model.optimize()

    def _create_model(self) -> None:
        """Create the model including variables, objective, and constraints."""
        self._create_base_variables()
        self._create_base_objective()
        self._create_base_constraints()
        self._create_user_constraints()
        self.model.write('model.lp')

    def _create_base_variables(self) -> None:
        """Create the base variables for the model."""
        self.var_x = self.model.addVars(range(len(self.items)), vtype=GRB.BINARY, name=lambda i: f"item_{i}")

    def _create_base_objective(self) -> None:
        """Create the base objective for the model."""
        self.model.setObjective(gp.quicksum(item['value'] * self.var_x[i] for i, item in enumerate(self.items)), GRB.MAXIMIZE)

    def _create_base_constraints(self) -> None:
        """Create the base constraints for the model."""
        self.constr_weight = self.model.addConstr(gp.quicksum(item['weight'] * self.var_x[i] for i, item in enumerate(self.items)) <= self.max_weight, "weight_constraint")

    def _create_user_constraints(self) -> None:
        """Create the user constraints for the model."""
        for i, user_constraint in enumerate(self.user_constraints):
            try:
                exec(user_constraint)
            except Exception as e:
                print(f"Error in user constraint {i}: {e}")

    def print_statistics(self) -> None:
        """Print statistics about the problem."""
        print(f'Status: {self.STATUS_MESSAGES.get(self.model.Status, "UNKNOWN")}')

        if self.model.SolCount > 0:
            print(f'Model name: {self.model.ModelName}')
            print(f'Objective: {self.model.ObjVal:.2f}')
            print(f'Number variables: {self.model.NumVars}')
            print(f'Number constraints: {self.model.NumConstrs}')
            print(f'Number iterations: {self.model.IterCount}')
            if self.model.IsMIP:
                print(f'Number B&B nodes: {self.model.NodeCount}')
            print(f'Runtime: {self.model.Runtime:.2f} seconds')
        else:
            print("No feasible solution found.")
        print()

    def get_results(self) -> Tuple[Optional[List[Dict[str, float]]], float, float]:
        if self.model.SolCount > 0:
            selected_items = [item for i, item in enumerate(self.items) if self.var_x[i].X > 0.5]
            total_value = sum(item['value'] for item in selected_items)
            total_weight = sum(item['weight'] for item in selected_items)
            return selected_items, total_value, total_weight
        else:
            return None, 0.0, 0.0