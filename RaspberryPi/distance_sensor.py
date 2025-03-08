import RPi.GPIO as GPIO
import time

# GPIO Setup
TRIG = 23  # GPIO23 (Physical pin 16)
ECHO = 24  # GPIO24 (Physical pin 18)
GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

def measure_distance():
    # Send trigger pulse
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    # Measure echo duration
    pulse_start = time.time()
    pulse_end = time.time()
    
    timeout = time.time() + 1  # 1-second timeout
    while GPIO.input(ECHO) == 0 and time.time() < timeout:
        pulse_start = time.time()
        
    timeout = time.time() + 1
    while GPIO.input(ECHO) == 1 and time.time() < timeout:
        pulse_end = time.time()

    # Calculate distance (cm)
    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150  # 343 m/s ÷ 2 (round trip)
    return round(distance, 2)

if __name__ == "__main__":
    while True:
        print(measure_distance())
        time.sleep(0.05)