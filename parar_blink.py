#!/usr/bin/env python3

import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)

led = 18 #porta do led

GPIO.setup(led,GPIO.OUT) #colocando led como saida
GPIO.output(led,GPIO.LOW) #desligando o led
GPIO.cleanup()

