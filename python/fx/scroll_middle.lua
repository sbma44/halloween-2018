print("running scroll_middle.lua")

tmr.unregister(6)
ws2812_effects.stop()

DELAY = 50

buf_a = ws2812.newBuffer(75, 3)
buf_b = ws2812.newBuffer(75, 3)
for i=1,75,1 do
	g, r, b = color_utils.hsv2grb(255, 255, (i-1) * 3)
	buf_a:set(i, g, r, b)
	buf_b:set(76-i, g, r, b)
end

function tic()
	ws2812.write(buf_a .. buf_b)
	buf_a:shift(-1, ws2812.SHIFT_CIRCULAR)
	buf_b:shift(1, ws2812.SHIFT_CIRCULAR)
	tmr.alarm(6, DELAY, tmr.ALARM_SINGLE, tic)
end

tmr.alarm(6, DELAY, tmr.ALARM_SINGLE, tic)
