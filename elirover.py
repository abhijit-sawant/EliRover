from gpiozero import Robot
from gpiozero import OutputDevice
import multiprocessing
import time
import smbus
import math

import RPi.GPIO as GPIO

class Gyro(object):
    '''
      Used following link to connect gyro and setup i2c
      https://tutorials-raspberrypi.com/measuring-rotation-and-acceleration-raspberry-pi/
    '''
    def __init__(self):
        self.__angle_x = 0
        self.__angle_y = 0
        self.__angle_z = 0
        self.__power_mgmt_1 = 0x6b
        self.__power_mgmt_2 = 0x6c
        self.__previous_time = 0
        self.__current_time = time.time()
        self.__bus = smbus.SMBus(1)
        self.__address = 0x68   # via i2cdetect
        self.__bus.write_byte_data(self.__address, self.__power_mgmt_1, 0)        
        
    def __read_byte(self, reg):
        return self.__bus.read_byte_data(self.__address, reg)
     
    def __read_word(self, reg):
        h = self.__bus.read_byte_data(self.__address, reg)
        l = self.__bus.read_byte_data(self.__address, reg+1)
        value = (h << 8) + l
        return value
     
    def __read_word_2c(self, reg):
        val = self.__read_word(reg)
        if (val >= 0x8000):
            return -((65535 - val) + 1)
        else:
            return val
        
    def getAngles(self):    
        self.__previous_time = self.__current_time
        self.__current_time = time.time()
        elapsed_time = self.__current_time - self.__previous_time
     
        xout = self.__read_word_2c(0x43) / 131
        yout = self.__read_word_2c(0x45) / 131
        zout = self.__read_word_2c(0x47) / 131
        
        self.__angle_x = self.__angle_x + xout * elapsed_time
        self.__angle_y = self.__angle_y + yout * elapsed_time
        self.__angle_z = self.__angle_z + zout * elapsed_time        
       
        return (int(self.__angle_x), int(self.__angle_y), int(self.__angle_z))       
    

class EliConMotion(object): 
    def __initAttr(self):
        self.__pwmLeft = OutputDevice(25)
        self.__pwmRight = OutputDevice(17)
        self.__pwmLeft.on()
        self.__pwmRight.on()        
        self.__robot = Robot(left=(23, 24), right=(22, 27))        
        
    def __setSpeed(self, left_speed, right_speed, bForward = True):
        mf_speed = 1
        if bForward is False:
            mf_speed = -1
        self.__robot.value = (mf_speed*left_speed, mf_speed*right_speed)
        
    def clear(self):
        self.__pwmLeft.off()
        self.__pwmRight.off()        
        
    def stop(self):
        self.__initAttr()
        self.__robot.stop()
        
    def __turn(self, angle, lm, rm):
        INIT_SPEED = 1.0
        KP = INIT_SPEED / (2.0 * angle)
        KI = KP / 100
        speed = INIT_SPEED
        self.__setSpeed(lm * speed, rm * speed)
        g = Gyro()
        totalDeviation = 0
        while True:
            ret = g.getAngles()
            curAngle = math.fabs(ret[2])            
            if curAngle >= angle: # - 20: #substarct 20 to compensate for overshoot
                self.__robot.stop()
                break
            print('curangle, speed %s %s' % (curAngle, speed))
            deviation = angle - curAngle
            speed = (KP * deviation) + (KI * totalDeviation)
            speed = min(speed, 1.0)
            self.__setSpeed(lm * speed, rm * speed)
            totalDeviation += deviation
            
    def turn_right(self, angle):
        self.__initAttr()
        self.__turn(angle, 1, -1)           
        
    def turn_left(self, angle):
        self.__initAttr()
        self.__turn(angle, -1, 1)
        
    def move(self, bForward = True):
        self.__initAttr()
        
        KP = 0.1
        SAMPLETIME = 0.000001
        SPEED = 0.9

        m_left_speed = SPEED
        m_right_speed = SPEED
        self.__setSpeed(m_left_speed, m_right_speed, bForward)
        
        g = Gyro()
        TARGET = g.getAngles()[2]
        while True:
            angle = g.getAngles()[2]
            deviation = math.fabs(angle - TARGET)
            if deviation != 0:
                correction = (deviation * KP) 
                if bForward is False:
                    if angle >= 0:   
                        m_right_speed += correction
                        m_left_speed -= correction
                    else:
                        m_right_speed -= correction
                        m_left_speed += correction
                else:
                    if angle <= 0:   
                        m_right_speed += correction
                        m_left_speed -= correction
                    else:
                        m_right_speed -= correction
                        m_left_speed += correction                 
                m_right_speed = min(max(m_right_speed, 0.8), 1)
                m_left_speed = min(max(m_left_speed, 0.8), 1)
                #print('Correction : %s, Left: %s, Right: %s\n' % (correction, m_left_speed, m_right_speed))
                self.__setSpeed(m_left_speed, m_right_speed, bForward)
            time.sleep(SAMPLETIME)        
        
class EliRover(object):
    def __init__(self):
        self.__process = None
        self.__conMotion = EliConMotion()
        
    def move_forward(self):
        self.__process = multiprocessing.Process(target=self.__conMotion.move)
        self.__process.start()
        
    def move_backward(self):
        self.__process = multiprocessing.Process(target=self.__conMotion.move, args=(False,))
        self.__process.start()
        
    def turn_right(self, angle):
        self.__process = multiprocessing.Process(target=self.__conMotion.turn_right, args=(angle,))
        self.__process.start()
        self.__process.join()
        
    def turn_left(self, angle):
        self.__process = multiprocessing.Process(target=self.__conMotion.turn_left, args=(angle,))
        self.__process.start()
        self.__process.join()       
        
    def stop(self):
        self.__terminateProc()
        proc = multiprocessing.Process(target=self.__conMotion.stop)
        proc.start()     
     
    def __terminateProc(self):
        if self.__process is not None:
            self.__process.terminate()
            self.__process.join()
            
       
def main():
    rover = EliRover()
    try:
        rover.turn_right(90)
        #time.sleep(5)
        #rover.stop()
        #rover.move_backward()
        #time.sleep(5)
        #rover.stop()
      
    except:
        raise
    finally:
        rover.stop()

if __name__ == '__main__':
    main()

#End of file: