# Baseline - Ongoing Collection Proof-of-Concept
This repository contains the code for the PoC representing ongoing collection of a baseline.

It was done as part of the internship done in PricewaterhouseCoopers (PwC).

## Modules
### Main (`main.py`)
This module contains the code for running the program and for the actual functionality. 
It uses a class called `Baseline` defined in `baseline.py`.

### Plot (`plot.py`)
This modules contains code for plotting the input data in various ways.
It is helpful to understand the distribution and its historical properties.

### Utilities (`utils.py`)
Some utilities for working on the data. Namely, finding the used statistics and extreme points.

## Running the code
### General
```
usage: main.py [-h] {poc,utils,plot} ... baseline_data

Proof Of Concept for ongoing baseline collection

positional arguments:
  baseline_data     Path to the CSV containing baseline data

optional arguments:
  -h, --help        show this help message and exit

subcommands:
  Available modules

  {poc,utils,plot}
```

In order to use the tool, you need to specify at least one dataset.
This is usually the baseline data itself, i.e. the training dataset.

### PoC
```
usage: main.py poc [-h] [--roc] positives_data negatives_data

Main module representing the PoC

positional arguments:
  positives_data  Path to the CSV containing data for positives, i.e. data
                  with which we should trigger an alert
  negatives_data  Path to the CSV containing data for negatives, i.e. data
                  with which we should NOT trigger an alert

optional arguments:
  -h, --help      show this help message and exit
  --roc           Plot the ROC curve of the results
```

To use this module, you also need to input data that should be compared to the baseline, i.e. test data.
The option `--roc` might be especially useful as it will plot the ROC curve using all three datasets.