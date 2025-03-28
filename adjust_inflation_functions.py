import pandas as pd
from typing import Literal
import os

def adjust_inflation(dates:list[str], values:list[float], currency:Literal['BRL','GBP','USD'], present_date:str=None):

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    if currency == 'BRL':
        df_daily_ipca = pd.read_csv(rf'{BASE_DIR}/databases/BRL Daily Inflation.csv')

    elif currency == 'USD':
        df_daily_ipca = pd.read_csv(rf'{BASE_DIR}/databases/USD Daily Inflation.csv')

    elif currency == 'GBP':
        df_daily_ipca = pd.read_csv(rf'{BASE_DIR}/databases/GBP Daily Inflation.csv')

    df_daily_ipca['Date'] = pd.to_datetime(df_daily_ipca['Date'])

    present_date = df_daily_ipca['Date'].max() if present_date == None else present_date

    df = pd.DataFrame({'Date': dates, 
                       'Value': values})
    
    df['Date'] = pd.to_datetime(df['Date'])

    present_date = pd.to_datetime(present_date)
    df_daily_ipca_to_present_date = df_daily_ipca[df_daily_ipca['Date'] <= present_date].copy()
    df_daily_ipca_to_present_date['Accumulated Inflation (%)'] = (1 + df_daily_ipca_to_present_date['Daily Inflation'])[::-1].cumprod()[::-1] - 1

    if present_date <= df_daily_ipca_to_present_date['Date'].max():
        df = df[(df['Date'] >= df_daily_ipca_to_present_date['Date'].min()) & (df['Date'] < present_date)]
    else:
        return f"The present date must be less than or equal to {df_daily_ipca_to_present_date['Date'].max().date()}"

    df = df.merge(df_daily_ipca_to_present_date, on='Date', how='left')
    df[f'Adjusted Value - {present_date.date()}'] = round(df['Value'] * (1 + df['Accumulated Inflation (%)']), 2)

    df['Accumulated Inflation (%)'] = round(df['Accumulated Inflation (%)'] * 100, 2)
    df = df.drop(columns=['Daily Inflation'])

    return df
