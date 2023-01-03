import time
import threading
from table import Table
from components import listen, send_update, run_tasks,update_timers,update_status

# RIP TIMERS
TIMER_ACTIVE = 30
TIMER_INVALID = 180
TIMER_FLUSH = 240

if __name__ == "__main__":
    
    received_queue = [] # Queue of received packets
    table = Table()     # Non-OS RoutingTable
    table.obtainOwn()   # Obtain directly connected interfaces
    
    # Creation of threads for concurrent functions
    t_listen = threading.Thread(target=listen, args=[received_queue])           # Listen for broadcast packets
    t_update = threading.Thread(target=send_update, args=[table])               # Send route-updates in brodcast on each interface
    t_taskr = threading.Thread(target=run_tasks, args=[received_queue, table])  # Manage tasks and received packets
    t_timer = threading.Thread(target=update_timers,args=[table])               # Manage timer ticking
    t_status = threading.Thread(target=update_status,args=[table])              # Manage the "Status" flag on the routing Table
    
    # Starting the threads
    t_taskr.start()
    t_update.start()
    t_listen.start()
    t_timer.start()
    t_status.start()
    
    # Printing the routing table every second
    while True:
        time.sleep(1)
        table.printall()


