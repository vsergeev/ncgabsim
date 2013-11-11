import random
import ff

ff.FiniteFieldArray.ff_precompute()

def choose_weighted_random(objects, scores):
    scores_cdf = []
    for s in scores[:]:
        scores_cdf.append(sum(scores_cdf) + s)

    random_score = random.random()*scores_cdf[-1]
    for index in range(len(scores_cdf)):
        if scores_cdf[index] > random_score:
            break

    return index

class Window():
    def __init__(self, keep_expired = False):
        self.window = []
        self.ttl = {}
        self.keep_expired = keep_expired

    def add(self, p, ttl):
        if p is None or p in self.window:
            return False

        self.window.append(p)
        self.ttl[str(p)] = ttl
        return True

    def prune(self):
        if self.keep_expired:
            return []

        # Create a list of expired objects
        expiredList = list(filter(lambda x: self.ttl[str(x)] == 0, self.window))

        # Remove all expired objects from our window
        for e in expiredList:
            self.window.remove(e)
            del self.ttl[str(e)]

        return expiredList

    def tick(self):
        # Decrement the TTL for each object in the window
        for x in self.window:
            self.ttl[str(x)] = max(0, self.ttl[str(x)] - 1)

        return self.prune()

    def live_objects(self):
        return list(filter(lambda x: self.ttl[str(x)] > 0, self.window))

    def objects(self):
        return self.window[:]

    def __str__(self):
        s = "Window\n"
        for x in self.window:
            s += "\t" + str(x) + " TTL: " + str(self.ttl[str(x)]) + "\n"
        return s

class Decoded_Window(Window):
    def __init__(self):
        Window.__init__(self, keep_expired = True)

    def choose_random_uniform(self, n):
        choices = self.live_objects()
        random.shuffle(choices)
        return choices[0 : min(n, len(choices))]

    def choose_random(self, n):
        choices = self.live_objects()
        scores = [self.ttl[str(c)] for c in choices]

        n = min(n, len(choices))
        chosen = []
        for i in range(n):
            k = choose_weighted_random(choices, scores)
            chosen.append(choices[k])
            del choices[k]
            del scores[k]

        return chosen

