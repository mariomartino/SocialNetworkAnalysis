from task3_auctioner import Auctioner
from task3_environment import Environment

N_SLOT = 10
N_ADVERTISER = 10
N_ROUNDS = 100000

if __name__ == "__main__":

    environment = Environment(N_SLOT, N_ADVERTISER)
    auctioner = Auctioner(N_SLOT, N_ADVERTISER)

    for slot in range(N_SLOT):

        for round in range(N_ROUNDS):

            adv_winner = auctioner.choose_arm(slot)
            clicked = environment.clicked(slot, adv_winner)
            auctioner.update_values(slot, adv_winner, clicked)

        auctioner.print_values(slot)
