print("running halloween.lua")

tmr.unregister(6)
ws2812_effects.stop()

ws2812_effects.set_speed(100)
ws2812_effects.set_brightness(50)
ws2812_effects.set_mode("halloween")
ws2812_effects.start()