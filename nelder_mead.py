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


def methodFunction(dot: Dot) -> float:
    return 2.8 * pow(dot.coord_y, 2) + 1.9 * dot.coord_x + 2.7 * pow(dot.coord_x, 2) + 1.6 - 1.9 * dot.coord_y


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
        self.      gamma = gamma
        self.startingDot = start_dot
        self. targetFunc = targetFunction

        self.dots[self.targetFunc(self.startingDot)] = self.startingDot

        print("\nТочки в списке после первоначального заполнения:")
        self.generateDotsInitial()
        for res in self.dots:
            print(str(res) + "\t: ", str(self.dots[res]))

        isDone = False

        iters = -1

        while not isDone:
            iters += 1

            min_val_dot, pre_max_val_dot, max_val_dot = self.getMinMaxPreMaxDotVal()

            cut_wc = self.findCutWeightCenter(max_val_dot[1])
            print("\nОтносительный центр тяжести расположен в точке")
            print(str(cut_wc))

            reflection = self.reflectDotAndResult(cut_wc, max_val_dot[1])
            print("\nОтраженная вершина и результат в ней")
            print(str(reflection[0]) + "\t:", str(reflection[1]))

            isDone = self.checkAndSwap(max_val_dot, reflection, pre_max_val_dot, min_val_dot, cut_wc)
            for res in self.dots:
                print(str(res) + "\t: ", str(self.dots[res]))
            
            print(iters)



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

    
    def checkAndSwap(self, exclusion: tuple, reflection: tuple, pre_max: tuple, least: tuple, cut_wc: Dot):
        if reflection[0] < exclusion[0]:
            self.dots[reflection[0]] = reflection[1]
            del self.dots[exclusion[0]]

            print("\nРезультат функции в отраженной точке меньше наибольшего, начинаю растяжение")
            return self.stretch(exclusion, reflection, pre_max, least, cut_wc)
        else:
            print("\nРезультат функции в отраженной точке больше наибольшего, начинаю сжатие")
            return self.compress(exclusion, reflection, pre_max, cut_wc)


    def stretch(self, exclusion: tuple, reflection: tuple, pre_max: tuple, least: tuple, cut_wc: Dot) -> bool:
        if reflection[0] < least[0]:
            stretched_dot = cut_wc + ((reflection[1] - cut_wc) * self.beta)
            stretched = (self.targetFunc(stretched_dot), stretched_dot)
            print("\nТочка после растяжения:")
            print(str(stretched[0]) + "\t:", str(stretched[1]))

            if stretched[0] < reflection[0]:
                print("\nРастяжение успешно!")
                print(str(stretched[0]) + " < " + str(reflection[0]))

                self.dots[stretched[0]] = stretched[1]
                del self.dots[reflection[0]]

                isDone = self.checkStopCriteria()
                for result, dot in self.dots.items():
                    print(str(result) + "\t:", str(dot))

                return isDone
            
        print("\nРастяжение не удалось, перехожу к сжатию")
        return self.compress(reflection, reflection, pre_max, cut_wc)


    def checkStopCriteria(self) -> bool:
        wc = self.findFullWeightCenter()

        #omega = (sum_dots(list(map(lambda dot: (dot - wc) ** 2, self.dots.values()))) * (1/(self.n + 1))) ** 0.5
        omega = pow(sum(list(map(lambda dot: pow(self.targetFunc(dot - wc), 2), self.dots.values()))), 0.5)
        if omega < self.epsilon:
            print("\nКритерий останова соблюден, завершение")
            print(str(omega) + " < " + str(self.epsilon) + "\n")
            return True
        
        print("\nКритерий останова НЕ соблюден, продолжаю")
        print(str(omega) + " > " + str(self.epsilon) + "\n")
        return False


    def compress(self, exclusion: tuple, reflection:tuple, pre_max: tuple, cut_wc: Dot) -> bool:
        compressed_dot = cut_wc + ((self.dots[exclusion[0]] - cut_wc) * self.gamma)
        compressed = (self.targetFunc(compressed_dot), compressed_dot)
        
        if pre_max[0] < reflection[0] < exclusion[0]:
            if compressed[0] < exclusion[0]:
                print("\nСжатие прошло успешно")
                print(str(compressed[0]) + " < " + str(exclusion[0]) + "\n")

                self.dots[compressed[0]] = compressed[1]
                del self.dots[exclusion[0]]

                return self.checkStopCriteria()
        
        return self.reduce()


    def reduce(self) -> bool:
        minValDot = self.findMinValDot()
        minDot = minValDot[1]

        res_to_del = []

        for result, dot in self.dots.copy().items():
            if dot == minDot:
                continue
            else:
                newDot = minDot + ((dot - minDot) * 0.5)
                self.dots[self.targetFunc(newDot)] = newDot
                res_to_del.append(result)

        for key in res_to_del:
            if key in self.dots.copy():
                del self.dots[key]

        return self.checkStopCriteria()


    def findMinValDot(self):
        '''
        Нахождение точки с наименьшим результатом функции в ней
        '''
        min_result = sys.maxsize

        for result, dot in self.dots.items():
            if result < min_result:
                min_result = result
                min_dot    = dot

        return (min_result, min_dot)

    
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


    def findFullWeightCenter(self) -> Dot:
        '''
        Нахождение центра тяжести всего симплекса
        '''
        return (sum_dots(self.dots.values())) * (1/(self.n + 1))


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


nelder_mead = NelderMead(n = 2, start_dot = Dot(0, 0), m = 0.75, beta = 1.85, gamma = 0.1, epsilon = 0.1, targetFunction = methodFunction)
