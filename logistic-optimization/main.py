from model import build_and_solve_model
from data_loader import load_data
from writer import write_solution
from config import FLOWS_CSV, CELLS_CSV

def main():
    data = load_data()
    model, variables = build_and_solve_model(data)
    flows_df, cells_df = write_solution(variables)
    flows_df.to_csv(FLOWS_CSV, index=False)
    cells_df.to_csv(CELLS_CSV, index=False)

if __name__ == "__main__":
    main()
