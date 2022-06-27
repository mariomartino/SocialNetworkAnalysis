import copy
import random
import numpy as np
import networkx as nx
import utils

def epsilon(auctioners, advertisers, e):
  """A method launching an Epsilon-Greedy experiment. The function with probability e returns a random advertiser, otherwile returns
  the best advertiser. 

  Args:
      auctioners (dict): A dictionary containing the expected value of revenue for each advertiser
      advertisers (dict): A dictionary contaning the clickthrough rates of the advertisers for each slot
      e (float): The epsilon value of the algorithm

  Returns:
      int: The integer representing the winner of the round
  """
  r1 = random.random()
  if r1 < e:
    arm = random.choice(list(advertisers.keys()))  
  else:
    arm = max(auctioners, key = lambda k: auctioners[k])
  
  return arm 

########################################################################################

  """Initialize the revenue per click rates for each slot and for each advertiser
  """
slot= dict()
for c in range(0,10):
  slot[c] = dict()
  for i in range(0,40):
    slot[c][i] = random.random() # Clickthrough rate of the slot c linked to the advertiser i

"""Initialize the revenue per click rates for each slot and for each advertiser
  """
advertisers = dict()
for i in range(0,40):
  advertisers[i] = dict()
  for a in range(0,len(slot.keys())):
    advertisers[i][a] = random.random() # Revenue per click of the advertiser

"""Initialize the expected auctioners' value for each slot and for each advertiser and how many times the auctioners have been chosen for each slot
  """
auctioners = dict()
chosen = dict()
for c in range(0,len(slot.keys())):
  auctioners[c] = dict()
  chosen[c] = dict()
  for i in range(0,len(advertisers.keys())):
    auctioners[c][i] = 0      # Save the expected value for the auctioner i and the slot c
    chosen[c][i] = 0          # Save how many times the single auctioner has been chosen for the slot c

"""Launch 100000 rounds for each slot to let auctioners to compute a realistic expected value launching epsilon-greedy algorithm.
"""
rounds = np.arange(0,100000,1)
for c in range(len(slot.keys())):
  for a in rounds:
    value = epsilon(auctioners[c], advertisers, 0.01)
    chosen[c][value] += 1
    r = random.random()
    if r < slot[c][value]:
      if chosen[c][value] > 1:
        auctioners[c][value] += (advertisers[value][c]/(chosen[c][value] - 1)) # Normalization phase, it represents the expected value so it needs to be normalized
      else:
        auctioners[c][value] += advertisers[value][c] 


    if chosen[c][value] > 1:
      auctioners[c][value] *= ((chosen[c][value] - 1)/chosen[c][value]) # Normalization phase, it represents the expected value so it needs to be normalized
  
for k,v in auctioners.items():
  print(str(k))
  for i in v.values():
    print("     "+str(i))

##### da fare ##########################
# Creazione Ambiente
# Eventualmente, programmazione a classi
# Decidere l'epsilon