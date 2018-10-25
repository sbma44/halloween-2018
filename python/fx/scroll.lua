DELAY = 50

tmr.unregister(6)

for i=1,75,1 do
	c = color_utils.hsv2grb(255, 255, (i-1) * 3)
	strip_buffer[i] = c
	strip_buffer[151-i] = c
end

function tic()
	ws2812.write(strip_buffer)
	strip_buffer:shift(1, ws2812.SHIFT_CIRCULAR)
	tmr.alarm(6, DELAY, tmr.ALARM_SINGLE, tic)
end

tmr.alarm(6, DELAY, tmr.ALARM_SINGLE, tic)