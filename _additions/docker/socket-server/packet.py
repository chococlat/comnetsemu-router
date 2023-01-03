# PACKET EXAMPLE:
#
#      command:version:
#      family:routetag:ipaddress:subnet:nexthop:metric
#      family:routetag:ipaddress:subnet:nexthop:metric
#      family:routetag:ipaddress:subnet:nexthop:metric
#      ...


class RIPPacket:

    def __new__(cls, *args, **kwargs):
        return super().__new__(cls)
    
    def __init__(self):
        self.command = ""
        self.version = ""
        self.entries = []

    # Importing data from a byte-string
    def str_import(self, byteString: bytes):
        rawstring = byteString.decode("utf-8")
        self.entries.clear()
        blocks = []
        temp = ""
        for c in range(len(rawstring)):
            if (rawstring[c] != ":"):
                temp += rawstring[c]
            else:
                blocks.append(temp)
                temp = ""
        blocks.append(temp)
        self.command = blocks.pop(0)
        self.version = blocks.pop(0)

        for i in range(len(blocks)//6):
            entry = {"Family": blocks[0+i*6],
                     "RouteTag": blocks[1+i*6],
                     "IPAddress": blocks[2+i*6],
                     "SubnetMask": blocks[3+i*6],
                     "NextHop": blocks[4+i*6],
                     "Metric": blocks[5+i*6]
                     }
            self.entries.append(entry)
            
    # Importing data to a byte-string
    def str_export(self) -> bytes:
        temp = ""
        temp += str(self.command)+":"
        temp += str(self.version)+":"
        for i in range(len(self.entries)):
            temp += str(self.entries[i]["Family"])+":"
            temp += str(self.entries[i]["RouteTag"])+":"
            temp += str(self.entries[i]["IPAddress"])+":"
            temp += str(self.entries[i]["SubnetMask"])+":"
            temp += str(self.entries[i]["NextHop"])+":"
            temp += str(self.entries[i]["Metric"])+":"
        return bytes(temp[:-1], "utf-8")

    # print the packet
    def print(self):
        print(f"Command: {self.command} - Version: {self.version}")
        for i in range(len(self.entries)):
            print(self.entries[i])
