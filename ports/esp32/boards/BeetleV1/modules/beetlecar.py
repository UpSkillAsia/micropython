import time
from machine import Pin, I2C
from machine import time_pulse_us
from machine import PWM
import machine

from time import sleep_us
from time import sleep
from time import sleep_ms
import utime

from neopixel import NeoPixel
from micropython import const
import framebuf
import os









#button state
buttonA_pin = 18
buttonB_pin = 5
button_a = Pin(buttonA_pin, Pin.IN, Pin.PULL_UP)
button_b = Pin(buttonB_pin, Pin.IN, Pin.PULL_UP)
toggle_state_a = False
toggle_state_b = False

def toggle_pin_a():
  global toggle_state_a
  toggle_state_a = not toggle_state_a

def toggle_interrupt_handler_a(pin_a):
  if pin_a.value() == 0:
    toggle_pin_a()

button_a.irq(trigger=Pin.IRQ_FALLING, handler=toggle_interrupt_handler_a)

def toggle_pin_b():
    global toggle_state_b
    toggle_state_b = not toggle_state_b

def toggle_interrupt_handler_b(pin_b):
    if pin_b.value() == 0:
        toggle_pin_b()

button_b.irq(trigger=Pin.IRQ_FALLING, handler=toggle_interrupt_handler_b)

def put_button_a():
    return button_a.value() == 1
def put_button_b():
    return button_b.value() == 1
#button end
#Ultrasonic state
ULTRASONIC_TRIGGER_PIN = 2
ULTRASONIC_ECHO_PIN = 15

def distance():
    return read(ULTRASONIC_TRIGGER_PIN, ULTRASONIC_ECHO_PIN)

def read(trig_pin, echo_pin):
    trigger = Pin(trig_pin, mode=Pin.OUT)
    echo = Pin(echo_pin, mode=Pin.IN)
    trigger.value(0)
    sleep_us(5)
    trigger.value(1)
    sleep_us(10)
    trigger.value(0)


    try:
        pulse_time = time_pulse_us(echo, 1, 1000000)
        d = (pulse_time / 2) / 29.1
        return int(d) if d < 400 else -1
    except OSError as ex:
        return -1
#Ultrasonic End
#LED state

def led_left_on():
    return Pin(33, Pin.OUT).value(1)
def led_left_off():
    return Pin(33, Pin.OUT).value(0)
def led_right_on():
    return Pin(12, Pin.OUT).value(1)
def led_right_off():
    return Pin(12, Pin.OUT).value(0)
#LED end

#NEO state
NEO_PIN = 4
NEO_COUNT = 2
np = NeoPixel(Pin(4, Pin.OUT), 2)

np_toggle = False

def neo_on():
    return np.write()


def rainbow_neo():
  for j in range(256):
        for i in range(np.n):
            WheelPos = (i * 1 + j) % 256
            if WheelPos < 85:
                np[i] = (int(WheelPos * 3), int(255 - WheelPos * 3), 0)
            elif WheelPos < 170:
                WheelPos -= 85
                np[i] = (int(255 - WheelPos * 3), 0, int(WheelPos * 3))
            else:
                WheelPos -= 170
                np[i] = (0, int(WheelPos * 3), int(255 - WheelPos * 3))
        np.write()
        sleep_ms(5)
#NEO END
#BUZZER STATE
def buzzerWrite(pin, freq=1000, duty=50, stop=0):
  pwm = PWM(Pin(pin))
  pwm.freq(freq)
  pwm.duty(int(duty / 100 * 1023))
  if stop > 0:
    sleep(stop)
    pwm.duty(0)
#BUZZER END
    
# register definitions
SET_CONTRAST = const(0x81)
SET_ENTIRE_ON = const(0xA4)
SET_NORM_INV = const(0xA6)
SET_DISP = const(0xAE)
SET_MEM_ADDR = const(0x20)
SET_COL_ADDR = const(0x21)
SET_PAGE_ADDR = const(0x22)
SET_DISP_START_LINE = const(0x40)
SET_SEG_REMAP = const(0xA0)
SET_MUX_RATIO = const(0xA8)
SET_COM_OUT_DIR = const(0xC0)
SET_DISP_OFFSET = const(0xD3)
SET_COM_PIN_CFG = const(0xDA)
SET_DISP_CLK_DIV = const(0xD5)
SET_PRECHARGE = const(0xD9)
SET_VCOM_DESEL = const(0xDB)
SET_CHARGE_PUMP = const(0x8D)

