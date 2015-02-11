local message = {}

local Message = {}
Message.__index = Message
setmetatable(Message, {__call = function(self, ...) return self.new(...) end})

function Message.new(nid, mid, name)
    local self = setmetatable({nid = nid, mid = mid, name = name}, Message)
    return self
end

function Message:__eq(other)
    return self.mid == other.mid
end

function Message:__tostring()
    return self.name
end

local DummyMessage = setmetatable({}, {__call = function(self, ...) return self.new(...) end})

function DummyMessage.new(nid)
    local mid = math.random(0, 2^32-1)
    local name = string.format("D%d-%04x", nid, mid)
    return Message.new(nid, mid, name)
end

local RealMessage = setmetatable({}, {__call = function(self, ...) return self.new(...) end})

function RealMessage.new(nid)
    local mid = math.random(0, 2^32-1)
    local name = string.format("R%d-%04x", nid, mid)
    return Message.new(nid, mid, name)
end

local EvilMessage = setmetatable({}, {__call = function(self, ...) return self.new(...) end})

function EvilMessage.new(nid)
    local mid = math.random(0, 2^32-1)
    local name = string.format("E%d-%04x", nid, mid)
    return Message.new(nid, mid, name)
end

local RLCMessage = setmetatable({}, {__call = function(self, ...) return self.new(...) end})

function RLCMessage.new(nid, messages)
    local mid = math.random(0, 2^32-1)

    local coefs = {}
    for i=1,#messages do
        coefs[i] = math.random(0, 2^8-1)
    end

    local name = string.format("LC%d-%04x", nid, mid)

    local self = Message.new(nid, mid, name)
    self.coefficients = coefs
    self.messages = messages
    return self
end

message.Message = Message
message.DummyMessage = DummyMessage
message.RealMessage = RealMessage
message.EvilMessage = EvilMessage
message.RLCMessage = RLCMessage

return message
