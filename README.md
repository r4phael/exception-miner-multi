An Empirical Study on Exception Handling Practices in Python Open-Source Projects
---
This repository includes the source code and data for our paper "An Empirical Study on Exception Handling Practices in Python Open-Source Projects".

## Requirements

- Python 3.6+

## Virtualenv (Windows)
1. Run `py -3.10 -m venv {virtualenv name}`
2. Go to Scripts repository in `{virtualenv name}/Scripts`
3. Run `activate`
4. 

## Build
To reproduce the results, follow the instructions below.

1. Back to root directory
2. Run `pip install -r requirements.txt` 
3. Run `python miner.py`

### Choosing a language
1. Run `python miner.py <language>`
current languages: python, typescript
default language: python

## Unit tests
To run the unit tests, follow the instructions below.

1. Run `python3 -m unittest`

## Coverage report  
To generate the coverage report, follow the instructions below.

1. Run `coverage run -m unittest`
2. Run `coverage report --omit *test_*,*__init__*`
