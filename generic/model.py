import gurobipy as gp
from gurobipy import GRB
from itertools import product
from collections.abc import Iterable

# Problem Description

# The company BIM (Best International Machines) produces two types of microchips, logic chips (1g silicon, 1g plastic, 4g copper) and memory chips (1g germanium, 1g plastic, 2g copper). Each of the logic chips can be sold for a 12€ profit, and each of the memory chips for a 9€ profit. The current stock of raw materials is as follows: 1000g silicon, 1500g germanium, 1750g plastic, 4800g copper. How many microchips of each type should be produced to maximize profit while respecting the availability of raw material stock?



# Updated model_data for a knapsack problem with cost, weight, and value
# model_data = {
#     "model_name": "ChipProduction",
#     "sets": {
#         "Chips": ["Logic", "Memory"],
#         "Materials": ["Silicon", "Germanium", "Plastic", "Copper"]
#     },
#     "parameters": {
#         "Profit": {  # Profit for each chip
#             "Logic": 12,
#             "Memory": 9
#         },
#         "Usage": {  # Material usage per chip type
#             "Silicon": {"Logic": 1, "Memory": 0},
#             "Germanium": {"Logic": 0, "Memory": 1},
#             "Plastic": {"Logic": 1, "Memory": 1},
#             "Copper": {"Logic": 4, "Memory": 2}
#         },
#         "Stock": {  # Available stock of each material
#             "Silicon": 1000,
#             "Germanium": 1500,
#             "Plastic": 1750,
#             "Copper": 4800
#         }
#     },
#     "variables": {
#         "x": {
#             "indices": {"i": "Chips"},
#             "type": "Integer",  # We assume an integer number of chips
#             "lower_bound": 0,  # Non-negative production quantities
#             "upper_bound": GRB.INFINITY  # No upper bound on production quantities
#         }
#     },
#     "objective": {
#         "sense": "maximize",  # Maximize profit
#         "expression": "gp.quicksum(variables['x'][i] * parameters['Profit'][i] for i in sets['Chips'])"
#     },
#     "constraints": {
#         "MaterialConstraint": {
#             "indices": {"m": "Materials"},
#             "expression": "gp.quicksum(variables['x'][i] * parameters['Usage'][m][i] for i in sets['Chips']) <= parameters['Stock'][m]"
#         }
#     }
# }

