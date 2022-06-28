import random

class Auctioner:

    expected_revenue = dict()
    chosen_advertiser = dict()
    revenue_per_click = dict()
    epsilon = 0.05

    def __init__(self, n_slot, n_advertiser):
        """Initialization phase for an aucioner actors. The funcion initializes all
        the dictionaries needed for the computation

        Args:
            n_slot (int): The number of slot the auctioner could assign
            n_advertiser (int): The number of the advertisers partecipating to the auction
        """
        
        ## Initialize the revenue per click of each slot for each advertiser
        for i in range(n_advertiser):
            self.revenue_per_click[i] = dict()
            for a in range(n_slot):
                self.revenue_per_click[i][a] = random.random()

        ## Initialize the revenue per click of each slot for each advertiser
        for c in range(n_slot):
            self.expected_revenue[c] = dict()
            self.chosen_advertiser[c] = dict()
            for i in range(n_advertiser):
                self.expected_revenue[c][i] = 0      # Save the expected value for the auctioner i and the slot c
                self.chosen_advertiser[c][i] = 0 

    def choose_arm(self, slot):
        """An Epsilon-Greedy implementation the auctioner uses to assign slots.

        Args:
            slot (int): The number representing the slot the algorithm must assign

        Returns:
            int: The number representing the winner advertiser
        """
        
        r1 = random.random()
        if r1 < self.epsilon:
            arm = random.choice(list(self.revenue_per_click.keys()))  
        else:
            arm = max(self.expected_revenue[slot], key = lambda k: self.expected_revenue[slot][k])

        self.chosen_advertiser[slot][arm] += 1
        
        return arm 
       
    def update_values(self, slot, advertiser, clicked):
        """The function updates the expected revenues of the auctioner respect to the winner advertiser and the slot 

        Args:
            slot (int): The number identifying the slot
            advertiser (int): The number identifying the advertiser
            clicked (bool): True if the environment said the ad has been clicked
        """
        
        if clicked:    
            if self.chosen_advertiser[slot][advertiser] > 1:
                self.expected_revenue[slot][advertiser] += (self.revenue_per_click[advertiser][slot]/(self.chosen_advertiser[slot][advertiser] - 1)) # Normalization phase, it represents the expected value so it needs to be normalized
            else:
                self.expected_revenue[slot][advertiser] += self.revenue_per_click[advertiser][slot] 

        if self.chosen_advertiser[slot][advertiser] > 1:
            self.expected_revenue[slot][advertiser] *= ((self.chosen_advertiser[slot][advertiser] - 1)/self.chosen_advertiser[slot][advertiser]) # Normalization phase, it represents the expected value so it needs to be normalized

    def print_values(self, slot):
        """The function prints the expected revenues for each advertiser for the input slot

        Args:
            slot (int): The number identifying the slot
        """
        
        print("Print for the slot:", slot)
        for adv, revenue in self.expected_revenue[slot].items():
            print("Adv -", adv, "Revenue -", revenue)