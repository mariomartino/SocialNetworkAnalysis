import random

def epsilon_greedy(choices, expected_values, e):
  """A method launching an Epsilon-Greedy experiment. The function with probability e returns a random choice, otherwile returns
  the best one. 
  Args:
      choices (list): A list containing the possible choices of the algorithm
      expected_values (dict): A dictionary contaning the expected values related to the possible choice. 
                              Format: ("choice" : "expected value")
      e (float): The epsilon value of the algorithm
  Returns:
      int: The integer representing the choice of the round
  """
  r1 = random.random()
  if r1 < e:
    arm = random.choice(choices) 
  else:
    arm = max(expected_values, key = lambda k: expected_values[k])
  
  return arm 