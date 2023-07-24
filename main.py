# GROWING BEYOND EARTH CONTROL BOX
# RASPBERRY PI PICO / MICROPYTHON

# FAIRCHILD TROPICAL BOTANIC GARDEN, SEPTEMBER 22, 2022

# The Growing Beyond Earth (GBE) control box is a device that controls
# the LED lights and fan in a GBE growth chamber. It can also control
# accessories including a 12v water pump and environmental sensors.
# The device is based on a Raspberry Pi Pico microcontroller running
# Micropython.

# This program (main.py) runs automatically each time the device is
# powered up.



# NOTE:
# any line that has "# type: ignore" I'm telling vscode to ignore type checks.
# This is only done in areas where I am ABSOLUTELY CERTAIN it won't cause problems.

# ensure that there are no variables from previous runs.
# makes running from a file much safer and less prone to weird issues.
globals().clear()

# Import Required libraries
import machine
import gbeformat
from ds3231 import DS3231
import seesaw
import stemma_soil_sensor
import ahtx0
import ina219
import os
import utime
import json
import uasyncio as asyncio
import neopixel
import binascii
#TODO use another library instead of ntptime that is non blocking and asynchronous
import ntptime
# add watchdog TODO!
from machine import WDT
from mqtt_as import MQTTClient,config

print("\n\n\n\n\n\n\n\n\n\n")
print('  ____ ____  _____')
print(' / ___| __ )| ____|   GROWING BEYOND EARTH(R)')
print('| |  _|  _ \\|  _|     FAIRCHILD TROPICAL BOTANIC GARDEN')
print('| |_| | |_) | |___    Raspberry Pi Pico W / Micropython')
print(' \\____|____/|_____|   Software release date: ?\n')
print('N E T W O R K   A N D   H A R D W A R E    S E T U P\n\n')


# Functions neccicary for the inizilization of the program
# They check if a directory or file exists

def dirExists(filename):
    try:
        return (os.stat(filename)[0] & 0x4000) != 0
    except OSError:
        return False


def fileExists(filename):
    try:
        return (os.stat(filename)[0] & 0x4000) == 0
    except OSError:
        return False


# Load extra libraries from /lib/, if not able to load, do not run the dependent async function and print a warning

libNotFoundMessage = " not found in /lib/, please make sure all the required libraries are in /lib/ in the pico. You can get a fresh copy of the entire program at https://github.com/Growing-Beyond-Earth/GBE-Box-Python-Experimental"

if not fileExists("/lib/ina219.py"):
    raise Exception(f"ina219.py{libNotFoundMessage}")

if not fileExists("/lib/ahtx0.py"):
    raise Exception(f"ahtx0.py{libNotFoundMessage}")

if not fileExists("/lib/stemma_soil_sensor.py"):
    raise Exception(
        f"stemma_soil_sensor.py{libNotFoundMessage}")

if not fileExists("/lib/seesaw.py"):
    raise Exception(f"seesaw.py{libNotFoundMessage}")

if not fileExists("/lib/ds3231.py"):
    raise Exception(f"ds3231.py{libNotFoundMessage}")

if not fileExists("/lib/gbeformat.py"):
    raise Exception(f"gbeformat.py{libNotFoundMessage}")

# Load Load lights, fan, time zone configuration from JSON file


# Check to see if gbe_settings exists
if not fileExists("/config/gbe_settings.json"):
    raise Exception("gbe_settings.json not found!, did you run SETUP.py?")

# Open the settings Json file
with open('/config/gbe_settings.json') as settings_file:
    config = json.load(settings_file)
    settings_file.close()

# Set up status LED on Control Box
np = neopixel.NeoPixel(machine.Pin(6), 1)
npc = {"red": [0, 1, 0], "green": [1, 0, 0], "blue": [0, 0, 1], "yellow": [
    0.6, 1, 0], "cyan": [0.8, 0, 0.8], "magenta": [0, 0.8, 0.8], "white": [0.6, 0.6, 0.6]}

# blue and yellow pulse at startup to indicate python software (grb color scheme used for np[0])
for val in range(0, 255):
    np[0] = [0, 0, val]
    np.write()
    utime.sleep_ms(2)
for val in range(255, -1, -1):
    np[0] = [0, 0, val]
    np.write()
    utime.sleep_ms(2)
for val in range(0, 255):
    np[0] = [val, val, 0]
    np.write()
    utime.sleep_ms(2)
for val in range(255, -1, -1):
    np[0] = [val, val, 0]
    np.write()
    utime.sleep_ms(2)

# -------  Networking setup --------

