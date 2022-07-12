import networkx as nx
import random
from collections import Counter

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
                    self.ectrs[u][w] = 0, 0  ## TODO: INIZIALIZZA AL MINIMO: 0.1
            return
        for u in self.history[t-1]["activated"].keys():  ## POSSIAMO MODIFICARE ECTRS MEMORIZZANDO ANCHE CHOSEN ?

            winner = self.history[t-1]["activated"][u]["ad"]
            chosen = self.ectrs[u][winner][1]
            last_ctr = self.ectrs[u][winner][0]
            clicked = last_ctr*(chosen - 1)
            ## TODO: Incrementa chosen
            if self.history[t-1]["activated"][u]["clicked"]:
                clicked += 1
            
            self.ectrs[u][winner] = clicked/chosen, chosen
            
    # non convince al 100%, ma funziona 
    def __seed(self, t):
        
        if t==0:

            seeds = set()
            hubs, auth = hits_matrices(self.G)
            hits_average(self.G, hubs, auth)  ## USEREI HITS HUBBINESS PER FONDAMENTO TEORICO

            av = list(self.G.nodes(data="average"))
            av.sort(key=lambda tup:tup[1], reverse=True)

            seeds.add(av[i][0] for i in range(self.B))

        else:
            seeds = self.history[t-1]["seeds"]

        return seeds


    def __epsilon_greedy_bids(self, bids, u):
        r = random.random()
        if r < 0.05:
            arm = random.choice(list(bids.keys()))
            return arm
        else:
            arms = []
            for w in self.ectrs[u].keys():
                arms.append((w, self.ectrs[u][w][0] * bids[w])) 
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
        
        if t == 0:
            return self.rev[i]
        
        tmp_bids = self.history[t-1]["activated"][u]["bids"]
        tmp_bids[i] = self.rev[i]
        array_winner = []
        for _ in range(10):
            array_winner.append(select(tmp_bids, u))
        counter = Counter(array_winner)
        tmp_winner = counter.most_common(1)
        tmp_pay = payment(tmp_bids, tmp_winner)

        if tmp_winner == i and tmp_pay == self.rev[i]:   # ADV i HA VINTO ED È UNA FIRST PRICE
            tmp_bids.pop(max(tmp_bids, key = lambda k : tmp_bids[k]))
            second = tmp_bids.pop(max(tmp_bids, key = lambda k : tmp_bids[k]))
            return (self.rev[i] + second)/2     # CERCO DI PAGARE DI MENO
        else:   # È UNA SECOND PRICE O LA VALUTO MENO DEGLI ALTRI
            return self.rev[i] 
    
    def cascade(self, seed):
        active = seed
        while len(active) > 0:
            for i in active:
                self.G.nodes[i]['act'] = True
            newactive = set()
            for i in active:
                for j in self.G[i]:
                    if 'act' not in self.G.nodes[j]:
                        r=random.random()
                        if r <= self.p[i][j]:
                            newactive.add(j)
            active = newactive
        
        nodes_active = list(nx.get_node_attributes(self.G, 'act').keys())

        for u in nodes_active:
            del self.G.node[u]["act"]
        
        return nodes_active

    def run(self, t, rctrs):
        rev = 0
        self.__update_ectrs(t)
        self.history[t] = dict()
        self.history[t]["seeds"] = self.__seed(t)
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
                payment = 0 # CREDO PERCHÈ NON CI SONO PAGAMENTI

            self.history[t]["activated"][u]["ad"] = ad
            self.history[t]["activated"][u]["payment"] = payment
        
        return rev
