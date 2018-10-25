DELAY = 50

tmr.unregister(6)

buf_a = ws2812.newBuffer(75, 3)
buf_b = ws2812.newBuffer(75, 3)
for i=1,75,1 do
	c = color_utils.hsv2grb(255, 255, (i-1) * 3)
	buf_a[i] = c
	buf_b[76-i] = c
end

function tic()
	ws2812.write(buf_a .. buf_b)
	buf_a:shift(-1, ws2812.SHIFT_CIRCULAR)
	buf_b:shift(1, ws2812.SHIFT_CIRCULAR)
	tmr.alarm(6, DELAY, tmr.ALARM_SINGLE, tic)
end

tmr.alarm(6, DELAY, tmr.ALARM_SINGLE, tic)