class SSD1306(framebuf.FrameBuffer):
    def __init__(self, width, height, external_vcc):
        self.width = width
        self.height = height
        self.external_vcc = external_vcc
        self.pages = self.height // 8
        self.buffer = bytearray(self.pages * self.width)
        super().__init__(self.buffer, self.width, self.height, framebuf.MONO_VLSB)
        self.init_display()

    def init_display(self):
        for cmd in (
            SET_DISP | 0x00,  # off
            # address setting
            SET_MEM_ADDR,
            0x00,  # horizontal
            # resolution and layout
            SET_DISP_START_LINE | 0x00,
            SET_SEG_REMAP | 0x01,  # column addr 127 mapped to SEG0
            SET_MUX_RATIO,
            self.height - 1,
            SET_COM_OUT_DIR | 0x08,  # scan from COM[N] to COM0
            SET_DISP_OFFSET,
            0x00,
            SET_COM_PIN_CFG,
            0x02 if self.width > 2 * self.height else 0x12,
            # timing and driving scheme
            SET_DISP_CLK_DIV,
            0x80,
            SET_PRECHARGE,
            0x22 if self.external_vcc else 0xF1,
            SET_VCOM_DESEL,
            0x30,  # 0.83*Vcc
            # display
            SET_CONTRAST,
            0xFF,  # maximum
            SET_ENTIRE_ON,  # output follows RAM contents
            SET_NORM_INV,  # not inverted
            # charge pump
            SET_CHARGE_PUMP,
            0x10 if self.external_vcc else 0x14,
            SET_DISP | 0x01,
        ):  # on
            self.write_cmd(cmd)
        self.fill(0)
        self.show()

    def poweroff(self):
        self.write_cmd(SET_DISP | 0x00)

    def poweron(self):
        self.write_cmd(SET_DISP | 0x01)

    def contrast(self, contrast):
        self.write_cmd(SET_CONTRAST)
        self.write_cmd(contrast)

    def invert(self, invert):
        self.write_cmd(SET_NORM_INV | (invert & 1))

    def show(self):
        x0 = 0
        x1 = self.width - 1
        if self.width == 64:
            # displays with width of 64 pixels are shifted by 32
            x0 += 32
            x1 += 32
        self.write_cmd(SET_COL_ADDR)
        self.write_cmd(x0)
        self.write_cmd(x1)
        self.write_cmd(SET_PAGE_ADDR)
        self.write_cmd(0)
        self.write_cmd(self.pages - 1)
        self.write_data(self.buffer)


class SSD1306_I2C(SSD1306):
    def __init__(self, width, height, addr=0x3C, external_vcc=False):
        machine = os.uname().machine
        if ("KidBright32" in machine) or ("KidMotor V4" in machine):
            self.i2c = I2C(1, scl=Pin(5), sda=Pin(4), freq=400000)
        elif ("Mbits" in machine) or ("OpenBIT" in machine):
            self.i2c = I2C(0, scl=Pin(21), sda=Pin(22), freq=400000)
        else:
            self.i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
        self.addr = addr
        self.temp = bytearray(2)
        self.write_list = [b"\x40", None]  # Co=0, D/C#=1
        super().__init__(width, height, external_vcc)

    def write_cmd(self, cmd):
        self.temp[0] = 0x80  # Co=1, D/C#=0
        self.temp[1] = cmd
        self.i2c.writeto(self.addr, self.temp)

    def write_data(self, buf):
        self.write_list[1] = buf
        self.i2c.writevto(self.addr, self.write_list)
#MOTOR STATE


RMOTOR1 = Pin(25, Pin.OUT)
LMOTOR1 = Pin(27, Pin.OUT)
RMOTOR2 = Pin(26, Pin.OUT)
LMOTOR2 = Pin(14, Pin.OUT)

RMOTOR1_PWM = PWM(Pin(25), freq=50000)
LMOTOR1_PWM = PWM(Pin(27), freq=50000)
RMOTOR2_PWM = PWM(Pin(26), freq=50000)
LMOTOR2_PWM = PWM(Pin(14), freq=50000)

