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
    """
    Pretty sudoku GUI, made with pygame. Only for showing purposes.
    """
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

        solution = self.sudoku.solve(puzzle)
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


class Shuffle:
    """
    Shuffling methods for more interesting and complex puzzles.
    """
    @staticmethod
    def transposing(table):
        """ Transposing the whole grid """
        table = map(list, zip(*table))
        return list(table)

    @staticmethod
    def swap_rows_small(table):
        """ Swap the two rows """
        area = random.randrange(0, 3, 1)
        line1 = random.randrange(0, 3, 1)
        N1 = area * 3 + line1

        line2 = random.randrange(0, 3, 1)
        while line1 == line2:
            line2 = random.randrange(0, 3, 1)

        N2 = area * 3 + line2

        table[N1], table[N2] = table[N2], table[N1]
        return table

    @staticmethod
    def swap_colums_small(table):
        table = Shuffle.transposing(table)
        table = Shuffle.swap_rows_small(table)
        table = Shuffle.transposing(table)
        return table

    @staticmethod
    def swap_rows_area(table):
        """ Swap the two area horizon """
        area1 = random.randrange(0, 3, 1)
        area2 = random.randrange(0, 3, 1)
        while area1 == area2:
            area2 = random.randrange(0, 3, 1)

        for i in range(0, 3):
            N1, N2 = area1 * 3 + i, area2 * 3 + i
            table[N1], table[N2] = table[N2], table[N1]

        return table

    @staticmethod
    def shuffle(table: list[list], amount: int):
        """
        Main function to shuffle the grid.

        :param table: un-shuffled sudoku
        :param amount: amount of times to shuffle
        :return: shuffled sudoku
        """
        shuffle_func = [Shuffle.transposing,
                        Shuffle.swap_rows_small,
                        Shuffle.swap_colums_small,
                        Shuffle.swap_rows_area]
        for i in range(1, amount):
            id_func = random.randrange(0, len(shuffle_func), 1)
            table = shuffle_func[id_func](table)
        return table


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
        """
        Creates static but solvable sudoku grid.

        :return: the same sudoku puzzle every time
        """
        result = [[0 for _ in range(9)] for _ in range(9)]
        for i in range(9):
            for j in range(9):
                result[i][j] = str((i * 3 + i // 3 + j) % 9 + 1)
        return result

    def recursive_len(self, item):
        """


        :param item: puzzle | list
        :return: length of all items in list that are not "*"
        """
        if type(item) == list:
            return sum(self.recursive_len(subitem) for subitem in item)
        else:
            return 1 if item != "*" else 0

    def generate_puzzle(self, solved_count) -> list[list]:
        result = self.create_static_puzzle()
        result = Shuffle.shuffle(result, 13)

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
            json.dump(puzzle, output_file)  # , indent=2)

    @staticmethod
    def read_puzzle(path: str = 'puzzle.json') -> list[list]:
        with open(path) as f:
            puzzle = json.load(f)
        return puzzle

    @staticmethod
    def check_solution(solution: list[list]) -> bool:
        """
        Checks if the puzzle solution is valid.

        :param solution: puzzle solution
        :return: `True` if the solution is valid, else `False`
        """
        for row in range(0, 9):
            d = {}
            for col in range(0, 9):
                val = solution[row][col]
                if val != '*' and val in d:
                    return False
                d[val] = 1

        for col in range(0, 9):
            d = {}
            for row in range(0, 9):
                val = solution[row][col]
                if val != '*' and val in d:
                    return False
                d[val] = 1

        for i in range(0, 3):
            for j in range(0, 3):
                d = {}
                for r in range(0, 3):
                    for c in range(0, 3):
                        row = (3 * i) + r
                        col = (3 * j) + c
                        val = solution[row][col]
                        if val != '*' and val in d:
                            return False
                        d[val] = 1
                        return True

    @staticmethod
    def cell_choice(puzzle: list[list], col_ind, row_ind):
        """
        Get all possible choices for a cell solution.

        :param puzzle: the puzzle
        :param col_ind: cell column index
        :param row_ind: cell row index
        :return: all possible cell solutions
        """
        solved_row_cells = [x for x in SudokuTerminal.get_row(puzzle, row_ind) if x != "*"]
        solved_column_cells = [x for x in SudokuTerminal.get_column(puzzle, col_ind) if x != "*"]
        solved_square_cells = [x for x in SudokuTerminal.get_square(puzzle, col_ind, row_ind) if x != "*"]
        solved = solved_row_cells.copy()
        solved.extend(x for x in solved_column_cells if x not in solved)
        solved.extend(x for x in solved_square_cells if x not in solved)
        cell_choices = [str(x) for x in range(1, 10) if str(x) not in solved]
        return cell_choices

    @staticmethod
    def get_cell_solutions(puzzle: list[list]):
        result = [[ ["solved"] for _ in range(9)] for _ in range(9)]
        for row_ind in range(len(puzzle)):
            for col_ind in range(len(puzzle[row_ind])):
                if puzzle[row_ind][col_ind] != "*":
                    continue
                cell_choices = SudokuTerminal.cell_choice(puzzle, col_ind, row_ind)
                result[row_ind][col_ind] = cell_choices
        return result

    @staticmethod
    def solve_all_ones(puzzle: list[list]):
        """
        Solves all cells that can be solved with `fill if theres a single possible answer` method.

        :param puzzle: sudoku puzzle
        """
        all_solutions = SudokuTerminal.get_cell_solutions(puzzle)
        while any(isinstance(item, list) and len(item) == 1 and item[0] != 'solved' for sublist in all_solutions for item in sublist):
            print("a")
            for row_ind in range(len(all_solutions)):
                for col_ind in range(len(all_solutions[row_ind])):
                    if puzzle[row_ind][col_ind] != "*":
                        continue
                    cell_choices = all_solutions[row_ind][col_ind]
                    if len(cell_choices) == 1:
                        puzzle[row_ind][col_ind] = cell_choices[0]
            all_solutions = SudokuTerminal.get_cell_solutions(puzzle)

    def solve(self, puzzle: list[list]) -> list[list]:
        result = copy.deepcopy(puzzle)
        if self.debug:
            print(f"solving sudoku!")
        if not any([item for item in result if any(x for x in item if x != "*")]):
            raise Exception("The sudoku is empty!")
        if self.recursive_len(result) < 17:
            raise Exception("This is not solvable!")
        self.solve_all_ones(result)
        print(self.check_solution(result))
        # while any("*" in sl for sl in result):
        # for row_ind in range(len(result)):
        #     row = result[row_ind]
        #     # if self.debug:
        #     #     print(f"sudoku row {row_ind}: {row}")
        #     if "*" not in row:
        #         continue
        #     for col_ind in range(len(row)):
        #         if row[col_ind] != "*":
        #             continue
        #         cell_choices = self.cell_choice(puzzle, col_ind, row_ind)
        #         if not cell_choices:
        #             if self.debug:
        #                 print(f"row {row_ind}, column {col_ind}, the cell: {row[col_ind]}")
        #             raise Exception("This is not solvable!")
        #         # if len(cell_choices) == 1:
        #         #     result[row_ind][col_ind] = cell_choices[0]
        #         else:
        #             print(f"the row: {result[row_ind]}")
        #             print(f"the column: {self.get_column(result, col_ind)}")
        #             print(f"the square: {self.get_square(result, col_ind, row_ind)}")
        #             print(f"choices: {cell_choices}")
        #             for choice in cell_choices:
        #                 result[row_ind][col_ind] = choice
        #                 if not self.check_solution(result):
        #                     result[row_ind][col_ind] = "*"
        #                     print('test')
        #                 else:
        #                     break
        #                     # result[row_ind] =
        #         solved = []
        if self.debug:
            print("sudoku solved!")
        return result


def main():
    game = SudokuGUI(debug=True)
    game.start(40)


if __name__ == "__main__":
    main()
