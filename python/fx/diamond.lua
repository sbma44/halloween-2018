print("running diamond.lua")

tmr.unregister(6)
ws2812_effects.stop()

DELAY = 200
BAND_WIDTH = 15

g, r, b = color_utils.colorWheel({{h}})

buf_a = ws2812.newBuffer(75, 3)
buf_b = ws2812.newBuffer(75, 3)
for j = 1, 75, 1 do
    if (j % (BAND_WIDTH * 2)) < BAND_WIDTH then
    	buf_a:set(j, g, r, b)
    	buf_b:set(76-j, g, r, b)
    else
    	buf_a:set(j, 0, 0, 0)
    	buf_b:set(76-j, 0, 0, 0)
    end
end

if {{offset}} > 0 and {{offset}} < 5 then
	buf_a:shift(-1 * BAND_WIDTH, ws2812.SHIFT_CIRCULAR)
    buf_b:shift(BAND_WIDTH, ws2812.SHIFT_CIRCULAR)
end

if {{offset}} > 1 and {{offset}} < 4 then
	buf_a:shift(-1 * BAND_WIDTH, ws2812.SHIFT_CIRCULAR)
    buf_b:shift(BAND_WIDTH, ws2812.SHIFT_CIRCULAR)
end

function tic()
    ws2812.write(buf_a .. buf_b)
    buf_a:shift(-1, ws2812.SHIFT_CIRCULAR)
    buf_b:shift(1, ws2812.SHIFT_CIRCULAR)
end

strip_buffer:fill(0, 0, 0)
ws2812.write(strip_buffer)

function start()
	print("starting diamond effect")
	tmr.alarm(6, DELAY, tmr.ALARM_AUTO, tic)
end

sec, usec, rate = rtctime.get()
print({{wait_until}} - sec)
tmr.alarm(6, 1000 * ({{wait_until}} - sec), tmr.ALARM_SINGLE, start)