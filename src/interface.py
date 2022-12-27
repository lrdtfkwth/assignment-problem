import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
from tkinter.simpledialog import askinteger
from tkinter.messagebox import showerror

MARGIN = 0  # Pixels around the board
CELL_WIDTH = 50  # Width of every board cell.


def command_help():
    about_window = tk.Toplevel()
    about_window.title('help')
    about_window.geometry('460x200')
    about_window.maxsize(460, 200)
    about_window.minsize(460, 200)

    abouttext = """ 1. you can create a new project or open old one
    2. if you created a new project fill the matrix correctly
    3. when you fill the matrix correctly click on solve or step
    4. the solution will appear on the interface
    5. you can chose to save the project for later use"""

    aboutlabel = tk.Label(about_window, text=abouttext)
    aboutlabel.pack(pady=50)


def command_about():
    help_window = tk.Toplevel()
    help_window.title('about')
    help_window.geometry('350x120')
    help_window.maxsize(350, 120)
    help_window.minsize(350, 120)

    helptext = """ This program is an implementation 
    of the hungarian algorithm (munkres) 
    for solving assignment problem. 
    Created by larid toufik and lachi nadir """

    helplabel = tk.Label(help_window, text=helptext)
    helplabel.pack(pady=20)


class Interface:

    def __init__(self, root, controller):
        self.__controller = controller

        self.menubar = self.set_menubar(root)

        self.__topframe = tk.Frame(root)
        self.__topframe.pack(side=tk.TOP, fill=tk.X)
        self._toppanel = TopPanel(self.__topframe)
        self._toppanel.solvebutton.configure(command=self.__controller.command_solve)
        self._toppanel.stepbutton.configure(command=self.__controller.command_step)

        self.__bottomframe = tk.Frame(root)
        self.__bottomframe.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        self._matrix = MatrixUi(self.__bottomframe, self.__controller)
        
        self.__bottomframe.columnconfigure(0, weight=1)
        self.__bottomframe.rowconfigure(0, weight=1)

        self._openpath = None
        self._savepath = None

    def set_menubar(self, root):
        menubar = tk.Menu(root)

        root.config(menu=menubar)

        filemenu = tk.Menu(menubar, tearoff=False)
        filemenu.add_command(label="New", command=self.new_project_window)
        filemenu.add_command(label="Open", command=self.__controller.command_open)
        filemenu.add_command(label="Save", command=self.__controller.command_save)

        filemenu.add_separator()

        filemenu.add_command(label="Exit", command=exit)
        menubar.add_cascade(label="File", menu=filemenu)

        helpmenu = tk.Menu(menubar, tearoff=False)
        helpmenu.add_command(label="Help", command=command_help)
        helpmenu.add_command(label="About", command=command_about)
        menubar.add_cascade(label="Help", menu=helpmenu)

        return menubar

    def open_project(self):
        ftypes = [('CSV files', '*.csv'), ('All files', '*')]
        self._openpath = fd.askopenfilename(title='Open a file', initialdir='~', filetypes=ftypes)
        return self._openpath

    def save_project(self):
        ftypes = [('CSV files', '*.csv'), ('All files', '*')]
        self._savepath = fd.asksaveasfilename(title='Save a file', initialdir='~', filetypes=ftypes)
        return self._savepath

    def new_project_window(self):
        size = askinteger("Input", "Input the size of the matrix")
        self.__controller.command_new_matrix(size)

    @staticmethod
    def showerror(title, msg):
        showerror(title, msg)

    @property
    def matrix(self):
        return self._matrix

    @property
    def toppanel(self):
        return self._toppanel