# model_data = {
#     "model_name": "GasDeliveryOptimization",
#     "sets": {
#         "Franchisees": ["Alice", "Badri", "Cara", "Dan", "Emma", "Fujita", "Grace", "Helen"],
#         "Suppliers": ["CurrentSupplier", "TerminalA", "TerminalB"]
#     },
#     "parameters": {
#         "Demand": {
#             "Alice": 30000,
#             "Badri": 40000,
#             "Cara": 50000,
#             "Dan": 20000,
#             "Emma": 30000,
#             "Fujita": 45000,
#             "Grace": 80000,
#             "Helen": 18000
#         },
#         "Supply": {
#             "CurrentSupplier": 500000,
#             "TerminalA": 100000,
#             "TerminalB": 80000
#         },
#         "Cost": {  # Costs in cents/gallon
#             "CurrentSupplier": {
#                 "Alice": 8.75,
#                 "Badri": 8.75,
#                 "Cara": 8.75,
#                 "Dan": 8.75,
#                 "Emma": 8.75,
#                 "Fujita": 8.75,
#                 "Grace": 8.75,
#                 "Helen": 8.75
#             },
#             "TerminalA": {
#                 "Alice": 8.3,
#                 "Badri": 8.1,
#                 "Cara": 8.3,
#                 "Dan": 9.3,
#                 "Emma": 10.1,
#                 "Fujita": 9.8,
#                 "Grace": 100,  # Not available
#                 "Helen": 7.5
#             },
#             "TerminalB": {
#                 "Alice": 10.2,
#                 "Badri": 12.0,
#                 "Cara": 100,  # Not available
#                 "Dan": 8.0,
#                 "Emma": 10.0,
#                 "Fujita": 10.0,
#                 "Grace": 8.0,
#                 "Helen": 10.0
#             }
#         }
#     },
#     "variables": {
#         "x": {
#             "indices": {"i": "Franchisees", "j": "Suppliers"},
#             "type": "Continuous",  # Allow fractional deliveries
#             "lower_bound": 0,
#             "upper_bound": GRB.INFINITY  # No upper bound in this case
#         },
#         "r": {
#             "type": "Continuous",
#             "lower_bound": 0,
#             "upper_bound": GRB.INFINITY
#         }
#     },
#     "objective": {
#         "sense": "minimize",
#         "expression": "variables['r']"
#     },
#     "constraints": {
#         "DemandConstraint": {
#             "indices": {"i": "Franchisees"},
#             "expression": "gp.quicksum(variables['x'][i, j] for j in sets['Suppliers'] if parameters['Cost'][j][i] is not None) == parameters['Demand'][i]"
#         },
#         "SupplyConstraint": {
#             "indices": {"j": "Suppliers"},
#             "expression": "gp.quicksum(variables['x'][i, j] for i in sets['Franchisees'] if parameters['Cost'][j][i] is not None) <= parameters['Supply'][j]"
#         },
#         "TotalRevenueConstraint": {
#             "expression": "variables['r'] * sum(parameters['Demand'][i] for i in sets['Franchisees']) >= gp.quicksum(variables['x'][i, j] * parameters['Cost'][j][i] for i in sets['Franchisees'] for j in sets['Suppliers'] if parameters['Cost'][j][i] is not None)"
#         }
#     }
# }

# model_data = {
#     "model_name": "GasDeliveryOptimization",
#     "sets": {
#         "Franchisees": ["Alice", "Badri", "Cara", "Dan", "Emma", "Fujita", "Grace", "Helen"],
#         "Suppliers": ["CurrentSupplier", "TerminalA", "TerminalB"]
#     },
#     "parameters": {
#         "Demand": {
#             "Alice": 30000,
#             "Badri": 40000,
#             "Cara": 50000,
#             "Dan": 20000,
#             "Emma": 30000,
#             "Fujita": 45000,
#             "Grace": 80000,
#             "Helen": 18000
#         },
#         "Supply": {
#             "CurrentSupplier": 500000,
#             "TerminalA": 100000,
#             "TerminalB": 80000
#         },
#         "Cost": {  # Costs in cents/gallon
#             "CurrentSupplier": {
#                 "Alice": 8.75,
#                 "Badri": 8.75,
#                 "Cara": 8.75,
#                 "Dan": 8.75,
#                 "Emma": 8.75,
#                 "Fujita": 8.75,
#                 "Grace": 8.75,
#                 "Helen": 8.75
#             },
#             "TerminalA": {
#                 "Alice": 8.3,
#                 "Badri": 8.1,
#                 "Cara": 8.3,
#                 "Dan": 9.3,
#                 "Emma": 10.1,
#                 "Fujita": 9.8,
#                 "Grace": 100,  # Not available
#                 "Helen": 7.5
#             },
#             "TerminalB": {
#                 "Alice": 10.2,
#                 "Badri": 12.0,
#                 "Cara": 100,  # Not available
#                 "Dan": 8.0,
#                 "Emma": 10.0,
#                 "Fujita": 10.0,
#                 "Grace": 8.0,
#                 "Helen": 10.0
#             }
#         }
#     },
#     "variables": {
#         "x": {
#             "indices": {"i": "Franchisees", "j": "Suppliers"},
#             "type": "Continuous",  # Allow fractional deliveries
#             "lower_bound": 0,
#             "upper_bound": GRB.INFINITY  # No upper bound in this case
#         }
#     },
#     "objective": {
#         "sense": "minimize",
#         "expression": "gp.quicksum(variables['x'][i, j] * parameters['Cost'][j][i] for i in sets['Franchisees'] for j in sets['Suppliers'] if parameters['Cost'][j][i] is not None)"
#     },
#     "constraints": {
#         "DemandConstraint": {
#             "indices": {"i": "Franchisees"},
#             "expression": "gp.quicksum(variables['x'][i, j] for j in sets['Suppliers'] if parameters['Cost'][j][i] is not None) == parameters['Demand'][i]"
#         },
#         "SupplyConstraint": {
#             "indices": {"j": "Suppliers"},
#             "expression": "gp.quicksum(variables['x'][i, j] for i in sets['Franchisees'] if parameters['Cost'][j][i] is not None) <= parameters['Supply'][j]"
#         }
#     }
# }


