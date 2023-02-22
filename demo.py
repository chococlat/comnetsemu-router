#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
"""
About: Testing basicRouter with the following topology:

    h1 - r1 --- r2 - h2
         |       |
         |       |
    h4 - r4 --- r3 - h3

"""

from mininet.link import TCLink
from mininet.log import info, setLogLevel
from mininet.node import Controller
from basicRouter import Routernet,RNET_Host
# from mininet.net import CLI
from comnetsemu.cli import CLI, spawnXtermDocker
import os

def run_net():

    net = Routernet(controller=Controller, link=TCLink)
    
    info("*** Adding controller\n")
    net.addController("c0")

    info("*** Adding hosts\n")
    h1 = net.addHost(
        "h1",
        cls=RNET_Host,
        dimage="d_host",
        ip="192.168.51.101/24",
        docker_args={
            "cpuset_cpus": "0", 
            "nano_cpus": int(1e8)
            },
    )
    h2 = net.addHost(
        "h2",
        cls=RNET_Host,
        dimage="d_host",
        ip="192.168.52.101/24",
        docker_args={
            "cpuset_cpus": "0", 
            "nano_cpus": int(1e8)
            },
    )
    h3 = net.addHost(
        "h3",
        cls=RNET_Host,
        dimage="d_host",
        ip="192.168.53.101/24",
        docker_args={
            "cpuset_cpus": "0", 
            "nano_cpus": int(1e8)
            },
    )
    h4 = net.addHost(
        "h4",
        cls=RNET_Host,
        dimage="d_host",
        ip="192.168.54.101/24",
        docker_args={
            "cpuset_cpus": "0", 
            "nano_cpus": int(1e8)
            },
    )
    
    info("*** Adding router\n")
    
    r1=net.addDockerRouter("r1")
    r2=net.addDockerRouter("r2")
    r3=net.addDockerRouter("r3")
    r4=net.addDockerRouter("r4")
    
    info("*** Creating links\n")
    net.addLink(h1, r1, bw=10, delay="10ms", intfName1="h1-r1", intfName2="r1-h1")
    net.addLink(h2, r2, bw=10, delay="10ms", intfName1="h2-r2", intfName2="r2-h2")
    net.addLink(h3, r3, bw=10, delay="10ms", intfName1="h3-r3", intfName2="r3-h3")
    net.addLink(h4, r4, bw=10, delay="10ms", intfName1="h4-r4", intfName2="r4-h4")
    
    net.addLink(r1, r2, bw=10, delay="10ms", intfName1="r1-r2", intfName2="r2-r1")
    net.addLink(r2, r3, bw=10, delay="10ms", intfName1="r2-r3", intfName2="r3-r2")
    net.addLink(r3, r4, bw=10, delay="10ms", intfName1="r3-r4", intfName2="r4-r3")
    net.addLink(r4, r1, bw=10, delay="10ms", intfName1="r4-r1", intfName2="r1-r4")
        
    r1.setIP("10.51.0.1",30,"r1-r2")
    r1.setIP("10.54.0.2",30,"r1-r4")
    r1.setIP("192.168.51.1",24,"r1-h1")
    
    r2.setIP("10.52.0.1",30,"r2-r3")
    r2.setIP("10.51.0.2",30,"r2-r1")
    r2.setIP("192.168.52.1",24,"r2-h2")
    
    r3.setIP("10.53.0.1",30,"r3-r4")
    r3.setIP("10.52.0.2",30,"r3-r2")
    r3.setIP("192.168.53.1",24,"r3-h3")
    
    r4.setIP("10.54.0.1",30,"r4-r1")
    r4.setIP("10.53.0.2",30,"r4-r3")
    r4.setIP("192.168.54.1",24,"r4-h4")
    

    info("\n\n*** Disabling ip forwarding on comnetsemu VM ...\n")
    os.system("sudo sysctl net.ipv4.ip_forward=0")
    info("\n*** Starting network\n")
    net.start()
    
    h1.setPseudoGateway("192.168.51.1")
    h2.setPseudoGateway("192.168.52.1")
    h3.setPseudoGateway("192.168.53.1")
    h4.setPseudoGateway("192.168.54.1")
        
    ######################################
    #### BEGINNING OF TESTING SECTION ####
    ######################################
    
    
    #### STATIC ROUTES
    info("*** TESTING STATIC ROUTES  ***\n")
    r1.initStaticRoutes()
    r1.addStaticRoute("192.168.52.0/24","10.51.0.2")
    r2.initStaticRoutes()
    r2.addStaticRoute("192.168.51.0/24","10.51.0.1",metric=22)
    
    info("*** Ping from h1 to h2 ***\n\n")
    print(h1.cmd("ping -c3 192.168.52.101"))
    
    info("*** Trace Route from h1 to h2 ***\n\n")
    print(h1.cmd("traceroute 192.168.52.101"))
    
    info("*** REMOVING STATIC ROUTES ***\n")
    r1.clearStaticRoutes()
    
    
    
    info("\n\n\n\n\n*** STARTING ROUTER TERMINALS ***\n")
    
    #### MANUAL START
    spawnXtermDocker("r1")
    spawnXtermDocker("r2")
    spawnXtermDocker("r3")
    spawnXtermDocker("r4")
    
    info("Execute the following command on the routers terminals to start the routing protocol:\n \"python3 ./home/main.py\"\n\n")
    info("CHANGING THE NETWORK WHILE ROUTING PROTOCOLS ARE RUNNING:")
    input("\npress ENTER to disable the interface r1-r2 on router r1")
    print(r1.cmd("ifconfig r1-r2 down"))
    input("\npress ENTER to enable the interface r1-r2 on router r1")
    print(r1.cmd("ifconfig r1-r2 up"))
    
    if True:  ## cmd CLI
        mainLoop=True
        innerLoop=True
        while mainLoop:
            choice = input("cmd: ")
            if (choice=="r1"):
                innerLoop=True
                while innerLoop:
                    innerchoice = input("cmd/r1: ")
                    if(innerchoice!="exit"):
                        print(r1.cmd(innerchoice))
                    else :
                        innerLoop=False
            elif (choice=="r2"):
                innerLoop=True
                while innerLoop:
                    innerchoice = input("cmd/r2: ")
                    if(innerchoice!="exit"):
                        print(r2.cmd(innerchoice))
                    else :
                        innerLoop=False
            elif (choice=="r3"):
                innerLoop=True
                while innerLoop:
                    innerchoice = input("cmd/r3: ")
                    if(innerchoice!="exit"):
                        print(r3.cmd(innerchoice))
                    else :
                        innerLoop=False
            elif (choice=="r4"):
                innerLoop=True
                while innerLoop:
                    innerchoice = input("cmd/r4: ")
                    if(innerchoice!="exit"):
                        print(r4.cmd(innerchoice))
                    else :
                        innerLoop=False
            elif (choice=="h1"):
                innerLoop=True
                while innerLoop:
                    innerchoice = input("cmd/h1: ")
                    if(innerchoice!="exit"):
                        print(h1.cmd(innerchoice))
                    else :
                        innerLoop=False
            elif (choice=="h2"):
                innerLoop=True
                while innerLoop:
                    innerchoice = input("cmd/h2: ")
                    if(innerchoice!="exit"):
                        print(h2.cmd(innerchoice))
                    else :
                        innerLoop=False
            elif (choice=="h3"):
                innerLoop=True
                while innerLoop:
                    innerchoice = input("cmd/h3: ")
                    if(innerchoice!="exit"):
                        print(h3.cmd(innerchoice))
                    else :
                        innerLoop=False
            elif (choice=="h4"):
                innerLoop=True
                while innerLoop:
                    innerchoice = input("cmd/h4: ")
                    if(innerchoice!="exit"):
                        print(h4.cmd(innerchoice))
                    else :
                        innerLoop=False
            elif (choice=="mininet"):
                CLI(net)
            elif (choice=="exit") :
                break

    
    ################################
    #### END OF TESTING SECTION ####
    ################################
    
    input("press enter to stop the network")
    info("*** Stopping network")
    net.stop()
    info("*** Enabling ip forwarding on comnetsemu VM ...\n")
    os.system("sudo sysctl net.ipv4.ip_forward=1")

if __name__ == "__main__":
    setLogLevel("info")
    run_net()
    