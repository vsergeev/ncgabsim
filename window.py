import random
import ctypes
ctypes.cdll.LoadLibrary("./ff.so")
cff = ctypes.CDLL("./ff.so")

# Pre-compute finite field tables
cff.ff8_precompute()
# Pre-allocate ctypes matrix
Matrix = (ctypes.c_uint8 * (2048 * 2048))()
# Pre-allocate ctypes solved indices array
SolvedIndices = (ctypes.c_uint16 * (2048))()

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
        self.ttl[p.pid] = ttl
        return True

    def prune(self):
        if self.keep_expired:
            return []

        # Create a list of expired objects
        expiredList = list(filter(lambda x: self.ttl[x.pid] == 0, self.window))

        # Remove all expired objects from our window
        for e in expiredList:
            self.window.remove(e)
            del self.ttl[e.pid]

        return expiredList

    def tick(self):
        # Decrement the TTL for each object in the window
        for x in self.window:
            self.ttl[x.pid] = max(0, self.ttl[x.pid] - 1)

        return self.prune()

    def live_objects(self):
        return list(filter(lambda x: self.ttl[x.pid] > 0, self.window))

    def objects(self):
        return self.window[:]

    def __str__(self):
        s = "Window\n"
        for x in self.window:
            s += "\t" + str(x) + " TTL: " + str(self.ttl[x.pid]) + "\n"
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
        scores = [self.ttl[c.pid] for c in choices]

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
        scores = [self.ttl[c.pid] for c in choices]

        return choices[choose_weighted_random(choices, scores)]

    def solve(self, decoded_window):
        # Map of column index -> message
        col_map = {}
        # Map of pid -> column index
        pid_map = {}

        num_cols = 0

        decoded = decoded_window.objects()
        # Gather unique columns from decoded messages
        for m in decoded:
            col_map[num_cols] = m
            pid_map[m.pid] = num_cols
            num_cols += 1
        num_rows = len(decoded)
        num_decoded = num_cols

        undecoded_lc = self.live_objects()
        # Gather unique columns from linear combinations
        for lc in undecoded_lc:
            for m in lc.messages:
                if m.pid not in pid_map:
                    col_map[num_cols] = m
                    pid_map[m.pid] = num_cols
                    num_cols += 1
        num_rows += len(undecoded_lc)

        # Clear matrix and solved indices
        cff.matrix_util_clear(SolvedIndices, Matrix, num_rows, num_cols)

        row = 0
        # Build decoded rows (... 0, 0, 1, 0, 0 ... )
        for m in decoded:
            Matrix[num_cols*row + pid_map[m.pid]] = 1
            row += 1

        # Build linear combined rows ( ..., a, b, c, d, ... )
        for lc in undecoded_lc:
            for i in range(len(lc.coefs)):
                Matrix[num_cols*row + pid_map[lc.messages[i].pid]] = lc.coefs[i]
            row += 1

        # rref matrix
        num_solved = cff.matrix_solve(SolvedIndices, Matrix, num_rows, num_cols)

        # Gather newly solved messages
        solved = []
        for i in range(num_solved):
            if SolvedIndices[i] >= num_decoded:
                m = col_map[SolvedIndices[i]]
                solved.append(m)

        return (num_rows, num_cols, solved)