# model_data = {
#     "model_name": "SendMoreMoneyPuzzle",
#     "sets": {
#         "Letters": ["S", "E", "N", "D", "M", "O", "R", "Y"],
#         "LetterPairs": [
#             ('S', 'E'), ('S', 'N'), ('S', 'D'), ('S', 'M'), ('S', 'O'), ('S', 'R'), ('S', 'Y'),
#             ('E', 'N'), ('E', 'D'), ('E', 'M'), ('E', 'O'), ('E', 'R'), ('E', 'Y'),
#             ('N', 'D'), ('N', 'M'), ('N', 'O'), ('N', 'R'), ('N', 'Y'),
#             ('D', 'M'), ('D', 'O'), ('D', 'R'), ('D', 'Y'),
#             ('M', 'O'), ('M', 'R'), ('M', 'Y'),
#             ('O', 'R'), ('O', 'Y'),
#             ('R', 'Y'),
#         ],
#     },
#     "parameters": {
#         "Base10Coefficients": {
#             "SEND": {"S": 1000, "E": 100, "N": 10, "D": 1},
#             "MORE": {"M": 1000, "O": 100, "R": 10, "E": 1},
#             "MONEY": {"M": 10000, "O": 1000, "N": 100, "E": 10, "Y": 1},
#         }
#     },
#     "variables": {
#         "x": {
#             "indices": {"i": "Letters"},
#             "type": "Integer",
#             "lower_bound": 0,
#             "upper_bound": 9,
#         },
#         "diff": {
#             "indices": {"pair": "LetterPairs"},
#             "type": "Binary",
#         },
#     },
#     "objective": {
#         "sense": "minimize",
#         "expression": "gp.quicksum(variables['x'][i] for i in sets['Letters'])"
#     },
#     "constraints": {
#         "EquationConstraint": {
#             "expression": (
#                 "gp.quicksum(variables['x'][letter] * parameters['Base10Coefficients']['SEND'][letter] "
#                 "for letter in parameters['Base10Coefficients']['SEND'])"
#                 " + gp.quicksum(variables['x'][letter] * parameters['Base10Coefficients']['MORE'][letter] "
#                 "for letter in parameters['Base10Coefficients']['MORE'])"
#                 " == gp.quicksum(variables['x'][letter] * parameters['Base10Coefficients']['MONEY'][letter] "
#                 "for letter in parameters['Base10Coefficients']['MONEY'])"
#             )
#         },
#         "UniqueDigitsConstraint": {
#             "expression": (
#                 "["
#                 "variables['x'][pair[0]] - variables['x'][pair[1]] - 10 * variables['diff'][pair] <= -1 "
#                 "for pair in sets['LetterPairs']"
#                 "] + ["
#                 "variables['x'][pair[1]] - variables['x'][pair[0]] - 10 * (1 - variables['diff'][pair]) <= -1 "
#                 "for pair in sets['LetterPairs']"
#                 "]"
#             )
#         },
#         "NonZeroLeadingDigitsConstraint": {
#             "expression": "[variables['x']['S'] >= 1, variables['x']['M'] >= 1]"
#         },
#     },
# }


