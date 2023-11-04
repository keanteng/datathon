import pandas as pd
import numpy as np
from datetime import *
from statsmodels.tsa.holtwinters import ExponentialSmoothing
import matplotlib.pyplot as ax1
from statsmodels.tsa.holtwinters import SimpleExpSmoothing
from statsmodels.tsa.stattools import adfuller
from pmdarima import auto_arima
from sklearn.metrics import mean_squared_error, mean_absolute_error
import matplotlib.pyplot as plt
import streamlit as st

# set wide layout
st.set_page_config(layout="wide")
state_input = st.selectbox('Select State', ['Kedah', 'Johor', 'Kelantan', 'Melaka', 'Negeri Sembilan', 'Pahang', 'Penang', 'Perak', 'Perlis', 'Sabah', 'Sarawak', 'Selangor', 'Terengganu', 'W.P Kuala Lumpur', 'W.P Labuan', 'W.P Putrajaya', 'Malaysia'])

# read xlsx data set
vacancy_rate = pd.read_csv('data/Vacancy Rate.csv', index_col = [0], parse_dates=[0])

# remove all the empty column
vacancy_rate = vacancy_rate.dropna(axis=1, how='all')
vacancy_rate.dropna(inplace=True)

# read data set
unemployment_rate = pd.read_csv('data/Unemployment Rate.csv')

# remove the empty columns
unemployment_rate = unemployment_rate.dropna(axis=1, how='all')

# change the type of vacancy_rate_employment as data frame
unemployment_rate = pd.DataFrame(unemployment_rate)

# change all the data in unemployment_rate to float data except the date
unemployment_rate.iloc[:,1:] = unemployment_rate.iloc[:,1:].astype(float)
unemployment_rate.iloc[:,0] = pd.to_datetime(unemployment_rate.iloc[:,0])
unemployment_rate = unemployment_rate.set_index('Date')

def ets_fore_a(data,i):
    # ets test
    ets_model = ExponentialSmoothing(data, trend='add', seasonal='add', seasonal_periods=i)
    ets_model_fit = ets_model.fit()
    ets_pred = ets_model_fit.forecast(8)
    return ets_pred
def ets_fore_b(data,i):
    # ets test
    ets_model = ExponentialSmoothing(data, trend='add', seasonal='mul', seasonal_periods=i)
    ets_model_fit = ets_model.fit()
    ets_pred = ets_model_fit.forecast(8)
    return ets_pred
def ets_fore_c(data,i):
    # ets test
    ets_model = ExponentialSmoothing(data, trend='mul', seasonal='add', seasonal_periods=i)
    ets_model_fit = ets_model.fit()
    ets_pred = ets_model_fit.forecast(8)
    return ets_pred
def ets_fore_d(data,i):
    # ets test
    ets_model = ExponentialSmoothing(data, trend='mul', seasonal='mul', seasonal_periods=i)
    ets_model_fit = ets_model.fit()
    ets_pred = ets_model_fit.forecast(8)
    return ets_pred

def ARIMA_fore(data):
    # arima test
    stepwise_model = auto_arima(data, start_p=1, start_q=1,
                                stepwise=True)
    stepwise_model.fit(data)
    arima_pred = stepwise_model.predict(n_periods=8)
    return arima_pred

def dateofforecast(data):
    forecast_date = ['2023-04-01', '2023-07-01', '2023-10-01', '2024-01-01', '2024-04-01', '2024-07-01', '2024-10-01','2025-01-01']
    forecast_date = pd.to_datetime(forecast_date)
    data.index = forecast_date
    
# ETS prediction
VETS_Kedah = ets_fore_a(vacancy_rate['Kedah'],6)
VETS_Melaka = ets_fore_a(vacancy_rate['Melaka'],6)
VETS_Negeri_Sembilan = ets_fore_c(vacancy_rate['Negeri Sembilan'],6)
VETS_Pahang = ets_fore_a(vacancy_rate['Pahang'],6)
VETS_Perlis = ets_fore_c(vacancy_rate['Perlis'],6)
VETS_Terengganu = ets_fore_a(vacancy_rate['Terengganu'],6)
VETS_Sabah = ets_fore_a(vacancy_rate['Sabah'],6)
VETS_Sarawak = ets_fore_a(vacancy_rate['Sarawak'],6)
VETS_Putrajaya = ets_fore_a(vacancy_rate['W.P Putrajaya'],6)

