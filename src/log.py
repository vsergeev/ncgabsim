import json
import termcolor
import os

class Log():
    def __init__(self, simParams):
        self.elog = []
        self.simParams = simParams

    def log(self, rnd, etype, nid, msg):
        e = { 'time': rnd, 'type': etype, 'nid': nid, 'msg': msg }
        self.elog.append(e)

        if self.simParams['PRINT_LOG']:
            ejson = json.dumps(e)
            if etype == "join" or etype == "leave": print(termcolor.colored(ejson, "yellow"))
            elif etype == "receive": print(termcolor.colored(ejson, "yellow"))
            elif etype == "insert": print(termcolor.colored(ejson, "red"))
            elif etype == "reduce": print(termcolor.colored(ejson, "blue"))
            elif etype == "decode": print(termcolor.colored(ejson, "green"))
            else: print(termcolor.colored(ejson, "white"))

    def dump(self):
        i = 0
        while True:
            path = "logs/%s-%d.log" % (self.simParams['NAME'], i)
            if not os.path.exists(path):
                break
            i += 1

        f = open(path, "w")
        for e in self.elog:
            f.write(json.dumps(e) + "\n")
        f.close()

        return path