# whether wifi config is false or exists will determine if wireless logging is enabled.
# You can also set this to false to Disable wifi
wifi_config = True

# checks whether wifi config exists, if not, omit any wifi related code
if not fileExists("/config/wifi_settings.json"):
    raise Exception("wifi_settings.json not found!, did you run SETUP.py?")

# Define the wifi device
# Get the Unique ID of the Pico. This line makes a conversion from an ascii string to a python string hex number
board_id = binascii.hexlify(machine.unique_id()).decode()

# Load wifi settings and connect to wifi if they are set up.
if wifi_config:
    with open('/config/wifi_settings.json') as wifi_file:
        wifi_config = json.load(wifi_file)
        wifi_file.close()
    config['ssid'] = wifi_config['NETWORK_NAME']
    config['wifi_pw'] = wifi_config['NETWORK_PASSWORD']
    config["queue_len"] = 1
    config['client_id'] = board_id
    #TODO make a central server that this will connect to, for now, connect to a raspberry pi on the local network
    config['server'] = "broker.hivemq.com"#'192.168.0.100'
    config['user'] = ""
    config['password'] = ""
    config['keepalive'] = 60
    config['ping_interval'] = 0
    config['ssl'] = False
    config['ssl_params'] = {}
    config['response_time'] = 10
    config['clean_init'] = True
    config['clean'] = True
    config['max_repubs'] = 4
    config['will'] = None
    config['port'] = 1883




# Setup for data logging




# -------Set up I2C bus 0 for devices inside the control box----

i2c0 = machine.I2C(0, sda=machine.Pin(16), scl=machine.Pin(17))

try:
    ina = ina219.INA219(0.1, i2c0)
    ina.configure()
    print("Connected to electrical current sensor")
except:
    ina = False

i2c1 = machine.I2C(1, sda=machine.Pin(18), scl=machine.Pin(19), freq=400000)

# ----Set up I2C bus 1 for devices outside the control box-------
# this will try and setup for all supported sensors.
try:
    seesaw = stemma_soil_sensor.StemmaSoilSensor(i2c1)
    print("Connected to soil moisture sensor")
except:
    seesaw = False

# setup the aht10
try:
    aht10 = ahtx0.AHT10(i2c1)
    aht10.initialize()
    print("test init worked!")
except Exception as e:
    print("test init failed")
    aht10 = False

# while True:
#     if aht10:
#         humid = aht10.relative_humidity
#         temp = aht10.temperature
#         print(humid,temp)
    

# ---Set internal clock using network time or I2C realtime clock---
# the variable "rtc", refers to the Micropython RTC library, NOT the external battery powered RTC.
# Machine.RTC() will attempt to be synced using the battery powered RTC or the Internet.
# If neither is available, it will run unsynced.
lt = False
batteryClock = False
rtc = machine.RTC()
accurateTime = True


try:  # get local time from I2C RTC
    batteryClock = DS3231(i2c0)
    # Add a zero at the end of the localtime table for formatting
    lt = ([x for x in batteryClock.DateTime()] + [0])  # type: ignore
except:
    pass

# Use internal clock if its time is already set
if machine.RTC().datetime()[0] > 2021:
    lt = list(machine.RTC().datetime())

try:  # Use network time if available
    ntptime.settime()  # Set the internal RTC time to the network time in UTC
    # Correct time for local time zone
    ct = utime.localtime(
        utime.time() - (abs(config["time zone"]["GMT offset"])) * 3600)
    lt = [ct[0], ct[1], ct[2], ct[6], ct[3], ct[4],
          ct[5], 0]   # Format time for setting RTC
    ntp = True
except:
    ntp = False

try:
    rtc.datetime(lt)  # Set internal clock with best available time
except:
    pass

try:
    if lt and batteryClock:
        batteryClock.DateTime(machine.RTC().datetime())  # Set I2C RTC
except:
    pass

if ntp:
    print("Connected to network time")
else:
    print("Failed to connect to the internet\nFalling back to i2c RTC")

if batteryClock:
    print("Connected to battery-powered internal clock")
elif ntp:
    print("Failed to connect to the i2c RTC\nFalling back to internet clock...")
else:
    print("Failed to connect to the i2c RTC\nFalling back to internal clock...")

if lt:
    print("Internal clock successfully set\n")
else:
    accurateTime = False
    print("Internal clock failed to set.\nFalling back to possibly unsynced clock...")

# Setup CSV logging

if not dirExists("/logs"):
    print("logs folder does not exist\nCreating logs folder...")
    os.mkdir("/logs")


