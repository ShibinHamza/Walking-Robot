
import time
import serial                #Pyserial library import for serial comm
import matplotlib.pyplot as plt
import matplotlib.animation as animation #For realtime plot

def animate(i, dataList, ser):
    ser.write(b'g')                                    
    arduinoData_string = ser.readline().decode('ascii') 
                                          

    try:
        arduinoData_float = abs(float(arduinoData_string))   
        dataList.append(arduinoData_float)              

    except:                                                                     
        pass

    dataList = dataList[-1000:]                 # show 1000 datapoints                      
    
    ax.clear()                                        
    ax.plot(dataList)                                  
    
    ax.set_ylim([0, 700])                       # Set ylimit                  
    ax.set_title("Current Plot")                       
    ax.set_ylabel("Current Value (mA)")                              

dataList = []                                       
                                                        
fig = plt.figure()                                   
ax = fig.add_subplot(111)                            

ser = serial.Serial("COM6", 9600)                       
time.sleep(2)                                      

                                                        
                                                        
ani = animation.FuncAnimation(fig, animate, frames=100, fargs=(dataList, ser), interval=100) 

plt.show()                                              
ser.close()  