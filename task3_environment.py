import random

class Environment:

    clicktrough_rates = dict()

    def __init__(self, n_slot, n_advertiser):
        """The function initialize the environment setting the clickthrough rates for each slot and each advertiser

        Args:
            n_slot (int): The number of the slots
            n_advertiser (int): The number of the advertisers
        """
        ## Initialize the clicktrough rates of each slot
        for i in range(n_slot):
            self.clicktrough_rates[i] = dict()
            for j in range(n_advertiser):
                self.clicktrough_rates[i][j] = random.random()

    def clicked(self, slot, advertiser):
        """The function compute, in a probabilistic way, if the ad's been clicked or not

        Args:
            slot (int): The number identifying the slot
            advertiser (int): The number identifying the winner advertiser

        Returns:
            bool: True if the ad has been clicked, else False.
        """
        r = random.random()
        if r < self.clicktrough_rates[slot][advertiser]:
            return True
        return False
