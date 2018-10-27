print("running diamond.lua")

tmr.unregister(6)
ws2812_effects.stop()

DELAY = 50
BAND_WIDTH = 15

--g, r, b = color_utils.colorWheel({{stable_h}})
g, r, b = color_utils.hsv2grb({{stable_h}}, 255, 25)
count = 0

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

function tic()
    ws2812.write(buf_a .. buf_b)
    buf_a:shift(-1)
    buf_b:shift(1)
    if count % (BAND_WIDTH * 2) < BAND_WIDTH then
        buf_a:set(75, g, r, b)
	buf_b:set(1, g, r, b)
    else
        buf_a:set(75, 0, 0, 0)
	buf_b:set(1, 0, 0, 0)
    end
    count = count + 1
end

strip_buffer:fill(0, 0, 0)
ws2812.write(strip_buffer)

function start()
	print("starting main loop")
	tmr.alarm(6, DELAY, tmr.ALARM_AUTO, tic)
end

sec, usec, rate = rtctime.get()
print({{wait_until}} - sec)
tmr.alarm(6, 1000 * ({{wait_until}} - sec), tmr.ALARM_SINGLE, start)
