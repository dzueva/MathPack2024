import copy

import pygame
import sys
import random
import itertools
import json


class Colors:
    BLACK = (0, 0, 0)
    WHITE = (200, 200, 200)
    RED = (255, 0, 0)


class SudokuGUI:
    def __init__(self, width=540, height=540):
        self.window_width = width
        self.window_height = height
        self.sudoku = SudokuTerminal()

        pygame.init()
        self.screen = pygame.display.set_mode((self.window_width, self.window_height))
        self.font = pygame.font.SysFont('arial', 50)

    def start(self, puzzle_path: str = 'puzzle.json'):
        try:
            puzzle = self.sudoku.read_puzzle(puzzle_path)
        except FileNotFoundError:
            puzzle = self.sudoku.generate_puzzle()
            self.sudoku.write_puzzle(puzzle, puzzle_path)

        solution = self.sudoku.solve(puzzle)
        self.sudoku.write_puzzle(solution, "puzzle_solution.json")
        self.draw_grid(puzzle=puzzle, solution=solution)

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            pygame.display.update()

    def draw_grid(self, puzzle: list[list], solution: list[list] = None):
        block_size = 60  # Set the size of the grid block
        for x in range(0, self.window_width, block_size):
            for y in range(0, self.window_height, block_size):
                row = x // 60
                column = y // 60
                puzzle_number = puzzle[row][column]
                if solution is not None and puzzle_number == "*":
                    solution_number = solution[row][column]
                    text = self.font.render(solution_number, True, Colors.RED)
                else:
                    text = self.font.render(puzzle_number if puzzle_number != "*" else "", True, Colors.WHITE)
                rect = pygame.Rect(x, y, block_size, block_size)
                self.screen.blit(text, (y + 20, x))
                pygame.draw.rect(self.screen, Colors.WHITE, rect, 1)


class SudokuTerminal:
    @staticmethod
    def get_column(matrix: list[list], column_ind: int) -> list:
        column = []
        for row in matrix:
            column.append(row[column_ind])
        return column

    @staticmethod
    def get_square(matrix: list[list], column_ind: int, row_ind: int) -> list:
        square = []
        start_row = (row_ind // 3) * 3
        start_col = (column_ind // 3) * 3
        for i in range(start_row, start_row + 3):
            for j in range(start_col, start_col + 3):
                square.append(matrix[i][j])
        return square

    def generate_puzzle(self) -> list[list]:
        result = [["*"] * 9] * 9
        for row in range(9):
            row_result = ["*"] * 9
            for i in range(random.randint(0, 9)):
                cell = random.randint(0, 8)
                check = ["0"]
                check.extend(x for x in row_result if x not in check)
                check.extend(x for x in self.get_column(result, cell) if x not in check)
                check.extend(x for x in self.get_square(result, cell, row) if x not in check)
                choice = [x for x in range(10) if str(x) not in check]
                if not choice:
                    continue
                cell_res = random.choice(choice)
                row_result[cell] = str(cell_res)
            result[row] = row_result
        return result

    @staticmethod
    def write_puzzle(puzzle: list[list], path: str = 'puzzle.json'):
        with open(path, 'w') as output_file:
            json.dump(puzzle, output_file, indent=2)

    @staticmethod
    def read_puzzle(path: str = 'puzzle.json') -> list[list]:
        with open(path) as f:
            puzzle = json.load(f)
        return puzzle

    def solve(self, puzzle: list[list]) -> list[list]:
        result = copy.deepcopy(puzzle)
        while any("*" in sl for sl in result):
            for row_ind in range(len(result)):
                row = result[row_ind]
                if "*" not in row:
                    continue
                solved_row_cells = [x for x in row if x != "*"]
                for col_ind in range(len(row)):
                    if row[col_ind] != "*":
                        continue
                    solved_column_cells = [x for x in self.get_column(result, col_ind) if x != "*"]
                    solved_square_cells = [x for x in self.get_square(result, col_ind, row_ind) if x != "*"]
                    solved = solved_row_cells.copy()
                    solved.extend(x for x in solved_column_cells if x not in solved)
                    solved.extend(x for x in solved_square_cells if x not in solved)
                    cell_choices = [str(x) for x in range(1, 10) if str(x) not in solved]
                    if not cell_choices:
                        print(f"row {row_ind}, column {col_ind}, the cell: {row[col_ind]}\nsolved cells: {solved}")
                        raise Exception("This is not solvable!")
                    if len(cell_choices) == 1:
                        row[col_ind] = cell_choices[0]
                    solved_column_cells = []
                    solved_square_cells = []
                    solved = []
                result[row_ind] = row
        return result


def main():
    game = SudokuGUI()
    game.start("puzzle_solvable.json")
    # puzzle = game.generate_puzzle()
    # game.write_puzzle(puzzle)


if __name__ == "__main__":
    main()
