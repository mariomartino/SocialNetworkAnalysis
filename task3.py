import copy
import random
import numpy as np
import networkx as nx
import utils

def epsilon(auctioners, advertisers, e):
  r1 = random.random()
  if r1 < e:
    arm = random.choice(list(advertisers.keys()))  
  else:
    arm = max(auctioners, key = lambda k: auctioners[k])
  
  return arm 

########################################################################################

slot= dict()
for c in range(0,10):
  slot[c] = dict()
  for i in range(0,40):
    slot[c][i] = random.random()

advertisers = dict()
for i in range(0,40):
  advertisers[i] = dict()
  for a in range(0,len(slot.keys())):
    advertisers[i][a] = random.random()

auctioners = dict()
chosen = dict()
for c in range(0,len(slot.keys())):
  auctioners[c] = dict()
  chosen[c] = dict()
  for i in range(0,len(advertisers.keys())):
    auctioners[c][i] = 0
    chosen[c][i] = 0

rounds = np.arange(0,100000,1)
for c in range(len(slot.keys())):
  for a in rounds:
    value = epsilon(auctioners[c], advertisers, 0.01)
    chosen[c][value] += 1
    r = random.random()
    if r < slot[c][value]:
      if chosen[c][value] > 1:
        auctioners[c][value] += (advertisers[value][c]/(chosen[c][value] - 1))
      else:
        auctioners[c][value] += advertisers[value][c]


    if chosen[c][value] > 1:
      auctioners[c][value] *= ((chosen[c][value] - 1)/chosen[c][value]) 
  
for k,v in auctioners.items():
  print(str(k))
  for i in v.values():
    print("     "+str(i))

##### da fare ##########################
# Creazione Ambiente
# Eventualmente, programmazione a classi
# Decidere l'epsilon