# ---------------Set up LED and fan control--------------------
# Connect 24v MOSFETs to PWM channels on GPIO Pins 0-4
# Set PWM frequency on all channels


r = machine.PWM(machine.Pin(0))
r.freq(20000)   # Red channel
g = machine.PWM(machine.Pin(1))
g.freq(20000)   # Green channel
b = machine.PWM(machine.Pin(2))
b.freq(20000)   # Blue channel
w = machine.PWM(machine.Pin(3))
w.freq(20000)   # White channel
f = machine.PWM(machine.Pin(4))
f.freq(20000)   # Fan

# Clean up lights in case of a previous crash
r.duty_u16(0)
g.duty_u16(0)
b.duty_u16(0)
w.duty_u16(0)

# Initialize variables for counting fan RPMs
fanSpinCounter = 0
fanCounterPrevMs = utime.ticks_ms()
fanCounterCurrentMs = utime.ticks_ms()

print("Hardware ID:    " + board_id)

# ----------------------Set up Functions -----------------------


def datetimeToSeconds(datetime):
    # Convert entered time from HH:MM to seconds since midnight
    return ((datetime[4]*60) + datetime[5]) * 60


def hourAndMinutestoSeconds(input_time):
    # Convert entered time from HH:MM to seconds since midnight
    inH, inM = map(int, input_time.split(':'))
    return (int(inH)*60 + int(inM)) * 60


def steadyLED(color): np[0] = tuple([int(rgb * 255)
                                     for rgb in npc[color]]); np.write()  # Status LED on



def fanPulse(pin):     # Count fan rotation, triggered twice per rotation
    global fanSpinCounter
    fanSpinCounter += 1


def tryGetINA():      # Read current sensor

    # check if the ina is already connected.
    if not ina:
        return -1, -1, -1

    try:
        return ina.voltage(), ina.current(), ina.power()  # type: ignore
    except:
        return -1, -1, -1

# returns (humidity,temp) from an aht10
def tryGetAht10():
    global aht10

    if not aht10:
        return -1, -1
    
    try:
        return aht10.relative_humidity, aht10.temperature # type: ignore
    except:
        return -1,-1

def tryGetSeesaw():   # Read soil moisture & temp sensor
    global seesaw

    # check to see if the seesaw is connected or not, if its not return -1.
    if not seesaw:
        return -1, -1

    try:
        return seesaw.get_moisture(), seesaw.get_temp()  # type: ignore
    except:
        return (-1, -1)


# read Co2 Temp and Humidity from the SCD sensor TODO
def tryGetSCD():
    pass

# gets the stats used for logging


def getStats():
    global fanCounterCurrentMs
    global fanCounterPrevMs
    global fanSpinCounter
    datetime = rtc.datetime()
    vol, mam, mwa = tryGetINA()  # Read current sensor
    # Read soil moisture & temp sensor
    soilMoisture, soilTermperature = tryGetSeesaw()
    fanCounterPrevMs = fanCounterCurrentMs
    fanCounterCurrentMs = utime.ticks_ms()
    return ([
        # gets the time in year-month-day format
        f"\"{datetime[0]}-{datetime[1]}-{datetime[2]}\"",
        f"\"{datetime[4]}:{datetime[5]}\"",
        # Duty of red green blue, and white LEDs (respectivly R G B, and W)
        round(r.duty_u16()/256),
        round(g.duty_u16()/256),
        round(b.duty_u16()/256),
        round(w.duty_u16()/256),
        # voltage, miliamps, and wattage
        round(vol, 2),
        round(mam),
        round(mwa/1000, 2),
        # Fan duty (spin speed)
        round(f.duty_u16()/256),
        # Calculations for how fast the fan is ACTUALLY spinning (eg: duty can be max but fan is stuck)
        fanSpinCounter/(fanCounterCurrentMs-fanCounterPrevMs)*30000,
        # readings from temp and moisture sensor
        soilTermperature,
        soilMoisture
    ])


# gets data with no accurate internal clock
def getStatsNoRTC():
    global fanCounterCurrentMs
    global fanCounterPrevMs
    global fanSpinCounter
    vol, mam, mwa = tryGetINA()  # Read current sensor
    # Read soil moisture & temp sensor
    soilMoisture, soilTermperature = tryGetSeesaw()
    fanCounterPrevMs = fanCounterCurrentMs
    fanCounterCurrentMs = utime.ticks_ms()
    return ([
        # this function is run when time is not known, therefore they have been replaced by "?"
        "\"?\"",
        "\"?\"",
        # Duty of red green blue, and white LEDs (respectivly R G B, and W)
        r.duty_u16()//256,
        g.duty_u16()//256,
        b.duty_u16()//256,
        w.duty_u16()//256,
        # voltage, miliamps, and wattage
        round(vol, 2),
        round(mam),
        round(mwa/1000, 2),
        # Fan duty (spin speed)
        round(f.duty_u16()/256),
        # Calculations for how fast the fan is ACTUALLY spinning (eg: duty can be max but fan is stuck)
        fanSpinCounter/(fanCounterCurrentMs-fanCounterPrevMs)*30000,
        # readings from temp and moisture sensor
        soilTermperature,
        soilMoisture
    ])



        


