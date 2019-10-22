print("running scroll_middle.lua")

tmr.unregister(6)
ws2812_effects.stop()

DELAY = 50

buf_a = ws2812.newBuffer(75, 3)
buf_b = ws2812.newBuffer(75, 3)
for j = 1, 75 do
    input_b = (j - 1)
    g, r, b = color_utils.hsv2grb({{stable_h}}, 255, input_b)
    buf_a:set(j, g, r, b)
    buf_b:set(76-j, g, r, b)
end

function tic()
    ws2812.write(buf_a .. buf_b)
    buf_a:shift(-2, ws2812.SHIFT_CIRCULAR)
    buf_b:shift(2, ws2812.SHIFT_CIRCULAR)
end

tmr.alarm(6, DELAY, tmr.ALARM_AUTO, tic)
