import serial, time

arduino = serial.Serial('COM5', 9600)
time.sleep(2)
rawString = arduino.readline()
lala=str(rawString)
lala=lala.replace("\\r\\n'","").replace("b'","")
print(lala)
while True:
    rawString = arduino.readline()
    print(str(rawString))
    arduino.write(b'3')

arduino.close()