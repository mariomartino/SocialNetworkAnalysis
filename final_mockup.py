import networkx as nx
import random
from collections import Counter

import numpy as np

from task2_hits import hits_hubs, hits_matrices

class AdService:
    

    def __init__(self, G, p, rev, B):
        """Initialize the object AdService, by assigning the values passed as parameter.

        Args:
            G (networkx.Graph): The graph on which the system runs the Ad Service
            p (dict): Dictionary containing the diffusion probabilities
            rev (dict): Dictionary containing for each advertiser its revenue per click
            B (int): The allowed number of seeds for step
        """
        self.G = G 
        self.p = p 
        self.rev = rev
        self.B = B 
        self.ectrs = None 
        self.history = None
    

    def __update_ectrs(self, t):
        """Il metodo aggiorna la stima dei Clickthrough Rates basandosi sulla storia dall'istante 0 all'istante t.

        Args:
            t (int): Timestep cui il metodo calcola la stima
        """
        if t == 0:
            self.ectrs=dict()
            for u in self.G.nodes():
                self.ectrs[u] = dict()
                for w in self.rev.keys():
                    self.ectrs[u][w] = .1, 0
            return
        for u in self.history[t-1]["activated"].keys():

            winner = self.history[t-1]["activated"][u]["ad"]
            chosen = self.ectrs[u][winner][1]
            last_ctr = self.ectrs[u][winner][0]
            clicked = last_ctr*(chosen)
            chosen += 1
            if self.history[t-1]["activated"][u]["clicked"]:
                clicked += 1

            ctr = max(clicked/chosen, .1)
            ctr = min(ctr, .6)

            self.ectrs[u][winner] = ctr, chosen
            

    def __seed(self, t):
        """Computes the seeds at the timestep t. The seeds are computed in the first iteration and then
        reported in the successive steps.

        Args:
            t (int): Timestep in which the seeds are computed

        Returns:
            set: The set containing the seeds nodes
        """
        
        if t==0:

            seeds = set()
            hubs, auth = hits_matrices(self.G)
            hits_hubs(self.G, hubs)

            av = list(self.G.nodes(data="hubs"))
            av.sort(key=lambda tup:tup[1], reverse=True)

            for i in range(self.B):
                seeds.add(av[i][0]) 

        else:
            seeds = self.history[t-1]["seeds"]

        return seeds


    def __epsilon_greedy_bids(self, bids, u):
        """The method implements an Epsilon-Greedy algorithm that select the winner advertiser.

        Args:
            bids (dict): The dictionary containing a bid for each advertiser
            u (int): The integer representing the node the system is evaluating

        Returns:
            int: The integer representing the winner advertiser
        """
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


    def __first_price(self, bids, winner):
        """The method returns the bid of the winner, in order to compute the payment in a first price auction.

        Args:
            bids (dict): The dictionary containing a bid for each advertiser
            winner (int): The integer representing the winner advertiser

        Returns:
            float: The payment of the winner in a first price auction
        """
        return bids[winner]


    def __second_price(self, bids, winner):
        """The method returns the bid of the winner, in order to compute the payment in a second price auction.

        Args:
            bids (dict): The dictionary containing a bid for each advertiser
            winner (int): The integer representing the winner advertiser

        Returns:
            float: The payment of the winner in a second price auction
        """
        pay=-1
        for i in bids.keys():
            if i != winner and bids[i] > pay:
                pay = bids[i]
                
        return pay


    def __annouce(self, t, u):
        """The method returns the two function the system uses in order to compute winner and payment.

        Args:
            t (int): The current timestep
            u (int): The integer representing the node the system is evaluating

        Returns:
            func, func: The two select and payment functions respectively
        """
        return self.__epsilon_greedy_bids, self.__second_price

 
    def __best_response(self, t, i, u, select, payment):
        """The function computes the best response bid for the current auction. It is valid for each advertiser.

        Args:
            t (int): The current timestep
            i (int): The integer representing the advertiser
            u (int): The integer representing the node
            select (func): The function that computes the winner advertiser
            payment (func): The function that computes the payment for the current auction

        Returns:
            float: The bid subbmitted
        """
        
        if t == 0:
            return self.rev[i]
        
        if u in self.history[t-1]["activated"]:
            tmp_bids = self.history[t-1]["activated"][u]["bids"].copy()
            tmp_bids[i] = self.rev[i]
        else:
            tmp_bids = self.rev.copy()
        
        array_winner = []
        for _ in range(10):
            array_winner.append(select(tmp_bids, u))
        counter = Counter(array_winner)
        tmp_winner = counter.most_common(1)[0][0]
        tmp_pay = payment(tmp_bids, tmp_winner)

        tmp_bids.pop(max(tmp_bids, key = lambda k : tmp_bids[k]))
        second = tmp_bids.pop(max(tmp_bids, key = lambda k : tmp_bids[k]))

        if tmp_winner == i and tmp_pay == self.rev[i]:
            return (self.rev[i] + second)/2
        elif tmp_winner == i and tmp_pay < self.rev[i]:
            return (self.rev[i] + tmp_pay)/2
        else:
            return min(self.rev[i], second)
    

    def cascade(self, seed):
        """The method implements an Indipendent Cascade Model for Information Diffusion.

        Args:
            seed (set): The set of the nodes active in the first step

        Returns:
            list: The list of all nodes active at the end
        """
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
            del self.G.nodes[u]["act"]

        return nodes_active


    def run(self, t, rctrs):
        """The function computes for the time step t an estimate of clickthrough rates through the function ectrs, then computes the set of
        seeds to be adopted in this time step through the function seed. It starts a cascade from these seeds, and collects the set of activated nodes

        Args:
            t (int): The current timestep
            rctrs (func): The oracle with the real Clickthrough Rates

        Returns:
            float: The revenue obtained in the current timestep
        """
        if t == 0:
            self.history = dict()
        rev = 0
        self.__update_ectrs(t)
        self.history[t] = dict()
        self.history[t]["seeds"] = self.__seed(t)
        self.history[t]["activated"] = dict()
        active = self.cascade(self.history[t]["seeds"])
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
                payment = 0

            self.history[t]["activated"][u]["ad"] = ad
            self.history[t]["activated"][u]["payment"] = payment

        return rev