# model_data = {
#     "model_name": "WeddingSeating",
#     "sets": {
#         "Families": ["1", "2", "3", "4", "5", "6"],
#         "Tables": ["1", "2", "3", "4", "5"]
#     },
#     "parameters": {
#         "m": {
#             "1": 6,
#             "2": 8,
#             "3": 2,
#             "4": 9,
#             "5": 13,
#             "6": 1
#         },
#         "c": {
#             "1": 8,
#             "2": 8,
#             "3": 10,
#             "4": 4,
#             "5": 9
#         },
#         "k": 3
#     },
#     "variables": {
#         "x": {
#             "indices": {"Family": "Families", "Table": "Tables"},
#             "type": "Integer",
#             "lower_bound": 0
#         }
#     },
#     "objective": {
#         "sense": "minimize",
#         "expression": "0"
#     },
#     "constraints": {
#         "FamilyAssignment": {
#             "indices": {"Family": "Families"},
#             "expression": "gp.quicksum(variables['x'][Family, Table] for Table in sets['Tables']) == parameters['m'][Family]"
#         },
#         "TableCapacity": {
#             "indices": {"Table": "Tables"},
#             "expression": "gp.quicksum(variables['x'][Family, Table] for Family in sets['Families']) <= parameters['c'][Table]"
#         },
#         "FamilyThreshold": {
#             "indices": {"Family": "Families", "Table": "Tables"},
#             "expression": "variables['x'][Family, Table] <= parameters['k']"
#         }
#     }
# }


# model_data = model_data = {
#     "model_name": "WeddingSeating_MinimizeTables",
#     "sets": {
#         "Families": ["1", "2", "3", "4", "5", "6"],
#         "Tables": ["1", "2", "3", "4", "5"]
#     },
#     "parameters": {
#         "m": {
#             "1": 6,
#             "2": 8,
#             "3": 2,
#             "4": 9,
#             "5": 13,
#             "6": 1
#         },
#         "c": {
#             "1": 8,
#             "2": 8,
#             "3": 10,
#             "4": 4,
#             "5": 9
#         },
#         "k": 3
#     },
#     "variables": {
#         "x": {
#             "indices": {"Family": "Families", "Table": "Tables"},
#             "type": "Integer",
#             "lower_bound": 0
#         },
#         "y": {
#             "indices": {"Table": "Tables"},
#             "type": "Binary"
#         }
#     },
#     "objective": {
#         "sense": "minimize",
#         "expression": "gp.quicksum(variables['y'][Table] for Table in sets['Tables'])"
#     },
#     "constraints": {
#         "FamilyAssignment": {
#             "indices": {"Family": "Families"},
#             "expression": "gp.quicksum(variables['x'][Family, Table] for Table in sets['Tables']) == parameters['m'][Family]"
#         },
#         "FamilyThreshold": {
#             "indices": {"Family": "Families", "Table": "Tables"},
#             "expression": "variables['x'][Family, Table] <= parameters['k']"
#         },
#         "TableUsage": {
#             "indices": {"Table": "Tables"},
#             "expression": "gp.quicksum(variables['x'][Family, Table] for Family in sets['Families']) <= parameters['c'][Table] * variables['y'][Table]"
#         },
#         "TableActivation": {
#             "indices": {"Table": "Tables"},
#             "expression": "variables['y'][Table] >= (gp.quicksum(variables['x'][Family, Table] for Family in sets['Families']) / parameters['c'][Table])"
#         }
#     }
# }