# Remove old log files, keeping the specified number
def cleanLogs(keep_number):
    try:
        log_list = os.listdir("logs")
        del_files = range(len(log_list)-keep_number)
        for idx in del_files:
            os.remove("logs/" + log_list[idx])
    except Exception as e:
        print("Error cleaning up log files:", e)


# Looks for open Unknown CSv date eg: UnknownDate(1).csv
def lookForUnknownNumber():
    unknownNumber = 1
    while True:
        if fileExists(f"/logs/UnknownDate({unknownNumber}).json"):
            unknownNumber += 1
            continue
        return unknownNumber


ledBuffer = []


def queueLedAction(ledNumber):
    ledBuffer.append(ledNumber)


# ----- setup async functions that will run in the async event loop -----

# attempts to upload files in /logs/, which are saved when
# uploading failes. does not run in main event loop, only runs in logData()
async def tryToUploadBackup(client):
    logFolder = os.listdir("/logs")
    for file in logFolder:
        try:
            with open(file, 'r') as f:
                data = json.load(f)
                await client.publish('data', data, qos = 1)
                f.close()
                os.remove(f)
        except Exception as e:
            print(f"failed to upload backup file \"{file}\", encountered error: {e}")


# syncs the time using the internet or rtc, runs every hour
async def syncTime():
    while True:
        await asyncio.sleep(3600)
        # attempt to set the time online, set the Battery Powered RTC too if possible
        try:
            ntptime.settime()
            print("online time set")
            if batteryClock:
                batteryClock.DateTime(rtc.datetime())  # type: ignore
            continue
        except:
            print(
                "WARNING: Failed to sync time online, Internal Clock and RTC may slowly drift away from accurate time")

# performs any led actions in ledBuffer
# 0 is a green pulse
# 1 is a red pulse
# 2 is a blue pulse
# add more led actions TODO


async def ledStatus():
    global ledBuffer
    global np
    global wifi_config

    while True:
        await asyncio.sleep_ms(1)

        if ledBuffer == []:
            continue
        else:
            ledNumber = ledBuffer.pop()

        for i in range(0, 255):
            ledColor = [0, 0, 0]
            ledColor[ledNumber] = i
            np[0] = ledColor
            np.write()
            await asyncio.sleep_ms(4)
        for i in range(255, -1, -1):
            ledColor = [0, 0, 0]
            ledColor[ledNumber] = i
            np[0] = ledColor
            np.write()
            await asyncio.sleep_ms(4)
        if not wifi_config:
            queueLedAction(2)


print(rtc.datetime)
# Log data to a file, {Year-month-day}.csv
# will log to UnknownDate(number).csv
async def watchDog():
    wdt = WDT(timeout=8388)
    while True:
        await asyncio.sleep_ms(1)
        wdt.feed()

# logs data and sends it to server, saves data if it fails to send.
async def logData(client):
    global accurateTime
    while True:
        await asyncio.sleep(3600)
        datetime = rtc.datetime()
        if accurateTime:
            allstats = getStats()
            logDir = f"/logs/{datetime[0]}-{datetime[1]}-{datetime[2]} {datetime[4]}:{datetime[5]}.json"
        else:
            allstats = getStatsNoRTC()
            logDir = f"/logs/UnknownDate({lookForUnknownNumber()}).json"

        # Try to upload the data, if fails, save it and try to upload later
        await tryToUploadBackup(client)

        try:
            await client.publish('data', allstats, qos = 1)
            continue
        except Exception as e:
            print(f"data upload failed: {e}")
            logFile = open(logDir, "w")
            print(f"saving to \"{logFile}\"")
            logFile.write(json.dumps(allstats))
            logFile.close()
        

# This handles outages, and attempts to reconnect if one is detected
# NOTE: this is not started in the main function, rather, its started in mqttHandler()
async def reconnect(client):
    while True:
        await asyncio.sleep(1)
        
        if client.isconnected():
            continue
        
        print("connection interrupted, attempting to recconect...")
        await asyncio.sleep(3)
        try:
            await client.connect()
            print("Conneted!")
        except Exception as e:
            print(f"failed to reconnect:{e}")
            await asyncio.sleep(5)