def forward(speed):
  RMOTOR1.on()
  RMOTOR1_PWM.duty(int(speed))
  LMOTOR1.on()
  LMOTOR1_PWM.duty(int(speed))
  RMOTOR2.off()
  RMOTOR2_PWM.duty(int(0))
  LMOTOR2.off()
  LMOTOR2_PWM.duty(int(0))

def stop():
  RMOTOR1.off()
  RMOTOR1_PWM.duty(int(0))
  LMOTOR1.off()
  LMOTOR1_PWM.duty(int(0))
  RMOTOR2.off()
  RMOTOR2_PWM.duty(int(0))
  LMOTOR2.off()
  LMOTOR2_PWM.duty(int(0))

def forward_for_sec(speed, duration):
  RMOTOR1.on()
  RMOTOR1_PWM.duty(int(speed))
  LMOTOR1.on()
  LMOTOR1_PWM.duty(int(speed))
  RMOTOR2.off()
  RMOTOR2_PWM.duty(int(0))
  LMOTOR2.off()
  LMOTOR2_PWM.duty(int(0))
  time.sleep(duration)
  stop()

def backward(speed):
  RMOTOR1.off()
  RMOTOR1_PWM.duty(int(0))
  LMOTOR1.off()
  LMOTOR1_PWM.duty(int(0))
  RMOTOR2.on()
  RMOTOR2_PWM.duty(int(speed))
  LMOTOR2.on()
  LMOTOR2_PWM.duty(int(speed))


def backward_for_sec(speed, duration):
  RMOTOR1.off()
  RMOTOR1_PWM.duty(int(0))
  LMOTOR1.off()
  LMOTOR1_PWM.duty(int(0))
  RMOTOR2.on()
  RMOTOR2_PWM.duty(int(speed))
  LMOTOR2.on()
  LMOTOR2_PWM.duty(int(speed))
  time.sleep(duration)
  stop()

def left(speed):
  RMOTOR1.on()
  RMOTOR1_PWM.duty(int(speed))
  LMOTOR1.off()
  LMOTOR1_PWM.duty(int(0))
  RMOTOR2.off()
  RMOTOR2_PWM.duty(int(0))
  LMOTOR2.on()
  LMOTOR2_PWM.duty(int(speed))

def left_for_sec(speed, duration):
  RMOTOR1.on()
  RMOTOR1_PWM.duty(int(speed))
  LMOTOR1.off()
  LMOTOR1_PWM.duty(int(0))
  RMOTOR2.off()
  RMOTOR2_PWM.duty(int(0))
  LMOTOR2.on()
  LMOTOR2_PWM.duty(int(speed))
  time.sleep(duration)
  stop()

def right(speed):
  RMOTOR1.off()
  RMOTOR1_PWM.duty(int(0))
  LMOTOR1.on()
  LMOTOR1_PWM.duty(int(speed))
  RMOTOR2.on()
  RMOTOR2_PWM.duty(int(speed))
  LMOTOR2.off()
  LMOTOR2_PWM.duty(int(0))

def right_for_sec(speed, duration):
  RMOTOR1.off()
  RMOTOR1_PWM.duty(int(0))
  LMOTOR1.on()
  LMOTOR1_PWM.duty(int(speed))
  RMOTOR2.on()
  RMOTOR2_PWM.duty(int(speed))
  LMOTOR2.off()
  LMOTOR2_PWM.duty(int(0))
  time.sleep(duration)
  stop()

#END STATE MOTOR
scale5 = [523 , 554 , 587 ,622 , 659 , 698 ,739 , 783 , 830 , 880 , 932 , 987 , 1046 , 0]

happy_birthday = [0 , 0 , 2 , 0 ,5 ,4 ,13, 0 ,0 , 2 ,0 ,7 ,5 ,13, 0 ,12 ,0 ,0 ,9 , 5 , 4 ,2, 13 , 9 , 9 , 9, 5 , 7 ,5]

darth_vader = [9, 9, 9, 5, 12, 9, 5, 12, 9]

jingle_bell = [4,4,4,13,4,4,4,13,4,7,0,2,4,13,5,5,5,13,5,5,5,13,5,4,4,4,4,13,4,2,2,4,2,7]

mary_little_lamb = [4,2,0,2,4,4,4,13,2,2,2,13,4,7,7,13,4,2,0,2,4,4,4,13,0,2,2,4,2,0]

