# drowsy-driving-and-drunk-driving-detection-system

This work aims to prevent drunk driving and drowsy driving. The driver's central nervous system is suppressed, making them easily agitated, and their reaction time and judgment are impaired. As the ability to assess whether they are in a state capable of safe driving is significantly diminished, even the act of turning on the ignition and pressing the pedal can be a problem for a drunk driver. To address this issue, this work utilizes an alcohol detection sensor before the driver turns on the ignition and presses the pedal, allowing for testing. If the driver is in a state of intoxication, the ignition can be turned off.


Drowsy drivers may close their eyes and have difficulty maintaining focus on the road. They often become aware of their hazardous condition either just before or after an accident. To protect drivers in such states, a preventive system is needed to alert them when they are dozing off. In this work, a camera system using OpenCV is employed, along with a buzzer, to detect drowsiness and notify the driver of the impending danger.

# How does it work?

This system follows a sequence of booting, alcohol measurement, and drowsy driving measurement loops.

## drunk-driving-detection

The ignition of the car is activated by pressing the brake pedal and then pressing the ignition button. This aspect is also incorporated into this project. It first checks whether the brake button has been pressed. When the user presses the brake button, the brake LED (red) lights up. Then, after pressing the ignition button, it checks if the brake is activated, and the ignition LED (yellow) lights up. The activation of the brake function can be confirmed through the on/off status of the brake LED. Similarly, when turning on the final device, the on/off status of both the brake LED and ignition LED is checked.


Once the device is started, the alcohol sensor initiates measurement. Users can blow air into the sensor to measure the alcohol level. The measured value is converted into a readable value for the mainboard, i.e., the Raspberry Pi, through the pcf8591t AD/DA converter. When the measured value from the alcohol sensor exceeds a certain threshold, all LEDs turn off, indicating that the ignition is turned off.

## drowsy-driving-detection

Using openCV on the video obtained from the Raspberry Pi camera, this project identifies landmarks of the eyes. Based on the landmark coordinates, it calculates the aspect ratio of the eyes (EAR). When the eyes are closed, the EAR value approaches 0. By utilizing this, eye blinking can be detected. In this project, a threshold of 0.3 is set, and if the EAR value falls below this threshold, it is considered as an indication of closed eyes. If eye closure persists for a certain duration, it is determined as drowsy driving, and a buzzer is activated. This operation is carried out by counting the number of frames where the EAR value is below the threshold. In this project, if the EAR value remains below the threshold for 48 frames or more, it is considered as drowsiness.

# Hardware

 describe the hardware used in the project

## Used modules

* <a href="https://www.devicemart.co.kr/goods/view?no=1327429">MQ-3</a>
* <a href="https://www.devicemart.co.kr/goods/view?no=12537448">pcf8591</a>
* <a href="https://www.devicemart.co.kr/goods/view?no=2851">LED</a>
* <a href="https://www.devicemart.co.kr/goods/view?no=1361702">button</a>
* <a href="https://www.devicemart.co.kr/goods/view?no=2736">buzzer</a>
* <a href="https://smartstore.naver.com/misoparts/products/5533715543?site_preference=device&NaPm=ct%3Dlfp2u7tv%7Cci%3Dshopn%7Ctr%3Dsls_myr%7Chk%3D7c9d00b72aacb4353e5e3af8bfcf9d3635777aaf%7Ctrx%3D">raspicam</a>
* <a href="https://www.devicemart.co.kr/goods/view?no=12234534">Raspberry Pi Model B 4GB</a>

## circuit diagram




# ref
https://pyimagesearch.com/2017/05/08/drowsiness-detection-opencv/
