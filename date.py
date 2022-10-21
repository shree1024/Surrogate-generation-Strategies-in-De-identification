#!/usr/bin/env python
# -*- coding: utf-8 -*- 
import datetime
import locale
import re
from datetime import datetime
import pandas as pd
from datetime import timedelta
import pydateinfer as dateinfer
import math
import numpy as np
import sys
from os import listdir
import dp
import logging

DATE_FORMAT = re.compile(
  r'('
  r'%[aAwdbBmyYHIpMSfzZjUWcxX%]|'  # formatting directives
  r'[.,\/#!$\^&\*;:{}=\-_`~() ]|'  # punctuation
  r'T'                             # date time separator e.g., in %Y-%m-%dT%H:%M:%S
  r')*'
)

def fully_parsed(date_format):
  return len(DATE_FORMAT.sub('', date_format)) == 0


class Date:

  def __init__(self, date_string, date_format, date_locale='en_US.UTF-8', c_year=2019):
    self.date_string = date_string
    self.format = date_format
    self.locale = date_locale
    locale.setlocale(locale.LC_ALL, self.locale)
    self.datetime = datetime.strptime(date_string, self.format)

    if self.is_hour(date_format):
      self.format = '%d'

    if not self.day_anchored():
      self.datetime = self.datetime.replace(day=15)

    if not self.year_anchored():
      self.datetime = self.datetime.replace(year=c_year)

  def is_hour(self, format_):
    return format_ == '%H'
  
  def year_anchored(self):
    return '%y' in self.format.lower()

  def day_anchored(self):
    return '%d' in self.format

  def season_offsets(self):
    from datetime import date
    current_date = self.datetime.date()
    year = current_date.year

    seasons = [
      (date(year, 3, 21), date(year, 6, 20)),  # spring
      (date(year, 6, 21), date(year, 9, 22)),  # summer
      (date(year, 9, 23), date(year, 12, 20)),  # autumn
    ]

    if date(year, 1, 1) <= current_date <= date(year, 3, 20):
      winter = (date(year - 1, 12, 21), date(year, 3, 20))
      seasons.append(winter)
    elif date(year, 12, 21) <= current_date <= date(year, 12, 31):
      winter = (date(year, 12, 21), date(year + 1, 3, 20))
      seasons.append(winter)

    return next(((current_date - start).days, (end - current_date).days)
      for (start, end) in seasons
      if start <= current_date <= end)

  def __str__(self):
    return u"Date(date_string={}, format={}, locale={}, datetime={})".format(
      self.date_string, self.format, self.locale, self.datetime)

  def __unicode__(self):
    return self.__str__()

  def __repr__(self):
    return self.__str__()

  def __eq__(self, other):
    return self.__dict__ == other.__dict__

def infer_format(date_string, locales=('en_US.UTF-8', 'fr_FR.UTF-8')):
    for locale_name in locales:
      locale.setlocale(locale.LC_ALL, locale_name)
      date_format = dateinfer.infer([date_string])

      if fully_parsed(date_format):
        return Date(date_string, date_format, locale_name)

    raise ValueError('Could parse date "{}" with given locales "{}"'.format(date_string, locales))


def date_processing(date, df):
  try:
    #format_pb = "%m/%d/%Y"
    parse = infer_format(date)
    #std = parse.datetime.strftime("%d/%m/%Y")
    orig_format = parse.format
    date_std = parse.datetime
    df = df.append({'Detected date':parse.date_string,'Date':date_std,'Format':orig_format},ignore_index=True)
  except Exception as e:
    print("Could not infer this date : {}".format(date))
    print(e)

  return df

def age_processing(age, df):
  value = int(re.search("\d+", age).group(0))
  df = df.append({'Age':age,'Value':value},ignore_index=True)
  return df

def age_to_date(age, anchor, mode = "back"):
  if mode == "back":
    date = anchor - timedelta(days=age*365)
  else :
    date = anchor + timedelta(days=age*365)
  return date.strftime("%d/%m/%Y")

# Separation of dates : 1->Normal date 2->Age|period
def parse_date(dates):
  df_age = pd.DataFrame(columns=['Age','Value'])
  df_date = pd.DataFrame(columns=['Detected date','Date','Format'])
  for date in dates:
    # Age|Period => Unit Consideration: Years
    # We can add other units : week|month
    if re.search("\d+ years", date):
      age = date
      df_age = age_processing(age, df_age)
    # Date Normale => Considération de l'unité : Jours
    else :
      # Date processing with class Date
      df_date = date_processing(date, df_date)
  return df_date, df_age

def df_to_date(df):
  df["Date"] = pd.to_datetime(df["Date"],errors = 'coerce',dayfirst=True)
  return df

def order_date(df_date, df_age):
  return df_date.sort_values("Date"), df_age.sort_values("Value")


def remove_duplicate_nan_date(df):
  result_df = df.drop_duplicates(subset=['Date'], keep='first')
  result_df = result_df[result_df['Date'].notnull()]
  return df, result_df

def remove_duplicate_age(df):
  result = df.drop_duplicates(subset=['Value'], keep='first')
  result = result[result['Value'].notnull()]
  return df, result

