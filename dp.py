import numpy as np
import math

# D = [l,u] q in D
def C_q(q,b,l,u) :
  return 1 - 1/2*(math.exp(-((q-l)/b)) + math.exp(-((u-l)/b)))

def delta_Q(l,u):
  return u-l

def delta_C(b,l,u) :
  return C_q(l+delta_Q(l,u),b,l,u)/C_q(l,b,l,u)

def f_b(b,l,u,epsilon):
  return delta_Q(l,u)/(epsilon - math.log(delta_C(b,l,u)))

def bounded_laplace_mech(l,u,epsilon) :
  left = delta_Q(l,u)
  right = f_b(left,l,u,epsilon)
  intervalSize = (left + right) * 2

  while (intervalSize > (right - left)) :
    intervalSize = right - left
    b = (left+right)/2
    if(f_b(b,l,u,epsilon) >= b):
      left=b
    if (f_b(b,l,u,epsilon) <= b):
      right = b
    
  return b

def laplace_noise(x,epsilon,sensitivity):
  return x + np.random.laplace(loc=0, scale=sensitivity/epsilon)

def const_proportionnel2(epsilon_G, intervals):
  somme = 0
  for x in intervals:
    somme += x
  return somme/epsilon_G

def const_proportionnel(epsilon_G, intervals):
  inverse_somme = 0
  for x in intervals :
    inverse_somme += 1/x 
  return epsilon_G/inverse_somme

def mEpsilon2(amplitude, CONSTANTE):
  return amplitude/CONSTANTE

def mEpsilon(amplitude, CONSTANTE):
  return CONSTANTE/amplitude

def normalization(list_i) :
  result = []
  min_l = min(list_i)
  max_l = max(list_i)
  for x in list_i :
    normalise_x = (x - min_l)/(max_l - min_l)
    result.append(normalise_x)
  return result

def calcul_epsilon_interval(list_i, CONSTANTE): 
  epsilon_interval = []
  for interval in list_i :
    epsilon = mEpsilon(interval,CONSTANTE)
    epsilon_interval.append(epsilon)
  return epsilon_interval

def laplace_noise(x,epsilon):
  SENSITIVITY = 1
  SCALE = SENSITIVITY/epsilon
  x_noisy = np.random.laplace(loc=x,scale=SCALE)
  while x_noisy < 0 :
    x_noisy = np.random.laplace(loc=x,scale=SCALE)
  return x_noisy
  
def bounded_laplace_noise(x,epsilon,l,u):
  SENSITIVITY = u - l
  #SENSITIVITY = 1
  SCALE = SENSITIVITY/epsilon
  #SCALE = bounded_laplace_mech(l,u,epsilon)
  #print(C_q(x,SCALE,l,u))
  x_noisy = (np.random.laplace(loc=x,scale=SCALE))/C_q(x,SCALE,l,u)
  #print(x_noisy, r, epsilon, SENSITIVITY)
  while(x_noisy>u or x_noisy<=l) :
    x_noisy = (np.random.laplace(loc=x,scale=SCALE))/C_q(x,SCALE,l,u)
  return x_noisy

def perturb_interval(list_i,NOISY_INTERVALS, sensitivity,l,u) :
  noisy_norm_intervals = []
  for x,epsilon in zip(list_i,NOISY_INTERVALS) :
    noisy_norm_intervals.append(bounded_laplace_noise(x,epsilon, sensitivity,l,u))
  return noisy_norm_intervals

def reconstitution_interval(list_n,list_i) :
  result = []
  max_l = max(list_i)
  min_l = min(list_i)
  for x in list_n : 
    interval = x * (max_l - min_l) + min_l
    result.append(interval)
  return result

if __name__ == '__main__':
  epsilon = 1
  u = 234
  l = 12
  b=(u-l)/epsilon
  expl = [234, 34, 26, 27, 12]
  result = []

  for x in expl : 
    r = (np.random.laplace(loc=x,scale=b))/C_q(x,b,l,u)
    #while(r>1000 or r<0) :
    #  r = (np.random.laplace(loc=x,scale=b))/C_q(x,b,l,u)
    result.append(r)

  print(result)