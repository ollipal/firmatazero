from .shared_board import shared_board, shared_lock

LED_BUILTIN = 13
DEFAULT_SERVO = 9


class DigitalOutputDevice:
    """
    Represents a generic pin output device.

    This class ha :meth:`on` method to switch the device on, a
    corresponding :meth:`off` method, and a :meth:`toggle` method.

    :type pin: int or str
    :param pin:
        The pin that the servo is connected to.
        If pin is not int or str :exc:`AssertionError`
        will be raised.

    :param bool active_high:
        If :data:`True` (the default), the :meth:`on` method will set the GPIO
        to HIGH. If :data:`False`, the :meth:`on` method will set the GPIO to
        LOW (the :meth:`off` method always does the opposite).

    :type initial_value: bool or None
    :param initial_value:
        If :data:`False` (the default), the device will be off initially.  If
        :data:`None`, the device will be left in whatever state the pin is
        found in when configured for output (warning: this can be on).  If
        :data:`True`, the device will be switched on initially.

    :type pin_factory: None
    :param pin_factory:
        This does not do anything, makes compatible with gpiozero code.
    """

    def __init__(
        self,
        pin=None,
        active_high=True,
        initial_value=False,
        pin_factory=None,  # Ignored
    ):

        assert isinstance(pin, (str, int))

        self._active_state = active_high
        self._pin = pin

        with shared_board() as board:
            self._board_pin = board.get_pin(f"d:{pin}:o")

        self.value = self._get_value(initial_value)

    def _get_value(self, value):
        return value if self._active_state else not value

    def on(self):
        """
        Turns the device on.
        """
        with shared_lock():
            self._board_pin.write(self._get_value(True))

    def off(self):
        """
        Turns the device off.
        """
        with shared_lock():
            self._board_pin.write(self._get_value(False))

    def toggle(self):
        """
        Reverse the state of the device. If it's on, turn it off; if it's off,
        turn it on.
        """
        with shared_lock():
            if self._get_value(self.value):
                self.off()
            else:
                self.on()

    @property
    def value(self):
        """
        Returns 1 if the device is currently active and 0 otherwise. Setting
        this property changes the state of the device.
        """
        with shared_lock():
            return self._board_pin.read()

    @value.setter
    def value(self, value):
        assert value in {True, False, 1, 0}

        with shared_lock():
            self._board_pin.write(value)

    @property
    def active_high(self):
        """
        When :data:`True`, the :attr:`value` property is :data:`True` when the
        device's :attr:`~GPIODevice.pin` is high. When :data:`False` the
        :attr:`value` property is :data:`True` when the device's pin is low
        (i.e. the value is inverted).

        This property can be set after construction; be warned that changing it
        will invert :attr:`value` (i.e. changing this property doesn't change
        the device's pin state - it just changes how that state is
        interpreted).
        """
        return self._active_state

    @active_high.setter
    def active_high(self, value):
        self._active_state = True if value else False
        self._inactive_state = False if value else True

    def __repr__(self):
        return (
            "<firmatazero.%s object on pin %r, active_high=%s, is_active=%s>"
            % (
                self.__class__.__name__,
                self.pin,
                self.active_high,
                self.is_active,
            )
        )


class LED:
    """
    Represents a light emitting diode(LED).

    Connect the cathode (short leg, flat side) of the LED to a ground pin;
    connect the anode (longer leg) to a limiting resistor; connect the other
    side of the limiting resistor to a pin (the limiting resistor can be
    placed either side of the LED).

    The following example will light the LED::

        from firmatazero import LED
        led = LED(13)
        led.on()

    :type pin: int or str
    :param pin:
        The pin which the LED is connected to.
        If pin is not int or str :exc:`AssertionError`
        will be raised.

    :type initial_value: bool or None
    :param initial_value:
        If :data:`False` (the default), the LED will be off initially.  If
        :data:`None`, the LED will be left in whatever state the pin is found
        in when configured for output (warning: this can be on).  If
        :data:`True`, the LED will be switched on initially.

    :type pin_factory: None
    :param pin_factory:
        This does not do anything, makes compatible with gpiozero code.
    """

    def __init__(
        self,
        pin=LED_BUILTIN,
        *,
        initial_value=False,
        pin_factory=None,  # Ignored
    ):
        assert isinstance(pin, (str, int))

        self._pin = pin

        with shared_board() as board:
            self._board_pin = board.get_pin(f"d:{pin}:o")

        if initial_value is True:
            self.value = initial_value

    def on(self):
        with shared_lock():
            self._board_pin.write(True)

    def off(self):
        with shared_lock():
            self._board_pin.write(False)

    def toggle(self):
        with shared_lock():
            if self.value:
                self.off()
            else:
                self.on()

    @property
    def is_lit(self):
        with shared_lock():
            return self.value

    @property
    def pin(self):
        with shared_lock():
            return self._pin

    @property
    def value(self):
        with shared_lock():
            return self._board_pin.read()

    @value.setter
    def value(self, value):
        assert value in {True, False, 1, 0}

        with shared_lock():
            self._board_pin.write(value)


