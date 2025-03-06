import util

# Your program should send TTLs in the range [1, TRACEROUTE_MAX_TTL] inclusive.
# Technically IPv4 supports TTLs up to 255, but in practice this is excessive.
# Most traceroute implementations cap at approximately 30.  The unit tests
# assume you don't change this number.
TRACEROUTE_MAX_TTL = 30

# Cisco seems to have standardized on UDP ports [33434, 33464] for traceroute.
# While not a formal standard, it appears that some routers on the internet
# will only respond with time exceeeded ICMP messages to UDP packets send to
# those ports.  Ultimately, you can choose whatever port you like, but that
# range seems to give more interesting results.
TRACEROUTE_PORT_NUMBER = 33434  # Cisco traceroute port number.

# Sometimes packets on the internet get dropped.  PROBE_ATTEMPT_COUNT is the
# maximum number of times your traceroute function should attempt to probe a
# single router before giving up and moving on.
PROBE_ATTEMPT_COUNT = 3

class IPv4:
    # Each member below is a field from the IPv4 packet header.  They are
    # listed below in the order they appear in the packet.  All fields should
    # be stored in host byte order.
    #
    # You should only modify the __init__() method of this class.
    version: int
    header_len: int  # Note length in bytes, not the value in the packet.
    tos: int         # Also called DSCP and ECN bits (i.e. on wikipedia).
    length: int      # Total length of the packet.
    id: int
    flags: int
    frag_offset: int
    ttl: int
    proto: int
    cksum: int
    src: str
    dst: str

    def __init__(self, buffer: bytes):
        b = ''.join(format(byte, '08b') for byte in [*buffer])
        self.version = int(b[:4], 2)
        self.header_len = int(b[4:8], 2) * 4
        self.tos = int(b[8:16], 2)
        self.length = int(b[16:32], 2)
        self.id = int(b[32:48], 2)
        self.flags = int(b[48:51], 2)
        self.frag_offset = int(b[51:64], 2)
        self.ttl = int(b[64:72], 2)
        self.proto = int(b[72:80], 2)
        self.cksum = int(b[80:96], 2)
        self.src = '.'.join(str(int(b[i:i+8], 2)) for i in [96, 104, 112, 120])
        self.dst = '.'.join(str(int(b[i:i+8], 2)) for i in [128, 136, 144, 152])

    def __str__(self) -> str:
        return f"IPv{self.version} (tos 0x{self.tos:x}, ttl {self.ttl}, " + \
            f"id {self.id}, flags 0x{self.flags:x}, " + \
            f"ofsset {self.frag_offset}, " + \
            f"proto {self.proto}, header_len {self.header_len}, " + \
            f"len {self.length}, cksum 0x{self.cksum:x}) " + \
            f"{self.src} > {self.dst}"


class ICMP:
    # Each member below is a field from the ICMP header.  They are listed below
    # in the order they appear in the packet.  All fields should be stored in
    # host byte order.
    #
    # You should only modify the __init__() function of this class.
    type: int
    code: int
    cksum: int

    def __init__(self, buffer: bytes):
        b = ''.join(format(byte, '08b') for byte in [*buffer])
        self.type = int(b[:8], 2)
        self.code = int(b[8:16], 2)
        self.cksum = int(b[16:32], 2)

    def __str__(self) -> str:
        return f"ICMP (type {self.type}, code {self.code}, " + \
            f"cksum 0x{self.cksum:x})"


class UDP:
    # Each member below is a field from the UDP header.  They are listed below
    # in the order they appear in the packet.  All fields should be stored in
    # host byte order.
    #
    # You should only modify the __init__() function of this class.
    src_port: int
    dst_port: int
    len: int
    cksum: int

    def __init__(self, buffer: bytes):
        b = ''.join(format(byte, '08b') for byte in [*buffer])
        self.src_port = int(b[:16], 2)
        self.dst_port = int(b[16:32], 2)
        self.len = int(b[32:48], 2)
        self.cksum = int(b[48:64], 2)

    def __str__(self) -> str:
        return f"UDP (src_port {self.src_port}, dst_port {self.dst_port}, " + \
            f"len {self.len}, cksum 0x{self.cksum:x})"

# TODO feel free to add helper functions if you'd like

def traceroute(sendsock: util.Socket, recvsock: util.Socket, ip: str) \
        -> list[list[str]]:
    """ Run traceroute and returns the discovered path.

    Calls util.print_result() on the result of each TTL's probes to show
    progress.

    Arguments:
    sendsock -- This is a UDP socket you will use to send traceroute probes.
    recvsock -- This is the socket on which you will receive ICMP responses.
    ip -- This is the IP address of the end host you will be tracerouting.

    Returns:
    A list of lists representing the routers discovered for each ttl that was
    probed.  The ith list contains all of the routers found with TTL probe of
    i+1.   The routers discovered in the ith list can be in any order.  If no
    routers were found, the ith list can be empty.  If `ip` is discovered, it
    should be included as the final element in the list.
    """
    # Code for A-stage1,2-----------begin
    # sendsock.set_ttl(TRACEROUTE_MAX_TTL)
    # sendsock.sendto("Potato".encode(), (ip, TRACEROUTE_PORT_NUMBER))
    # if recvsock.recv_select():
    #     buf, address = recvsock.recvfrom()
    #     print(f"Packet bytes: {buf.hex()}")
    #     ip1 = IPv4(buf)
    #     icmp = ICMP(buf[ip1.header_len:])
    #     ip2 = IPv4(buf[ip1.header_len + 8:])
    #     udp = UDP(buf[ip1.header_len + 8 + ip2.header_len:])
    #     print(ip1)
    #     print(icmp)
    #     print(ip2)
    #     print(udp)
    # Code for A-stage1,2-----------end

    msg = "Potato"
    routers = []
    for ttl in range(1, TRACEROUTE_MAX_TTL+1):
        sendsock.set_ttl(ttl)
        routers_of_ttl = []
        for _ in range(PROBE_ATTEMPT_COUNT):
            sendsock.sendto(msg.encode(), (ip, TRACEROUTE_PORT_NUMBER))
            if recvsock.recv_select():
                buf, address = recvsock.recvfrom()
                ip1 = IPv4(buf)
                icmp = ICMP(buf[ip1.header_len:])
                if icmp.type == 11 and icmp.code == 0:
                    if routers_of_ttl.count(ip1.src) == 0:
                        routers_of_ttl.append(ip1.src)
                elif icmp.type == 3 and icmp.code == 3:
                    routers_of_ttl.append(ip1.src)
                    util.print_result(routers_of_ttl, ttl)
                    return routers
        util.print_result(routers_of_ttl, ttl)
        routers.append(routers_of_ttl)
    return routers


if __name__ == '__main__':
    args = util.parse_args()
    ip_addr = util.gethostbyname(args.host)
    print(f"traceroute to {args.host} ({ip_addr})")
    traceroute(util.Socket.make_udp(), util.Socket.make_icmp(), ip_addr)
