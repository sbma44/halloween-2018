SERVER = "10.1.1.2"

function connect()
    tmr.unregister(6)
    ws = websocket.createClient()
    
    ws:on("connection", function(ws)
        print(string.format("connected to %s", server))
    end)
    
    ws:on("receive", function(_, msg, opcode)
	   print("received payload")
       pcall(loadstring(msg))
    end)
    
    ws:on("close", function(_, status)
	   print("connection closed")
	   ws = nil
	   tmr.alarm(6, 1000, tmr.ALARM_SINGLE, connect)
    end)

    print(string.format("connecting to %s:8765", SERVER))
    ws:connect(string.format("ws://%s:8765", SERVER))
    ws:send(wifi.sta.getmac())
end

sntp.sync()
sec, usec, rate = rtctime.get()
print(string.format("finished NTP sync, current time is %d", sec))

tmr.alarm(6, 0, tmr.ALARM_SINGLE, connect)