class Servo:
    """
    Represents a PWM-controlled servo motor connected to a pin.

    Connect a power source (e.g. a battery pack or the 5V pin) to the power
    cable of the servo (this is typically colored red); connect the ground
    cable of the servo (typically colored black or brown) to the negative of
    your battery pack, or a pin; connect the final cable (typically colored
    white or orange) to the pin you wish to use for controlling the servo.

    The following code will make the servo move between its minimum, maximum,
    and mid-point positions with a pause between each::

        from frimatazero import Servo
        from time import sleep

        servo = Servo(9)
        while True:
            servo.min()
            sleep(1)
            servo.mid()
            sleep(1)
            servo.max()
            sleep(1)

    You can also use the :attr:`value` property to move the servo to a
    particular position, on a scale from -1 (min) to 1 (max) where 0 is the
    mid-point::

        from gpiozero import Servo

        servo = Servo(9)

        servo.value = 0.5

    :type pin: int or str
    :param pin:
        The pin that the servo is connected to.
        If pin is not int or str :exc:`AssertionError`
        will be raised.

    :param float initial_value:
        If ``0`` (the default), the device's mid-point will be set initially.
        Other values between -1 and +1 can be specified as an initial position.

    :param float min_pulse_width:
        The pulse width corresponding to the servo's minimum position. This
        defaults to 0.544ms.

    :param float max_pulse_width:
        The pulse width corresponding to the servo's maximum position. This
        defaults to 2.4ms.

    :type pin_factory: None
    :param pin_factory:
        This does not do anything, makes compatible with gpiozero code.
    """

    def __init__(
        self,
        pin=DEFAULT_SERVO,
        *,
        initial_value=0.0,
        min_pulse_width=0.544 / 1000,
        max_pulse_width=2.4 / 1000,
        # frame_width=20/1000, removed, could damage servo if ignored
        pin_factory=None,  # Ignored
    ):
        assert isinstance(pin, (str, int))
        assert isinstance(initial_value, (int, float))
        assert -1 <= initial_value <= 1
        assert isinstance(min_pulse_width, (int, float))
        assert isinstance(max_pulse_width, (int, float))

        with shared_board() as board:
            self._board_pin = board.get_pin(f"d:{pin}:s")
            board.servo_config(
                pin,
                min_pulse=int(min_pulse_width * 1000.0 * 1000.0),
                max_pulse=int(max_pulse_width * 1000.0 * 1000.0),
                angle=int(Servo._to_degrees(initial_value)),
            )

    # Remap a number from one range to another.
    # Based on Arduino's map():
    # https://www.arduino.cc/reference/en/language/functions/math/map/
    @staticmethod
    def _map(x, in_min, in_max, out_min, out_max):
        return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

    @staticmethod
    def _to_degrees(x):
        return Servo._map(x, -1, 1, 0, 180)

    @staticmethod
    def _to_value(x):
        return Servo._map(x, 0, 180, -1, 1)

    def min(self):
        """
        Set the servo to its minimum position.
        """
        with shared_lock():
            self.value = -1

    def mid(self):
        """
        Set the servo to its mid-point position.
        """
        with shared_lock():
            self.value = 0

    def max(self):
        """
        Set the servo to its maximum position.
        """
        with shared_lock():
            self.value = 1

    @property
    def value(self):
        with shared_lock():
            return Servo._to_value(self._board_pin.read())

    @value.setter
    def value(self, value):
        assert isinstance(value, (int, float))
        assert -1 <= value <= 1

        with shared_lock():
            self._board_pin.write(Servo._to_degrees(value))

    @property
    def is_active(self):
        with shared_lock():
            return True  # detach not supported yet
