# genNYC

Master branch

[![CircleCI](https://circleci.com/gh/js4785/gennyc/tree/master.svg?style=svg&circle-token=124081d210b8e259fcd3b53281fe4aac26cc6776)](https://circleci.com/gh/js4785/gennyc/tree/master)

Development branch

[![CircleCI](https://circleci.com/gh/js4785/gennyc/tree/development.svg?style=svg&circle-token=124081d210b8e259fcd3b53281fe4aac26cc6776)](https://circleci.com/gh/js4785/gennyc/tree/development)

COMS4156 Advanced Software Engineering  | Spring 2018

## Team:
Ivy Chen (ic2389)
James Shin (js4785)
Kayvon Seif-Naraghi (kss2153)
Teresa Choe (tc2716)

## Introduction

genNYC is an application to help people discover events in NYC.

This code is used for the purposes of COMS 4156 - Advanced Software Engineering course at Columbia University, New York.
This is a boilerplate python flask code along with configurations for Circle CI and Google Cloud.

This code is used for the purposes of COMS 4156 - Advanced Software Engineering course at Columbia University, New York. 
This is a boilerplate python flask code along with configurations for Circle CI and Google Cloud.

## Coverage
To test statement coverage locally (which is the [`coverage.py`](https://coverage.readthedocs.io/en/coverage-4.5.1/) default), follow these steps:

1. `pip install coverage`
2. `cd` to `gennyc/`
3. Run the coverage tests:
   - `coverage run -a tests/test_main.py`
   - `coverage run -a tests/test_predictor.py`
   - `coverage run -a tests/test_user.py`
4. `coverage report --omit="/usr/local/lib/python2.7/dist-packages/*","tests/*"`

The following output is observed:

```
Name                  Stmts   Miss  Cover
-----------------------------------------
code/event.py            41      0   100%
code/main.py            426    103    76%
code/model_api.py        15      1    93%
code/predictor.py       119     13    89%
code/recommender.py      68      7    90%
code/surveys.py           7      0   100%
code/user_class.py       38      5    87%
-----------------------------------------
TOTAL                   714    129    82%
```

Also, when step 3 is run with `--branch` coverage, the following is observed:

```
Name                  Stmts   Miss Branch BrPart  Cover
-------------------------------------------------------
code/event.py            41      1      2      0    98%
code/main.py            426    103    122     30    72%
code/model_api.py        15      1      2      1    88%
code/predictor.py       119     13     52      4    85%
code/recommender.py      68      7     10      0    91%
code/surveys.py           7      0      0      0   100%
code/user_class.py       38      5      6      2    80%
-------------------------------------------------------
TOTAL                   714    130    194     37    78%
```

Thus, we have 82% statement coverage and 78% branch coverage.
 

## Licensing

Copyright (C) 2018 Columbia University.