class Gossip_Window(Window):
    def __init__(self):
        Window.__init__(self, keep_expired = False)
        # Keep active objects in a dictionary by source as well
        self.active_objects_by_source = {}

    def add(self, src, p, ttl):
        if Window.add(self, p, ttl) == True:
            # Create a new list for the source if it's not in our dictionary
            if src not in self.active_objects_by_source:
                self.active_objects_by_source[src] = []

            # Add the message to the source's list
            self.active_objects_by_source[src].append(p)
            return True

        return False

    def prune(self):
        expiredList = Window.prune(self)
        # For each expired object
        for e in expiredList:
            for src in self.active_objects_by_source:
                # If the object exists in this source's list
                if e in self.active_objects_by_source[src]:
                    # Delete it
                    self.active_objects_by_source[src].remove(e)
                    # Delete the source's list if it's empty now
                    if len(self.active_objects_by_source[src]) == 0:
                        del self.active_objects_by_source[src]
                    break
        return expiredList

    def choose_random_uniform(self):
        # Choose a random source
        source = random.choice(list(self.active_objects_by_source.keys()))

        # Gather a list of objects by this source
        objects = self.active_objects_by_source[source]

        return random.choice(objects)

    def choose_random(self):
        # Choose a random source
        source = random.choice(list(self.active_objects_by_source.keys()))

        # Gather a list of objects by this source
        choices = self.active_objects_by_source[source]
        scores = [self.ttl[str(c)] for c in choices]

        return choices[choose_weighted_random(choices, scores)]

    def fast_rref(self, m, b, x):
        done = False
        pi = 0

        # Iterate through each row
        for j in range(len(m)):
            # While we do not have a pivot for this row
            while m[j][pi] == 0:
                # Find a row below to swap with for a pivot at pi
                for k in range(j+1, len(m)):
                    if m[k][pi] != 0:
                        # Swap with this row
                        (m[j], m[k]) = (m[k], m[j])
                        (b[j], b[k]) = (b[k], b[j])
                        break

                # Increment pivot index if we could not find a row to swap with
                if m[j][pi] == 0:
                    pi += 1

                # If there is no pivots left, we're done reducing
                if pi == len(m[0]):
                    done = True
                    break

            if done:
                break

            # Divide through to have a pivot of 1
            m[j] = [ ff.FiniteFieldArray.ff_elem_div(m[j][i], m[j][pi]) for i in range(len(m[0])) ]

            # Eliminate above & below
            for k in range(len(m)):
                if k != j and m[k][pi] != 0:
                    m[k] = [ ff.FiniteFieldArray.ff_elem_sub(m[k][i], \
                      ff.FiniteFieldArray.ff_elem_mul(m[j][i], m[k][pi])) for i in range(len(m[0])) ]

            # Move onto the next pivot
            pi += 1
            # If there is no pivots left, we're done reducing
            if pi == len(m[0]):
                break

        solved = []
        used = []

        for i in range(len(m)):
            # If this row has only one non-zero entry
            reduced_coefs = [1*(m[i][j] != 0) for j in range(len(m[0]))]
            if sum(reduced_coefs) == 1:
                # Add the solution to our solved list
                solved.append(x[reduced_coefs.index(1)])
                # Add the decoded LC to our used list
                used.append(b[i])

        return (solved, used)

    def solve(self, decoded_window):
        unsolved_message_map = {}

        # Get a list of decoded messages
        decoded_messages = decoded_window.objects()

        # Make a list of undecoded linear combinations
        undecoded_lc = []
        for lc in self.live_objects():
            # If we've decoded this entire linear combination, don't add it
            if sum([p in decoded_messages for p in lc.messages]) == len(lc.messages):
                continue
            undecoded_lc.append(lc)

        # Put together a list of all decoded messages referenced by undecoded
        # linear combinations
        ref_decoded_messages = []
        for lc in undecoded_lc:
            for p in lc.messages:
                if p in decoded_messages and p not in ref_decoded_messages:
                    ref_decoded_messages.append(p)

        # Assemble x of mx=b
        #   x maps messages to column indices
        x = {}
        # Assign a col index to each referenced decoded message
        for p in ref_decoded_messages:
            x[str(p)] = len(x)
        # Assign a col index to each undecoded message
        for lc in undecoded_lc:
            for p in lc.messages:
                if str(p) not in x:
                    x[str(p)] = len(x)
                    unsolved_message_map[str(p)] = p

        # Assemble m and b of mx = b
        m = []
        b = []
        # Create a row for each solved message
        for p in ref_decoded_messages:
            r = [0] * len(x)
            r[x[str(p)]] = 1
            m.append(r)
            b.append(p)
        # Create a row for each linear combination
        for lc in undecoded_lc:
            r = [0] * len(x)
            for i in range(len(lc.messages)):
                pid = str(lc.messages[i])
                coef = lc.coefs[i]
                r[x[pid]] = coef
            m.append(r)
            b.append(lc)

        # Information about the size of this reduce attempt
        b_pids = [str(p) for p in b]
        m_numrows = len(m)
        m_numcols = len(m[0]) if m_numrows > 0 else 0

        (solved, used) = self.fast_rref(m, b, sorted(x, key=x.get))

        # Remove previously decoded objects from our solution
        for p in ref_decoded_messages:
            if str(p) in solved:
                solved.remove(str(p))
            if p in used:
                used.remove(p)

        # Map message ids to message objects in our solution
        for i in range(len(solved)):
            solved[i] = unsolved_message_map[solved[i]]

        # Information about the solution of this reduce attempt
        s_pids = [str(p) for p in solved]

        return (m_numrows, m_numcols, b_pids, s_pids, solved)