twinkle_twinkle = [0, 0, 6, 6, 9, 9, 6, 13, 5, 5, 4, 4, 2, 2, 0, 13, 6, 6, 5, 5, 4, 4, 2, 13, 6, 6, 5, 5, 4, 4, 2, 13, 0, 0, 6, 6, 9, 9, 6, 13, 5, 5, 4, 4, 2, 2, 0]

bitsy_spider = [9, 0, 0, 2, 4, 4, 13, 4, 2, 0, 2, 4, 2, 13, 4, 4, 5, 7, 13, 7, 5, 4, 5, 7, 4, 0, 0, 2, 4, 13, 4, 2, 0, 2, 4, 0, 13, 7, 7, 0, 0, 0, 2, 4, 4, 13, 4, 2, 0, 2, 4, 0]

class SSD1306(framebuf.FrameBuffer):
    def __init__(self, width, height, external_vcc):
        self.width = width
        self.height = height
        self.external_vcc = external_vcc
        self.pages = self.height // 8
        self.buffer = bytearray(self.pages * self.width)
        super().__init__(self.buffer, self.width, self.height, framebuf.MONO_VLSB)
        self.init_display()

    def init_display(self):
        for cmd in (
            SET_DISP | 0x00,  # off
            # address setting
            SET_MEM_ADDR,
            0x00,  # horizontal
            # resolution and layout
            SET_DISP_START_LINE | 0x00,
            SET_SEG_REMAP | 0x01,  # column addr 127 mapped to SEG0
            SET_MUX_RATIO,
            self.height - 1,
            SET_COM_OUT_DIR | 0x08,  # scan from COM[N] to COM0
            SET_DISP_OFFSET,
            0x00,
            SET_COM_PIN_CFG,
            0x02 if self.width > 2 * self.height else 0x12,
            # timing and driving scheme
            SET_DISP_CLK_DIV,
            0x80,
            SET_PRECHARGE,
            0x22 if self.external_vcc else 0xF1,
            SET_VCOM_DESEL,
            0x30,  # 0.83*Vcc
            # display
            SET_CONTRAST,
            0xFF,  # maximum
            SET_ENTIRE_ON,  # output follows RAM contents
            SET_NORM_INV,  # not inverted
            # charge pump
            SET_CHARGE_PUMP,
            0x10 if self.external_vcc else 0x14,
            SET_DISP | 0x01,
        ):  # on
            self.write_cmd(cmd)
        self.fill(0)
        self.show()

    def poweroff(self):
        self.write_cmd(SET_DISP | 0x00)

    def poweron(self):
        self.write_cmd(SET_DISP | 0x01)

    def contrast(self, contrast):
        self.write_cmd(SET_CONTRAST)
        self.write_cmd(contrast)

    def invert(self, invert):
        self.write_cmd(SET_NORM_INV | (invert & 1))

    def show(self):
        x0 = 0
        x1 = self.width - 1
        if self.width == 64:
            # displays with width of 64 pixels are shifted by 32
            x0 += 32
            x1 += 32
        self.write_cmd(SET_COL_ADDR)
        self.write_cmd(x0)
        self.write_cmd(x1)
        self.write_cmd(SET_PAGE_ADDR)
        self.write_cmd(0)
        self.write_cmd(self.pages - 1)
        self.write_data(self.buffer)


class SSD1306_I2C(SSD1306):
    def __init__(self, width, height, addr=0x3C, external_vcc=False):
        machine = os.uname().machine
        if ("KidBright32" in machine) or ("KidMotor V4" in machine):
            self.i2c = I2C(1, scl=Pin(5), sda=Pin(4), freq=400000)
        elif ("Mbits" in machine) or ("OpenBIT" in machine):
            self.i2c = I2C(0, scl=Pin(21), sda=Pin(22), freq=400000)
        else:
            self.i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
        self.addr = addr
        self.temp = bytearray(2)
        self.write_list = [b"\x40", None]  # Co=0, D/C#=1
        super().__init__(width, height, external_vcc)

    def write_cmd(self, cmd):
        self.temp[0] = 0x80  # Co=1, D/C#=0
        self.temp[1] = cmd
        self.i2c.writeto(self.addr, self.temp)

    def write_data(self, buf):
        self.write_list[1] = buf
        self.i2c.writevto(self.addr, self.write_list)
        
#END STATE OLED