# ARIMA prediction
VETS_Johor = ARIMA_fore(vacancy_rate['Johor'])
VETS_Kelantan = ARIMA_fore(vacancy_rate['Kelantan'])
VETS_Penang = ARIMA_fore(vacancy_rate['Pulau Pinang'])
VETS_Perak = ARIMA_fore(vacancy_rate['Perak'])
VETS_Selangor = ARIMA_fore(vacancy_rate['Selangor'])
VETS_Kuala_Lumpur = ARIMA_fore(vacancy_rate['W.P Kuala Lumpur'])
VETS_Labuan = ARIMA_fore(vacancy_rate['W.P Labuan'])
VETS_Total = ARIMA_fore(vacancy_rate['Total'])

# Change the Starting date of the forecast
dateofforecast(VETS_Kedah)
dateofforecast(VETS_Melaka)
dateofforecast(VETS_Negeri_Sembilan)
dateofforecast(VETS_Pahang)
dateofforecast(VETS_Perlis)
dateofforecast(VETS_Terengganu)
dateofforecast(VETS_Sabah)
dateofforecast(VETS_Sarawak)
dateofforecast(VETS_Putrajaya)
dateofforecast(VETS_Johor)
dateofforecast(VETS_Kelantan)
dateofforecast(VETS_Penang)
dateofforecast(VETS_Perak)
dateofforecast(VETS_Selangor)
dateofforecast(VETS_Kuala_Lumpur)
dateofforecast(VETS_Labuan)
dateofforecast(VETS_Total)

# ETS Model
Johor_vpred = ets_fore_a(unemployment_rate[['Johor']],6)
Kedah_pred = ets_fore_d(unemployment_rate[['Kedah']],6)
Kelantan_pred = ets_fore_d(unemployment_rate[['Kelantan']],6)
Melaka_pred = ets_fore_b(unemployment_rate[['Melaka']],6)
Pahang_pred = ets_fore_c(unemployment_rate[['Pahang']],6)
Perak_pred = ets_fore_c(unemployment_rate[['Perak']],6)
Perlis_pred = ets_fore_c(unemployment_rate[['Perlis']],6)
Sabah_pred = ets_fore_a(unemployment_rate[['Sabah']],6)
Sarawak_pred = ets_fore_d(unemployment_rate[['Sarawak']],6)
Selangor_pred = ets_fore_d(unemployment_rate[['Selangor']],6)
Terengganu_pred = ets_fore_b(unemployment_rate[['Terengganu']],6)
Labuan_pred = ets_fore_d(unemployment_rate['W.P Labuan'],6)

# ARIMA Model
UARIMA_N9_pred = ARIMA_fore(unemployment_rate[['Negeri Sembilan']])
UARIMA_Penang_pred = ARIMA_fore(unemployment_rate[['Pulau Pinang']])
UARIMA_KL_pred = ARIMA_fore(unemployment_rate[['W.P Kuala Lumpur']])
UARIMA_Putrajaya_pred = ARIMA_fore(unemployment_rate[['W.P Putrajaya']])
UARIMA_Malaysia_pred = ARIMA_fore(unemployment_rate[['Total']])

# Change the Starting date of the forecast
dateofforecast(Johor_vpred)
dateofforecast(Kedah_pred)
dateofforecast(Kelantan_pred)
dateofforecast(Melaka_pred)
dateofforecast(Pahang_pred)
dateofforecast(Perak_pred)
dateofforecast(Perlis_pred)
dateofforecast(Sabah_pred)
dateofforecast(Sarawak_pred)
dateofforecast(Selangor_pred)
dateofforecast(Terengganu_pred)
dateofforecast(Labuan_pred)
dateofforecast(UARIMA_N9_pred)
dateofforecast(UARIMA_Penang_pred)
dateofforecast(UARIMA_KL_pred)
dateofforecast(UARIMA_Putrajaya_pred)
dateofforecast(UARIMA_Malaysia_pred)

