import random

class Message():
    def __init__(self, name, pid):
        self.name = name
        self.pid = pid

    def __str__(self):
        return self.name

    def __eq__(self, other):
        if (self.name == other.name):
            return True
        return False

class DummyMessage(Message):
    def __init__(self):
        pid = random.getrandbits(32)
        Message.__init__(self, "R%04x" % pid, pid)

class RealMessage(Message):
    def __init__(self, nid):
        pid = random.getrandbits(32)
        Message.__init__(self, "M%d/%04x" % (nid, pid), pid)

class EvilMessage(Message):
    def __init__(self, nid):
        pid = random.getrandbits(32)
        Message.__init__(self, "E%d/%04x" % (nid, pid), pid)

class RLC(Message):
    def __init__(self, messages):
        coefs = [random.randint(0, 255) for p in messages]
        pid = random.getrandbits(32)
        name = "LC/(" + ",".join([p.name for p in messages]) + ")" + "/(" + \
                       ",".join(["%02x" % c for c in coefs]) + ")"
        Message.__init__(self, name, pid)
        self.messages = messages
        self.coefs = coefs