class TopPanel:

    def __init__(self, frame):
        self.__frame = tk.Frame(frame)
        self.__frame.pack(side=tk.TOP, fill=tk.X)

        self._solvebutton = tk.Button(frame, text="solve")
        self._solvebutton.pack(side=tk.RIGHT, padx=20, pady=20)
        
        self._stepbutton = tk.Button(frame, text="step")
        self._stepbutton.pack(side=tk.RIGHT, padx=20, pady=20)

        self.__reslabel = tk.Label(frame, text="total cost: ")
        self.__reslabel.pack(side=tk.LEFT, padx=20, pady=20)

    def set_label(self, total_cost):
        self.__reslabel.config(text="total cost: " + str(total_cost))

    def reset_label(self):
        self.__reslabel.config(text="total cost:")

    @property
    def solvebutton(self):
        return self._solvebutton

    @property
    def stepbutton(self):
        return self._stepbutton


class MatrixUi:

    def __init__(self, frame, controller):
        self.__controller = controller

        self.__row, self.__col = 0, 0
        self.__WIDTH, self.__HEIGHT = 0, 0
        self.__size = 0

        self.__matrix_field = tk.Canvas(frame)
        self.__matrix_field.grid(row=0, column=0, sticky=tk.E + tk.W + tk.N + tk.S)

        self.__cellentry = tk.Entry(self.__matrix_field)

        self.__scrolly = tk.Scrollbar(frame, orient="vertical", command=self.__matrix_field.yview)
        self.__scrollx = tk.Scrollbar(frame, orient="horizontal", command=self.__matrix_field.xview)
        
        self.__matrix_field.configure(xscrollcommand=self.__scrollx.set, yscrollcommand=self.__scrolly.set)

        self.__scrollx.grid(row=1, column=0, sticky=tk.E + tk.W)
        self.__scrolly.grid(row=0, column=1, sticky=tk.N + tk.S)

        sizegrip = ttk.Sizegrip(frame)
        sizegrip.grid(row=1, column=1)

        self.__matrix_field.bind("<Button-1>", self.cell_clicked)
        self.__cellentry.bind('<Return>', self.handle_cell_entry)

    def init_empty_matrix(self, size):
        self.__size = int(size)

        # Width and height of the whole board
        self.__WIDTH = self.__HEIGHT = CELL_WIDTH * int(size)

        self.__matrix_field.configure(scrollregion=(0, 0, self.__WIDTH, self.__HEIGHT))

        self.__matrix_field.delete("line")
        self.__matrix_field.delete("numbers")
        self.__matrix_field.delete("marked")
        self.__matrix_field.delete("covered")
        for i in range(int(size) + 1):
            color = "black"

            x0 = MARGIN + i * CELL_WIDTH
            y0 = MARGIN
            x1 = MARGIN + i * CELL_WIDTH
            y1 = self.__HEIGHT + MARGIN
            self.__matrix_field.create_line(x0, y0, x1, y1, tags="line", fill=color)

            x0 = MARGIN
            y0 = MARGIN + i * CELL_WIDTH
            x1 = self.__WIDTH + MARGIN
            y1 = MARGIN + i * CELL_WIDTH
            self.__matrix_field.create_line(x0, y0, x1, y1, tags="line", fill=color)

        self.__matrix_field.focus_set()

    def draw_matrix_lines(self):
        # Width and height of the whole board
        self.__WIDTH = self.__HEIGHT = CELL_WIDTH * self.__size

        for i in range(self.__size + 1):
            color = "black"

            x0 = MARGIN + i * CELL_WIDTH
            y0 = MARGIN
            x1 = MARGIN + i * CELL_WIDTH
            y1 = self.__HEIGHT + MARGIN
            self.__matrix_field.create_line(x0, y0, x1, y1, tags="line", fill=color)

            x0 = MARGIN
            y0 = MARGIN + i * CELL_WIDTH
            x1 = self.__WIDTH + MARGIN
            y1 = MARGIN + i * CELL_WIDTH
            self.__matrix_field.create_line(x0, y0, x1, y1, tags="line", fill=color)

        self.__matrix_field.focus_set()

    def fill_matrix(self):
        self.__matrix_field.delete("numbers")
        for i in range(int(self.__size)):
            for j in range(int(self.__size)):
                cell_value = self.__controller.get_cost_matrix(i, j)
                x = MARGIN + j * CELL_WIDTH + CELL_WIDTH / 2
                y = MARGIN + i * CELL_WIDTH + CELL_WIDTH / 2
                color = "black"
                self.__matrix_field.create_text(x, y, text=cell_value, tags="numbers", fill=color)
        
        self.__matrix_field.focus_set()

    def cell_clicked(self, event):
        deltax = int(self.__scrollx.get()[0] * CELL_WIDTH * self.__size)
        deltay = int(self.__scrolly.get()[0] * CELL_WIDTH * self.__size)

        x, y = event.x, event.y

        x += deltax
        y += deltay

        if MARGIN < x < self.__WIDTH - MARGIN and MARGIN < y < self.__HEIGHT - MARGIN:
            
            # get row, col number from x, y coordinates
            row, col = (y - MARGIN) // CELL_WIDTH, (x - MARGIN) // CELL_WIDTH
            
            # if cell was selected already - deselect it
            if (row, col) == (self.__row, self.__col):
                self.__row, self.__col = -1, -1
            else:
                self.__row, self.__col = row, col
        else:
            self.__row, self.__col = -1, -1

        self.draw_cursor()

    def draw_cursor(self):
        self.__matrix_field.delete("cursor")
        if self.__row >= 0 and self.__col >= 0:
            x0 = MARGIN + self.__col * CELL_WIDTH + 1
            y0 = MARGIN + self.__row * CELL_WIDTH + 1
            x1 = MARGIN + (self.__col + 1) * CELL_WIDTH - 1
            y1 = MARGIN + (self.__row + 1) * CELL_WIDTH - 1

            self.__cellentry.icursor(tk.END)
            self.__matrix_field.create_window(x0, y0, width=x1 - x0, height=y1 - y0,
                                              window=self.__cellentry, anchor='nw', tags="cursor")

            value = self.__controller.get_cost_matrix(self.__row, self.__col)
            if value is not None:
                self.__cellentry.delete(0, tk.END)
                self.__cellentry.insert(tk.END, str(value))
            self.__cellentry.focus_set()

    def handle_cell_entry(self, event):
        if self.__row >= 0 and self.__col >= 0 and self.__cellentry.get().isdigit():
            self.__controller.set_cost_matrix(self.__row, self.__col, int(self.__cellentry.get()))

            # move to the next cell if it not the end of the matrix
            if self.__row >= self.__size-1:
                self.__col, self.__row = -1, -1
                self.__cellentry.delete(0, tk.END)
            else:
                self.__row = self.__row + 1
                self.__cellentry.delete(0, tk.END)
            self.fill_matrix()
            self.draw_cursor()
        return event

    def draw_marked(self, res):
        self.__matrix_field.delete("marked")
        for row, col in res:
            x0 = MARGIN + col * CELL_WIDTH + 1
            y0 = MARGIN + row * CELL_WIDTH + 1
            x1 = MARGIN + (col + 1) * CELL_WIDTH - 1
            y1 = MARGIN + (row + 1) * CELL_WIDTH - 1

            self.__matrix_field.create_rectangle(x0, y0, x1, y1, fill="dark red", outline="red", tags="marked")

    def draw_covered(self, rows, cols):
        self.__matrix_field.delete("covered")
        for i, row in enumerate(rows):
            if row:
                x0 = MARGIN + 0
                y0 = MARGIN + i * CELL_WIDTH + 1
                x1 = MARGIN + self.__size * CELL_WIDTH - 1
                y1 = MARGIN + (i + 1) * CELL_WIDTH - 1
                self.__matrix_field.create_rectangle(x0, y0, x1, y1, fill="blue", outline="blue", tags="covered")
        
        for i, col in enumerate(cols):
            if col:
                x0 = MARGIN + i * CELL_WIDTH + 1
                y0 = MARGIN + 0
                x1 = MARGIN + (i + 1) * CELL_WIDTH - 1
                y1 = MARGIN + self.__size * CELL_WIDTH - 1
                self.__matrix_field.create_rectangle(x0, y0, x1, y1, fill="blue", outline="blue", tags="covered")
