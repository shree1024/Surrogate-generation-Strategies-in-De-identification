import math
import pandas as pd
import numpy as np
import ast
from math import sin, cos, sqrt, atan2, radians

def distance_between_points(x_lat,x_long,y_lat,y_long) :
  # approximate radius of earth in km
  R = 6371.0

  lat1 = radians(x_lat)
  lon1 = radians(x_long)
  lat2 = radians(y_lat)
  lon2 = radians(y_long)

  dlon = lon2 - lon1
  dlat = lat2 - lat1

  a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
  c = 2 * atan2(sqrt(a), sqrt(1 - a))

  distance = R * c

  return distance

def dist_from_others(lat, lon, dataframe, RAYON):
  coord = ",".join([str(lat),str(lon)])
  #loc = dataframe[dataframe['coordonnees_gps'] == coord]
  communes_coord = list(dataframe['gps coordinates'])
  #print(len(communes_coord))
  distances = []
  for coord in communes_coord:
    lat_, lon_ = coord_to_latlong(coord)
    distances.append(round(distance_between_points(lat, lon, lat_, lon_), 2))
  curr_df = dataframe.copy()
  curr_df['dist_geo'] = distances
  curr_df = curr_df[curr_df['dist_geo'] < RAYON]
  curr_df = curr_df[['city', 'city code', 'overall population', 'cancer incidence rate', 'stroke']]
  return curr_df

def distance_C(x, y):
  x = np.array(x)
  y = np.array(y)
  return np.linalg.norm(x-y)

def coord_to_latlong(str_):
  x, y = str_.split(',')
  x, y = float(x), float(y)
  return x, y

# Function de Normalisation
def normalization (x, MAX, MIN):
  return (x-MIN)/(MAX-MIN)

def normalize_features(df, features):
  for feature in features :
    LIST = list(df[feature])
    MAX_F = max(LIST)
    MIN_F = min(LIST)
    new_col = feature + "_normalized"
    df[new_col] = df[[feature]].apply(lambda x : normalization(x, MAX_F, MIN_F))
  return df

def vector_distance(code, df, features):
  commune = df[df['city code'] == code]
  # Recuperation des caractéristiques : population
  x = []
  #Ajout des caractéristiques : Population|cancer incidence rate|stroke
  for feature in features :
    x.append(commune[feature+'_normalized'].values[0])
  
  distances = []
  for index, row in df.iterrows() :
      y = []
      #Ajout des caractéristiques : Population|cancer incidence rate|stroke
      y.append(row[feature+'_normalized'])
      
      #Distance des vecteurs
      distances.append(distance_C(x,y))
  
  df['distances'] = distances
  return df
 
def score(x, k):
  #print(x.values)
  return math.exp(-(k*x))

def score2(x,k):
  return k - x

def pdf(x, epsilon):
  return math.exp(epsilon*x)

def scores(df, k=3):
  df['scores'] = df['distances'].apply(lambda x : score2(x, k))
  return df

def pdfs(df, epsilon):
  df['pdf'] = df['scores'].apply(lambda x : pdf(x, epsilon))
  return df