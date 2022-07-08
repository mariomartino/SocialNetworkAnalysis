import networkx as nx
import random

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
        
        for u in self.history[t-1]["activated"].keys():
            winner = self.history[t-1]["activated"][u]["ad"]
            chosen = 0
            for j in range(t):
                if u in self.history[j]["activated"] and self.history[j]["activated"][u]["ad"] == winner:
                    chosen += 1
            if chosen > 1:
                self.ectrs[u][winner] = (self.ectrs[u][winner] + self.history[t-1]["activated"][u]["payment"])*chosen/(chosen+1)
            else:
                self.ectrs[u][winner] = (self.ectrs[u][winner] + self.history[t-1]["activated"][u]["payment"])
        
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

    def __epsilon_greedy_bids(self, bids):
        pass

    #A possible choice for payment function
    def __first_price(bids, winner):
        return bids[winner]

    #Another possible choice for the payment function
    def __second_price(bids, winner):
        pay=-1
        for i in bids.keys():
            if i != winner and bids[i] > pay:
                pay = bids[i]
                
        return pay

    # MOCK-UP IMPLEMENTATION: It always announces that the winner will be the advertiser with the highest bid and it will pay the second highest bid
    # takes the time step t and node u, returns the select function and the payment function 
    def __annouce(self, t, u):
        return self.__higher_bid, self.__second_price

    #NOT IMPLEMENTED. Simply returns a random bid
    # takes the time step t, 
    # advertiser i, 
    # node u, 
    # select function, 
    # payment function and returs the bid for i
    def __best_response(self, t, i, u, select, payment):
        return random.random()

    #NOT IMPLEMENTED. It simply adds to the revenue a random integer for each node if the oracle states that a click occurs for a randomly selected bidder
    def run(self, t, rctrs):
        #rev = 0
        #for u in self.G.nodes():
        #    i = random.choice(range(len(self.rev.keys())))
        #    if rctrs(u,i):
        #        rev += random.randint(1, 10)
        #return rev
        rev = 0
        new_ectrs = self.__update_ectrs(t)
        self.history[t]["seed"] = self.__seed(t)
        for u in self.history[t]:
            i = random.choice(range(len(self.rev.keys())))
            winner, pay = self.__annouce(t,u)
            bid = self.__best_response(t,i,u,winner,pay)
            if rctrs(u,i):
                rev += self.rev[i]
        return rev
