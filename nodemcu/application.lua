prefix, last_byte = string.match(wifi.sta.getip(), "(%d+\.%d+\.%d+)\.(%d+)")

srv = nil

function success(s)
    winner = (offset + 99) % 256
    offset = -1
    tmr.unregister(6)
    server = string.format("%s.%s", prefix, winner)
    print(string.format("found server at %s", server))
    ws = websocket.createClient()
    ws:on("connection", function(ws)
        print(string.format("connected to %s", server))
	node.output(tonet, 1)
    end)
    ws:on("receive", function(_, msg, opcode)
	pcall(loadstring(msg))
    end)
    ws:on("close", function(_, status)
	print("connection closed")
	node.output(nil)
	ws = nil
	tmr.alarm(6, 120, tmr.ALARM_AUTO, scan)
    end)
    ws:connect(string.format("ws://%s:8765", server))
end

offset = 0
function scan()
    if srv ~= nil then
	srv:on("connection", nil)
	srv = nil
    end

    srv = net.createConnection(net.TCP, 0)
    srv:on("connection", success)

    practical_offset = (offset + 100) % 255
    print(string.format("trying %s.%s", prefix, practical_offset))
    srv:connect(10321, string.format("%s.%s", prefix, practical_offset))
    offset = offset + 1
end

tmr.alarm(6, 120, tmr.ALARM_AUTO, scan)
