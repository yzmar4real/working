from genie.testbed import load
import sys
import time
import logging


testbed = load('device.yml')

for dev in testbed:
    dev.connect(learn_hostname=True,init_exec_commands=[],init_config_commands=[],log_stdout=True)
    
    