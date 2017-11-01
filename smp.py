#Authors:
#   Kenny Denmark
#   Patrick Jenkins
#   Leslie McAdoo
#
#   Python 3
#

# Sources used:
#   https://stackoverflow.com/questions/976882/shuffling-a-list-of-objects
#   https://stackoverflow.com/questions/19306976/python-shuffling-with-a-parameter-to-get-the-same-result
#   https://www.tutorialspoint.com/python3/list_index.htm
#   https://en.wikipedia.org/wiki/Stable_marriage_problem
#   https://stackoverflow.com/questions/18296755/python-max-function-using-key-and-lambda-expression
#   https://docs.python.org/3/library/functions.html

# We need to cite the paper mentioned here:
#   http://pmneila.github.io/PyMaxflow/maxflow.html

from random import shuffle

#The number of strategies that we have
NUM_STRATEGIES = 3
#The default value of the "top N" strategy
DEFAULT_TOP_N = 10

# This function generates a random stable marriage problem with n 
#   members of each set
#TODO: Have this parameterized by a seed as well, to replicate the run
def generate_instance(n):
    prefs = [list(range(n)) for i in range(2*n)]
    for x in prefs:
        shuffle(x)
    return (prefs[0:n], prefs[n:])

def get_matching(a_prefs, b_prefs, strategy, param):
    #Verify the preferences to be legal

    length = len(a_prefs)

    #This dictionaries refer to the current "engagements"
    set_a = {i:None for i in range(length)}
    set_b = {i:None for i in range(length)}

    #These keep track of who "proposed" to who
    #   This is which a proposed to which b
    proposals = {i:{} for i in range(length)}
    #   This is the number of proposals that each a has made
    proposed = {i:0 for i in range(length)}

    #Initialize each a to free
    free_a = list(set_a.keys())

    #Round counter
    i = 0

    #For each free a
    while(free_a):
        #This constitutes 1 "round"
        for a in free_a:
            #Find the b that a should propose to next
            next_b = a_prefs[a][proposed[a]]
            #Propose to next_b
            if(i in proposals[next_b].keys()):
                proposals[next_b][i].append(a)
            else:
                proposals[next_b][i] = [a]
            #Increment the next to propose to
            proposed[a] += 1

        process_proposals(proposals, b_prefs, set_a, set_b, strategy, param)

        #Increase round number
        i += 1

        #Recreate the free array
        free_a = [a for a in set_a.keys() if ((set_a[a] == None) and proposed[a] < length)]

    #Before returning, make sure that this is legal
    if(verify(set_a, set_b)):
        return set_a, set_b
    else:
        print("There was an error")
        exit()

# This is going to process proposals in a variety of different ways
def process_proposals(proposals, b_prefs, set_a, set_b, strategy, param):
    #Default strategy
    if(strategy == 0):
        for b in set_b.keys():
            #Only look at the most current round
            if(proposals[b].keys()):
                i = max(proposals[b].keys())
                #Get the best a that proposed to b this round
                best_a = min(proposals[b][i], key = lambda x: b_prefs[b].index(x))
                #If b doesn't have a match
                if(set_b[b] == None):
                    #Set b's match to be best_a
                    set_b[b] = best_a
                    #Set best_a's match to be b
                    set_a[best_a] = b
                #Otherwise, if b's match is less preferable to best_a
                elif(b_prefs[b].index(set_b[b]) > b_prefs[b].index(best_a)):
                    #Break match with current match
                    set_a[set_b[b]] = None
                    set_a[best_a] = b
                    set_b[b] = best_a

    #Accept the best proposal in the first round you are proposed to (no tradeups)
    elif(strategy == 1):
        for b in set_b.keys():
            if(set_b[b] == None and proposals[b].keys()):
                i = max(proposals[b].keys())
                best_a = min(proposals[b][i], key = lambda x: b_prefs[b].index(x))
                set_b[b] = best_a
                set_a[best_a] = b

    #Accept first in top N (param), with no trade ups
    elif(strategy == 2):
        for b in set_b.keys():
            if(set_b[b] == None and proposals[b].keys()):
                i = max(proposals[b].keys())
                best_a = min(proposals[b][i], key = lambda x: b_prefs[b].index(x))
                if(b_prefs[b].index(best_a) < param):
                    set_a[best_a] = b
                    set_b[b] = best_a



    #Other strategies go here

    return set_a, set_b

# This is a safety wrapper for the index() method of lists, so that we don't have
#   to rewrite too much code to account for not everyone being matched
def safe_index(elements, x):
    if(x == None):
        return len(elements)
    return elements.index(x)

# Verify that the matching is legal
def verify(set_a, set_b):
    #Here we check to see if the match is legal (no entity in more than 1 match)
    list_a, list_b = [0]*len(set_a.keys()), [0]*len(set_b.keys())
    for a in set_a.values():
        if(not (a == None)):
            list_b[a] += 1
            if(list_b[a] > 1):
                return False
    for b in set_b.values():
        if(not (b == None)):
            list_a[b] += 1
            if(list_a[b] > 1):
                return False

    #Check that each match goes both ways
    for a in set_a.keys():
        if(not (set_a[a] == None) and set_b[set_a[a]] != a):
            return False

    return True

# This should check whether or not the matching is stable
def check_stability(set_a, set_b, a_prefs, b_prefs):
    #For every a
    for a in set_a:
        index = safe_index(a_prefs[a], set_a[a])
        #For every b that a prefers more than their match
        for i in range(index):
            b = a_prefs[a][i]
            #If b prefers a, or is not matched, we have instability
            if(set_b[b] == None or b_prefs[b].index(a) < b_prefs[b].index(set_b[b])):
                return False
    return True

# This should calculate the values of our chosen metrics
def evaulate_matching(set_a, set_b, a_prefs, b_prefs):

    #Maybe do some precomputation if this gets really really slow

    #Values of metrics
    metrics = [0]*7
    n = len(set_a.keys())

    #First number is the total number of pairs that would "cheat" with each other
    #   (intuitively, if a1 is matched with b3, but prefers b1 or b2, this will be 2)
    if(not check_stability(set_a, set_b, a_prefs, b_prefs)):
        for a in set_a:
            index = safe_index(a_prefs[a], set_a[a])
            for i in range(index):
                b = a_prefs[a][i]
                if(set_b[b] == None or b_prefs[b].index(a) < b_prefs[b].index(set_b[b])):
                    metrics[0] += 1

    #Second number is the maximum number of cheating pairs that we could have at a time
    #   (assuming that if any given a will only cheat on their partner with one b)
    #   (this we frame as a maxflow problem)
    #TODO: Actually do this

    #Third number is number of a's (or, equivalently, b's) that have no match
    metrics[2] = sum([1 for a in set_a.keys() if set_a[a] == None])

    #Fourth number is the average "distance" of a match (how far down the preference 
    #   list your partner is) for the A set
    metrics[3] = round(sum([safe_index(a_prefs[a], set_a[a]) for a in set_a.keys()]) / n, 3)

    #Fifth number is the average "distance" for the B set
    metrics[4] = round(sum([safe_index(b_prefs[b], set_b[b]) for b in set_b.keys()]) / n, 3)

    #Sixth number is the max distance for the A set
    metrics[5] = max([safe_index(a_prefs[a], set_a[a]) for a in set_a.keys()])

    #Seventh number is the max distance for the B set
    metrics[6] = max([safe_index(b_prefs[b], set_b[b]) for b in set_b.keys()])

    #Other metrics go here

    return metrics

def smp(length):
    a_prefs, b_prefs = generate_instance(length)

    for strategy in range(NUM_STRATEGIES):
        set_a, set_b = get_matching(a_prefs, b_prefs, strategy, length/20)
        #print(set_a, set_b)
        print(evaulate_matching(set_a, set_b, a_prefs, b_prefs))


def main():
    #print(generate_instance(5))
    smp(750)

main()