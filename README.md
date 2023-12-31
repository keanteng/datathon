# UN Datathon 2023 <!-- omit in toc -->

![Static Badge](https://img.shields.io/badge/license-MIT-blue)
![Static Badge](https://img.shields.io/badge/python-3.11-blue)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![](https://img.shields.io/badge/Space-Huggingface-ff9d00)](https://huggingface.co/spaces/keanteng/job)
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](hhttps://datathon-emttgsfqrseems4jkeemcf.streamlit.app/)
![Static Badge](https://img.shields.io/badge/job-solution-brightgreen)


A GitHub repo to document competition materials for submission to the UN Datathon 2023. An app version of the data solution is hosted on the web using [Streamlit](https://streamlit.io/) Cloud. 

*📌Update on November 5th 2023, since the application would require more resources to run and maintain, the application is now hosted on [Huggingface](https://huggingface.co/) for a better accessibility.*


**Table of Contents:**
- [Theme of UN Datathon 2023](#theme-of-un-datathon-2023)
- [About](#about)
  - [Project Title](#project-title)
  - [Project Summary](#project-summary)
- [Using This Repository](#using-this-repository)
  - [Pre-requisite](#pre-requisite)
  - [Using A Specific Branch](#using-a-specific-branch)
  - [API Configuration](#api-configuration)
  - [App Deployment](#app-deployment)
  - [Using Virtual Environment](#using-virtual-environment)
- [Data Source](#data-source)
- [Methodology](#methodology)


## Theme of UN Datathon 2023
- The need to accelerate progress towards the United Nations Sustainable Development Goals (SDGs)
- To create an innovative data solution which tackles local sustainable development challenges, and which leverages one or several of the six transitions.
  - Food systems;
  - Energy access and affordability;
  - Digital connectivity;
  - Education;
  - Jobs and social protection; and
  - Climate change, biodiversity loss and pollution*.

## About

### Project Title 

Geo-based Sustainable Job Solution

### Project Summary 
Understanding Malaysia's labor market structural issues for resilient and sustainable economic growth. Malaysia remains stuck in a low-wage and low-skill economy because of the work offered domestically, and not because of the talent available. There are also significant skills mismatches between graduates and industry needs.

## Using This Repository

### Pre-requisite
To launch the app on using the `streamlit` module, you have to install the `streamlit` library via terminal:

```py
py -m pip install streamlit
```

After that, make sure you clone the whole repository to your local machine for usage purpose:

```py
git clone https://github.com/keanteng/datathon
```
### Using A Specific Branch

If you would like to access a particular branch of this repository, run:

```py
git clone -b branch_name https://github.com/keanteng/datathon
```

### API Configuration
The deployment of the API would require PaLM-2 API authentication, first create a `config.py` file in the `\backend` folder, so that inside the folder you have the following files:

```
- backend
  - __init__.py
  - functions.py
  - config.py
```

Then go this [website](https://developers.generativeai.google/) to register for you API token. Then in the `config.py` file, put the following code:

```py
PALM_TOKEN =  'YOUR_TOKEN'
```

### App Deployment

To deploy the app on your local machine, run:

```py
py -m streamlit run app.py
```

### Using Virtual Environment
If you are using virtual environment via `.venv`, you can install the dependencies via:

```py
py -m pip install -r requirements.txt
```

## Data Source
The data used in this study consists of public data published by government and institutions and scraped data from the web, here is the table for reference:

Dataset | Publisher
:-- | --:
Labour Market Review | OpenDOSM
LinkedIn Scraped Job Data | LinkedIn
Map Layers (Districit, Facilities, Points of Interest) | HOTOSM Malaysia
Labour Force Statistics | OpenDOSM
Job Profile Data | ILMIA Malaysia


## Methodology
This study makes use of language model, natural language processing model as well as time series model to create a job solution pipeline. 

Model | Description
:-- | --:
Pathways Language Model 2 (PaLM-2) | Transformed based LLM by Google
Time Series Forecasting Model | From `scikit-learn`, `pmdarima` & `statsmodel` Library
NLP Model | From `scikit-learn` library and `nltk` library


MIT License 2023 © Isekai Truck: Ang Zhi Nuo, Connie Hui Kang Yi, Khor Kean Teng, Ling Sing Cheng, Tan Yu Jing