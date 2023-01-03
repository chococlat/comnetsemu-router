""" 
    main functions
"""
import socket
import time
from packet import RIPPacket
from interfaces import get_local_interfaces
from table import Table

# Default entries for the rip packet
COMM_REQUEST = 1
COMM_UPDATE = 2
RIP_V = 1

# Listen for broadcast packets
def listen(_out):

    listener = socket.socket(
        socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)  # UDP
    listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    listener.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    listener.bind(("", 5005))
    while True:
        data, addr = listener.recvfrom(1024)
        present = False
        for tup in get_local_interfaces().items():
            if (addr[0] == tup[1]):
                present = True  # True to filter out owned packets
        if (present == False):
            _out.append((addr, data))
            

# Send route-updates in brodcast on each interface
def send_update(_table: Table):

    iplist = []
    for tup in get_local_interfaces().items():
        item = str(tup[1])
        if (item.startswith("127") == False and item.startswith("172") == False):
            iplist.append(item)

    while True:
        for ip in iplist:
            sender = socket.socket(
                socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)  # UDP
            sender.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            sender.bind((ip, 0))

            packet = RIPPacket()
            packet.command = COMM_UPDATE
            packet.version = RIP_V
            for entry in _table.routes:
                p_entry = {"Family": 2,
                           "RouteTag": 0,
                           "IPAddress": entry["Destination"],
                           "SubnetMask": entry["Netmask"],
                           "NextHop": entry["Gateway"],
                           "Metric": entry["Cost"]
                           }
                packet.entries.append(p_entry)

            sender.sendto(packet.str_export(), ("<broadcast>", 5005))
            sender.close()
        time.sleep(30)

# Send a single update (non-loop)
def single_update(_table: Table, requestedIPs: list):
    
    iplist = []
    for tup in get_local_interfaces().items():
        item = str(tup[1])
        if (item.startswith("127") == False and item.startswith("172") == False):
            iplist.append(item)

    for ip in iplist:
        sender = socket.socket(
            socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)  # UDP
        sender.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sender.bind((ip, 0))
        packet = RIPPacket()
        packet.command = COMM_UPDATE
        packet.version = RIP_V
        for entry in _table.routes:
            for i in range(len(requestedIPs)):
                if (entry["Destination"] == requestedIPs[i][0] and entry["Netmask"] == requestedIPs[i][1]):
                    p_entry = {"Family": 2,
                               "RouteTag": 0,
                               "IPAddress": entry["Destination"],
                               "SubnetMask": entry["Netmask"],
                               "NextHop": entry["Gateway"],
                               "Metric": entry["Cost"]
                               }
                    packet.entries.append(p_entry)
        if (len(packet.entries) > 0):
            sender.sendto(packet.str_export(), ("<broadcast>", 5005))
            sender.close()


# Manage tasks and received packets          
def run_tasks(_queue: list, _table: Table):
    while True:
        _table.updateOSTable()
        _table.clean2()
        if (len(_queue) > 0):
            packet = RIPPacket()
            (addr, data) = _queue.pop()
            packet.str_import(data)
            if (packet.command == str(COMM_REQUEST)):
                templist = []
                for entry in packet.entries:
                    templist.append((entry["IPAddress"], entry["SubnetMask"]))
                single_update(_table, templist)
            elif (packet.command == str(COMM_UPDATE)):
                iplist = []
                for tup in get_local_interfaces().items():
                    item = str(tup[1])
                    if (item.startswith("127") == False and item.startswith("172") == False):
                        iplist.append(item)
                for entry in packet.entries:
                    check = False
                    for ip in iplist:
                        if (ip==entry["NextHop"]):
                            check = True
                    if(check):
                        pass
                    elif(_table.isPresent(entry["IPAddress"],entry["SubnetMask"],"SELF")):
                        pass
                    elif(_table.isPresent(entry["IPAddress"],entry["SubnetMask"],addr[0])):
                        index = _table.getIndex(entry["IPAddress"],entry["SubnetMask"],addr[0])
                        _table.routes[index]["Timer"]=0
                        _table.routes[index]["Status"]="Active"
                        _table.routes[index]["Cost"]=int(entry["Metric"])+1
                    else:
                        _table.addroute(entry["IPAddress"],entry["SubnetMask"],addr[0],int(entry["Metric"])+1,0,"Active")
                pass
            else:
                print(f"Packet was invalid ({packet.command})")


# Request updates for specific routes
def ask_all(IPs: list):
    packet1 = RIPPacket()
    packet1.command = COMM_REQUEST
    packet1.version = RIP_V
    for dest, mask in IPs:        
        packet1.entries.append({"Family": 2,
                               "RouteTag": 0,
                               "IPAddress": dest,
                               "SubnetMask": mask,
                               "NextHop": 0,
                               "Metric": 0
                               })
    iplist = []
    for tup in get_local_interfaces().items():
        item = str(tup[1])
        if (item.startswith("127") == False and item.startswith("172") == False):
            iplist.append(item)

    for ip in iplist:
        asker = socket.socket(
            socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)  # UDP
        asker.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        asker.bind((ip, 0))
        asker.sendto(packet1.str_export(), ("<broadcast>", 5005))
        asker.close()
    packet1.entries.clear()
    
    
# Manage timer ticking
def update_timers(_table:Table):
    while True:
        for route in _table.routes:
            if(route["Timer"]!=-1):
                route["Timer"]+=1
        time.sleep(1)
        
        
# Manage the "Status" flag on the routing Table        
def update_status(_table:Table):
    while True:
        for route in _table.routes:
            if(route["Timer"]>=30 and route["Timer"]<=180):
                route["Status"]="Waiting"
            elif(route["Timer"]>=180 and route["Timer"]<=240):
                route["Status"]="Invalid"
            elif(route["Timer"]>=240):
                route["Status"]="toFlush"
        time.sleep(1)


# Not used
def cleaner(_table:Table):
    while True:
        _table.clean()
        time.sleep(5)