def set_interval_between_age(df):
  try:
    indice, first_line = next(df.iterrows())
    list_interval = []
    list_interval.append(first_line['Value'])
    for indice, row in df.iterrows():
      if row['Value'] - first_line['Value'] != 0:
        first_age = first_line['Value']
        second_age = row['Value']
        list_interval.append(second_age - first_age)

    df['Age_Intervalles'] = list_interval
    return df, list_interval
  except Exception as e :
    return df, list_interval

def set_interval_between_date(df):
  list_interval = []
  try:
    indice, first_line = next(df.iterrows())
    for indice, row in df.iterrows():

      if (row['Date'] != first_line['Date']):
        # Calcul de l'intervalle entre les deux dates
        first_date = first_line['Date']
        seconde_date = row['Date']
        
        days = abs(first_date - seconde_date).days
        list_interval.append(days)

        first_line = row
    # Exemple pour le papier
    #datetime_str = '04/03/2020'
    #datetime_object = datetime.strptime(datetime_str, '%d/%m/%Y')
    datetime_object = datetime.now()
    
    list_interval.append((datetime_object-df.iloc[-1]['Date']).days)

    #print(len(list_interval))
    df['Date_Intervalles'] = list_interval
    LIST_INTERVAL = list_interval
    return df, LIST_INTERVAL
  except Exception as e :
    return df, list_interval

def noisy_interval(df_date, df_age ,EPSILON):
  noisy_interval_list_d = []
  noisy_interval_list_a = []
  for index, row in df_date.iterrows():
    date_interval = row['Date_Intervalles']
    noisy_interval = dp.laplace_noise(date_interval,EPSILON)
    noisy_interval_list_d.append(noisy_interval)

  for index, row in df_age.iterrows():
    age_interval = row['Age_Intervalles']
    noisy_interval = dp.laplace_noise(age_interval, EPSILON)
    noisy_interval_list_a.append(noisy_interval)

  df_age['Noisy_Intervals'] = noisy_interval_list_a
  df_date['Noisy_Intervals'] = noisy_interval_list_d
  #df['Epsilon_Intervals'] = epsilon_interval
  return df_date, df_age

# def normalise_month(str_):
#   str_ = str_.replace('January','janvier')
#   str_ = str_.replace('February','février')
#   str_ = str_.replace('March','mars')
#   str_ = str_.replace('April','avril')
#   str_ = str_.replace('May','mai')
#   str_ = str_.replace('June','juin')
#   str_ = str_.replace('July','juillet')
#   str_ = str_.replace('August','août')
#   str_ = str_.replace('September','septembre')
#   str_ = str_.replace('October','octobre')
#   str_ = str_.replace('November','novembre')
#   str_ = str_.replace('December','decembre')

#   return str_

# def normalise_month_in_lookup_table(lookup_table):
#   for x in lookup_table.items():
#     key, value = x
#     lookup_table[key] = normalise_month(value)

  return lookup_table

def reconstruct_age_from_interval(df):
  ages_reconstruct = []
  indice, first_line = next(df.iterrows())
  ages_reconstruct.append(round(first_line['Noisy_Intervals']))
  first_age_noisy = ages_reconstruct[0]
  for indice, row in df.iterrows():
    if (row['Noisy_Intervals'] != first_line['Noisy_Intervals']):
      second_age_noisy = row['Noisy_Intervals']
      curr_age = round(second_age_noisy+first_age_noisy)
      ages_reconstruct.append(curr_age)

      first_age_noisy = curr_age
  df['Noisy_Age'] = ages_reconstruct
  return df

def reconstruct_date_from_interval(df):
  dates_reconstruct = []

  #datetime_str = '04/03/2020'
  #datetime_object = datetime.strptime(datetime_str, '%d/%m/%Y')
  #list_interval.append((datetime_object-df.iloc[-1]['Date_Standard']).days)

  begin_date = datetime.now()
  #begin_date = datetime_object
  for i in range(df.shape[0] - 1, -1, -1):  
    #print(df_standard_ordre.iloc[i])

    new_date = begin_date - timedelta(days=int(df.iloc[i]['Noisy_Intervals']))
    dates_reconstruct.append(new_date.strftime("%d/%m/%Y"))
    begin_date = new_date
 
  # print(dates_reconstruct)
  idx = len(dates_reconstruct) - 1
  new_dates_reconst = []
  while (idx >= 0):
    new_dates_reconst.append(dates_reconstruct[idx])
    idx = idx - 1

  df['Dates_reconst'] = new_dates_reconst
  return df

def date_to_orignal_format(df):
  dates = []
  for index, row in df.iterrows():
    date = datetime.strptime(row['Dates_reconst'],"%d/%m/%Y")
    orig_format = row['Format']

    date_f = date.strftime(orig_format)
    dates.append(date_f)

  df['Noisy_Date'] = dates
  return df

def date_to_original_sequence(df):
  return df.sort_index()

def construct_lookup_table(df_date, df_age):
  LOOKUP_TABLE = dict()
  for index, row in df_age.iterrows():
    age = row['Value']
    key = row['Age']
    if "old" in key:
      value = str(row['Noisy_Age']) + " years old"
    else:
      value = str(row['Noisy_Age']) + " years"
    LOOKUP_TABLE[key] = value

  for index, row in df_date.iterrows():
    date = row['Date']
    key = row['Detected date']
    value = row['Noisy_Date']
    
    LOOKUP_TABLE[key] = value
  return LOOKUP_TABLE