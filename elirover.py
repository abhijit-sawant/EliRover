from gpiozero import Robot
from gpiozero import OutputDevice
import multiprocessing
import time
import smbus
import math

import RPi.GPIO as GPIO

class Gyro(object):
    def __init__(self):
        self.__angle_x = 0
        self.__angle_y = 0
        self.__angle_z = 0
        self.__power_mgmt_1 = 0x6b
        self.__power_mgmt_2 = 0x6c
        self.__previous_time = 0
        self.__current_time = time.time()
        self.__bus = smbus.SMBus(1) # bus = smbus.SMBus(0) fuer Revision 1
        self.__address = 0x68   # via i2cdetect
        # Aktivieren, um das Modul ansprechen zu koennen
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
    

class Encoder(object):
    def __init__(self, pin):
        GPIO.setmode(GPIO.BCM)
        self._value = 0
        self.__pin = pin
        GPIO.setup(self.__pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.add_event_detect(self.__pin, GPIO.RISING, callback=self._increment, bouncetime=23)
        
    def reset(self):
        self._value = 0        

    def clear(self):
        GPIO.remove_event_detect(self.__pin)
        
    def _increment(self, pin):
        self._value += 1
                
    @property
    def value(self):
        return self._value
    
class EliConMotion(object): 
    def __initAttr(self):
        self.__pwmLeft = OutputDevice(25)
        self.__pwmRight = OutputDevice(17)
        self.__pwmLeft.on()
        self.__pwmRight.on()        
        self.__robot = Robot(left=(23, 24), right=(22, 27))        
        self.__enLeft = Encoder(5)
        self.__enRight = Encoder(19)
        
    def __setSpeed(self, left_speed, right_speed, bForward = True):
        mf_speed = 1
        if bForward is False:
            mf_speed = -1
        self.__robot.value = (mf_speed*left_speed, mf_speed*right_speed)
        
    def clear(self):
        self.__enLeft.clear()
        self.__enRight.clear()
        self.__pwmLeft.off()
        self.__pwmRight.off()        
        
    def stop(self):
        self.__initAttr()
        self.__robot.stop()
        
    def __turn(self, angle, lm, rm):
        INIT_SPEED = 1
        speed = INIT_SPEED
        self.__setSpeed(lm * speed, rm * speed)
        g = Gyro()
        while True:
            ret = g.getAngles()
            curAngle = math.fabs(ret[2])            
            if curAngle >= angle: # - 20: #substarct 20 to compensate for overshoot
                self.__robot.stop()
                break
            #print('curangle %s %s' % (curAngle, speed))
            speed = max((INIT_SPEED * ((angle - curAngle)/angle)), 0.3)
            self.__setSpeed(lm * speed, rm * speed)
            
    def turn_right(self, angle):
        self.__initAttr()
        self.__turn(angle, 1, -1)           
        
    def turn_left(self, angle):
        self.__initAttr()
        self.__turn(angle, -1, 1)
        
    def move(self, bForward = True):
        self.__initAttr()
        
        KP = 0.025
        KD = 0.0125
        KI = 0.00625
        SAMPLETIME = 0.000001
        SPEED = 0.6
        
        e_left_prev_error = 0
        e_right_prev_error = 0
        e_left_sum_error = 0
        e_right_sum_error = 0
        m_left_speed = SPEED
        m_right_speed = SPEED
        self.__setSpeed(m_left_speed, m_right_speed, bForward)
        
        g = Gyro()
        TARGET = g.getAngles()[2]
        #print('Target %s\n' % TARGET)
        
        while True:
            angle = g.getAngles()[2]
            deviation = angle - TARGET
            if deviation != 0:
                correction = min((math.fabs(deviation) * SPEED), 1)
                #print('min ( %s, %s)' % ((math.fabs(deviation) * SPEED), 1))
                if bForward is False:
                    if angle >= 0:   
                        m_right_speed = correction
                    else:
                        m_left_speed = correction
                else:
                    if angle <= 0:   
                        m_right_speed = correction
                    else:
                        m_left_speed = correction                    
                #print('Angle, Left, Right: %s, %s, %s\n' % (angle, m_left_speed, m_right_speed))
                self.__setSpeed(m_left_speed, m_right_speed, bForward)
            time.sleep(SAMPLETIME)        
        
        
    def move_old(self, bForward = True):
        self.__initAttr()
        
        TARGET = 30
        KP = 0.025
        KD = 0.0125
        KI = 0.00625
        SAMPLETIME = 0.000001
        
        e_left_prev_error = 0
        e_right_prev_error = 0
        e_left_sum_error = 0
        e_right_sum_error = 0
        m_left_speed = 1
        m_right_speed = 1
        self.__setSpeed(m_left_speed, m_right_speed, bForward)
        while True:             
            e_left_error = TARGET - self.__enLeft.value
            e_right_error = TARGET - self.__enRight.value
            m_left_speed += (e_left_error * KP) + (e_left_prev_error * KD) + (e_left_sum_error * KI)
            m_right_speed += (e_right_error * KP) + (e_right_prev_error * KD) + (e_right_sum_error * KI)
            m_left_speed = max(min(1, m_left_speed), 0)
            m_right_speed = max(min(1, m_right_speed), 0)
            self.__setSpeed(m_left_speed, m_right_speed, bForward)
            #print("e1 {} e2 {}".format(self.__enLeft.value, self.__enRight.value))
            #print("e_left_error: %s e_right_error: %s" % (e_left_error, e_right_error))
            #print("m1 {} m2 {}".format(m_left_speed, m_right_speed))
            self.__enLeft.reset()
            self.__enRight.reset()
            time.sleep(SAMPLETIME)
            e_left_prev_error = e_left_error
            e_right_prev_error = e_right_error
            e_left_sum_error += e_left_error
            e_right_sum_error += e_right_error        
        
    
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
        #time.sleep(40)
      
    except:
        raise
    finally:
        rover.stop()

if __name__ == '__main__':
    main()

#End of file: