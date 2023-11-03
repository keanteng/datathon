# UN Datathon 2023 <!-- omit in toc -->

![Static Badge](https://img.shields.io/badge/license-MIT-blue)
![Static Badge](https://img.shields.io/badge/python-3.11-blue)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://google.com)


A GitHub repo to store competition materials for submission to the UN Datathon 2023.


**Table of Contents:**
- [Theme](#theme)
- [Using This Repository](#using-this-repository)
  - [Pre-requisite](#pre-requisite)
  - [Using A Specific Branch](#using-a-specific-branch)
  - [App Deployment](#app-deployment)
  - [Using Virtual Environment](#using-virtual-environment)


## Theme
- The need to accelerate progress towards the United Nations Sustainable Development Goals (SDGs)
- To create an innovative data solution which tackles local sustainable development challenges, and which leverages one or several of the six transitions.
  - Food systems;
  - Energy access and affordability;
  - Digital connectivity;
  - Education;
  - Jobs and social protection; and
  - Climate change, biodiversity loss and pollution*.

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