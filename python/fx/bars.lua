print("running bars.lua")

CYCLE = 1000

tmr.unregister(6)
ws2812_effects.stop()

strip_buffer:fill(0, 0, 0)
ws2812.write(strip_buffer)

function loop_a()
    g, r, b = color_utils.colorWheel({{stable_h}})
    strip_buffer:fill(g, r, b)
    ws2812.write(strip_buffer)
    tmr.alarm(6, CYCLE / 6, tmr.ALARM_SINGLE, loop_b)
    strip_buffer:fill(0, 0, 0)
end

function loop_b()
    ws2812.write(strip_buffer)
    tmr.alarm(6, 5 * (CYCLE / 6), tmr.ALARM_SINGLE, loop_a)
end

function start()
    print("starting main loop")
    ws2812.write(strip_buffer)
    tmr.alarm(6, ({{offset}} * (CYCLE / 6)) + 5000, tmr.ALARM_SINGLE, loop_a)
end

sec, usec, rate = rtctime.get()
tmr.alarm(6, (1000 * ({{wait_until}} - sec)), tmr.ALARM_SINGLE, start)
g, r, b = color_utils.colorWheel(30)
strip_buffer:fill(g, r, b)