model_data = {
    "model_name": "SEND_MORE_MONEY",
    "sets": {
        "Letters": ["S", "E", "N", "D", "M", "O", "R", "Y"],
        "Digits": list(range(10)),
        "Positions": list(range(4))  # 0 to 3, representing units to thousands
    },
    "parameters": {},
    "variables": {
        "x": {
            "indices": {"l": "Letters", "d": "Digits"},
            "type": "Binary",
            "lower_bound": 0,
            "upper_bound": 1
        },
        "carry": {
            "indices": {"p": "Positions"},
            "type": "Integer",
            "lower_bound": 0,
            "upper_bound": 1
        }
    },
    "objective": {
        "sense": "maximize",
        "expression": "0"  # This is a constraint satisfaction problem, so we don't need an objective function
    },
    "constraints": {
        "UniqueAssignment": {
            "indices": {"l": "Letters"},
            "expression": "gp.quicksum(variables['x'][l,d] for d in sets['Digits']) == 1"
        },
        "UniqueDigit": {
            "indices": {"d": "Digits"},
            "expression": "gp.quicksum(variables['x'][l,d] for l in sets['Letters']) <= 1"
        },
        "NonZeroM": {
            "expression": "variables['x']['M',0] == 0"
        },
        "Units": {
            "expression": "gp.quicksum(d * variables['x']['D',d] for d in sets['Digits']) + gp.quicksum(d * variables['x']['E',d] for d in sets['Digits']) == gp.quicksum(d * variables['x']['Y',d] for d in sets['Digits']) + 10 * variables['carry'][0]"
        },
        "Tens": {
            "expression": "gp.quicksum(d * variables['x']['N',d] for d in sets['Digits']) + gp.quicksum(d * variables['x']['R',d] for d in sets['Digits']) + variables['carry'][0] == gp.quicksum(d * variables['x']['E',d] for d in sets['Digits']) + 10 * variables['carry'][1]"
        },
        "Hundreds": {
            "expression": "gp.quicksum(d * variables['x']['E',d] for d in sets['Digits']) + gp.quicksum(d * variables['x']['O',d] for d in sets['Digits']) + variables['carry'][1] == gp.quicksum(d * variables['x']['N',d] for d in sets['Digits']) + 10 * variables['carry'][2]"
        },
        "Thousands": {
            "expression": "gp.quicksum(d * variables['x']['S',d] for d in sets['Digits']) + gp.quicksum(d * variables['x']['M',d] for d in sets['Digits']) + variables['carry'][2] == gp.quicksum(d * variables['x']['O',d] for d in sets['Digits']) + 10 * variables['carry'][3]"
        },
        "FinalCarry": {
            "expression": "variables['carry'][3] == gp.quicksum(d * variables['x']['M',d] for d in sets['Digits'])"
        }
    }
}

