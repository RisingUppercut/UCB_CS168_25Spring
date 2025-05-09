"""
Your awesome Distance Vector router for CS 168

Based on skeleton code by:
  MurphyMc, zhangwen0411, lab352
"""

import sim.api as api
from cs168.dv import (
    RoutePacket,
    Table,
    TableEntry,
    DVRouterBase,
    Ports,
    FOREVER,
    INFINITY,
)


class DVRouter(DVRouterBase):

    # A route should time out after this interval
    ROUTE_TTL = 15

    # -----------------------------------------------
    # At most one of these should ever be on at once
    SPLIT_HORIZON = True
    POISON_REVERSE = False
    # -----------------------------------------------

    # Determines if you send poison for expired routes
    POISON_EXPIRED = False

    # Determines if you send updates when a link comes up
    SEND_ON_LINK_UP = False

    # Determines if you send poison when a link goes down
    POISON_ON_LINK_DOWN = False

    def __init__(self):
        """
        Called when the instance is initialized.
        DO NOT remove any existing code from this method.
        However, feel free to add to it for memory purposes in the final stage!
        """
        assert not (
            self.SPLIT_HORIZON and self.POISON_REVERSE
        ), "Split horizon and poison reverse can't both be on"

        self.start_timer()  # Starts signaling the timer at correct rate.

        # Contains all current ports and their latencies.
        # See the write-up for documentation.
        self.ports = Ports()

        # This is the table that contains all current routes
        self.table = Table()
        self.table.owner = self

        ##### Begin Stage 10A #####
        self.history = {}   # store dict {port : {dst, latency}}
        ##### End Stage 10A #####

    def add_static_route(self, host, port):
        """
        Adds a static route to this router's table.

        Called automatically by the framework whenever a host is connected
        to this router.

        :param host: the host.
        :param port: the port that the host is attached to.
        :returns: nothing.
        """
        # `port` should have been added to `peer_tables` by `handle_link_up`
        # when the link came up.
        assert port in self.ports.get_all_ports(), "Link should be up, but is not."

        ##### Begin Stage 1 #####
        self.table[host] = TableEntry(dst=host, port=port, 
                                     latency=self.ports.get_latency(port), expire_time=FOREVER)
        ##### End Stage 1 #####

    def handle_data_packet(self, packet, in_port):
        """
        Called when a data packet arrives at this router.

        You may want to forward the packet, drop the packet, etc. here.

        :param packet: the packet that arrived.
        :param in_port: the port from which the packet arrived.
        :return: nothing.
        """
        
        ##### Begin Stage 2 #####
        dst = packet.dst
        if not dst in self.table or self.table[dst].latency >= INFINITY:
            return
        self.send(packet, port=self.table[dst].port)
        ##### End Stage 2 #####

    def send_routes(self, force=False, single_port=None):
        """
        Send route advertisements for all routes in the table.

        :param force: if True, advertises ALL routes in the table;
                      otherwise, advertises only those routes that have
                      changed since the last advertisement.
               single_port: if not None, sends updates only to that port; to
                            be used in conjunction with handle_link_up.
        :return: nothing.
        """
        
        ##### Begin Stages 3, 6, 7, 8, 10 #####
        def actual_send(entry, out_port, is_poison_reverse):
            """
            Determines what the actual advertisement would look like if sent out of out_port.

            :param entry: the original entry in the routing table
            :param out_port: the port to send to
            :param is_poison_reverse: whether poison_reverse if enabled
            :return: the actual send advertisement
            """
            actual_latency = entry.latency
            if is_poison_reverse and entry.port == out_port:
                actual_latency = INFINITY

            return TableEntry(dst=entry.dst,
                              port=entry.port,
                              latency=min(actual_latency, INFINITY), 
                              expire_time=0) # expire_time typically not relevant for history comparison
        
        def is_in_history(self, send_entry, port):
            """
            Check whether the current advertisement is the same
            with the previous sent one(don't care about expire_time between each other).
            
            :param send_entry: the current advertisement being checked
            :param post: the port we want to send this advertisement to
            :return: nothing
            """
            dst = send_entry.dst
            if not (port in self.history):
                return False
            if not (dst in self.history[port]):
                return False
            return self.history[port][dst] == send_entry.latency
                          
        def update_history(self, send_entry, port):
            """
            Update history with the entry just sent

            :param send_entry: the current advertisement being checked
            :param post: the port we want to send this advertisement to
            :return: nothing
            """
            if port not in self.history:
                self.history[port] = {} 
            self.history[port][send_entry.dst] = send_entry.latency
            
            
        for dst, entry in self.table.items():
            for p in self.ports.get_all_ports():
                if single_port and p != single_port:
                    continue

                send_entry = actual_send(entry, p, self.POISON_REVERSE)
                if (not force and is_in_history(self, send_entry, p)):
                    continue
                if self.SPLIT_HORIZON and entry.port == p:
                    continue
                
                self.send_route(p, dst, send_entry.latency)
                
                if (not force):
                    update_history(self, send_entry, p)
        ##### End Stages 3, 6, 7, 8, 10 #####

    def expire_routes(self):
        """
        Clears out expired routes from table.
        accordingly.
        """
        
        ##### Begin Stages 5, 9 #####
        to_delete = []
        for dst, entry in self.table.items():
            if (entry.expire_time != FOREVER and 
               api.current_time() >= entry.expire_time):
                to_delete.append(dst)
    
        for dst in to_delete:
            if (not self.POISON_EXPIRED):
                self.table.pop(dst)
            else:
                temp = self.table[dst]
                self.table[dst] = TableEntry(dst=dst, port=temp.port, 
                                             latency=INFINITY, expire_time=api.current_time()+self.ROUTE_TTL)

        ##### End Stages 5, 9 #####

    def handle_route_advertisement(self, route_dst, route_latency, port):
        """
        Called when the router receives a route advertisement from a neighbor.

        :param route_dst: the destination of the advertised route.
        :param route_latency: latency from the neighbor to the destination.
        :param port: the port that the advertisement arrived on.
        :return: nothing.
        """
        
        ##### Begin Stages 4, 10 #####
        if (not route_dst in self.table or
            route_latency + self.ports.get_latency(port) < self.table[route_dst].latency or 
            self.table[route_dst].port == port):
            self.table[route_dst] = TableEntry(dst=route_dst, port=port, 
                                    latency=route_latency + self.ports.get_latency(port), 
                                    expire_time=api.current_time()+self.ROUTE_TTL)
            self.send_routes(force=False)


        ##### End Stages 4, 10 #####

    def handle_link_up(self, port, latency):
        """
        Called by the framework when a link attached to this router goes up.

        :param port: the port that the link is attached to.
        :param latency: the link latency.
        :returns: nothing.
        """
        self.ports.add_port(port, latency)

        ##### Begin Stage 10B #####
        if self.SEND_ON_LINK_UP:
            self.send_routes(force=True, single_port=port)
        ##### End Stage 10B #####

    def handle_link_down(self, port):
        """
        Called by the framework when a link attached to this router goes down.

        :param port: the port number used by the link.
        :returns: nothing.
        """
        self.ports.remove_port(port)

        ##### Begin Stage 10B #####
        to_delete = self.table.keys()
        
        if self.POISON_ON_LINK_DOWN:
            for dst, entry in self.table.items():
                if (entry.port == port):
                    poison = TableEntry(dst=dst, port=entry.port, 
                                        latency=INFINITY, expire_time=entry.expire_time)
                    self.table[dst] = poison
            self.send_routes(single_port=None)
        else:
            to_delete = []
            for dst, entry in self.table.items():
                if (entry.port == port):
                    to_delete.append(dst)
            for dst in to_delete:
                self.table.pop(dst)
                
        ##### End Stage 10B #####

    # Feel free to add any helper methods!
