import random
import numpy as np
import networkx as nx
import utils

def epsilon(arms,rounds,e):
  reward = 0
  for t in rounds:
    r = random.random()
    if r > e:
      arm = random.choice(list(arms.keys()))
    else:
      arm = list(arms.values()).index(max(arms.values()))
    
    reward += arms[arm]




###############################################
## Main test ##

G = utils.load_node("email-Eu-core.txt", True, " ")

arms = dict()
for i in range(0,99):
  arms[i] = random.randint(1,100)

rounds = np.arange(20)
e = 0.4

epsilon(arms,rounds,e)