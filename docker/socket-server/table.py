import pyroute2
import socket
from netlib import intMask, dottedMask
import os

def exists(elem,lroutes:list):
    for r in lroutes:
        if (elem==r):return True
    return False
        

class Table:
    
    routes = [] # List of current routes

    # Return True if the route is present
    def isPresent(self, IP: str, Mask: str, Gateway: str):
        temp = False
        for route in self.routes:
            if (route["Destination"] == IP and route["Netmask"] == Mask and route["Gateway"] == Gateway):
                temp = True
        return temp

    # Return the index of a route if present, return -1 absent
    def getIndex(self, IP: str, Mask: str, Gateway: str):
        for i in range(len(self.routes)):
            if (self.routes[i]["Destination"] == IP and self.routes[i]["Netmask"] == Mask and self.routes[i]["Gateway"] == Gateway):
                return i
        return -1

    # Delete a given route
    def delete(self, IP: str, Mask: str, Gateway: str):
        for route in self.routes:
            if (route["Destination"] == IP and route["Netmask"] == Mask and route["Gateway"] == Gateway):
                self.routes.remove(route)

    # Search for kernel-defined routes in the system (Directly connected devices)
    def obtainOwn(self):
        # print("DEBUG_1\n")
        temproute = []

        ipr = pyroute2.IPRoute()
        routes = ipr.get_routes(family=socket.AF_INET)
        ipr.close()

        lroutes = []
        for route in routes:

            entry = {}
            entry["Mask"] = route["dst_len"]
            for (a, b) in route["attrs"]:
                entry[a] = b

            if (entry["RTA_TABLE"] == 254 and
                    entry.get("RTA_PREFSRC") != None and
                    entry.get("RTA_DST") != None and
                    entry["RTA_DST"].startswith("172") == False
                ):
                lroutes.append(entry)
                
        # print("DEBUG_2\n")
        for route in lroutes:
            temproute.append({
                "Destination": route["RTA_DST"],
                "Netmask": dottedMask(int(route["Mask"])),
                "Gateway": "SELF",
                "Cost": 0,
                "Timer": -1,
                "Status": "Fixed",
                "OS_Table": "present"
            })
        # print("DEBUG_3\n")
        remember = -1
        for i in range(len(self.routes)):
            if(self.routes[i]["Status"]=="Fixed"):
                if (exists(self.routes[i],temproute)==False):
                    remember = i
        if (remember!=-1):
            self.routes.pop(remember)
        # print("DEBUG_4\n")
        for route in temproute:
            if (exists(route,self.routes)==False):
                self.routes.append(route)
        # print("DEBUG_5\n")
        
        
        

    # Add an entry to the routing table
    def addroute(self, Destination: str, Netmask: str, Gateway: str, Cost: int, Timer: int, Status: str):
        self.routes.append({
            "Destination": Destination,
            "Netmask": Netmask,
            "Gateway": Gateway,
            "Cost": Cost,
            "Timer": Timer,
            "Status": Status,
            "OS_Table": "absent"
        })

    # Clear the whole table, and then obtain default routes
    def flush(self):
        self.routes = []
        self.obtainOwn()

    # Print the table
    def printall(self):
        print("___________________________________________________________________________________________")
        print("   Destination       Netmask           Gateway           Cost  Timer  Status      OS_Table")
        print("¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯")
        for i in range(len(self.routes)):
            print(str(i).ljust(3),end="")
            print(str(self.routes[i]["Destination"]).ljust(17), end=" ")
            print(str(self.routes[i]["Netmask"]).ljust(17), end=" ")
            print(str(self.routes[i]["Gateway"]).ljust(17), end=" ")
            print(str(self.routes[i]["Cost"]).ljust(5), end=" ")
            print(str(self.routes[i]["Timer"]).ljust(6), end=" ")
            print(str(self.routes[i]["Status"]).ljust(11), end=" ")
            print(str(self.routes[i]["OS_Table"]).ljust(11))

    # Clean-up bad routes (version 1), not in use
    def clean(self):
        temp = []
        for i in range(len(self.routes)):
            if (self.routes[i]["Cost"] <= 15 and self.routes[i]["Status"] != "toFlush"):
                temp.append(self.routes[i])
            elif (self.routes[i]["Status"] == "Invalid"):
                if (self.routes[i]["OS_Table"] == "present"):
                    self.setRouteOFF(i)
        self.routes = temp
        # print("check")
    
    # Clean-up bad routes (version 2), in use   
    def clean2(self):
        for i in range(len(self.routes)):
            if ((self.routes[i]["Cost"] >15 or self.routes[i]["Status"] == "Invalid") and self.routes[i]["OS_Table"]=="present"):
                self.setRouteOFF(i)
        for route in self.routes:
            if(route["Status"]=="toFlush"):
                self.routes.remove(route)

    # Set a given route in the OS routing table        
    def setRouteON(self, index: int):
        line = "ip route add "
        line += self.routes[index]["Destination"]
        line += "/"
        line += str(intMask(self.routes[index]["Netmask"]))
        line += " via "
        line += self.routes[index]["Gateway"]
        line += " metric 55"
        # print(f"RULE IS: {line}\n")
        if (os.system(line) == 0):
            # print("SUCCESS!\n")
            self.routes[index]["OS_Table"] = "present"
        else:
            print("Route-on: FAIL!\n")

    # Remove a given route from the OS routing table   
    def setRouteOFF(self, index: int):
        line = "ip route del "
        line += self.routes[index]["Destination"]
        line += "/"
        line += str(intMask(self.routes[index]["Netmask"]))
        line += " via "
        line += self.routes[index]["Gateway"]
        line += " metric 55"
        # print(f"RULE IS: {line}\n")
        if (os.system(line) == 0):
            # print("SUCCESS!\n")
            self.routes[index]["OS_Table"] = "absent"
        else:
            print("Route-off: FAIL!\n")

    # Given a route, return the index of the route that is active for that destination
    def indexOfPresent(self, ind: int):
        for i in range(len(self.routes)):
            if (self.routes[i]["Destination"] == self.routes[ind]["Destination"] and
                    self.routes[i]["Netmask"] == self.routes[ind]["Netmask"]):
                if (self.routes[i]["OS_Table"] == "present" and i != ind):
                    # print(f"RETURN INDEX {i} of already existing route")
                    # print(f"CURRENT ROUTE IS :{self.routes[ind]}")
                    # print(f"(OLD) ROUTE IS :{self.routes[i]}")
                    return i
        # print("RETURNED -1\n")
        return -1

    # Return true if the given route is the best route
    def isBest(self, index: int):
        check = True
        for i in range(len(self.routes)):
            if (self.routes[i]["Destination"] == self.routes[index]["Destination"] and
                    self.routes[i]["Netmask"] == self.routes[index]["Netmask"]):
                if (self.routes[i]["Cost"] < self.routes[index]["Cost"] and (self.routes[i]["Status"] == "Active" or self.routes[i]["Status"] == "Waiting")):
                    check = False
                    # print(f"RETURN INDEX {i} of better route")
                    # print(f"CURRENT ROUTE IS :{self.routes[index]} at index {index}")
                    # print(f"BETTER ROUTE IS :{self.routes[i]}")
                elif (self.routes[i]["Cost"] == self.routes[index]["Cost"] and self.routes[i]["OS_Table"] == "present"):
                    check = False
        # if(check==False):print(f"Result of isBest({self.routes[index]})=FALSE")
        return check

    # Set routing rules in the OS-routing table
    def updateOSTable(self):
        for i in range(len(self.routes)):
            if (self.routes[i]["Status"] == "Active" or self.routes[i]["Status"] == "Waiting"):
                if (self.isBest(i) and self.routes[i]["OS_Table"] == "absent" and self.routes[i]["Status"] != "Fixed"):
                    indp = self.indexOfPresent(i)
                    if (indp != -1):
                        self.setRouteOFF(indp)
                    self.setRouteON(i)
