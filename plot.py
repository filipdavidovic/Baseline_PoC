import matplotlib.pyplot as plt
import scipy.stats
import numpy as np

import utils
from baseline import Baseline


def time_series(metrics, figure_num):
    plt.figure(figure_num)
    plt.plot_date([row[0] for row in metrics], [row[1] for row in metrics], xdate=True, linestyle='-',
                  marker='')
    plt.xlabel('Time')
    plt.ylabel('Resource Usage')
    plt.gcf().autofmt_xdate()  # Format date
    plt.show()


def histogram(metrics, figure_num):
    global min, max

    # Calculate data needed to plot the normal distribution graph
    stats = utils.stats(metrics)
    dist = scipy.stats.norm(stats['mean'], stats['std_dev'])
    minimum = int(min(metrics))
    maximum = int(max(metrics))
    values = [value for value in range(minimum, maximum, (maximum - minimum) // 100)]
    probabilities = [dist.pdf(value) for value in values]

    # Plot
    plt.figure(figure_num)
    plt.hist(metrics, bins=50, density=True)
    plt.plot(values, probabilities)
    plt.show()


def base_slot_histogram(metrics, figure_num):
    # baseline = Baseline(metrics, 3, 1.0)  # Threshold is not important here
    # baseline = [[[1, 2, 2, 3, 3, 3, 2, 2, 1] for _ in range(24)] for _ in range(7)]
    #
    # plt.figure(figure_num)
    # fig, axs = plt.subplots(7, 24)
    # for day in range(7):
    #     for hour in range(24):
    #         data = baseline[day][hour]
    #         axs[day][hour].imshow(data)
    # plt.show()

    # data = np.array([1, 2, 2, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5, 5, 5])
    # x = np.linspace(1, 3)
    # hist = np.histogram(data, bins=5)
    #
    # plt.figure(figure_num)
    # im = plt.imshow(hist[0][np.newaxis, :], cmap='plasma')
    # plt.xticks([])
    # plt.yticks([])
    # plt.colorbar()
    # plt.show()

    raise NotImplementedError('TBD')
