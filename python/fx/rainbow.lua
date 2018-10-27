print("running rainbow.lua")


function start()
    tmr.unregister(6)
    ws2812_effects.stop()

    print("starting main loop")
    ws2812_effects.set_speed(255)
    ws2812_effects.set_brightness(100)
    ws2812_effects.set_color(g, r, b)
    ws2812_effects.set_mode("rainbow_cycle", 2)
    ws2812_effects.set_mode("cycle", -3)
    ws2812_effects.start()
end

sec, usec, rate = rtctime.get()
print({{wait_until}} - sec)
tmr.alarm(6, 1000 * ({{wait_until}} - sec), tmr.ALARM_SINGLE, start)
