from time import sleep

from firmatazero import DigitalOutputDevice

relay = DigitalOutputDevice(7, active_high=False, initial_value=True)
relay.on()
sleep(1)
relay.off()
sleep(1)
