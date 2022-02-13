from numpy import inner
import psutil
import time


bytes_sent=0
bytes_recv=0

for i in range(2):
    net_info = psutil.net_io_counters(pernic=False)
    bytes_sent = net_info.bytes_sent - bytes_sent
    bytes_recv = net_info.bytes_recv - bytes_recv
    
    time.sleep(0.5)

print(bytes_sent*2, bytes_recv*2)
