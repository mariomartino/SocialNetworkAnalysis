import random
import numpy as np
import networkx as nx
import utils

def epsilon(arms,rounds,e):
  reward = dict({a :0 for a in arms.keys()})
  for t in rounds:
    r = random.random()
    if r > e:
      arm = random.choice(list(arms.keys()))
    else:
      arm = list(arms.values()).index(max(arms.values()))
    
    reward[arm] = reward[arm] + arms[arm]

  for k,v in reward.items():
    if v > 0:
      print(str(k) + ": " + str(v))

###############################################
## Main test ##

G = utils.load_node("email-Eu-core.txt", True, " ")

arms = dict()
for i in range(0,99):
  #arms[i] = random.randint(1,100)
  arms[i] = 1

rounds = np.arange(100)
e = 0.3

epsilon(arms,rounds,e)