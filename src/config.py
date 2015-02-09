import copy

simConfig = 1

# Cooperative Peer Simulation

SimTemplate = {
    'NAME':                     "",
    'DESC':                     "",

    'LOOKUP_PERCENT':           0.25,
    'CODE_SIZE':                4,
    'TTL_DECODE':               30,
    'TTL_GOSSIP':               10,

    'SIM_NUM_PEERS':            0,
    'SIM_NUM_EVIL_PEERS':       0,
    'CONTRIBUTE_INTERVAL':      0,

    'SIM_WARMUP_DECODES':       50,
    'SIM_DURATION_INSERTS':     100,

    'SEED':                     0,

    'PRINT_LOG':                False,
}

if simConfig == 1:
    NumPeersSweep = [10, 25, 50, 100]
    ContributeIntervalSweep = [7.0, 10, 12.0, 15.0, 17.0, 20.0, 22.0]
    SeedSweep = [0x1, 0x2, 0x3]
    SeedSweep = [0x1]

    SimParamsList = []
    for numPeers in NumPeersSweep:
        for contributeInterval in ContributeIntervalSweep:
            for seed in SeedSweep:
                name = "Sim-N%d-R%d-S%d" % (numPeers, contributeInterval, seed)
                params = copy.deepcopy(SimTemplate)
                params['NAME'] = name
                params['SEED'] = seed
                params['SIM_NUM_PEERS'] = numPeers
                params['CONTRIBUTE_INTERVAL'] = contributeInterval
                SimParamsList.append(params)

if simConfig == 7:
    NumPeersSweep = [25]
    ContributeIntervalSweep = [7.0, 10, 12.0, 15.0, 17.0, 20.0, 22.0]
    SeedSweep = [0x1, 0x2, 0x3]

    SimParamsList = []
    for numPeers in NumPeersSweep:
        for contributeInterval in ContributeIntervalSweep:
            for seed in SeedSweep:
                name = "SimSelect2-N%d-R%d-S%d" % (numPeers, contributeInterval, seed)
                params = copy.deepcopy(SimTemplate)
                params['NAME'] = name
                params['SEED'] = seed
                #params['SELECTION'] = 'Uniform'
                params['SELECTION'] = 'Weighted'
                params['SIM_NUM_PEERS'] = numPeers
                params['CONTRIBUTE_INTERVAL'] = contributeInterval
                SimParamsList.append(params)

################################################################################

# Evil Peer Simulations

SimTemplate = {
    'NAME':                     "Evil-Base",
    'DESC':                     "",

    'LOOKUP_PERCENT':           0.25,
    'CODE_SIZE':                4,
    'TTL_DECODE':               30,
    'TTL_GOSSIP':               20,

    'SIM_NUM_PEERS':            0,
    'SIM_NUM_EVIL_PEERS':       0,
    'CONTRIBUTE_INTERVAL':      20,

    'SIM_EVIL_PEER_TYPE':       "",

    'SIM_WARMUP_DECODES':       50,
    'SIM_DURATION_INSERTS':     75,

    'PRINT_LOG':                False,
}

# Inactive, Underdetermined Gossip
if simConfig == 2:
    EvilPeerTypeSweep = ["inactive", "underdetermined"]
    NumPeersSweep = [10, 20, 30]
    pNumEvilPeersSweep = [0.0, 0.10, 0.20, 0.30]
    SeedSweep = [0x1, 0x2, 0x3]

    SimParamsList = []
    for evilPeerType in EvilPeerTypeSweep:
        for numPeers in NumPeersSweep:
            for pNumEvilPeers in pNumEvilPeersSweep:
                for seed in SeedSweep:
                    name = "Evil-%s-N%d-E%0.2f-S%d" % (evilPeerType, numPeers, pNumEvilPeers, seed)
                    params = copy.deepcopy(SimTemplate)
                    params['NAME'] = name
                    params['SEED'] = seed
                    params['SIM_NUM_PEERS'] = numPeers
                    params['SIM_NUM_EVIL_PEERS'] = int(pNumEvilPeers * params['SIM_NUM_PEERS'])
                    params['SIM_EVIL_PEER_TYPE'] = evilPeerType
                    SimParamsList.append(params)

