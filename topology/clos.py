from mininet.net import Mininet
from mininet.topo import Topo
from mininet.link import Link, Intf
from mininet.log import setLogLevel, info
from mininet.cli import CLI
from p4_mininet import P4Switch, P4Host

import argparse
import time
import os
import redis
import socket

import link_status_pb2

os.system("sudo mn -c")


class MyTopo():

    def __init__(self):

        self.sw_path = "/usr/local/bin/simple_switch"
        self.json_path = "../p4_source_code/my_int.json"
        self.thrift_port = 9090
        self.device_id = 1
        self.pcap_dump = False

        self.spine_sw_list = []
        self.leaf_sw_list = []
        self.tor_sw_list = []
        self.s0 = None
        self.h_list = []

        self.net = Mininet(host=P4Host,
                           switch=P4Switch,
                           controller=None)

        self.r1 = redis.Redis(host='localhost', port=6379,
                              db=1, decode_responses=True)
        self.r2 = redis.Redis(host='localhost', port=6379,
                              db=2, decode_responses=True)

    def CreateNet(self):

        spine_num = 2
        set_num = 2
        leaf_num = set_num
        tor_num = 2
        h_num = 2
        pod_num = 2

        # Create spine switch
        for i in xrange(set_num):
            self.spine_sw_list.append([])
            for j in xrange(spine_num):
                sw = self.net.addSwitch('s%d_s%d' % (i + 1, j + 1),
                                        sw_path=self.sw_path,
                                        json_path=self.json_path,
                                        thrift_port=self.thrift_port,
                                        nanolog="ipc:///tmp/bm-%d-log.ipc" % self.device_id,
                                        device_id=self.device_id,
                                        pcap_dump=self.pcap_dump)
                self.r2.set('sw%d' % self.device_id, 's%d_s%d' %
                            (i + 1, j + 1))
                self.spine_sw_list[i].append(sw)
                self.thrift_port += 1
                self.device_id += 1

        # Create leaf switch
        for i in xrange(pod_num):
            self.leaf_sw_list.append([])
            for j in xrange(leaf_num):
                sw = self.net.addSwitch('p%d_l%d' % (i + 1, j + 1),
                                        sw_path=self.sw_path,
                                        json_path=self.json_path,
                                        thrift_port=self.thrift_port,
                                        nanolog="ipc:///tmp/bm-%d-log.ipc" % self.device_id,
                                        device_id=self.device_id,
                                        pcap_dump=self.pcap_dump)
                self.r2.set('sw%d' % self.device_id, 'p%d_l%d' %
                            (i + 1, j + 1))
                self.leaf_sw_list[i].append(sw)
                self.thrift_port += 1
                self.device_id += 1

        # Create tor switch
        for i in xrange(pod_num):
            self.tor_sw_list.append([])
            for j in xrange(tor_num):
                sw = self.net.addSwitch('p%d_t%d' % (i + 1, j + 1),
                                        sw_path=self.sw_path,
                                        json_path=self.json_path,
                                        thrift_port=self.thrift_port,
                                        nanolog="ipc:///tmp/bm-%d-log.ipc" % self.device_id,
                                        device_id=self.device_id,
                                        pcap_dump=self.pcap_dump)
                self.r2.set('sw%d' % self.device_id, 'p%d_t%d' %
                            (i + 1, j + 1))
                self.tor_sw_list[i].append(sw)
                self.thrift_port += 1
                self.device_id += 1

        # Connect spine switch and leaf switch
        for i in xrange(set_num):
            for j in xrange(spine_num):
                for k in xrange(pod_num):
                    self.net.addLink(
                        self.spine_sw_list[i][j], self.leaf_sw_list[k][i])
                    self.r1.set(
                        '%s--%s' % (self.spine_sw_list[i][j].name, self.leaf_sw_list[k][i].name), "Spine-Leaf")

        # Connect leaf switch and tor switch
        for i in xrange(pod_num):
            for j in xrange(leaf_num):
                for k in xrange(tor_num):
                    self.net.addLink(
                        self.leaf_sw_list[i][j], self.tor_sw_list[i][k])
                    self.r1.set(
                        '%s--%s' % (self.leaf_sw_list[i][j].name, self.tor_sw_list[i][k].name), "Leaf-ToR")

        # Connect tor switch and host
        for i in xrange(pod_num):
            self.h_list.append([])
            for j in xrange(tor_num):
                self.h_list[i].append([])
                for k in xrange(h_num):
                    h = self.net.addHost('p%d_t%d_%d' % (i + 1, j + 1, k+1),
                                         ip='10.%d.%d.%d/32' % (i+1, j+1, k+1),
                                         mac='00:00:00:%s:%s:%s' % (hex(i+1)[2:], hex(j+1)[2:], hex(k+1)[2:]))
                    self.net.addLink(h, self.tor_sw_list[i][j])
                    self.h_list[i][j].append(h)

        self.net.start()

        os.system("sudo sh dump_flow_table.sh")

        for i in xrange(pod_num):
            for j in xrange(tor_num):
                for k in xrange(h_num):
                    h = self.h_list[i][j][k]
                    # h.cmd('../packet/recv >../packet/tmp/10_%d_%d_%d_recv &' % (i+1, j+1, k+1))
                    h.cmd('../packet/recv >../packet/tmp/10_%d_%d_%d_recv >/dev/null &'% (i+1, j+1, k+1))

        for i in xrange(pod_num):
            for j in xrange(tor_num):
                for k in xrange(h_num):
                    h = self.h_list[i][j][k]
                    # h.cmd('../packet/send >../packet/tmp/10_%d_%d_%d_send &' % (i+1, j+1, k+1))
                    h.cmd('../packet/send >../packet/tmp/10_%d_%d_%d_send >/dev/null &'% (i+1, j+1, k+1))

        # ################################################
        # Testing part:

        # Socket for changing link status
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        if os.path.exists("./link_status_socket"):
            os.unlink("./link_status_socket")
        sock.bind("./link_status_socket")
        sock.listen(5)

        # Receiving cmd...
        while True:
            conn, clientAddr = sock.accept()
            message = conn.recv(1024)
            if message:
                cmd = link_status_pb2.LinkStatus()
                cmd.ParseFromString(message)
                self.net.configLinkStatus(cmd.node_1, cmd.node_2, cmd.status)
                print("%s--%s--%s" % (cmd.node_1, cmd.node_2, cmd.status))
        # ################################################

        CLI(self.net)
        self.net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    test = MyTopo()
    test.CreateNet()
