from machine import Pin
from machine import Timer
from time import sleep_ms
import bluetooth
from neopixel import NeoPixel

ble_msg = ""
is_ble_connected = False
has_sent_hello = False
class ESP32_BLE():
    def __init__(self, name):
        # Create internal objects for the onboard LED
        # blinking when no BLE device is connected
        # stable ON when connected
        self.led = Pin(12, Pin.OUT)
        self.timer1 = Timer(0)
        
        self.name = name
        self.ble = bluetooth.BLE()
        self.ble.active(True)
        self.disconnected()
        self.ble.irq(self.ble_irq)
        self.register()
        self.advertiser()

    def connected(self):
        global is_ble_connected
        is_ble_connected = True
        self.led.value(1)
        self.timer1.deinit()

    def disconnected(self):
        global is_ble_connected
        global has_sent_hello
        is_ble_connected = False
        has_sent_hello = False     
        self.timer1.init(period=100, mode=Timer.PERIODIC, callback=lambda t: self.led.value(not self.led.value()))

    def ble_irq(self, event, data):
        global ble_msg
        
        if event == 1: #_IRQ_CENTRAL_CONNECT:
                       # A central has connected to this peripheral
            self.connected()

        elif event == 2: #_IRQ_CENTRAL_DISCONNECT:
                         # A central has disconnected from this peripheral.
            self.advertiser()
            self.disconnected()
        
        elif event == 3: #_IRQ_GATTS_WRITE:
                         # A client has written to this characteristic or descriptor.          
            buffer = self.ble.gatts_read(self.rx)
            ble_msg = buffer.decode('UTF-8').strip()
            
    def register(self):        
        # Nordic UART Service (NUS)
        NUS_UUID = '6E400001-B5A3-F393-E0A9-E50E24DCCA9E'
        RX_UUID = '6E400002-B5A3-F393-E0A9-E50E24DCCA9E'
        TX_UUID = '6E400003-B5A3-F393-E0A9-E50E24DCCA9E'
            
        BLE_NUS = bluetooth.UUID(NUS_UUID)
        BLE_RX = (bluetooth.UUID(RX_UUID), bluetooth.FLAG_WRITE)
        BLE_TX = (bluetooth.UUID(TX_UUID), bluetooth.FLAG_NOTIFY)
            
        BLE_UART = (BLE_NUS, (BLE_TX, BLE_RX,))
        SERVICES = (BLE_UART, )
        ((self.tx, self.rx,), ) = self.ble.gatts_register_services(SERVICES)

    def send(self, data):
        self.ble.gatts_notify(0, self.tx, data + '\n')

    def advertiser(self):
        name = bytes(self.name, 'UTF-8')
        adv_data = bytearray('\x02\x01\x02') + bytearray((len(name) + 1, 0x09)) + name
        self.ble.gap_advertise(100, adv_data)
        print(adv_data)
        print("rn")
                # adv_data
                # raw: 0x02010209094553503332424C45
                # b'x02x01x02ttESP32BLE'
                #
                # 0x02 - General discoverable mode
                # 0x01 - AD Type = 0x01
                # 0x02 - value = 0x02
                
                # https://jimmywongiot.com/2019/08/13/advertising-payload-format-on-ble/
                # https://docs.silabs.com/bluetooth/latest/general/adv-and-scanning/bluetooth-adv-data-basics



led = Pin(12, Pin.OUT)
but = Pin(18, Pin.IN)

NEO_PIN = 4
NEO_COUNT = 2

np = NeoPixel(Pin(NEO_PIN, Pin.OUT), NEO_COUNT)



#ble = ESP32_BLE("ESP32BLE")

def buttons_irq(pin):
    led.value(not led.value())
    ble.send('LED state will be toggled.')
    print('LED state will be toggled.')   
but.irq(trigger=Pin.IRQ_FALLING, handler=buttons_irq)

def neorainbow():
        for j in range(256):
            for i in range(np.n):
                WheelPos = (i * 1 + j) & 255
                if WheelPos < 85:
                    np[i] = (int((WheelPos * 3)), int((255 - WheelPos * 3)), 0)
                elif WheelPos < 170:
                    WheelPos -= 85
                    np[i] = (int((255 - WheelPos * 3)), 0, int((WheelPos * 3)))
                else:
                    WheelPos -= 170
                    np[i] = (0, int((WheelPos * 3)), int((255 - WheelPos * 3)))
            np.write()  # Write the final colors to the NeoPixel strip
            sleep_ms(5)

def neo_off():
    np.fill((0, 0, 0))
    np.write()

   


    

def blue_connect():
    global is_ble_connected
    global has_sent_hello
    global ble
    if is_ble_connected and not has_sent_hello:
        for i in range(120):
            ble.send('beetlecar_bluetooth_is_ready')
        has_sent_hello = True
        print('beetlecar_bluetooth_is_ready')
    sleep_ms(100)


'''class comman_blu:
    
    if ble_msg == 'read_LED':
        print(ble_msg)
        ble_msg = ""
        print('LED is ON.' if led.value() else 'LED is OFF')
        ble.send('LED is ON.' if led.value() else 'LED is OFF')
    elif ble_msg == 'led on':
        led.value(1)
        print(ble_msg)
        ble_msg = ""
        print('LED is ON.' )
        ble.send('LED is ON.')
    elif ble_msg == 'led off':
        led.value(0)
        print(ble_msg)
        ble_msg = ""
        print('LED is OFF.' )
        ble.send('LED is OFF.')
    elif ble_msg == 'neo on':
        neorainbow()
        print(ble_msg)
        ble_msg = ""
        print('LED is OFF.' )
        ble.send('LED is OFF.')
    elif ble_msg == 'neo off':
        neo_off()
        print(ble_msg)
        ble_msg = ""
        print('LED is OFF.' )
        ble.send('LED is OFF.')
    sleep_ms(100)'''
