#!/usr/bin/env python
# coding: utf-8

import smbus
import time

#----------VARIABLES--------------
bus = smbus.SMBus(1)

addr = 0x40
MODE1 = 0x00
MODE2 = 0x01
LED0_ON_L = 0x06
LED0_ON_H = 0x07
LED0_OFF_L = 0x08
LED0_OFF_H = 0x09
ALL_LED_ON_L = 0xFA  
ALL_LED_ON_H = 0xFB	
ALL_LED_OFF_L = 0xFC	
ALL_LED_OFF_H = 0xFD	
PRESCALE = 0xFE		
LED_MULTIPLIER = 4
CLOCK_FREQ = 25000000

mg90_0 = 205
mg90_45 = 328
mg90_90 = 410
mg90_135 = 523
mg90_180 = 615
#----------------------------------

#--------DIAGNOSTICS------------------------------------------------------------
def MODE1_probe(raw = bus.read_byte_data(addr,MODE1)):
    '''
          MODE1_probe(raw = bus.read_byte_data(addr,MODE1))
          Affiche l'état actuel du registre MODE1 et la signification de chaque bit.
          Option :
          raw: byte, pour tester l'état de MODE1 pour un byte précis
		  ''' 
    print(hex(raw))
    raw = bin(raw)[2:]
    result = [0 for k in range(8)]
    if len(raw) == 1 :
        result[7] = int(raw[0])
    else :
        for j in range(len(raw)):
            result[7-len(raw)+j+1] = int(raw[j])
    print('\nMODE1')
    print(result)
    #Analyse des résultats
    if result[0] == 0:
        print('0 : Redémarrage désactivé')
    else :
        print('1 : Redémarrage activé')
    if result[1] == 0:
        print('0 : CLK externe désactivée')
    else :        
        print('1 : CLK externe activée')
    if result[2] == 0:
        print('0 : Auto-incrémentation désactivée')
    else :
        print('1 : Auto-incrémentation activée')
    if result[3] == 0:
        print('0 : Mode veille désactivé')
    else :
        print('1 : Mode veille activé, oscillateur désactivé')
    if result[4] == 0:
        print('0 : SUB1 désactivé')
    else :
        print('1 : SUB1 activé')
    if result[5] == 0:
        print('0 : SUB2 désactivé')
    else :
        print('1 : SUB2 activé')
    if result[6] == 0:
        print('0 : SUB3 désactivé')
    else :
        print('1 : SUB3 activé')
    if result[7] == 0:
        print('0 : ALLCALL désactivé')
    else :
        print('1 : ALLCALL activé\n')
    return   
def MODE2_probe(raw = bus.read_byte_data(addr,MODE2)):
    '''
          MODE2_probe(raw = bus.read_byte_data(addr,MODE2))
          Affiche l'état actuel du registre MODE2 et la signification de chaque bit.
          Option :
          raw: byte, pour tester l'état de MODE2 pour un byte précis'''
    
    raw = bin(raw)[2:]
    result = [0 for k in range(8)] 
    if len(raw) == 1 :
        result[7] = int(raw[0])
    else :
        for j in range(len(raw)):
            result[7-len(raw)+j+1] = int(raw[j])
    print('\nMODE2:')
    print(result)
    #Analyse des résultats
    print('0\n0\n0')          
    if result[3] == 0:
        print('0 : Sortie non-inversée')
    else :
        print('1 : Sortie inversée')
    if result[4] == 0:
        print('0 : Actualisation de l\'output sur STOP')
    else :
        print('1 : Actualisation de l\'output sur ACK')
    if result[5] == 0:     
        print('0 : Output en collecteur ouvert')
    else :
        print('1 : Output en cascade à point milieu')
    if result[6] == 0:
        if result[7] == 0:
            print('0\n0 : OE = 1 => Désactivation des LED')
        else :
            if result[5] == 0 :
                print('0\n1 : OE = 1 => Augmentation de l\'impédance des LED')
            else :
                print('0\n1 : OE = 1 => Activation des LED')
    else :
        print('1\n'+str(result[7])+': OE = 1 => Augmentation de l\'impédance des LED\n')
	return
#-------------------------------------------------------------------------------

#------------------PCA9685-------------------------------------------------------
def sleep():
	print('Mise en veille')
	mode = (bus.read_byte_data(addr, MODE1) | 0x10)
	bus.write_byte_data(addr, MODE1, mode) #Bit SLEEP effacé
	return

def wake():
	print('Sortie de veille')
	mode = (bus.read_byte_data(addr, MODE1) & 0xEF)
	bus.write_byte_data(addr, MODE1, mode)
	time.sleep(0.0006)
	mode = (bus.read_byte_data(addr, MODE1) & 0x5F)
	bus.write_byte_data(addr, MODE1, mode) 
	return

def set_PWM_freq(freq):
	prescale = (CLOCK_FREQ / 4096 / freq) -1
	oldmode = bus.read_byte_data(addr, MODE1) & 0xEF
	newmode = (oldmode & 0x7F) | 0x10
	
	print('Prescale à :'+str(prescale))
	print('Fréquence :'+str(freq))
	print('MODE1 passe de '+str(hex(oldmode))+' à '+str(hex(newmode)))

	bus.write_byte_data(addr,MODE1, newmode)
	bus.write_byte_data(addr,PRESCALE, prescale)
	bus.write_byte_data(addr,MODE1, oldmode)
	time.sleep(0.01)
	bus.write_byte_data(addr, MODE1, oldmode | 0x80)
	return

def set_PWM(channel, time_on, time_off):
	bus.write_byte_data(addr,LED0_ON_L + LED_MULTIPLIER * channel, (time_on & 0xFF) )
	bus.write_byte_data(addr,LED0_ON_H + LED_MULTIPLIER * channel, (time_on >> 8) )
	bus.write_byte_data(addr,LED0_OFF_L + LED_MULTIPLIER * channel, (time_off & 0xFF) )
	bus.write_byte_data(addr,LED0_OFF_H + LED_MULTIPLIER * channel, (time_off >> 8) )
	return

def get_PWM(channel):
	a = bus.read_byte_data(addr,LED0_OFF_L + LED_MULTIPLIER * channel)
	b = bus.read_byte_data(addr,LED0_OFF_H + LED_MULTIPLIER * channel)
	return (a + (b << 8))