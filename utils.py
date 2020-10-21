import numpy as np


def stats(metrics):
    mean = np.mean(metrics)
    std_dev = np.std(metrics)

    return {
        'mean': mean,
        'std_dev': std_dev
    }


def minmax(metrics, n):
    metrics = np.sort(metrics)

    return {
        'mins': metrics[0:n],
        'maxs': metrics[-n:]
    }
