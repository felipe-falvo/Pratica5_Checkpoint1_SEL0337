#!/usr/bin/env python3

import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

led = 18 #porta do led
GPIO.setup(led,GPIO.OUT) #colocando o led como saida

#funcao para ele ficar piscando
try:
    while True:
        GPIO.output(led,GPIO.HIGH) #ligando o led
        time.sleep(0.2)
        GPIO.output(led,GPIO.LOW) #desligando o led
        time.sleep(0.2)
except KeyboardInterrupt:
    GPIO.cleanup() #limpando as portas
