# System modules
import argparse
import csv
import datetime

# Imported modules
import numpy as np
import tabulate
import matplotlib.pyplot as plt

# Project modules
from baseline import Baseline
import utils
import plot


def parse_data(baseline_data_path):
    metrics = []

    with open(baseline_data_path, 'r') as f:
        reader = csv.reader(f, delimiter=';')

        for row in reader:
            if len(row) < 2 or any([not value for value in row]):
                print('Skipping: {}'.format(row))
                continue
            metrics.append([datetime.datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S'), float(row[1])])

    return metrics


def main(baseline_data, positives_data, negatives_data, plot_roc_curve):
    baseline = Baseline(baseline_data, 3)
    thresholds = np.arange(start=0, stop=1, step=0.001)
    results = []

    # For each of the possible thresholds find the number of true- and false-positives
    for threshold in thresholds:
        num_true_positives = 0
        num_false_positives = 0

        for positive in positives_data:
            if baseline.is_alerting(positive[0], positive[1], threshold):
                num_true_positives += 1

        for negative in negatives_data:
            if baseline.is_alerting(negative[0], negative[1], threshold):
                num_false_positives += 1

        results.append((threshold, num_true_positives / len(positives_data), num_false_positives / len(negatives_data)))

    # Print the results
    print(tabulate.tabulate(results, ('Threshold', 'True Positives Ratio', 'False Positives Ratio')))
    print('\n\n# positive samples: {}\n# negative samples: {}'.format(len(positives_data), len(negatives_data)))

    # Plot the ROC curve
    if plot_roc_curve:
        plt.figure(1)
        plt.plot([row[2] for row in results], [row[1] for row in results])
        plt.xlabel('False Positives Ratio')
        plt.ylabel('True Positives Ratio')
        plt.plot([1.1, -0.1], [-0.1, 1.1], '--r')  # EER line
        plt.show()


if __name__ == '__main__':
    '''
    Parse arguments
    '''
    parser = argparse.ArgumentParser(description='Proof Of Concept for ongoing baseline collection')
    subparsers = parser.add_subparsers(description='Available modules')

    parser.add_argument('baseline_data', action='store', help='Path to the CSV containing baseline data')

    # Main module
    poc_parser = subparsers.add_parser('poc', description='Main module representing the PoC')
    poc_parser.add_argument('positives_data', action='store', help='Path to the CSV containing data for positives, '
                                                                   'i.e. data with which we should trigger an alert')
    poc_parser.add_argument('negatives_data', action='store', help='Path to the CSV containing data for negatives, '
                                                                   'i.e. data with which we should NOT trigger an '
                                                                   'alert')
    poc_parser.add_argument('--roc', action='store_true', default=False, help='Plot the ROC curve of the results')
    poc_parser.set_defaults(which='poc')

    # Utils subparser
    utils_parser = subparsers.add_parser('utils', description='Utilities for manipulating the data')
    utils_parser.add_argument('--min-max', action='store', dest='minmax', type=int, default=0, choices=range(1, 30),
                              help='Find the given number of minimum and maximum values')
    utils_parser.add_argument('--stats', action='store_true', default=False, help='Print statistics for the baseline '
                                                                                  'data')
    utils_parser.set_defaults(which='utils')

    # Plotting subparser
    plot_parser = subparsers.add_parser('plot', description='Functions to plot the data')
    plot_parser.add_argument('--time-series', action='store_true', default=False, dest='time_series',
                             help='Plot a historical time series graph')
    plot_parser.add_argument('--histogram', action='store_true', default=False, help='Plot a histogram for all '
                                                                                     'baseline data')
    plot_parser.add_argument('--base-slot-histogram', action='store_true', default=False, dest='base_slot_histogram',
                             help='Plot a histogram for each base slot')
    plot_parser.set_defaults(which='plot')

    args = parser.parse_args()

    '''
    Call appropriate functions based on arguments
    '''
    baseline_data = parse_data(args.baseline_data)
    if args.which == 'poc':
        positives_data = parse_data(args.positives_data)
        negatives_data = parse_data(args.negatives_data)
        main(baseline_data, positives_data, negatives_data, args.roc)
    elif args.which == 'utils':
        if args.minmax > 0:
            minmax = utils.minmax([row[1] for row in baseline_data], args.minmax)

            print('Minimal {} values:'.format(args.minmax))
            for n in minmax['mins']:
                print('\t{}'.format(n))

            print('Maximal {} values:'.format(args.minmax))
            for n in minmax['maxs']:
                print('\t{}'.format(n))
        if args.stats:
            stats = utils.stats([row[1] for row in baseline_data])

            print('Mean: {}\nStd. Deviation: {}'.format(stats['mean'], stats['std_dev']))
    elif args.which == 'plot':
        plt_counter = 1
        if args.time_series:
            plot.time_series(baseline_data, plt_counter)
            plt_counter += 1
        if args.histogram:
            plot.histogram([row[1] for row in baseline_data], plt_counter)
            plt_counter += 1
        if args.base_slot_histogram:
            plot.base_slot_histogram(baseline_data, plt_counter)
            plt_counter += 1
