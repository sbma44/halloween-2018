print("running scroll.lua")

tmr.unregister(6)
ws2812_effects.stop()
DELAY = 25
strip_buffer:fill(0,0,0)
for j=1,70 do
    input_b = (j - 1) * 2
    g, r, b = color_utils.hsv2grb(0, 255, input_b)
    strip_buffer:set(j, g, r, b)
    strip_buffer:set(141-j, g, r, b)
end

strip_buffer:shift({{offset}} * 15, ws2812.SHIFT_CIRCULAR)

function tic()
    ws2812.write(strip_buffer)
    strip_buffer:shift(2, ws2812.SHIFT_CIRCULAR)
end

function start()
    print("starting scroll effect")
    tmr.alarm(6, DELAY, tmr.ALARM_AUTO, tic)
end

sec, usec, rate = rtctime.get()
print({{wait_until}} - sec)
tmr.alarm(6, 1000 * ({{wait_until}} - sec), tmr.ALARM_SINGLE, start)
