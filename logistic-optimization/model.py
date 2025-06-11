from collections import defaultdict
import gurobipy as gp
from enums import VariableType, CostType

def add_heap_stock_variable(model, variables, nodeId, data):
    if nodeId in data["intermediateNodes"]:
        max_capacity = sum(data["intermediateNodes"][nodeId]["cells"].values())
        if nodeId not in variables[VariableType.STOCK.value]:
            variables[VariableType.STOCK.value][nodeId] = model.addVar(0, max_capacity)

def compute_missing_input_output(model, variables, objectives, neg_contribs, pos_contribs, data):
    for nodeId, value in data["terminalNodes"].items():
        if value < 0:
            flows = gp.quicksum([variables[VariableType.FLOW.value][idx]*ratio for idx, ratio in pos_contribs[nodeId]])
            quantity = -value
            model.addLConstr(lhs=flows, rhs=quantity, sense=gp.GRB.LESS_EQUAL)
            objectives[CostType.MISSING_OUTPUT] += (quantity - flows)
        else:
            flows = gp.quicksum([variables[VariableType.FLOW.value][idx]*ratio for idx, ratio in neg_contribs[nodeId]])
            quantity = value
            model.addLConstr(lhs=flows, rhs=quantity, sense=gp.GRB.LESS_EQUAL)
            objectives[CostType.MISSING_INPUT] += (quantity - flows)

def compute_minimum_quantity_reqs(model, variables, limits, objectives, costType):
    for details in limits.values():
        l_edges, minQ, maxQ = details[0], details[1], details[2]
        if len(l_edges) == 0: continue
        flows = gp.quicksum([variables[VariableType.FLOW.value][idx]*ratio for idx, ratio in l_edges])
        if maxQ is not None:
            model.addLConstr(lhs=flows, rhs=maxQ, sense=gp.GRB.LESS_EQUAL)
        if minQ > 0:
            slack = model.addVar(lb=-float("inf"))
            model.addLConstr(lhs=flows + slack, rhs=minQ, sense=gp.GRB.GREATER_EQUAL)
            objectives[costType] += slack

def build_and_solve_model(data):
    model = gp.Model("HeapModel")
    variables = defaultdict(dict)
    variables[VariableType.CELL.value] = defaultdict(dict)
    objectives = {v: gp.LinExpr() for v in CostType}
    pos_contribs = defaultdict(list)
    neg_contribs = defaultdict(list)

    for edgeId, edge in data["edges"].items():
        from_, to_, transport = edge["from"], edge["to"], edge["transport"]
        add_heap_stock_variable(model, variables, from_, data)
        add_heap_stock_variable(model, variables, to_, data)
        pos_contribs[to_].append((edgeId, 1))
        neg_contribs[from_].append((edgeId, 1))
        if to_ in data["transformedNodes"]:
            for tNode, ratio in data["transformedNodes"][to_].get(from_, {}).items():
                pos_contribs[tNode].append((edgeId, ratio))
        variables[VariableType.FLOW.value][edgeId] = model.addVar()
        if transport:
            objectives[CostType.LOGISTIC] += edge["cost"] * variables[VariableType.FLOW.value][edgeId]

    for heapNodeId, heapNode in data["intermediateNodes"].items():
        stock_var = variables[VariableType.STOCK.value].get(heapNodeId)
        if stock_var is None: continue
        timePeriodId = heapNode["timePeriod"]
        mix_cells = gp.LinExpr()
        for cellId, cap in heapNode["cells"].items():
            bin_var = model.addVar(vtype=gp.GRB.BINARY)
            variables[VariableType.CELL.value][(cellId, timePeriodId)][heapNodeId] = bin_var
            mix_cells += bin_var * cap
        in_flows = gp.quicksum([variables[VariableType.FLOW.value][idx]*ratio for idx, ratio in pos_contribs[heapNodeId]])
        out_flows = gp.quicksum([variables[VariableType.FLOW.value][idx]*ratio for idx, ratio in neg_contribs[heapNodeId]])
        prev_stock = variables[VariableType.STOCK.value].get(heapNode.get("previous"), gp.LinExpr())
        model.addLConstr(lhs=stock_var, rhs=prev_stock + in_flows - out_flows, sense=gp.GRB.EQUAL)
        model.addLConstr(lhs=stock_var, rhs=mix_cells, sense=gp.GRB.LESS_EQUAL)

    for cell, cell_vars in variables[VariableType.CELL.value].items():
        model.addLConstr(lhs=gp.quicksum(cell_vars.values()), rhs=1, sense=gp.GRB.LESS_EQUAL)

    compute_minimum_quantity_reqs(model, variables, data["limitQuantities"], objectives, CostType.MISSING_MINIMUM_QUANTITIES)
    compute_missing_input_output(model, variables, objectives, neg_contribs, pos_contribs, data)

    model.setObjectiveN(objectives[CostType.MISSING_MINIMUM_QUANTITIES], index=0, priority=4, weight=1)
    model.setObjectiveN(objectives[CostType.MISSING_INPUT], index=1, priority=3, weight=1)
    model.setObjectiveN(objectives[CostType.MISSING_OUTPUT], index=2, priority=2, weight=1)
    model.setObjectiveN(objectives[CostType.LOGISTIC], index=3, priority=1, weight=1)
    model.setParam("MIPGap", 0.01)
    model.optimize()

    return model, variables
