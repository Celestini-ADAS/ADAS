import COMS 
from COMS import *
import time

number = 40

Tx = com_handler() #create object
Rx = com_handler()

Tx._init_('COM8',9600,number) #initialize com port with baud rate and number of bytes in a single packet
Rx._init_('COM9',9600,number)

info_Tx = np.ones(5) #info to transfer
time_Stamp = time.time()

Tx.send(info_Tx) # sending info
while(not Rx.check_recv()):
	pass

delT = time.time() - time_Stamp
info_Rx = Rx.read()

print(delT)
print(info_Rx)
Tx.close()
Rx.close()

