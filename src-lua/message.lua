local message = {}

local Message = {}
Message.__index = Message
setmetatable(Message, {__call = function(self, ...) return self.new(...) end})

function Message.new(id, name)
    local self = setmetatable({id = id, name = name}, Message)
    return self
end

function Message:__eq(other)
    return self.id == other.id
end

function Message:__tostring()
    return self.name
end

local DummyMessage = setmetatable({}, {__call = function(self, ...) return self.new(...) end})

function DummyMessage.new(nid)
    local id = math.random(0, 2^32-1)
    local name = string.format("D%d-%04x", nid, id)
    return Message.new(id, name)
end

local RealMessage = setmetatable({}, {__call = function(self, ...) return self.new(...) end})

function RealMessage.new(nid)
    local id = math.random(0, 2^32-1)
    local name = string.format("R%d-%04x", nid, id)
    return Message.new(id, name)
end

local EvilMessage = setmetatable({}, {__call = function(self, ...) return self.new(...) end})

function EvilMessage.new(nid)
    local id = math.random(0, 2^32-1)
    local name = string.format("E%d-%04x", nid, id)
    return Message.new(id, name)
end

message.Message = Message
message.DummyMessage = DummyMessage
message.RealMessage = RealMessage
message.EvilMessage = EvilMessage

return message
