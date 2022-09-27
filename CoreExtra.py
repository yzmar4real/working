from ipaddress import IPv4Address
from genie.testbed import load
from pyats.log.utils import banner
from genie.libs.conf.vlan import Vlan
from genie.libs.conf.interface import Interface

import sys
import time
import logging
import pandas as pd

df = pd.read_excel('Branch_Core.xlsx', sheet_name='vlan')
bf = pd.read_excel('Branch_Core.xlsx', sheet_name='intf_trunk')

print(df)
print(df)

testbed = load('device.yml')

for dev in testbed:
    dev.connect(learn_hostname=True,init_exec_commands=[],init_config_commands=[],log_stdout=True)
    
    '''
            
    This section represents code that pushes default configuration on the switch 
            
    '''
                   
    dev.configure("ip prefix-list DEFAULT seq 5 permit 0.0.0.0/0\n"
                 "ip prefix-list IPV4-PRIVATE seq 5 permit 10.0.0.0/8 le 32\n"
                 "ip prefix-list IPV4-PRIVATE seq 10 permit 172.16.0.0/12 le 32\n"
                 "ip prefix-list IPV4-PRIVATE seq 15 permit 192.168.0.0/16 32\n"
                 "ip route 0.0.0.0 0.0.0.0 Null0 200 name DEFAULT-FOR-FLOORS")   
    
    dev.configure("route-map ADVERTISE-2-SDWAN deny 5\n"
                  "match ip address prefix-list DEFAULT\n"
                  "route-map ADVERTISE-2-SDWAN permit 10\n"
                  "match ip address prefix-list IPV4-PRIVATE\n"
                  "route-map ADVERTISE-MAP permit 10\n"
                  "match ip address prefix-list DEFAULT IPV4-PRIVATE\n"
                  "route-map DEFAULT-2-ACCESS permit 5\n"
                  "match ip address prefix-list DEFAULT")                                                                     