vacancy_rate.dateformat = vacancy_rate.index.strftime('%Y-%m-%d')
unemployment_rate.dateformat = unemployment_rate.index.strftime('%Y-%d-%m')

def forecast_plot(state):
    state = state.title()
    if state == 'Kedah':
        fig, ax1 = plt.subplots()
        plt.figure(figsize=(12, 8))

        ax1.plot(vacancy_rate.index, vacancy_rate['Kedah'], label='Vacancy Rate')
        ax1.plot(VETS_Kedah, label='Forecast of Vacancy Rate')
        ax1.legend(loc='upper left')
        ax1.set_xlabel('Date')
        ax1.set_ylabel('Vacancy Rate')
        
        ax2 = ax1.twinx()
        ax2.plot(unemployment_rate.index, unemployment_rate['Kedah'], 'r', label='Unemployment Rate')
        ax2.plot(Kedah_pred, 'b', label='Forecast of Unemployment Rate')
        ax2.legend(loc='upper left', bbox_to_anchor=(0, .95))
        ax2.set_ylabel('Unemployment Rate')
        plt.rcParams['figure.figsize'] = (20, 12)
        st.pyplot(fig)
        
    elif state == 'Johor':
        fig, ax1 = plt.subplots()
        plt.figure(figsize=(12, 8))

        ax1.plot(vacancy_rate.index, vacancy_rate['Johor'], label='Vacancy Rate')
        ax1.plot(VETS_Johor, label='Forecast of Vacancy Rate')
        ax1.legend(loc='upper left')
        ax1.set_xlabel('Date')
        ax1.set_ylabel('Vacancy Rate')
        
        ax2 = ax1.twinx()
        ax2.plot(unemployment_rate.index, unemployment_rate['Johor'], 'r', label='Unemployment Rate')
        ax2.plot(Johor_vpred, 'b', label='Forecast of Unemployment Rate')
        ax2.legend(loc='upper left', bbox_to_anchor=(0, .95))
        ax2.set_ylabel('Unemployment Rate')
        plt.rcParams['figure.figsize'] = (20, 12)
        st.pyplot(fig)
        

    elif state == 'Kelantan':
        fig, ax1 = plt.subplots()
        plt.figure(figsize=(12, 8))

        ax1.plot(vacancy_rate.index, vacancy_rate['Kelantan'], label='Vacancy Rate')
        ax1.plot(VETS_Kelantan, label='Forecast of Vacancy Rate')
        ax1.legend(loc='upper left')
        ax1.set_xlabel('Date')
        ax1.set_ylabel('Vacancy Rate')
        
        ax2 = ax1.twinx()
        ax2.plot(unemployment_rate.index, unemployment_rate['Kelantan'], 'r', label='Unemployment Rate')
        ax2.plot(Kelantan_pred, 'b', label='Forecast of Unemployment Rate')
        ax2.legend(loc='upper left', bbox_to_anchor=(0, .95))
        ax2.set_ylabel('Unemployment Rate')
        plt.rcParams['figure.figsize'] = (20, 12)
        st.pyplot(fig)
        
    elif state == 'Melaka':
        fig, ax1 = plt.subplots()
        plt.figure(figsize=(12, 8))

        ax1.plot(vacancy_rate.index, vacancy_rate['Melaka'], label='Vacancy Rate')
        ax1.plot(VETS_Melaka, label='Forecast of Vacancy Rate')
        ax1.legend(loc='upper left')
        ax1.set_xlabel('Date')
        ax1.set_ylabel('Vacancy Rate')
        
        ax2 = ax1.twinx()
        ax2.plot(unemployment_rate.index, unemployment_rate['Melaka'], 'r', label='Unemployment Rate')
        ax2.plot(Melaka_pred, 'b', label='Forecast of Unemployment Rate')
        ax2.legend(loc='upper left', bbox_to_anchor=(0, .95))
        ax2.set_ylabel('Unemployment Rate')
        plt.rcParams['figure.figsize'] = (20, 12)
        st.pyplot(fig)
        
    elif state == 'Negeri Sembilan':
        fig, ax1 = plt.subplots()
        plt.figure(figsize=(12, 8))

        ax1.plot(vacancy_rate.index, vacancy_rate['Negeri Sembilan'], label='Vacancy Rate')
        ax1.plot(VETS_Negeri_Sembilan, label='Forecast of Vacancy Rate')
        ax1.legend(loc='upper left')
        ax1.set_xlabel('Date')
        ax1.set_ylabel('Vacancy Rate')
        
        ax2 = ax1.twinx()
        ax2.plot(unemployment_rate.index, unemployment_rate['Negeri Sembilan'], 'r', label='Unemployment Rate')
        ax2.plot(UARIMA_N9_pred, 'b', label='Forecast of Unemployment Rate')
        ax2.legend(loc='upper left', bbox_to_anchor=(0, .95))
        ax2.set_ylabel('Unemployment Rate')
        plt.rcParams['figure.figsize'] = (20, 12)
        st.pyplot(fig)
        
    elif state == 'Pahang':
        fig, ax1 = plt.subplots()
        plt.figure(figsize=(12, 8))

        ax1.plot(vacancy_rate.index, vacancy_rate['Pahang'], label='Vacancy Rate')
        ax1.plot(VETS_Pahang, label='Forecast of Vacancy Rate')
        ax1.legend(loc='upper left')
        ax1.set_xlabel('Date')
        ax1.set_ylabel('Vacancy Rate')
        
        ax2 = ax1.twinx()
        ax2.plot(unemployment_rate.index, unemployment_rate['Pahang'], 'r', label='Unemployment Rate')
        ax2.plot(Pahang_pred, 'b', label='Forecast of Unemployment Rate')
        ax2.legend(loc='upper left', bbox_to_anchor=(0, .95))
        ax2.set_ylabel('Unemployment Rate')
        plt.rcParams['figure.figsize'] = (20, 12)
        st.pyplot(fig)
        
    elif state == 'Penang':
        fig, ax1 = plt.subplots()
        plt.figure(figsize=(12, 8))

        ax1.plot(vacancy_rate.index, vacancy_rate['Pulau Pinang'], label='Vacancy Rate')
        ax1.plot(VETS_Penang, label='Forecast of Vacancy Rate')
        ax1.legend(loc='upper left')
        ax1.set_xlabel('Date')
        ax1.set_ylabel('Vacancy Rate')
        
        ax2 = ax1.twinx()
        ax2.plot(unemployment_rate.index, unemployment_rate['Pulau Pinang'], 'r', label='Unemployment Rate')
        ax2.plot(UARIMA_Penang_pred, 'b', label='Forecast of Unemployment Rate')
        ax2.legend(loc='upper left', bbox_to_anchor=(0, .95))
        ax2.set_ylabel('Unemployment Rate')
        plt.rcParams['figure.figsize'] = (20, 12)
        st.pyplot(fig)
        
    elif state == 'Perak':
        fig, ax1 = plt.subplots()
        plt.figure(figsize=(12, 8))

        ax1.plot(vacancy_rate.index, vacancy_rate['Perak'], label='Vacancy Rate')
        ax1.plot(VETS_Perak, label='Forecast of Vacancy Rate')
        ax1.legend(loc='upper left')
        ax1.set_xlabel('Date')
        ax1.set_ylabel('Vacancy Rate')
        
        ax2 = ax1.twinx()
        ax2.plot(unemployment_rate.index, unemployment_rate['Perak'], 'r', label='Unemployment Rate')
        ax2.plot(Perak_pred, 'b', label='Forecast of Unemployment Rate')
        ax2.legend(loc='upper left', bbox_to_anchor=(0, .95))
        ax2.set_ylabel('Unemployment Rate')
        plt.rcParams['figure.figsize'] = (20, 12)
        st.pyplot(fig)
        
    elif state == 'Perlis':
        fig, ax1 = plt.subplots()
        plt.figure(figsize=(12, 8))

        ax1.plot(vacancy_rate.index, vacancy_rate['Perlis'], label='Vacancy Rate')
        ax1.plot(VETS_Perlis, label='Forecast of Vacancy Rate')
        ax1.legend(loc='upper left')
        ax1.set_xlabel('Date')
        ax1.set_ylabel('Vacancy Rate')
        
        ax2 = ax1.twinx()
        ax2.plot(Perlis_pred, 'b', label='Forecast of Unemployment Rate')
        ax2.plot(unemployment_rate.index, unemployment_rate['Perlis'], 'r', label='Unemployment Rate')
        ax2.legend(loc='upper left', bbox_to_anchor=(0, .95))
        ax2.set_ylabel('Unemployment Rate')
        plt.rcParams['figure.figsize'] = (20, 12)
        st.pyplot(fig)
        
    elif state == 'Sabah':
        fig, ax1 = plt.subplots()
        plt.figure(figsize=(12, 8))

        ax1.plot(vacancy_rate.index, vacancy_rate['Sabah'], label='Vacancy Rate')
        ax1.plot(VETS_Sabah, label='Forecast of Vacancy Rate')
        ax1.legend(loc='upper left')
        ax1.set_xlabel('Date')
        ax1.set_ylabel('Vacancy Rate')
        
        ax2 = ax1.twinx()
        ax2.plot(Sabah_pred, 'b', label='Forecast of Unemployment Rate')
        ax2.plot(unemployment_rate.index, unemployment_rate['Sabah'], 'r', label='Unemployment Rate')
        ax2.legend(loc='upper left', bbox_to_anchor=(0, .95))
        ax2.set_ylabel('Unemployment Rate')
        plt.rcParams['figure.figsize'] = (20, 12)
        st.pyplot(fig)
        
    elif state == 'Sarawak':
        fig, ax1 = plt.subplots()
        plt.figure(figsize=(12, 8))

        ax1.plot(vacancy_rate.index, vacancy_rate['Sarawak'], label='Vacancy Rate')
        ax1.plot(VETS_Sarawak, label='Forecast of Vacancy Rate')
        ax1.legend(loc='upper left')
        ax1.set_xlabel('Date')
        ax1.set_ylabel('Vacancy Rate')
        
        ax2 = ax1.twinx()
        ax2.plot(Sarawak_pred, 'b', label='Forecast of Unemployment Rate')
        ax2.plot(unemployment_rate.index, unemployment_rate['Sarawak'], 'r', label='Unemployment Rate')
        ax2.legend(loc='upper left', bbox_to_anchor=(0, .95))
        ax2.set_ylabel('Unemployment Rate')
        plt.rcParams['figure.figsize'] = (20, 12)
        st.pyplot(fig)
        
    elif state == 'Selangor':
        fig, ax1 = plt.subplots()
        plt.figure(figsize=(12, 8))

        ax1.plot(vacancy_rate.index, vacancy_rate['Selangor'], label='Vacancy Rate')
        ax1.plot(VETS_Selangor, label='Forecast of Vacancy Rate')
        ax1.legend(loc='upper left')
        ax1.set_xlabel('Date')
        ax1.set_ylabel('Vacancy Rate')
        
        ax2 = ax1.twinx()
        ax2.plot(Selangor_pred, 'b', label='Forecast of Unemployment Rate')
        ax2.plot(unemployment_rate.index, unemployment_rate['Selangor'], 'r', label='Unemployment Rate')
        ax2.legend(loc='upper left', bbox_to_anchor=(0, .95))
        ax2.set_ylabel('Unemployment Rate')
        plt.rcParams['figure.figsize'] = (20, 12)
        st.pyplot(fig)
        
    elif state == 'Terengganu':
        fig, ax1 = plt.subplots()
        plt.figure(figsize=(12, 8))

        ax1.plot(vacancy_rate.index, vacancy_rate['Terengganu'], label='Vacancy Rate')
        ax1.plot(VETS_Terengganu, label='Forecast of Vacancy Rate')
        ax1.legend(loc='upper left')
        ax1.set_xlabel('Date')
        ax1.set_ylabel('Vacancy Rate')
        
        ax2 = ax1.twinx()
        ax2.plot(Terengganu_pred, 'b', label='Forecast of Unemployment Rate')
        ax2.plot(unemployment_rate.index, unemployment_rate['Terengganu'], 'r', label='Unemployment Rate')
        ax2.legend(loc='upper left', bbox_to_anchor=(0, .95))
        ax2.set_ylabel('Unemployment Rate')
        plt.rcParams['figure.figsize'] = (20, 12)
        st.pyplot(fig)
        
    elif state == 'W.P Kuala Lumpur':
        fig, ax1 = plt.subplots()
        plt.figure(figsize=(12, 8))

        ax1.plot(vacancy_rate.index, vacancy_rate['W.P Kuala Lumpur'], label='Vacancy Rate')
        ax1.plot(VETS_Kuala_Lumpur, label='Forecast of Vacancy Rate')
        ax1.legend(loc='upper left')
        ax1.set_xlabel('Date')
        ax1.set_ylabel('Vacancy Rate')
        
        ax2 = ax1.twinx()
        ax2.plot(UARIMA_KL_pred, 'b', label='Forecast of Unemployment Rate')
        ax2.plot(unemployment_rate.index, unemployment_rate['W.P Kuala Lumpur'], 'r', label='Unemployment Rate')
        ax2.legend(loc='upper left', bbox_to_anchor=(0, .95))
        ax2.set_ylabel('Unemployment Rate')
        plt.rcParams['figure.figsize'] = (20, 12)
        st.pyplot(fig)
        
    elif state == 'W.P Labuan':
        fig, ax1 = plt.subplots()
        plt.figure(figsize=(12, 8))

        ax1.plot(vacancy_rate.index, vacancy_rate['W.P Labuan'], label='Vacancy Rate')
        ax1.plot(VETS_Labuan, label='Forecast of Vacancy Rate')
        ax1.legend(loc='upper left')
        ax1.set_xlabel('Date')
        ax1.set_ylabel('Vacancy Rate')
        
        ax2 = ax1.twinx()
        ax2.plot(Labuan_pred, 'b', label='Forecast of Unemployment Rate')
        ax2.plot(unemployment_rate.index, unemployment_rate['W.P Labuan'], 'r', label='Unemployment Rate')
        ax2.legend(loc='upper left', bbox_to_anchor=(0, .95))
        ax2.set_ylabel('Unemployment Rate')
        plt.rcParams['figure.figsize'] = (20, 12)
        st.pyplot(fig)
        
    elif state == 'W.P Putrajaya':
        fig, ax1 = plt.subplots()
        plt.figure(figsize=(12, 8))

        ax1.plot(vacancy_rate.index, vacancy_rate['W.P Putrajaya'], label='Vacancy Rate')
        ax1.plot(VETS_Putrajaya, label='Forecast of Vacancy Rate')
        ax1.legend(loc='upper left')
        ax1.set_xlabel('Date')
        ax1.set_ylabel('Vacancy Rate')
        
        ax2 = ax1.twinx()
        ax2.plot(UARIMA_Putrajaya_pred, 'b', label='Forecast of Unemployment Rate')
        ax2.plot(unemployment_rate.index, unemployment_rate['W.P Putrajaya'], 'r', label='Unemployment Rate')
        ax2.legend(loc='upper left', bbox_to_anchor=(0, .95))
        ax2.set_ylabel('Unemployment Rate')
        plt.rcParams['figure.figsize'] = (20, 12)
        st.pyplot(fig)
        
    elif state == 'Malaysia':
        fig, ax1 = plt.subplots()
        plt.figure(figsize=(20, 12))

        ax1.plot(vacancy_rate.index, vacancy_rate['Total'], label='Vacancy Rate')
        ax1.plot(VETS_Total, label='Forecast of Vacancy Rate')
        ax1.legend(loc='upper left')
        ax1.set_xlabel('Date')
        ax1.set_ylabel('Vacancy Rate')
        
        ax2 = ax1.twinx()
        ax2.plot(UARIMA_Malaysia_pred, 'b', label='Forecast of Unemployment Rate')
        ax2.plot(unemployment_rate.index, unemployment_rate['Total'], 'r', label='Unemployment Rate')
        ax2.legend(loc='upper left', bbox_to_anchor=(0, .95))
        ax2.set_ylabel('Unemployment Rate')
        plt.rcParams['figure.figsize'] = (20, 12)
        st.pyplot(fig)
        
        
with st.sidebar:
    with st.expander("Vacancy Rate"):
        forecast_plot(state_input)