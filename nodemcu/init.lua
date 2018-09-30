dofile("credentials.lua")

function startup()
    if file.open("init.lua") == nil then
        print("init.lua deleted or renamed")
    else
        print("Running")
        file.close("init.lua")
        -- the actual application is stored in 'application.lua'
        dofile("application.lua")
    end
end

function listap(t)
    print("got back AP list")
    found = false
    for bssid, ssid in pairs(t) do
	ssid = string.match(ssid, "([^,]+),-")
	if wifi_credentials[ssid] ~= nil then
	    print(string.format("Connecting to %s", ssid))
	    wifi.setmode(wifi.STATION)
	    sta_config = {}
	    sta_config.ssid = ssid
	    sta_config.pwd = wifi_credentials[ssid]
	    wifi.sta.config(sta_config)
	    found = true
	end
    end
    if not found then
	tmr.alarm(2, 1000, tmr.ALARM_SINGLE, function() wifi.sta.getap(1, listap) end)
    end
end

function wifi_check()
    if wifi.sta.getip() == nil then
        -- print("Waiting for IP address...")
	tmr.alarm(1, 1000, tmr.ALARM_SINGLE, wifi_check)
    else
        tmr.stop(1)
        print("WiFi connection established, IP address: " .. wifi.sta.getip())
        print("You have 2 seconds to abort")
        print("Waiting...")
        tmr.alarm(0, 2000, 0, startup)

        ws2812_effects.set_color(100,255,0)
        ws2812_effects.set_mode("static")
        ws2812_effects.start()
    end
end

ws2812.init()
strip_buffer = ws2812.newBuffer(150, 3)
ws2812_effects.init(strip_buffer)
ws2812_effects.set_color(0,0,0)
ws2812_effects.set_mode("static")
ws2812_effects.start()

wifi.sta.getap(1, listap)
tmr.alarm(1, 1000, tmr.ALARM_SINGLE, wifi_check)
