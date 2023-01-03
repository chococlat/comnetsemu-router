"""
Useful tools to convert net variables
"""
import nmap
import netifaces
import time

# Given an integer mask, return the dotted-string form
def dottedMask(m: int):
    temp = []
    st = ""
    for i in range(m):
        temp.append(1)
    for i in range(32-m):
        temp.append(0)
    for i in range(4):
        stemp = []
        for j in range(8):
            stemp.append(temp[i*8+j])
        st += str(toDec(stemp))+"."
    return st[:-1]

# Given a dotted-string mask, return the single integer form
def intMask(_dottedMask: str):
    st_list = []
    temp_word = ""
    bit_list = []
    for c in _dottedMask:
        if(c!="."):
            temp_word+=c
        else:
            st_list.append(temp_word)
            temp_word=""
    st_list.append(temp_word)
    for w in st_list:
        bit_list.extend(toBin(int(w),8))
    for i in range(len(bit_list)):
        if bit_list[i]==0:
            return i
    return len(bit_list)
        

# Convert Decimal to Binary
def toBin(value: int, fill: int = 0):
    bitlist = []
    while True:
        bitlist.append(value % 2)
        value = int(value/2)
        if (value == 0):
            break
    while (len(bitlist) < fill):
        bitlist.append(0)
    bitlist.reverse()
    return bitlist

# Convert Binary to Decimal
def toDec(_bitlist: list):
    _bitlist.reverse()
    temp = 0
    for i in range(len(_bitlist)):
        temp = temp+_bitlist[i]*2**i
    return temp

# Given an IP address and the mask, return the subnet
def getSubnet(_ip: str, _mask: str):
    ip_quarters_dec = []
    temp = ""
    for i in range(len(_ip)):
        if (_ip[i] != '.'):
            temp += _ip[i]
        else:
            ip_quarters_dec.append(temp)
            temp = ""
    ip_quarters_dec.append(temp)
    mask_quarters_dec = []
    temp = ""
    for i in range(len(_mask)):
        if (_mask[i] != '.'):
            temp += _mask[i]
        else:
            mask_quarters_dec.append(temp)
            temp = ""
    mask_quarters_dec.append(temp)
    binIp = [toBin(int(ip_quarters_dec[0]), 8),
             toBin(int(ip_quarters_dec[1]), 8),
             toBin(int(ip_quarters_dec[2]), 8),
             toBin(int(ip_quarters_dec[3]), 8)]
    binMask = [toBin(int(mask_quarters_dec[0]), 8),
               toBin(int(mask_quarters_dec[1]), 8),
               toBin(int(mask_quarters_dec[2]), 8),
               toBin(int(mask_quarters_dec[3]), 8)]
    intmask = 0
    for i in range(4):
        for j in range(8):
            if binMask[i][j] == 0:
                binIp[i][j] = 0
            else:
                intmask += 1
    res = str(toDec(binIp[0]))+"."+str(toDec(binIp[1])) + "." + \
        str(toDec(binIp[2]))+"."+str(toDec(binIp[3]))+"/"+str(intmask)
    return res

# Get all the available nodes, using nmap
def netScan(verbosity: int = 0):
    interfaces = netifaces.interfaces()
    subnetList = []
    for i in range(len(interfaces)):
        info = netifaces.ifaddresses(str(interfaces[i]))
        if (info[2][0]["addr"] != "127.0.0.1"):
            temp = getSubnet(info[2][0]["addr"], info[2][0]["netmask"])
            if (temp != "172.17.0.0/16"):
                subnetList.append(temp)

    foundHosts = []
    start_time = time.time()
    for i in range(len(subnetList)):
        start_time2 = time.time()
        if (verbosity > 0):
            print(f"Scanning : {subnetList[i]}...")
        nm = nmap.PortScanner()
        nm.scan(hosts=subnetList[i], arguments="-sn")
        for i in range(len(nm.all_hosts())):
            foundHosts.append(nm.all_hosts()[i])
        if (verbosity > 0):
            print("--- %s seconds ---" % round((time.time() - start_time2), 2))

    if (verbosity > 0):
        for i in range(len(foundHosts)):
            print(foundHosts[i])
    if (verbosity > 0):
        print("TOTAL --- %s seconds ---" %
              round((time.time() - start_time), 2))
    return foundHosts


