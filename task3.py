import copy
import random
import numpy as np
import networkx as nx
import utils

def epsilon(arms,rounds,e):
  copy_arm = copy.deepcopy(arms)
  reward = dict({a :0 for a in arms.keys()})
  for t in rounds:
    r = random.random()
    if r > e:
      arm = random.choice(list(copy_arm.keys()))
    else:
      arm = list(copy_arm.values()).index(max(copy_arm.values()))
    
    reward[arm] = reward[arm] + copy_arm[arm]
    copy_arm[arm] = 0

  best_arm = list(reward.items())
  best_arm.sort(key=lambda tup:tup[1], reverse=True)
  return best_arm[0]
  

###############################################
## Main test ##

G = utils.load_node("email-Eu-core.txt", True, " ")

aucts = dict()
for i in range(0,40):
  aucts[i] = dict()
  for a in range(0,100):
    aucts[i][a] = random.random()

advs = dict()
for c in range(0,10):
  advs[c] = random.random()

rounds = np.arange(0,100,1)

res = dict()

temp = copy.deepcopy(aucts)
for c in range(len(advs.keys())):
  partial = dict()
  for a in temp.keys():
    partial[a] = epsilon(temp[a], rounds, advs[c])
  
  best_auct = list(partial.items())
  best_auct.sort(key=lambda tup:tup[1], reverse=True)
  res[c] = best_auct[0][0]

  del temp[best_auct[0][0]]

for k,v in res.items():
  print("ADV "+str(k)+": Auctioner "+str(v))