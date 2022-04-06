from utime import sleep
import uasyncio as asyncio
import json

speaker = 0

f = open("settings.json", "r+b")

db = json.load(f)
volume = db["volume"]

f.close()

def valmap(value, istart, istop, ostart, ostop):
  return int(ostart + (ostop - ostart) * ((value - istart) / (istop - istart)))

def border(ssd):
    ssd.rect(0, 0, 128, 128, ssd.rgb(255,0,0))

def buzz(buzzerPinObject,frequency,sound_duration,silence_duration):
    buzzerPinObject.duty_u16(volume)
    buzzerPinObject.freq(frequency)
    sleep(sound_duration)
    buzzerPinObject.duty_u16(int(65536*0))
    sleep(silence_duration)

def gameOver():
    speaker.duty_u16(volume)
    speaker.freq(1046)
    sleep(.15)
    speaker.duty_u16(0)
    sleep(.1)
    speaker.duty_u16(volume)
    speaker.freq(1046)
    sleep(.15)
    speaker.duty_u16(0)
    sleep(.1)
    speaker.duty_u16(volume)
    speaker.freq(783)
    sleep(.15)
    speaker.duty_u16(0)
    sleep(.1)
    speaker.duty_u16(volume)
    speaker.freq(659)
    sleep(.15)
    speaker.duty_u16(0)
    sleep(.1)
    speaker.duty_u16(volume)
    speaker.freq(493)
    sleep(.15)
    speaker.duty_u16(0)
    sleep(.1)
    speaker.duty_u16(volume)
    speaker.freq(587)
    sleep(.15)
    speaker.duty_u16(0)
    sleep(.1)
    speaker.duty_u16(volume)
    speaker.freq(523)
    sleep(.3)
    speaker.duty_u16(0)

async def gameOver_async():
    speaker.duty_u16(volume)
    speaker.freq(1046)
    await asyncio.sleep(.15)
    speaker.duty_u16(0)
    await asyncio.sleep(.1)
    speaker.duty_u16(volume)
    speaker.freq(1046)
    await asyncio.sleep(.15)
    speaker.duty_u16(0)
    await asyncio.sleep(.1)
    speaker.duty_u16(volume)
    speaker.freq(783)
    await asyncio.sleep(.15)
    speaker.duty_u16(0)
    await asyncio.sleep(.1)
    speaker.duty_u16(volume)
    speaker.freq(659)
    await asyncio.sleep(.15)
    speaker.duty_u16(0)
    await asyncio.sleep(.1)
    speaker.duty_u16(volume)
    speaker.freq(493)
    await asyncio.sleep(.15)
    speaker.duty_u16(0)
    await asyncio.sleep(.1)
    speaker.duty_u16(volume)
    speaker.freq(587)
    await asyncio.sleep(.15)
    speaker.duty_u16(0)
    await asyncio.sleep(.1)
    speaker.duty_u16(volume)
    speaker.freq(523)
    await asyncio.sleep(.3)
    speaker.duty_u16(0)

def update_volume():
    global volume
    f = open("settings.json", "r+b")

    db = json.load(f)
    volume = db["volume"]

    f.close()

def coin():
    buzz(speaker, 659, .075, 0)
    buzz(speaker, 1046, .15, .1)

def setSpeaker(speaker1):
    global speaker
    speaker = speaker1

def changeDirection():
    buzz(speaker, 659, .02, 0)

async def changeDirection_async():
    speaker.duty_u16(volume)
    speaker.freq(659)
    await asyncio.sleep(.02)
    speaker.duty_u16(int(65536*0))

def play_tune(tune):
    for i in tune:
        buzz(speaker, i[0], i[1], i[2])

async def play_tune_async(tune, q):
    while True:
        for i in tune:
            if not q.empty():
                queue = await q.get()
                if queue == "pause":
                    speaker.duty_u16(0)
                    while True:
                        msg = await q.get()
                        print(msg)
                        if msg == "resume":
                            break
                    await asyncio.sleep(.05)
            speaker.duty_u16(volume)
            speaker.freq(i[0])
            await asyncio.sleep(i[1])
            speaker.duty_u16(int(65536*0))
            await asyncio.sleep(i[2])
