import copy

import pygame
import sys
import random
import json


class Colors:
    BLACK = (0, 0, 0)
    WHITE = (200, 200, 200)
    RED = (255, 0, 0)


class SudokuGUI:
    def __init__(self, width=540, height=540, debug=False):
        self.window_width = width
        self.window_height = height
        self.debug = debug
        self.sudoku = SudokuTerminal(debug)

        pygame.init()
        self.screen = pygame.display.set_mode((self.window_width, self.window_height))
        self.font = pygame.font.SysFont('arial', 50)

    def start(self, puzzle_solved_count: int = 80, puzzle_path: str = 'puzzle.json'):
        try:
            puzzle = self.sudoku.read_puzzle(puzzle_path)
        except FileNotFoundError:
            puzzle = self.sudoku.generate_puzzle(puzzle_solved_count)
            if not self.debug:
                self.sudoku.write_puzzle(puzzle, puzzle_path)

        solution = None #self.sudoku.solve(puzzle)
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
    def __init__(self, debug=False):
        self.debug = debug

    @staticmethod
    def get_row(matrix: list[list], row_ind: int) -> list:
        return matrix[row_ind]

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

    @staticmethod
    def create_static_puzzle() -> list[list]:
        result = [[0 for _ in range(9)] for _ in range(9)]
        for i in range(9):
            for j in range(9):
                result[i][j] = str((i * 3 + i // 3 + j) % 9 + 1)
        return result

    def recursive_len(self, item):
        if type(item) == list:
            return sum(self.recursive_len(subitem) for subitem in item)
        else:
            return 1 if item != "*" else 0

    def generate_puzzle(self, solved_count) -> list[list]:
        def shuffle_rows_in_block(puzzle):
            block_ind = random.randint(0, 2) * 3
            rows = puzzle[block_ind:block_ind + 3]
            random.shuffle(rows)
            puzzle[block_ind:block_ind + 3] = rows
            return puzzle

        def shuffle_cols_in_block(puzzle):
            transposed_puzzle = list(map(list, zip(*puzzle)))
            transposed_puzzle = shuffle_rows_in_block(transposed_puzzle)
            return list(map(list, zip(*transposed_puzzle)))

        def shuffle_blocks(puzzle):
            blocks = [puzzle[i:i + 3] for i in range(0, 9, 3)]
            random.shuffle(blocks)
            return [block[j] for block in blocks for j in range(3)]

        result = self.create_static_puzzle()
        result = shuffle_rows_in_block(result)
        result = shuffle_cols_in_block(result)
        result = shuffle_blocks(result)

        solved = self.recursive_len(result)
        solved_count = 81 if solved_count > 81 else solved_count
        if not self.debug:
            solved_count = 17 if solved_count < 17 else solved_count
            # An ordinary sudoku puzzle with a unique solution must have at least 17 clues.
            # Source: https://en.wikipedia.org/wiki/Mathematics_of_Sudoku
        while solved > solved_count:
            row_ind = random.randint(0, 8)
            col_ind = random.randint(0, 8)
            result[row_ind][col_ind] = "*"
            solved = self.recursive_len(result)
        if self.debug:
            print(f"sudoku generated, solved cells: {solved}")
        return result

    @staticmethod
    def write_puzzle(puzzle: list[list], path: str = 'puzzle.json'):
        with open(path, 'w') as output_file:
            json.dump(puzzle, output_file)#, indent=2)

    @staticmethod
    def read_puzzle(path: str = 'puzzle.json') -> list[list]:
        with open(path) as f:
            puzzle = json.load(f)
        return puzzle

    def solve(self, puzzle: list[list]) -> list[list]:
        result = copy.deepcopy(puzzle)
        if self.debug:
            print(f"solving sudoku!")
        if not any([item for item in result if any(x for x in item if x != "*")]):
            raise Exception("The sudoku is empty!")
        if self.recursive_len(result) < 17:
            raise Exception("This is not solvable!")
        while any("*" in sl for sl in result):
            for row_ind in range(len(result)):
                row = result[row_ind]
                if self.debug:
                    print(f"sudoku row {row_ind}: {row}")
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
                        if self.debug:
                            print(f"row {row_ind}, column {col_ind}, the cell: {row[col_ind]}\nsolved cells: {solved}")
                        raise Exception("This is not solvable!")
                    if len(cell_choices) == 1:
                        row[col_ind] = cell_choices[0]
                    solved_column_cells = []
                    solved_square_cells = []
                    solved = []
                result[row_ind] = row
        if self.debug:
            print("sudoku solved!")
        return result


def main():
    game = SudokuGUI(debug=True)
    game.start(46)


if __name__ == "__main__":
    main()
