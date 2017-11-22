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

import random
from math import log
import timeit

#The number of strategies that we have
NUM_STRATEGIES = 4
#Number of metrics that we have
NUM_METRICS = 6



PRECISION = 4

# This function generates a random stable marriage problem with n 
#   members of each set
#TODO: Have this parameterized by a seed as well, to replicate the run
def generate_instance(n, seed = 1234):
    prefs = [list(range(n)) for i in range(2*n)]
    rand = random.Random(seed)
    for x in prefs:
        rand.shuffle(x)
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

        #print("ROUND", i)

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

    #Accept best in top f(n, param, num_props_received_before_this)
    elif(strategy == 3):
        for b in set_b.keys():
            if(set_b[b] == None and proposals[b].keys()):
                i = max(proposals[b].keys())
                best_a = min(proposals[b][i], key = lambda x: b_prefs[b].index(x))
                threshold = desperation_count(len(b_prefs), param, sum([len(proposals[b][x]) for x in range(i) if x in proposals[b].keys()]))
                #print(threshold, param)
                if(b_prefs[b].index(best_a) < threshold):
                    set_a[best_a] = b
                    set_b[b] = best_a



    #Other strategies go here

    return set_a, set_b

# All of these functions have the property that they go through (0,1) and (n,n)
#   This is a measure of the distance away from the top match they are willing to go
#   (as a function of how many proposals they have received)
def desperation_count(n, param, num_props):
    #print(n, param, num_props)
    #Linear function
    if(param == 0):
        return n/(n-1)*num_props + 1
    #Quadratic function
    elif(param == 1):
        return 1/n*(num_props**2) + 1
    #Exponential function
    elif(param == 2):
        return n**(num_props/n)
    #Logarithmic function
    elif(param == 3):
        return (n-1)/log(n+1)*log(num_props+1) + 1


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
def evaluate_matching(set_a, set_b, a_prefs, b_prefs):

    #Maybe do some precomputation if this gets really really slow

    #print(set_a, set_b)

    #Values of metrics
    metrics = [0]*NUM_METRICS
    n = len(set_a.keys())

    #First number is number of a's (or, equivalently, b's) that have no match
    metrics[0] = sum([1 for a in set_a.keys() if set_a[a] == None])

    #Second number is the total number of pairs that would "cheat" with each other
    #   (intuitively, if a1 is matched with b3, but prefers b1 or b2, this will be 2)
    if(not check_stability(set_a, set_b, a_prefs, b_prefs)):
        for a in set_a:
            index = safe_index(a_prefs[a], set_a[a])
            for i in range(index):
                b = a_prefs[a][i]
                if(set_b[b] == None or b_prefs[b].index(a) < b_prefs[b].index(set_b[b])):
                    metrics[1] += 1.0
        #This needs additional normalization
        metrics[1] = metrics[1]/(n)#*n)

    #Third number is the average "distance" of a match (how far down the preference 
    #   list your partner is) for the A set
    metrics[2] = sum([safe_index(a_prefs[a], set_a[a]) for a in set_a.keys()]) / (n)

    #Fourth number is the average "distance" for the B set
    metrics[3] = sum([safe_index(b_prefs[b], set_b[b]) for b in set_b.keys()]) / (n)

    #Fifth number is the max distance for the A set, not including the unmatched people
    #   (which would make this length)
    metrics[4] = max([safe_index(a_prefs[a], set_a[a]) for a in set_a.keys() if(set_a[a] != None)])

    #Sixth number is the max distance for the B set
    metrics[5] = max([safe_index(b_prefs[b], set_b[b]) for b in set_b.keys() if(set_b[b] != None)])

    #Other metrics go here

    return metrics

def smp(length, iters = 1, time_iters = 1):

    #We should come up with good short names for these
    strategies = [
        "GS",
        "BF",
        "TN",
        "ID"
    ]

    desperate_flags = 4
    #Percentiles for Top N strategies (strictly it's Top N %)
    percentiles = [1, 5, 10, 20, 25, 33, 50, 75]

    #This looks bad, but is hopefully dynamic enough to not randomly break
    #Essentially we want to store measurements of a run, which is identified
    #   by the strategy, and a single parameter (which is 0 and doesn't matter)
    #   for all but the TopN. We will make these tuples keys in the dictionary
    keys = list(zip(strategies[:-2], [0]*(NUM_STRATEGIES-2)))
    keys += list(zip([strategies[-2]]*len(percentiles), percentiles))
    keys += list(zip([strategies[-1]]*desperate_flags, range(desperate_flags)))

    keys = sorted(keys)

    #This should be restructured to be less memory intensive

    measurements = dict(zip(keys, [[0]*(NUM_METRICS+1)]*len(keys)))    

    for i in range(iters):
        inp = generate_instance(length)
        setup = "from __main__ import get_matching\na_prefs, b_prefs = %s, %s"% inp

        for (k,p) in keys:

            strategy = strategies.index(k)
            param = p
            if(strategy == 2):
                param = length*p/100

            # This looks clunky, but it repeats the computation some number of times
            #   Unfortunately, that destroys the result, so we run it again
            time = min(timeit.repeat("get_matching(a_prefs, b_prefs, %d, %d)"%(strategy, param), setup=setup, repeat=time_iters, number=1))
            print("Iteration %d Strategy %s started"%(i, (k+str(p))))

            set_a, set_b = get_matching(inp[0], inp[1], strategy, param)

            # Append time to the measurements list
            meas = evaluate_matching(set_a, set_b, inp[0], inp[1])
            meas.append(time)
            temp = measurements[(k,p)]

            measurements[(k,p)] = [x+y for (x,y) in zip(temp, meas)]
            print("Iteration %d Strategy %s finished in %.3f"%(i, (k+str(p)), time))
        print("Iteration %d finished"%i)

    for (k,p) in keys:            
        # Average and normalize
        temp_meas = measurements[(k,p)]
        measurements[(k,p)] = [round(x/(iters*length), PRECISION) for x in temp_meas[:-1]] + [round(temp_meas[-1]/iters, PRECISION)]

        if(p == 0):
            print(k + ":")
        else:
            print(k + str(p) + ":")
        print("\t", str(measurements[(k,p)]))


    return measurements



def main():
    #print(generate_instance(5))
    data = {}
    first_time = True

    #Run on sizes of up to 2048
    Ns = [2**i for i in range(4, 12)]
    Is = [30 for i in range(4,12)]
    N = 1024
    iters = 5

    # Iterate this lots of times
    #for (N, iters) in zip(Ns, Is):
    print(N, iters)
    vals = smp(N, iters)
    for k in vals:
        if(not (k in data)):
            data[k] = {}
        data[k][N] = vals[k]

    keys = sorted(data.keys())

    for k in keys:
        for n in data[k]:
            print(n, k, "\t", data[k][n])

if  __name__ == "__main__":
    main()