# Connect to the internet
async def mqttHandler(client):
    print("attempting to connect...")
    while not client.isconnected():
        try:
            await client.connect()
            print("Conneted!")
        except Exception as e:
            print(f"connection failed:{e}")
            await asyncio.sleep(5)
    
    asyncio.create_task(reconnect(client))

    while client.isconnected():
        print("send loop ran!")
        await asyncio.sleep(1)
        await client.publish('growbox-data', "i'm alive!!!", qos = 1)

# Listen for hardware changes, if detected, attempt to connect.
# This function connects hardware, this is in case of accidental
# unplugging or hardware failure. TODO
async def hardwareListener():
    global seesaw
    global ina
    global aht10

    # These variables are to make sure hardware messages aren't printed multiple times
    seesawDebounce = True
    inaDebounce = True
    ahtDebounce = True
    while True:
        await asyncio.sleep_ms(500)
        # attempt to connect to the seesaw if its not already connected
        if not seesaw:
            try:
                seesaw = stemma_soil_sensor.StemmaSoilSensor(i2c1)
                print("i2c soil sensor connected.")
                seesawDebounce = True
                queueLedAction(0)
            except:
                pass

        # attempt to connect to the INA if its not already connected
        if not ina:
            try:
                ina = ina219.INA219(0.1, i2c0)
                ina.configure()
                print("Connected to current sensor")
                inaDebounce = True
                queueLedAction(0)
            except:
                pass

        if not aht10:
            try:
                aht10 = ahtx0.AHT10(i2c1)
                aht10.initialize()
                queueLedAction(0)
            except:
                pass


        # check to see if readings are working, if not, set the hardware variable to false

        if (tryGetSeesaw() == (-1, -1)) and seesawDebounce:
            print("i2c soil sensor disconnected")
            seesawDebounce = False
            seesaw = False
            queueLedAction(1)

        if (tryGetINA() == (-1, -1, -1)) and inaDebounce:
            print("INA disconnected")
            inaDebounce = False
            ina = False
            queueLedAction(1)
        
        if (tryGetAht10() == (-1,-1)) and ahtDebounce:
            print("aht Disconnected")
            ahtDebounce = False
            aht10 = False
            queueLedAction(1)


# Changes the lights and fans based off the time and user configurations
# ask a gradient option for tapering of brightness of light TODO


async def controlLightsAndFan():
    print(config["lights"]["timer"]["on"], config["lights"]["timer"]["off"])
    startLightTime = hourAndMinutestoSeconds(
        config["lights"]["timer"]["on"])-60

    endLightTime = hourAndMinutestoSeconds(config["lights"]["timer"]["off"])-60
    while True:
        datetimeSeconds = datetimeToSeconds(rtc.datetime())
        if (datetimeSeconds > startLightTime) and (datetimeSeconds < endLightTime):
            # Maximum brightness = 200
            r.duty_u16(int(min(200, config['lights']['duty']['red']))*256)
            # Maximum brightness = 89
            g.duty_u16(int(min(89, config['lights']['duty']['green']))*256)
            # Maximum brightness = 94
            b.duty_u16(int(min(94, config['lights']['duty']['blue']))*256)
            # Maximum brightness = 146
            w.duty_u16(int(min(146, config['lights']['duty']['white']))*256)
            # Maximum fan power = 255
            f.duty_u16(
                int(min(255, config['fan']['duty']['when lights on'])) * 256)
        else:
            # Lights off
            r.duty_u16(0)
            g.duty_u16(0)
            b.duty_u16(0)
            w.duty_u16(0)
            f.duty_u16(
                int(min(255, config['fan']['duty']['when lights off'])) * 256)
        await asyncio.sleep_ms(1)


# Main Async Function, all it does is run the coroutines
async def main():
    client = MQTTClient(config)
    await asyncio.gather(
        syncTime(), 
        controlLightsAndFan(), 
        logData(client), 
        hardwareListener(), 
        ledStatus(),
        mqttHandler(client),
        watchDog(),)



# Set up an interrupt (trigger) to count fan rotations for RPM calculation
p5 = machine.Pin(5, machine.Pin.IN, machine.Pin.PULL_UP)
p5.irq(trigger=machine.Pin.IRQ_FALLING, handler=fanPulse)

# Setup the main async event loop
print(rtc.datetime())
print("starting main event loop...")
asyncio.run(main())

# End of file
