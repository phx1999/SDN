"""Example Topology Manager Template
CSCI1680

This class is meant to serve as an example for how you can track the
network's topology from netwokr events.

**You are not required to use this file**: feel free to extend it,
change its structure, or replace it entirely.

"""

from ryu.topology.switches import Port, Switch, Link
import heapq


class Device():
    """Base class to represent an device in the network.

    Any device (switch or host) has a name (used for debugging only)
    and a set of neighbors.
    """

    def __init__(self, name):
        self.name = name
        self.neighbors = set()

    def __str__(self):
        return "{}({})".format(self.__class__.__name__,
                               self.name)


class TMSwitch(Device):
    """Representation of a switch, extends Device

    This class is a wrapper around the Ryu Switch object,
    which contains information about the switch's ports
    """

    def __init__(self, name, switch):
        super(TMSwitch, self).__init__(name)

        self.switch = switch
        self.neighbors = []
        # TODO:  Add more attributes as necessary

    def get_dpid(self):
        """Return switch DPID"""
        return self.switch.dp.id

    def get_ports(self):
        """Return list of Ryu port objects for this switch
        """
        return self.switch.ports

    def get_dp(self):
        """Return switch datapath object"""
        return self.switch.dp

    def add_neighbor(self, dst):
        self.neighbors.append(dst)

    def delete_neighbor(self, dst):
        for des_swi in self.neighbors:
            if des_swi.dpid == dst.dpid:
                self.neighbors.remove(des_swi)

    # . . .


class TMHost(Device):
    """Representation of a host, extends Device

    This class is a wrapper around the Ryu Host object,
    which contains information about the switch port to which
    the host is connected
    """

    def __init__(self, name, host):
        super(TMHost, self).__init__(host)

        self.host = host
        self.switch_id = host.port.dpid
        self.switch_port = host.port.port_no
        # TODO:  Add more attributes as necessary

    def get_mac(self):
        return self.host.mac

    def get_ips(self):
        return self.host.ipv4

    def get_port(self):
        """Return Ryu port object for this host"""
        return self.host.port

    # . . .


class TopoManager():
    """
    Example class for keeping track of the network topology

    """

    def __init__(self):
        # TODO:  Initialize some data structures
        self.all_devices = []
        self.switches = []
        self.hosts = []
        self.flow_table = {}
        self.list = []
        pass

    def add_switch(self, sw):
        name = "switch_{}".format(sw.dp.id)
        switch = TMSwitch(name, sw)

        self.all_devices.append(switch)
        self.switches.append(switch)

        # TODO:  Add switch to some data structure(s)

    def add_host(self, h):
        name = "host_{}".format(h.mac)
        host = TMHost(name, h)

        self.all_devices.append(host)
        self.hosts.append(host)

        # TODO:  Add host to some data structure(s)

    def add_link(self, src, dst):
        for s in self.switches:
            if s.get_dpid() == src.dpid:
                s.add_neighbor(dst)
            elif s.get_dpid() == dst.dpid:
                s.add_neighbor(src)

    def dele_link(self, src, dst):
        for s in self.switches:
            if s.get_dpid() == src.dpid:
                s.delete_neighbor(dst)
            elif s.get_dpid() == dst.dpid:
                s.delete_neighbor(src)

    def dele_switch(self, switch):
        sw = None
        for s in self.switches:
            if s.get_dpid() == switch.dp.id:
                sw = s
                break
        for n in sw.neighbors:
            swDst = None
            for s in self.switches:
                if s.get_dpid() == n.dpid:
                    swDst = s
            swDst.delete_neighbor(switch)
        self.all_devices.remove(sw)
        self.switches.remove(sw)

    def init_distance(self, s):
        distance = {}
        for sw in self.switches:
            if sw.get_dpid() != s:
                distance[sw.get_dpid()] = 999999
            else:
                distance[sw.get_dpid()] = 0
                # self.list[s][sw.get_dpid()] = s
        return distance

    def dijkstra(self):
        self.list = []
        self.flow_table = {}
        for i in range(len(self.switches) + 1):
            dict1 = {}
            self.list.append(dict1)
            del dict1
        for sw in self.switches:
            sID = sw.get_dpid()
            heap = []
            heapq.heappush(heap, (sID, 0))
            visited = []
            dist = self.init_distance(sID)

            while len(heap) > 0:
                Min = heapq.heappop(heap)
                switch = Min[0]
                distance = Min[1]
                visited.append(sID)
                neighbor = []
                for i in self.switches:
                    if i.get_dpid() == switch:
                        neighbor = i.neighbors
                for node in neighbor:
                    dst = node.dpid
                    if dst not in visited and distance + 1 < dist[dst]:
                        dist[dst] = distance + 1
                        heapq.heappush(heap, (dst, distance + 1))
                        self.list[sID][dst] = switch
                        self.flow_table[(dst, sID)] = node.port_no

    def shortest_path(self, root):
        List = [[] for i in range(len(self.switches) + 1)]
        for sw in self.switches:
            sID = sw.get_dpid()
            if (root, sID) not in self.flow_table.keys() or (sID, root) not in self.flow_table.keys():
                continue
            if sID != root:
                List[sID].append(sID)
                tmp = sID
                if root >= len(self.list):
                    continue
                x = tmp in self.list[root].keys()
                count = 0
                while x and self.list[root][tmp] != root:
                    count += 1
                    tmp = self.list[root][tmp]
                    List[sID].insert(0, tmp)
                List[sID].insert(0, root)
        return List

    def topology_graph(self):
        graph = set()
        for sw in self.switches:
            for n in sw.neighbors:
                graph.add((sw.get_dpid(), n.dpid))
        return graph

    # . . .
