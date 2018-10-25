print("running scroll.lua")

tmr.unregister(6)
ws2812_effects.stop()
DELAY = 200
for j=1,75 do
    input_b = (j - 1) * 3
    g, r, b = color_utils.hsv2grb(0, 255, input_b)
    strip_buffer:set(j, g, r, b)
    strip_buffer:set(151-j, g, r, b)
end

function tic()
    ws2812.write(strip_buffer)
    strip_buffer:shift(1, ws2812.SHIFT_CIRCULAR)
end

tmr.alarm(6, DELAY, tmr.ALARM_AUTO, tic)
