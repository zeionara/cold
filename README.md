# Cold

**Co**mmunity **l**abelling **d**river - a tool for inferring labels for data elements using provided corpus of annotations. In particular, the tools attempts to solve the *cold*-start problem of the recommender systems.

## Installation

To install the project dependencies, create a conda environment using the provided config file:

```sh
conda env create -f environment.yml
```

## Launch

To run the project in a manual mode, execute the following command:

```sh
python -m cold probe assets/default/train.cld assets/default/spec.yml
```

## Test

To run tests, use the following command:

```sh
python -m unittest discover test
```
