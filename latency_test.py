import COMS 
from COMS import *
import time

number = 40

Tx = com_handler()
Rx = com_handler()

Tx._init_('COM8',9600,number)
Rx._init_('COM9',9600,number)

info_Tx = np.ones(5)
time_Stamp = time.time()

Tx.send(info_Tx)
while(not Rx.check_recv()):
	pass

delT = time.time() - time_Stamp
info_Rx = Rx.read()

print(delT)
print(info_Rx)
Tx.close()
Rx.close()

