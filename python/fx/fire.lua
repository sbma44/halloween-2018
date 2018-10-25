print("running fire.lua")

tmr.unregister(6)
ws2812_effects.stop()

ws2812_effects.set_speed(100)
ws2812_effects.set_brightness(50)
ws2812_effects.set_mode("fire")
ws2812_effects.start()