import logging
import sys


class Munkres:

    def __init__(self):
        self.__C = None
        self.__row_covered = []
        self.__col_covered = []
        self.__n = 0
        self.__original_length = 0
        self.__original_width = 0
        self.__z_r = 0
        self.__z_c = 0
        self.__marked = None
        self.__path = None

    def setup(self, cost_matrix):
        self.__C = cost_matrix
        self.__n = len(self.__C)
        self.__original_length = len(cost_matrix)
        self.__original_width = len(cost_matrix[0])
        self.__row_covered = [False for _ in range(self.__n)]
        self.__col_covered = [False for _ in range(self.__n)]
        self.__z_r = 0
        self.__z_c = 0
        self.__path = self.__make_matrix(self.__n * 2, 0)
        self.__marked = self.__make_matrix(self.__n, 0)

    def get_col_covered(self):
        return self.__col_covered

    def get_row_covered(self):
        return self.__row_covered

    def get_marked(self):
        results = []
        for i in range(self.__original_length):
            for j in range(self.__original_width):
                if self.__marked[i][j] == 1:
                    results += [(i, j)]

        return results

    def solve_all(self):
        done = False
        step = 1

        steps = {1: self.__step1,
                 2: self.__step2,
                 3: self.__step3,
                 4: self.__step4,
                 5: self.__step5,
                 6: self.__step6}

        while not done:
            try:
                if step == 7:
                    break
                func = steps[step]
                step = func()
            except KeyError:
                print("the key is invalid")
                done = True
            except Exception as e:
                print("unexpected error")
                logging.exception(e)
                done = True

    def solve_step(self, step):

        steps = {1: self.__step1,
                 2: self.__step2,
                 3: self.__step3,
                 4: self.__step4,
                 5: self.__step5,
                 6: self.__step6}

        try:
            if step == 7:
                return
            func = steps[step]
            step = func()
            return step
        except KeyError:
            print("the key is invalid")
        except Exception as e:
            print("unexpected error")
            logging.exception(e)

    @staticmethod
    def __make_matrix(n, val):
        matrix = []
        for _ in range(n):
            matrix += [[val for _ in range(n)]]
        return matrix

    def __step1(self):
        n = self.__n
        for i in range(n):
            minval = min(self.__C[i])
            for j in range(n):
                self.__C[i][j] -= minval

        for i in range(n):
            minval = min(list(zip(*self.__C))[i])
            for j in range(n):
                self.__C[j][i] -= minval

        return 2

    def __step2(self):
        n = self.__n
        for i in range(n):
            for j in range(n):
                if (self.__C[i][j] == 0) and \
                   (not self.__col_covered[j]) and \
                   (not self.__row_covered[i]):
                    self.__marked[i][j] = 1
                    self.__col_covered[j] = True
                    self.__row_covered[i] = True

        self.__clear_covers()
        return 3

    def __step3(self):
        n = self.__n
        count = 0
        for i in range(n):
            for j in range(n):
                if self.__marked[i][j] == 1:
                    self.__col_covered[j] = True
                    count += 1

        if count >= n:
            return 7
        else:
            step = 4

        return step

    def __step4(self):
        step = 0
        done = False
        row = -1
        col = -1
        star_col = -1
        while not done:
            (row, col) = self.__find_a_zero()
            if row < 0:
                done = True
                step = 6
            else:
                self.__marked[row][col] = 2
                star_col = self.__find_star_in_row(row)
                if star_col >= 0:
                    col = star_col
                    self.__row_covered[row] = True
                    self.__col_covered[col] = False
                else:
                    done = True
                    self.__z_r = row
                    self.__z_c = col
                    step = 5

        return step

    def __step5(self):
        count = 0
        path = self.__path
        path[count][0] = self.__z_r
        path[count][1] = self.__z_c
        done = False
        while not done:
            row = self.__find_star_in_col(path[count][1])
            if row >= 0:
                count += 1
                path[count][0] = row
                path[count][1] = path[count-1][1]
            else:
                done = True

            if not done:
                col = self.__find_prime_in_row(path[count][0])
                count += 1
                path[count][0] = path[count-1][0]
                path[count][1] = col

        self.__convert_path(path, count)
        self.__clear_covers()
        self.__erase_primes()
        return 3

    def __step6(self):
        minval = self.__find_smallest()
        for i in range(self.__n):
            for j in range(self.__n):
                if self.__row_covered[i]:
                    self.__C[i][j] += minval
                if not self.__col_covered[j]:
                    self.__C[i][j] -= minval
        return 4

    def __find_smallest(self):
        minval = sys.maxsize
        for i in range(self.__n):
            for j in range(self.__n):
                if (not self.__row_covered[i]) and (not self.__col_covered[j]) and (minval > self.__C[i][j]):
                    minval = self.__C[i][j]
        return minval

    def __find_a_zero(self):
        row = -1
        col = -1
        i = 0
        n = self.__n
        done = False

        while not done:
            j = 0
            while True:
                if (self.__C[i][j] == 0) and \
                   (not self.__row_covered[i]) and \
                   (not self.__col_covered[j]):
                    row = i
                    col = j
                    done = True
                j += 1
                if j >= n:
                    break
            i += 1
            if i >= n:
                done = True

        return row, col

    def __find_star_in_row(self, row):
        col = -1
        for j in range(self.__n):
            if self.__marked[row][j] == 1:
                col = j
                break

        return col

    def __find_star_in_col(self, col):
        row = -1
        for i in range(self.__n):
            if self.__marked[i][col] == 1:
                row = i
                break

        return row

    def __find_prime_in_row(self, row):
        col = -1
        for j in range(self.__n):
            if self.__marked[row][j] == 2:
                col = j
                break

        return col

    def __convert_path(self, path, count):
        for i in range(count+1):
            if self.__marked[path[i][0]][path[i][1]] == 1:
                self.__marked[path[i][0]][path[i][1]] = 0
            else:
                self.__marked[path[i][0]][path[i][1]] = 1

    def __clear_covers(self):
        for i in range(self.__n):
            self.__row_covered[i] = False
            self.__col_covered[i] = False

    def __erase_primes(self):
        for i in range(self.__n):
            for j in range(self.__n):
                if self.__marked[i][j] == 2:
                    self.__marked[i][j] = 0
