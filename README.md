<div align="center">

# Kaggle-Knowledge-Competitions

[![Kaggle](http://img.shields.io/badge/Kaggle-Competitions-44c5ce.svg)](https://www.kaggle.com/competitions)
[![Blog](http://img.shields.io/badge/Blog-TBD-c044ce.svg)](https://charl-ai.github.io/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)


</div>

## Executive Summary

This project aims so solve Kaggle 'getting started' competitions with a variety of different deep learning frameworks and libraries. The main focus is to implement relatively standard deep learning models in each framework to get a better understanding of their respective strengths and weaknesses. Each framework is a 'mini-project', with its own directory containing the code for all of the competitions. The table below shows the competitions included, as well as the models and frameworks used.

|                   | Digit Classifier (ResNet18 ~98% accuracy) | Sales Forecasting (LSTM ~?% RMSLE) | Art Generation (StyleGAN3 ~? FID) | Titanic Survival (MLP ~?% Accuracy)| Tweet NLP (BERT ~80% F1) |
|-------------------|-----------------------------|--------------------------|-----------------------------|--------------------------|--------------------------|
| PyTorch           | <ul><li>- [x] </li></ul>    | <ul><li>- [ ] </li></ul> | <ul><li>- [ ] </li></ul>    | <ul><li>- [ ] </li></ul> | <ul><li>- [ ] </li></ul> |
| PyTorch Lightning | <ul><li>- [x] </li></ul>    | <ul><li>- [ ] </li></ul> | <ul><li>- [ ] </li></ul>    | <ul><li>- [ ] </li></ul> | <ul><li>- [x] </li></ul> |
| TensorFlow        | <ul><li>- [ ] </li></ul>    | <ul><li>- [ ] </li></ul> | <ul><li>- [ ] </li></ul>    | <ul><li>- [ ] </li></ul> | <ul><li>- [ ] </li></ul> |
| JAX               | <ul><li>- [ ] </li></ul>    | <ul><li>- [ ] </li></ul> | <ul><li>- [ ] </li></ul>    | <ul><li>- [ ] </li></ul> | <ul><li>- [ ] </li></ul> |
| Haiku             | <ul><li>- [ ] </li></ul>    | <ul><li>- [ ] </li></ul> | <ul><li>- [ ] </li></ul>    | <ul><li>- [ ] </li></ul> | <ul><li>- [ ] </li></ul> |

You might notice that I have only given the rough score that each method attains, not specific scores for each method/framework combination. This project is really about getting proficient in each of the deep learning libraries, not scoring highly on the competitions. It is also worth noting that these competitions seem to suffer from overfitting on the public leaderboards - for example, the MNIST competition has submissions with 100% accuracy! I am not interested in this extreme game of tuning/overfitting as I don't think there is much to be learned by doing so; this is also why I avoid diving into feature engineering, XGBoost, or traditional ML methods in this project (even though they are all good methods for these competitions). This is not a data science project, it is about practicing coding in different styles.


## Installation

This project includes both a `requirements.txt` file, as well as a `Dockerfile` and `devcontainer.json`. This enables two methods for installation.

### Method 1: devcontainers (recommended for easily reproducing the development environment)

If you have Docker and VScode (with the remote development extension pack) installed, you can reproduce the entire development environment including OS, Python version, and dependencies by simply running `Remote containers: Clone Repository in Container Volume` from the command palette (alternatively, you could clone the repository and run `Remote Containers: Open folder in Container`). This is the easiest way to install the project. If you use Docker but don't like VScode, feel free to try building from the Dockerfile, although some small changes might be necessary.

Caveat: Currently the container will install the version of PyTorch compatible with CUDA 11.3 (featured on cards such as the RTX 3090). If your card only supports 10.2, you can comment out the last line of the Dockerfile to install the correct version. In future, I will design the container to check your CUDA capability and do this automatically for you.

### Method 2: python virtual environments (more involved, but more familiar to most researchers and requires no docker installation)

First, clone the repo, it is recommended to use the GitHub CLI:
```bash
# clone project
gh repo clone Charl-AI/Kaggle-Knowledge-Competitions

# change to project directory
cd Kaggle-Knowledge-Competitions
```

Create and activate a virtual environment, then install the dependencies. Note: please make sure you are using Python 3.8 as this is what the project was built on.

```bash
python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt --no-cache-dir
```

If you are having CUDA issues, you can find the PyTorch builds for each version of CUDA [here](https://pytorch.org/get-started/locally/). For example, an NVIDIA RTX 3090 uses the CUDA 11.3 compute platform, this can be installed by running:

```bash
pip3 install torch==1.10.0+cu113 torchvision==0.11.1+cu113 torchaudio==0.10.0+cu113 -f https://download.pytorch.org/whl/cu113/torch_stable.html
```

## Data

The data used in this project is downloadable through the Kaggle API. By default, all models expect the data to be located in ```data/``` by default, but this can usually be changed if necessary. To download the data using the Kaggle API, first ensure you have your Kaggle API key stored in ```~/.kaggle/kaggle.json```, then run the included shell script, ensuring you are running it from the project root (i.e. the directory containing this README):

```bash
bash ./download_data.sh
```

## Running

Each mini-project has its own README, describing how to properly do training, inference, visualisation, and submission of results. Generally, this project tries to use notebooks in place of `main.py` files to enable easy visualisation of results. A nice benefit is that the notebook outputs get uploaded to GitHub, so you can see the outputs of the code without downloading and running it.
