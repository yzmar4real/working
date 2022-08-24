from operator import contains
from genie.testbed import load
from pyats.log.utils import banner
from genie.libs.conf.vlan import Vlan
from genie.libs.conf.interface import Interface
import sys
import time
import logging
import pandas as pd


# vlan_deck = {'name':['P2P_Core_1','P2P_Core_2','Data','Voice','CCTV','AP_MGT','GTH_P2P_Core_1','TFM_P2P_Core_2'], 
#               'id':['764','864','20','503','200','600','765','866'], 
#               'type':['UPLINK','UPLINK','DATA','VOICE','CORE_L3','CORE_L3','DOWNLINK','DOWNLINK'], 
#               'ip_add':['172.18.160.18','172.18.161.18','172.24.161.1','172.21.160.1','N/A','N/A','N/A','N/A'], 
#               'subnet': ['255.255.255.252','255.255.255.252','255.255.255.0','255.255.255.0','N/A','N/A','N/A','N/A']}

# df = pd.DataFrame(vlan_deck)

# vf = pd.DataFrame(dhcp_deck)

df = pd.read_excel('Book2.xlsx', sheet_name='vlan')
vf = pd.read_excel('Book2.xlsx', sheet_name='dhcp')

print(vf)
print(df)

testbed = load('device.yml')

for dev in testbed:
    dev.connect(learn_hostname=True,init_exec_commands=[],init_config_commands=[],log_stdout=True)

    '''
    This section represents code that will create vlans based on legend input list of vlans
    
    '''
    for indx in df.index:
        vlan_name_var = df['name'][indx]
        vlan_id_var = df['id'][indx]
        new_vlan = Vlan(vlan_id=vlan_id_var, name=vlan_name_var)
        dev.add_feature(new_vlan)
        output_vlan = new_vlan.build_config()#(apply=False)
        # print(output_vlan[dev.name])
   
    '''
    This section represents code that will create the SVI's as required on the device
    '''

    for indx in df.index:
        if df['ip_add'][indx] == 'None':
            print('Skipping non layer 3 SVI')
        else:
            vlan_id_var = df['id'][indx]
            vlan_ipadd_var = df['ip_add'][indx]
            vlan_subnet_var = df['subnet'][indx]
            vlan_id_vari = 'Vlan' + str(vlan_id_var)

            intf_confg = Interface(name=vlan_id_vari, device=dev)
            intf_confg.description = 'LAYER 3 SVI'
            intf_confg.enabled = True
            intf_confg.ipv4_enabled = True
            intf_confg.ipv4 = vlan_ipadd_var
            intf_confg.ipv4.netmask = vlan_subnet_var
            output_intf = intf_confg.build_config()#(apply=False)
            # print(output_intf)

            '''
            This section represents code that will create the EIGRP Routing instances on the switch
            '''
            dev.configure("router eigrp CBN\n"
                          "address-family ipv4 unicast autonomous-system 10\n"
                          f"network {vlan_ipadd_var} 0.0.0.0\n"
                          f"af-interface {vlan_id_vari}\n"  
                          "no passive-interface\n"
                          "exit-af-interface\n")                                                       

    '''
    This section represents code that will create the DHCP infrastructure setup 
    '''

    for indx in vf.index:
        dhcp_name_var = vf['name'][indx]
        dhcp_excl_start_var = vf['excl_start'][indx]
        dhcp_excl_end_var = vf['excl_end'][indx]
        dhcp_iprange_var = vf['ip_range'][indx]
        dhcp_host_var = vf['host'][indx]
        dhcp_mac_var = vf['mac_address'][indx]
        dhcp_ipmask_var = vf['ip_mask'][indx]
        dhcp_defgw_var = vf['def_gw'][indx]

        if vf['type'][indx] == 'static':
            dev.configure(f"ip dhcp excluded-address {dhcp_excl_start_var}\n"
                      f"ip dhcp pool {dhcp_name_var}-RESERVATION\n"
                      f"host {dhcp_host_var} {dhcp_ipmask_var}\n"
                      f"client-identifier {dhcp_mac_var}\n"
                      f"default-router {dhcp_defgw_var}\n"
                      "dns-server 172.24.90.70 172.24.90.152 172.24.154.111\n"
                      "domain-name cenbank.net")
        else:
            dev.configure(f"ip dhcp excluded-address {dhcp_excl_start_var} {dhcp_excl_end_var}\n"
                      f"ip dhcp pool {dhcp_name_var}-RESERVATION\n"
                      f"network {dhcp_iprange_var} {dhcp_ipmask_var}\n"
                      f"default-router {dhcp_defgw_var}\n"
                      "dns-server 172.24.90.70 172.24.90.152 172.24.154.111\n"
                      "domain-name cenbank.net")