# Decodable with CODE_SIZE = 4
if simConfig == 3:
    EvilPeerTypeSweep = ["decodable"]
    NumPeersSweep = [25]
    pNumEvilPeersSweep = [0.0, 0.10, 0.20, 0.30]
    SeedSweep = [0x1, 0x2, 0x3]

    SimParamsList = []
    for evilPeerType in EvilPeerTypeSweep:
        for numPeers in NumPeersSweep:
            for pNumEvilPeers in pNumEvilPeersSweep:
                for seed in SeedSweep:
                    name = "Evil-%s-CS4-N%d-E%0.2f-S%d" % (evilPeerType, numPeers, pNumEvilPeers, seed)
                    params = copy.deepcopy(SimTemplate)
                    params['NAME'] = name
                    params['SEED'] = seed
                    params['SIM_NUM_PEERS'] = numPeers
                    params['SIM_NUM_EVIL_PEERS'] = int(pNumEvilPeers * params['SIM_NUM_PEERS'])
                    params['SIM_EVIL_PEER_TYPE'] = evilPeerType
                    params['CODE_SIZE'] = 4
                    SimParamsList.append(params)

# Decodable with CODE_SIZE = 6
if simConfig == 4:
    EvilPeerTypeSweep = ["decodable"]
    NumPeersSweep = [25]
    pNumEvilPeersSweep = [0.0, 0.10, 0.20, 0.30]
    SeedSweep = [0x1, 0x2, 0x3]

    SimParamsList = []
    for evilPeerType in EvilPeerTypeSweep:
        for numPeers in NumPeersSweep:
            for pNumEvilPeers in pNumEvilPeersSweep:
                for seed in SeedSweep:
                    name = "Evil-%s-CS6-N%d-E%0.2f-S%d" % (evilPeerType, numPeers, pNumEvilPeers, seed)
                    params = copy.deepcopy(SimTemplate)
                    params['NAME'] = name
                    params['SEED'] = seed
                    params['SIM_NUM_PEERS'] = numPeers
                    params['SIM_NUM_EVIL_PEERS'] = int(pNumEvilPeers * params['SIM_NUM_PEERS'])
                    params['SIM_EVIL_PEER_TYPE'] = evilPeerType
                    params['CODE_SIZE'] = 6
                    SimParamsList.append(params)

# Decodable with CODE_SIZE = 10
if simConfig == 5:
    EvilPeerTypeSweep = ["decodable"]
    NumPeersSweep = [25]
    pNumEvilPeersSweep = [0.0, 0.10, 0.20, 0.30]
    SeedSweep = [0x1, 0x2, 0x3]

    SimParamsList = []
    for evilPeerType in EvilPeerTypeSweep:
        for numPeers in NumPeersSweep:
            for pNumEvilPeers in pNumEvilPeersSweep:
                for seed in SeedSweep:
                    name = "Evil-%s-CS10-N%d-E%0.2f-S%d" % (evilPeerType, numPeers, pNumEvilPeers, seed)
                    params = copy.deepcopy(SimTemplate)
                    params['NAME'] = name
                    params['SEED'] = seed
                    params['SIM_NUM_PEERS'] = numPeers
                    params['SIM_NUM_EVIL_PEERS'] = int(pNumEvilPeers * params['SIM_NUM_PEERS'])
                    params['SIM_EVIL_PEER_TYPE'] = evilPeerType
                    params['CODE_SIZE'] = 10
                    SimParamsList.append(params)


# Colluded Decodable with CODE_SIZE = 8
if simConfig == 6:
    EvilPeerTypeSweep = ["colluded"]
    NumPeersSweep = [20]
    pNumEvilPeersSweep = [0.0, 0.10, 0.20, 0.30]
    SeedSweep = [0x1, 0x2, 0x3]

    SimParamsList = []
    for evilPeerType in EvilPeerTypeSweep:
        for numPeers in NumPeersSweep:
            for pNumEvilPeers in pNumEvilPeersSweep:
                for seed in SeedSweep:
                    name = "Evil-%s-CS6-N%d-E%0.2f-S%d" % (evilPeerType, numPeers, pNumEvilPeers, seed)
                    params = copy.deepcopy(SimTemplate)
                    params['NAME'] = name
                    params['SEED'] = seed
                    params['SIM_NUM_PEERS'] = numPeers
                    params['SIM_NUM_EVIL_PEERS'] = int(pNumEvilPeers * params['SIM_NUM_PEERS'])
                    params['SIM_EVIL_PEER_TYPE'] = evilPeerType
                    params['CODE_SIZE'] = 8
                    SimParamsList.append(params)

