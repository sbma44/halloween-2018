SERVER = "192.168.10.51"
ssid, pwd, bssid_set, bssid = wifi.sta.getconfig()
if servers[ssid] ~= nil then
    SERVER = servers[ssid]
end

function connect()
    tmr.unregister(6)
    ws = websocket.createClient()
    
    ws:on("connection", function(ws)
        sec, usec, rate = rtctime.get()
        print(string.format("connected to %s at %s", SERVER, sec))
        ws:send(wifi.sta.getmac())
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
end

sntp.sync(nil, connect)
