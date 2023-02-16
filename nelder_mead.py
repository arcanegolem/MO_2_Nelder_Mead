from math import sqrt, exp, pow
from dot import Dot, sum_dots
import sys

def targetFunction(dot: Dot) -> float:
    '''
    Функция 13 варианта
    '''
    return pow(dot.coord_x, 2) + exp(pow(dot.coord_x, 2) + pow(dot.coord_y, 2)) + (4 * dot.coord_x) + (3 * dot.coord_y)


def guidedFunction(dot: Dot) -> float:
    return pow(dot.coord_x, 2) - (dot.coord_x * dot.coord_y) + (3 * pow(dot.coord_y, 2)) - dot.coord_x


class NelderMead:
    '''
    Класс для минимизации функции методом Нельдера-Мида

    n: Размерность функции
    m: Длина ребра
    beta: Параметр растяжения
    gamma: Параметр сжатия
    epsilon: Точность поиска
    targetFunction: Минимизируемая функция
    '''

    result_matrix: list
    dots         : dict = {}

    startingDot  : Dot

    n            : int

    m            : float
    beta         : float
    gamma        : float
    epsilon      : float

    def __init__(self, n: int, start_dot: Dot, m: float, beta: float, gamma: float, epsilon: float, targetFunction) -> None:
        self.          n = n
        self.          m = m
        self.    epsilon = epsilon
        self.       beta = beta
        self.startingDot = start_dot
        self. targetFunc = targetFunction

        self.dots[self.targetFunc(self.startingDot)] = self.startingDot

        print("\nТочки в списке после первоначального заполнения:")
        self.generateDotsInitial()
        for res in self.dots:
            print(str(res) + "\t: ", str(self.dots[res]))

        iters = -1

        min_val_dot, pre_max_val_dot, max_val_dot = self.getMinMaxPreMaxDotVal()

        cut_wc = self.findCutWeightCenter(max_val_dot[1])

        reflection = self.reflectDotAndResult(cut_wc, max_val_dot[1])

        self.checkAndSwap(max_val_dot, reflection)
        for result, dot in self.dots.items():
                print(str(result) + "\t:", str(dot))


    def getMinMaxPreMaxDotVal(self):
        sorted_dots = dict(sorted(self.dots.items(), key = lambda item: item[0]))
        items = list(sorted_dots.items())

        return items

    
    def generateDotsInitial(self):
        '''
        Создание начальных точек
        '''
        newDot_1 = self.startingDot + Dot(self.calcDelta1(), self.calcDelta2())
        newDot_2 = self.startingDot + Dot(self.calcDelta2(), self.calcDelta1())

        self.dots[self.targetFunc(newDot_1)] = newDot_1
        self.dots[self.targetFunc(newDot_2)] = newDot_2

    
    def checkAndSwap(self, exclusion: tuple, reflection: tuple):
        '''
        Проверка отраженной точки и при успехе замена исключаемой, при неудаче редукция
        '''
        if reflection[0] < exclusion[0]:
            self.dots[reflection[0]] = reflection[1]
            del self.dots[exclusion[0]]
        else:
            self.compress()


    def compress(self):
        pass

    
    def reflectDotAndResult(self, wc, dot) -> tuple:
        '''
        Отражение точки и возвращение точки и координат функции в этой точке
        '''
        reflected_dot = (wc * 2) - dot
        return (self.targetFunc(reflected_dot), reflected_dot)


    def findCutWeightCenter(self, excludedDot: Dot) -> Dot:
        '''
        Центр тяжести без исключаемой точки
        '''
        operated_dots = []

        for result, dot in self.dots.items():
            if dot != excludedDot:
                operated_dots.append(dot)

        return (sum_dots(operated_dots)) * (1/self.n)


    def calcDelta1(self) -> float:
        '''
        Получение первой дельты
        '''
        return ((sqrt(self.n + 1) - 1) / (self.n * sqrt(2))) * self.m
    
    
    def calcDelta2(self) -> float:
        '''
        Получение второй дельты
        '''
        return ((sqrt(self.n + 1) + self.n - 1) / (self.n * sqrt(2))) * self.m


nelder_mead = NelderMead(n = 2, start_dot = Dot(0, 0), m = 1, beta = 2.8, gamma = 0.4, epsilon = 0.1, targetFunction = guidedFunction)