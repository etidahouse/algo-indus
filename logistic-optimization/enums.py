from enum import Enum

class VariableType(Enum):
    FLOW = 1
    STOCK = 2
    CELL = 3

class CostType(Enum):
    MISSING_INPUT = 1
    MISSING_MINIMUM_QUANTITIES = 2
    MISSING_OUTPUT = 3
    LOGISTIC = 4