def create_and_solve_generic_model(model_data):
    # Create the model
    model = gp.Model(model_data["model_name"])

    # Define sets and parameters
    sets = model_data["sets"]
    parameters = model_data["parameters"]

    # Create variables with bounds
    variables = {}
    for var_name, var_data in model_data["variables"].items():
        # Check if the variable has indices
        if "indices" in var_data:
            indices = var_data["indices"]  # Dictionary of index variable names to set names
            index_var_names = list(indices.keys())
            index_sets = [sets[set_name] for set_name in indices.values()]
        else:
            index_var_names = []
            index_sets = []

        var_type = var_data["type"]
        if var_type == "Binary":
            vtype = GRB.BINARY
        elif var_type == "Integer":
            vtype = GRB.INTEGER
        elif var_type == "Continuous":
            vtype = GRB.CONTINUOUS
        else:
            raise ValueError(f"Unknown variable type: {var_type}")

        # Set the lower and upper bounds from the model_data
        lb = var_data.get("lower_bound", 0)  # Default to 0 if no lower_bound is given
        ub = var_data.get(
            "upper_bound", GRB.INFINITY
        )
        
        # Default to infinity if no upper_bound is given
        if ub == "GRB.INFINITY":
            ub = GRB.INFINITY

        # Create variables using addVars, applying the bounds
        print(index_sets)
        if index_sets:  # If there are indices, create indexed variables
            var = model.addVars(*index_sets, vtype=vtype, lb=lb, ub=ub, name=var_name)
        else:  # If there are no indices, create a scalar variable
            var = model.addVar(vtype=vtype, lb=lb, ub=ub, name=var_name)

        variables[var_name] = var

    # Build the namespace for eval()
    namespace = {
        "gp": gp,
        "GRB": GRB,
        "model": model,
        "variables": variables,
        "parameters": parameters,
        "sets": sets,
    }

    # Define the objective
    objective_data = model_data["objective"]
    objective_sense = objective_data["sense"]
    objective_expression = objective_data["expression"]

    # Evaluate the objective expression
    if objective_expression:
        obj_expr = eval(objective_expression, namespace)

        # Set the objective
        if objective_sense.lower() == "minimize":
            model.setObjective(obj_expr, GRB.MINIMIZE)
        elif objective_sense.lower() == "maximize":
            model.setObjective(obj_expr, GRB.MAXIMIZE)
        else:
            raise ValueError(f"Unknown objective sense: {objective_sense}")

    # Add constraints
    constraints_data = model_data["constraints"]

    for constraint_name, constraint_data in constraints_data.items():
        indices = constraint_data.get(
            "indices", {}
        )  # Dictionary of index variable names to set names
        expression = constraint_data["expression"]
        # Get index variable names and their corresponding sets
        index_var_names = list(indices.keys())
        index_sets = [sets[set_name] for set_name in indices.values()]
        # Create all combinations of indices
        index_combinations = list(product(*index_sets)) if index_sets else [()]
        for index_tuple in index_combinations:
            # Build local namespace
            local_namespace = {}
            # Add index variables to the local namespace
            for var_name, index_value in zip(index_var_names, index_tuple):
                local_namespace[var_name] = index_value
            # Merge namespaces
            eval_namespace = namespace.copy()
            eval_namespace.update(local_namespace)
            # Evaluate the constraint expression
            expr = eval(expression, eval_namespace)
            # Add the constraint(s) to the model
            constr_suffix = f"_{'_'.join(map(str, index_tuple))}" if index_tuple else ""
            if isinstance(expr, Iterable) and not isinstance(
                expr, (gp.LinExpr, gp.QuadExpr, gp.TempConstr)
            ):
                for idx, constr_expr in enumerate(expr):
                    constr_name = f"{constraint_name}{constr_suffix}_{idx}"
                    model.addConstr(constr_expr, name=constr_name)
            else:
                constr_name = f"{constraint_name}{constr_suffix}"
                model.addConstr(expr, name=constr_name)

    # Optimize the model
    model.optimize()

    # Print the solution
    if model.status == GRB.OPTIMAL:
        output_string = "\nOptimal solution found:\n"
        print("\nOptimal solution found:")

        # Loop through all variables in the model
        for var_name, var in variables.items():
            print(f"\nVariable {var_name}:")
            output_string += f"\nVariable {var_name}:\n"

            # Check if the variable is indexed or scalar
            if isinstance(var, dict):  # Indexed variables (tupledict)
                for (
                    key
                ) in var.keys():  # Iterate through all keys of the tupledict (indices)
                    value = var[key].X  # Retrieve the optimized value for each variable
                    if abs(value) > 1e-6:  # Print variables with significant values
                        print(f"  {key}: {value}")
                        output_string += f"  {key}: {value}\n"
            else:  # Scalar variable (not indexed)
                value = var.X  # Retrieve the optimized value for the scalar variable
                if abs(value) > 1e-6:  # Print variables with significant values
                    print(f"  {var_name}: {value}")
                    output_string += f"  {var_name}: {value}\n"
    else:
        print("No optimal solution found.")
        output_string = "No optimal solution found."
        model.computeIIS()
        print("\nThe following constraints and bounds are in the IIS:")
        for c in model.getConstrs():
            if c.IISConstr:
                print(f"Constraint {c.ConstrName} is in the IIS")
                output_string += f"\nConstraint {c.ConstrName} is in the IIS\n"
        for v in model.getVars():
            if v.IISLB or v.IISUB:
                print(f"Variable {v.VarName} has an IIS bound")
                output_string += f"\nVariable {v.VarName} has an IIS bound\n"
        model.write("model.ilp")
        print("IIS written to 'model.ilp'. Use Gurobi's tools to inspect the infeasibility.")

    return output_string