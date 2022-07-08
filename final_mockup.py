import networkx as nx
import random

import numpy as np

from task2_hits import hits_average, hits_matrices

class AdService:
    
    def __init__(self, G, p, rev, B):
        self.G = G # network
        self.p = p # dictionary of diffusion probabilities
        self.rev = rev # dictionary of each advertiser of its revenue per click
        self.B = B # integer
        self.ectrs = None # dictionary for each node u and advertiser i, contains an estimate of clickthough rate of i on u
        self.history = None # collects for each time step, which seeds have been selected
    
    def __update_ectrs(self, t):
        if t == 0:
            self.ectrs=dict()
            for u in self.G.nodes():
                self.ectrs[u] = dict()
                for w in self.rev.keys():
                    self.ectrs[u][w] = 0
        else:
            for u in self.history[t-1]["activated"].keys():
                winner = self.history[t-1]["activated"][u]["ad"]
                chosen = 0
                clicked = 0
                for j in range(t):
                    if u in self.history[j]["activated"] and self.history[j]["activated"][u]["ad"] == winner:
                        chosen += 1
                        if self.history[j]["activated"][u]["clicked"]:
                            clicked += 1
                
                self.ectrs[u][winner] = clicked/chosen
            
    # non convince al 100%, ma funziona 
    def __seed(self, t):
        seeds = set()
        hubs, auth = hits_matrices(self.G)
        hits_average(self.G, hubs, auth)

        av = list(self.G.nodes(data="average"))
        av.sort(key=lambda tup:tup[1], reverse=True)

        for u in av:
            if len(seeds) < self.B:
                seeds.add(u[0])
            else:
                break
        return seeds


    def __epsilon_greedy_bids(self, bids, u):
        r1 = random.random()
        if r1 < 0.05:
            arm = random.choice(bids.keys()) ## forse da fare il cast in list
        else:
            arms = []
            for w in self.ectrs[u].keys():
                arms.append((w, self.ectrs[u][w] * self.rev[w]))
            arm = max(arms, key = lambda k:k[1])
        return arm[0]

    #A possible choice for payment function
    def __first_price(bids, winner):
        return bids[winner]

    #Another possible choice for the payment function
    def __second_price(self, bids, winner):
        pay=-1
        for i in bids.keys():
            if i != winner and bids[i] > pay:
                pay = bids[i]
                
        return pay

    # MOCK-UP IMPLEMENTATION: It always announces that the winner will be the advertiser with the highest bid and it will pay the second highest bid
    # takes the time step t and node u, returns the select function and the payment function 
    def __annouce(self, t, u):
        return self.__epsilon_greedy_bids, self.__second_price

    #NOT IMPLEMENTED. Simply returns a random bid
    # takes the time step t, 
    # advertiser i, 
    # node u, 
    # select function, 
    # payment function 
    # returs the bid for i
    def __best_response(self, t, i, u, select, payment):
        return random.random()
    
    def cascade(self, seed):
        # active represents the set S_t in the description above
        active = seed
        while len(active) > 0:
            for i in active:
                #This allows to keep track of S_<t, i.e. the set of nodes activated before time t
                self.G.nodes[i]['act'] = True
            # newactive represents the set S_{t+1}
            newactive = set()
            for i in active:
                for j in self.G[i]:
                    if 'act' not in self.G.nodes[j]:
                        r=random.random()
                        if r <= self.p[i][j]:
                            newactive.add(j)
            active = newactive
        
        nodes_active = list(nx.get_node_attributes(self.G, 'act').keys())
        
        return nodes_active

    def run(self, t, rctrs):
        rev = 0
        self.history = dict()
        self.__update_ectrs(t)
        self.history[t] = dict()
        self.history[t]["seed"] = self.__seed(t)
        self.history[t]["activated"] = dict()
        active = self.cascade(self.history[t]["seed"])
        for u in active:
            self.history[t]["activated"][u] = dict()
            winner, pay = self.__annouce(t,u)
            self.history[t]["activated"][u]["bids"] = dict()
            for i in self.rev.keys():
                bid = self.__best_response(t,i,u,winner,pay)
                self.history[t]["activated"][u]["bids"][i] = bid

            ad = winner(self.history[t]["activated"][u]["bids"], u)
            payment = pay(self.history[t]["activated"][u]["bids"], ad)

            if rctrs(u,ad):
                self.history[t]["activated"][u]["clicked"] = True
                rev += payment
            else:
                self.history[t]["activated"][u]["clicked"] = False

            self.history[t]["activated"][u]["ad"] = ad
            self.history[t]["activated"][u]["payment"] = payment
        
        return rev
