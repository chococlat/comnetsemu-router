from mininet.node import  Host
from comnetsemu.net import Containernet
from comnetsemu.node import DockerHost

# For the implementation of basicRouter, two classes are inherited:
#
# -  Topo from mininet.topo ---------------> addRouter() from addNode()
# -  Containernet from comnetsemu.net -----> addRouter() from addHost()  (maybe different name?)


class Routernet(Containernet):

    def addRouter(self, name: str, **params):

        # ip=None : workaround to avoid the auto assignment of ip (10.0.0.x) when first link is created
        r = self.addHost(name, cls=BasicRouter, ip=None, **params)
        return r

    def addDockerRouter(self, name: str,**params):

        # ip=None : workaround to avoid the auto assignment of ip (10.0.0.x) when first link is created
        r = self.addHost(
            name,cls=DockerRouter,ip=None,dimage="d_router",
            docker_args={"cpuset_cpus": "0", "nano_cpus": int(1e8)}, 
            **params)
        return r




class RNET_Host(DockerHost):
    """ predefined routes on dockerhosts
    """

    def setPseudoGateway(self, pseudo_gateway: str, destinationIP: str = None):
        """
        Set a pseudo-default gateway, so that private ip addresses dont try to use the default gateway 172.x.x.x .
        If only <gateway> parameter is used, the following rules are added:
        -> ip route add 192.168.0.0/16 via <pseudo_gateway>
        -> ip route add 10.0.0.0/8 via <pseudo_gateway>

        Args:
            pseudo_gateway (str): The gateway to use.
            destinationIP (str, optional): The ip address/(or pool) included in the rule.
        """
        if (destinationIP != None):
            self.cmd("ip route add " + destinationIP +
                     " via " + pseudo_gateway)
        else:
            print(self.cmd("ip route add 192.168.0.0/16 via " + pseudo_gateway))
            print(self.cmd("ip route add 10.0.0.0/8 via " + pseudo_gateway))
    
    

class BasicRouter(Host):
    """
    A Router class inherited from mininet Node.
    """
    
    def config(self, **params):

        super(BasicRouter, self).config(**params)
        self.cmd('sysctl net.ipv4.ip_forward=1')

    def terminate(self):
        self.cmd('sysctl net.ipv4.ip_forward=0')
        super(BasicRouter, self).terminate()

    def addStaticRoute(self, destinationIP: str,  gateway: str = None, device: str = None, metric: int = None):
        """Add a static routing rule

        Args:
            destinationIP (str): Destination of the packets
            prefixLen (int): Netmask/Genmask of the destinationIP
            gateway (str): Where the packets must be redirected
            device (str): Wich network interface/card must be used
            metric (int): Wich metric/priority must be associated with this routing rule
        """
        cline = destinationIP
        if (gateway!=None):
            cline +=" via " +gateway
        if (device!=None):
            cline +=" dev " +device
        if (metric!=None):
            cline +=" metric " +str(metric)
        print("\nAdding the rule:" + cline)
        print(f"On node: {self}")
        print("OUTPUT IS: "+self.cmd("sudo ip route add " + cline))
        self.static_routes.append(cline)


class DockerRouter(DockerHost):
    
    def initStaticRoutes(self):
        self.static_routes=[]
        
    def addStaticRoute(self, destinationIP: str,  gateway: str = None, device: str = None, metric: int = None):
        """Add a static routing rule

        Args:
            destinationIP (str): Destination of the packets
            prefixLen (int): Netmask/Genmask of the destinationIP
            gateway (str): Where the packets must be redirected
            device (str): Wich network interface/card must be used
            metric (int): Wich metric/priority must be associated with this routing rule
        """
        
        cline = destinationIP
        if (gateway!=None):
            cline +=" via " +gateway
        if (device!=None):
            cline +=" dev " +device
        if (metric!=None):
            cline +=" metric " +str(metric)
        print("\nAdding the rule:" + cline)
        print(f"On node: {self}")
        print(" "+self.cmd("ip route add " + cline))
        self.static_routes.append(cline)
    
    def clearStaticRoutes(self):
        for route in self.static_routes:
            print(" \n"+self.cmd("ip route del " + route))
        self.static_routes.clear()
    

