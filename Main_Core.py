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
            vlan_desc_var = df['description'][indx]
            
            intf_confg = Interface(name=vlan_id_vari, device=dev)
            intf_confg.description = vlan_desc_var
            intf_confg.enabled = True
            intf_confg.ipv4_enabled = True
            intf_confg.ipv4 = vlan_ipadd_var
            intf_confg.ipv4.netmask = vlan_subnet_var
            output_intf = intf_confg.build_config()#(apply=False)
            #print(output_intf)                

            '''
            This section represents code that will create the EIGRP Routing instances on the switch
            '''
            dev.configure("router eigrp 10\n"
                          f"network {vlan_ipadd_var} 0.0.0.0\n"
                          f"distribute-list route-map DEFAULT-2-ACCESS out {vlan_id_vari}\n")                                                   

            
    '''
    This section represents code that will create Trunk interface port assignments for the infrastructure (UPLINK & DOWNLINK)
    '''
    
    for indx in bf.index:
        intf_desc_var = bf['description'][indx]
        intf_name_start_var = bf['intf_name_start'][indx]
        intf_type_var = bf['type'][indx]
                
        if intf_type_var == 'UPLINK':        
            print('UPLINK PORTS ALREADY CONFIGURED')                 
        else:    
            if intf_type_var == 'DOWNLINK':

                for indx in df.index: 
                               
                    if df['type'][indx] == 'DOWNLINK':
                        vlan_roll = df['id'][indx]
                        dev.configure(f"interface {intf_name_start_var}\n"#
                                    f"description {intf_desc_var}\n"
                                    "switchport mode trunk\n"
                                    "switchport trunk native vlan 900\n"
                                    "switchport trunk allowed vlan 900\n"
                                    f"switchport trunk allowed vlan add {vlan_roll}\n"
                                    "no shutdown") 
                    else:
                        print('DOWNLINK PORTS ALL CONFIGURED') 

    # Adding the downlink vlans as part of the logic 
    
    for indx in bf.index:
        intf_desc_var = bf['description'][indx]
        intf_name_start_var = bf['intf_name_start'][indx]
        intf_type_var = bf['type'][indx]

        for indx in df.index: 
                                               
            if df['type'][indx] == 'DOWNLINK':
                    vlan_roll = df['id'][indx]
                    
                    dev.configure(f"interface {intf_name_start_var}\n"#
                                  f"switchport trunk allowed vlan add {vlan_roll}")
            else:
                print('PORTS ALL CONFIGURED') 


    # Adding the core_L3 vlans as part of the logic 
    
    for indx in bf.index:
        intf_desc_var = bf['description'][indx]
        intf_name_start_var = bf['intf_name_start'][indx]
        intf_type_var = bf['type'][indx]

        for indx in df.index: 
                                               
            if df['type'][indx] == 'CORE_L3':
                    vlan_roll = df['id'][indx]
                    
                    dev.configure(f"interface {intf_name_start_var}\n"#
                                  f"switchport trunk allowed vlan add {vlan_roll}")
            else:
                print('PORTS ALL CONFIGURED') 