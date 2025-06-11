import pandas as pd
from enums import VariableType

def write_solution(variables):
    flows = []
    cells = []
    for edgeId, var in variables[VariableType.FLOW.value].items():
        if var.X > 1e-3:
            flows.append({"edgeId": edgeId, "value": var.X})
    for cellIdPeriod, productDict in variables[VariableType.CELL.value].items():
        for productId, var in productDict.items():
            if var.X > 1e-3:
                cells.append({
                    "cellId": cellIdPeriod[0],
                    "timePeriodId": cellIdPeriod[1],
                    "productId": productId,
                    "value": var.X
                })
    return pd.DataFrame(flows), pd.DataFrame(cells)
