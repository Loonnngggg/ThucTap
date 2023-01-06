#!/usr/bin/env python
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Node
from mininet.log import setLogLevel, info
from mininet.cli import CLI

# Đọc file input
with open('input.txt', 'r') as f:
    input = f.readlines()
data = []
for i in input:
    data.append(i.strip())

# Gắn địa chỉ cho các biến
ipnetwork1 = data[2]    # Địa chỉ ip mạng 1
ipnetwork2 = data[3]    # Địa chỉ ip mạng 2
ipr1_in = data[5]       # Địa chỉ ip router 1 trong mạng 1
ipr2_in = data[6]       # Địa chỉ ip router 2 trong mạng 2
ipr1_out = data[8]      # Địa chỉ ip router 1 ngoài mạng (trong 10.100.0.0)
ipr2_out = data[10]     # Địa chỉ ip router 2 ngoài mạng (trong 10.100.0.0)
iph1 = data[11]         # Địa chỉ ip host 1
iph2 = data[12]         # Địa chỉ ip host 2
iph3 = data[13]         # Địa chỉ ip host 3
iph4 = data[14]         # Địa chỉ ip host 4

####


class LinuxRouter(Node):
    def config(self, **params):
        super(LinuxRouter, self).config(**params)
        self.cmd('sysctl net.ipv4.ip_forward=1')

    def terminate(self):
        self.cmd('sysctl net.ipv4.ip_forward=0')
        super(LinuxRouter, self).terminate()


class NetworkTopo(Topo):
    def build(self, **_opts):
        # Thêm 2 router ở 2 mạng khác nhau
        r1 = self.addHost('r1', cls=LinuxRouter, ip=ipr1_in)
        r2 = self.addHost('r2', cls=LinuxRouter, ip=ipr2_in)

        # Thêm 2 switch
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')

        # Thêm link giữa router-switch
        self.addLink(s1,
                     r1,
                     intfName2='r1-eth1',
                     params2={'ip': ipr1_in})

        self.addLink(s2,
                     r2,
                     intfName2='r2-eth1',
                     params2={'ip': ipr2_in})

        # Thêm link giữa 2 router
        self.addLink(r1,
                     r2,
                     intfName1='r1-eth2',
                     intfName2='r2-eth2',
                     params1={'ip': ipr1_out},
                     params2={'ip': ipr2_out})

        # Thêm host
        h1 = self.addHost(name='h1',
                          ip=iph1,
                          defaultRoute='via ' + ipr1_in[:-3])
        h2 = self.addHost(name='h2',
                          ip=iph2,
                          defaultRoute='via ' + ipr1_in[:-3])
        h3 = self.addHost(name='h3',
                          ip=iph3,
                          defaultRoute='via ' + ipr2_in[:-3])
        h4 = self.addHost(name='h4',
                          ip=iph4,
                          defaultRoute='via ' + ipr2_in[:-3])

        # Thêm link giữa host-switch
        self.addLink(h1, s1)
        self.addLink(h2, s1)
        self.addLink(h3, s2)
        self.addLink(h4, s2)


def run():
    topo = NetworkTopo()
    net = Mininet(topo=topo)

    # Thêm định tuyến giữa 2 mạng
    info(net['r1'].cmd("ip route add " + ipnetwork2 + " via " + ipr2_out[:-3] + " dev r1-eth2"))
    # r1 cần đi đến mạng 2
    # ipnetwork2 là địa chỉ mạng cần đến, ipr2_out là địa chỉ IP next hop, r1-eth2 là exit interface
    info(net['r2'].cmd("ip route add " + ipnetwork1 + " via " + ipr1_out[:-3] + " dev r2-eth2"))
    # r2 cần đi đến mạng 1
    # ipnetwork1 là địa chỉ mạng cần đến, ipr1_out là địa chỉ IP next hop, r2-eth2 là exit interface

    net.start()
    CLI(net)
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    run()