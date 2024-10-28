from cProfile import label

import matplotlib.pyplot as plt
import numpy as np


def show_10x():
    x = np.arange(1, 100)
    y = 10 * x

    plt.title('color')
    plt.plot(x, x, color = 'skyblue', label = 'skyblue')
    plt.plot(x, y, 'pink', label = 'pink')
    plt.legend()
    plt.show()


def show_sin():
    x = np.arange(0, 2 * np.pi, 0.1)
    y = np.sin(x)

    plt.title('plotting')
    plt.plot(x,y, color = 'skyblue', label = 'skyblue')
    plt.show()


def show_x_square():
    x = np.square(-20, 21)
    y = np.square(x)

    plt.plot(x, y)
    plt.show()


def show_line():
    plt.title('linestyle')
    plt.plot([10, 20, 30, 40], color ='r', linestyle='--', label='dashed')
    plt.plot([40, 30, 20, 10], 'g', ls='--', label='dotted')
    plt.legend()
    plt.show()


def show_marker():
    plt.title('marker')
    plt.plot([10,20,30,40], 'r.', label='circle')
    plt.plot([40,30,20,10], 'gv', label='triangle')
    plt.legend()
    plt.show()


def main():
    """ 실행함수 """
    # show_10x()
    # show_sin()
    # show_x_square()
    # show_line()
    show_marker()

if __name__ == "__main__":
    main()