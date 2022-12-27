import tkinter as tk  # python 3
import copy
import csv

from munkres import Munkres
from interface import Interface


class Controller:
    def __init__(self):
        self.__root = tk.Tk()
        self.__munkres = Munkres()
        self.__ui = Interface(self.__root, self)

        self.__size = 0
        self.__origin_matrix = []
        self.__cost_matrix = []
        self.__step = 1

    @staticmethod
    def init_cost_matrix(size, value=None):
        return [[value for _ in range(size)] for _ in range(size)]

    def set_cost_matrix(self, row, col, value):
        self.__cost_matrix[row][col] = self.__origin_matrix[row][col] = int(value)

    def get_cost_matrix(self, row, col):
        return self.__cost_matrix[row][col]

    def get_total_cost(self):
        total_cost = 0
        for row, col in self.__munkres.get_marked():
            total_cost += self.__origin_matrix[row][col]
        return total_cost

    def is_fill_matrix(self):
        for i in range(self.__size):
            for j in range(self.__size):
                if self.__origin_matrix[i][j] is None:
                    return False
        return True

    @staticmethod
    def pad_matrix(matrix, pad_value=0):
        max_columns = 0
        total_rows = len(matrix)

        for row in matrix:
            max_columns = max(max_columns, len(row))

        total_rows = max(max_columns, total_rows)

        new_matrix = []
        for row in matrix:
            row_len = len(row)
            new_row = row[:]
            if total_rows > row_len:
                # Row too short. Pad it.
                new_row += [pad_value] * (total_rows - row_len)
            new_matrix += [new_row]

        while len(new_matrix) < total_rows:
            new_matrix += [[pad_value] * total_rows]

        return new_matrix

    def command_solve(self):
        if self.is_fill_matrix():
            self.__munkres.setup(self.__cost_matrix)
            self.__munkres.solve_all()

            self.__ui.matrix.draw_marked(self.__munkres.get_marked())
            self.__ui.matrix.fill_matrix()
            self.__ui.matrix.draw_matrix_lines()
            self.__ui.toppanel.set_label(self.get_total_cost())
        else:
            self.__ui.showerror("error", "matrix is not filled correctly")

    def command_step(self):
        if self.is_fill_matrix():
            if self.__step == 1:
                self.__munkres.setup(self.__cost_matrix)

            self.__step = self.__munkres.solve_step(self.__step)

            self.__ui.matrix.draw_covered(self.__munkres.get_row_covered(), self.__munkres.get_col_covered())
            self.__ui.matrix.draw_marked(self.__munkres.get_marked())
            self.__ui.matrix.draw_matrix_lines()
            self.__ui.matrix.fill_matrix()

            if self.__step == 7:
                self.__ui.toppanel.set_label(self.get_total_cost())

        else:
            self.__ui.showerror("error", "matrix is not filled correctly")

    def command_new_matrix(self, size):
        self.__size = size
        self.__origin_matrix = self.init_cost_matrix(self.__size)
        self.__cost_matrix = copy.deepcopy(self.__origin_matrix)

        self.__ui.matrix.init_empty_matrix(self.__size)
        self.__ui.toppanel.reset_label()

        self.__step = 1

    def command_open(self):
        filepath = self.__ui.open_project()
        if filepath:
            with open(filepath, 'r') as csvfile:
                csv_reader = csv.reader(csvfile, delimiter=',')

                self.__origin_matrix = self.pad_matrix(
                        [list(map(int, line)) for line in csv_reader])

                self.__cost_matrix = copy.deepcopy(self.__origin_matrix)
                self.__size = len(self.__origin_matrix)

                self.__ui.matrix.init_empty_matrix(self.__size)
                self.__ui.matrix.fill_matrix()
                self.__ui.toppanel.reset_label()

        self.__step = 1

    def command_save(self):
        filepath = str(self.__ui.save_project())
        if filepath:
            with open(filepath, 'w') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerows(self.__origin_matrix)

    def run(self):
        self.__root.title('assignment problem')
        self.__root.geometry('800x600')
        self.__root.minsize(800, 600)

        logo = tk.PhotoImage(file='../img/Python-logo.png')
        self.__root.iconphoto(False, logo)

        self.__root.mainloop()
