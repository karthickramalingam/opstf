import unicodedata
#!/usr/bin/env python
'''
Created on 24-Aug-2016

Author : Terralogic team

OpenSwitchCliDriver is the basic driver which will handle the OpenSwitch functions.

'''
import xmldict
import pexpect
import re
import os
import ast
import time
import sys
import csv
import testfail
import logger as log
from robot.libraries.BuiltIn import BuiltIn 


global step

#--------------------------------------------------------------------------------#
#----------------------Displaying the Sleep time on Console----------------------#
#--------------------------------------------------------------------------------#

def displaytime(times,msg=''):
    log.info("Process is running...! please wait for "+str(times)+ "-seconds ")
    log.info(".....Thanks for waiting......")
    time.sleep(int(times))
#--------------------------------------------------------------------------------#
#------------Getting device configuration info from device.cfg   file------------#
#--------------------------------------------------------------------------------#

def config_to_dict(device):
          xml = open(device+'.cfg').read()
          
          try :
                parsedInfo = xmldict.xml_to_dict(xml)
                return parsedInfo
          except :
                return "Unable to convert configuration file.Check the configuration file" 

#--------------------------------------------------------------------------------#
#--------Configure is used to confiure the given device with given cmd's---------#
#--------------------------------------------------------------------------------#
def Configure(device,configure,command=''):

           device_name=Device_parser(device)
          
           device_config=config_to_dict(device_name)
           testname = BuiltIn().get_variable_value("${TEST_NAME}")
           
	   config_commands=device_config[device_name][testname][configure]             
           
           command_list = config_commands.split('\n')
           
           connected_device=Connect(device)
           connected_device.sendline('configure terminal')
           connected_device.expect('#')
           for i in command_list: 
               connected_device.sendline(i)
               connected_device.expect('#')
               #log.detail( connected_device.before
         
           connected_device.sendline(command)
           connected_device.expect('#')
           connected_device.sendline('sh run')
           connected_device.expect('#')
           log.detail(connected_device.before) 
           connected_device.sendline('end')
           connected_device.expect('#')
           
#--------------------------------------------------------------------------------#
#-------------------Configuration for BGP authentication ------------------------#
#--------------------------------------------------------------------------------#

def ConfigureRoute(device,configure,command=''):
           device_name=Device_parser(device)
           log.step('Configure '+configure+' on '+device_name)
           device_config=config_to_dict(device_name)
	   
           testname = BuiltIn().get_variable_value("${TEST_NAME}")
	   config_commands=device_config[device_name][testname][configure]             
           
           command_list = config_commands.split('\n')
         
           connected_device=Connect(device)
           connected_device.sendline('configure terminal')
           connected_device.expect('#')
           for i in command_list: 
               connected_device.sendline(i)
               connected_device.expect('#')
           connected_device.sendline(command)
           connected_device.expect('#')
           connected_device.sendline('end')
           connected_device.expect('#')
	   connected_device.sendline('sh run')
           connected_device.expect('#')
           log.detail(connected_device.before)
           if configure == 'bgppassword' or configure =='password':
               log.success("password configured successfully")
           if configure == 'routemap' :
               log.success("routemap configured successfully")
           if configure == 'prefixlist' :
               log.success("prefixlist configured successfully")
               
#--------------------------------------------------------------------------------#     
#------------Used to fetch connection info from OPS_Device.param file------------#
#--------------------------------------------------------------------------------#

def Device_Info(device):
          Device_param=open('Device.params').read()
          Devices_Lists=Device_param.splitlines() 
          for i in Devices_Lists:
               patterntern=device
               patterntern_match=re.search(patterntern,i)
               if patterntern_match:          
                  Split_Device_param=i.split(',')
                  return Split_Device_param

#--------------------------------------------------------------------------------#
#-------------Connect is used to connect to given device(switch) ----------------#
#--------------------------------------------------------------------------------#

def Connect(device):
        device_name=Device_parser(device)
        device_Info=Device_Info(device_name)
        ip_address=device_Info[1]
        port=device_Info[2]
        user=device_Info[3]
        password=device_Info[4]
        mode=device_Info[5]
        refused="ssh: connect to host " +ip_address+ " port 22: Connection refused"
        connectionInfo = pexpect.spawn('ssh -p '+port +' ' +user+'@'+ip_address,env={ "TERM": "xterm-mono" },maxread=50000 )
        i = 7
        while i == 7:
            i =connectionInfo.expect( ['Are you sure you want to continue connecting','password:|Password:',pexpect.EOF,pexpect.TIMEOUT,refused,'>|#|\$','Host key verification failed.'],120 )  
            if i == 0:  # Accept key, then expect either a password prompt or access
                connectionInfo.sendline( 'yes' )
                i = 7  # Run the loop again
                continue
            if i == 1:  # Password required                
                connectionInfo.sendline(password)
                connectionInfo.expect( '>|#|\$')
                if connectionInfo.expect:
                    log.failure('Password for '+device_name+' is incorrect')
                    raise testfail.testFailed('Password for '+device_name+' is incorrect')
                    break
            elif i == 2:
                log.failure('End of File Encountered while Connecting '+device_name)
                raise testfail.testFailed('End of File Encountered while Connecting '+device_name)
                break
            elif i == 3:  # timeout
                log.failure('Timeout of the session encountered while connecting')
                raise testfail.testFailed('Timeout of the session encountered')
                break
            elif i == 4:
                log.failure('Connection to '+device_name+' refused')
                raise testfail.testFailed('Connection to '+device_name+' refused')
                break
            elif i == 5:
                pass
            elif i == 6:
                cmd="ssh-keygen -R ["+ip_address+"]:"+port
                os.system(cmd)
                i = 7
                continue
        connectionInfo.sendline("")
        connectionInfo.expect( '>|#|\$' )
        if mode=='OPS':
           connectionInfo.sendline('vtysh')
           connectionInfo.expect('>|#|\$')
        #log.step('Connection to the '+device_name+' is Established')
        return connectionInfo


def Connect_device(device):
    device_name=Deviceparser(device)
    device_Info=Get_deviceInfo(device_name)
    # name=device_Info[0]
    ip_address=device_Info[1]
    port=device_Info[2]
    user=device_Info[3]
    password=device_Info[4]
    mode=device_Info[5]
    refused="ssh: connect to host " +ip_address+ " port 22: Connection refused"
    connectionInfo = pexpect.spawn('ssh -p '+port +' ' +user+'@'+ip_address,env={ "TERM": "xterm-mono" },maxread=50000 )
    expect = 7
    while expect == 7:
        expect =connectionInfo.expect( ['Are you sure you want to continue connecting','password:|Password:',pexpect.EOF,pexpect.TIMEOUT,refused,'>|#|\$','Host key verification failed.'],120 )  
        if expect == 0:  # Accept key, then expect either a password prompt or access
            connectionInfo.sendline( 'yes' )
            expect = 7  # Run the loop again
            continue
        if expect == 1:  # Password required                
            connectionInfo.sendline(password)
            connectionInfo.expect( '>|#|\$')
            if connectionInfo.expect:
                log.failure('Password for '+device_name+' is incorrect')
                raise testfail.testFailed('Password for '+device_name+' is incorrect')
                break
        elif expect == 2:
            log.failure('End of File Encountered while Connecting '+device_name)
            raise testfail.testFailed('End of File Encountered while Connecting '+device_name)
            break
        elif expect == 3:  # timeout
            log.failure('Timeout of the session encountered while connecting')
            raise testfail.testFailed('Timeout of the session encountered')
            break
        elif expect == 4:
            log.failure('Connection to '+device_name+' refused')
            raise testfail.testFailed('Connection to '+device_name+' refused')
            break
        elif expect == 5:
            pass
        elif expect == 6:
            cmd='ssh-keygen -R ['+ip_address+']:'+port
            os.system(cmd)
            connectionInfo = pexpect.spawn('ssh -p '+port +' ' +user+'@'+ip_address,env={ "TERM": "xterm-mono" },maxread=50000 )
            expect = 7
            continue
    connectionInfo.sendline("")
    connectionInfo.expect( '>|#|\$' )
    if mode=='OPS':
        connectionInfo.sendline('vtysh')
        connectionInfo.expect('>|#|\$')
    return connectionInfo


#--------------------------------------------------------------------------------#
#----------------Converting XML int Dict and Fecting the Device info-------------#
#--------------------------------------------------------------------------------#

def Device_parser(device) :
            device=str(device)
            xml = open('OpenSwitch_FT_01.params').read() 
            parsedInfo = xmldict.xml_to_dict(xml)
            devicename=parsedInfo['TestCase']['Device'][device]
            return devicename   

def calltestcaseparams(testcase):
           testcase=str(testcase)
           xml = open('OpenSwitch_FT_01.params').read()
           tc=xmldict.xml_to_dict(xml)
           devicename=tc['TestCase'][testcase]
           return devicename


#--------------------------------------------------------------------------------#
#---------------------- Used to Check BGP neighborship state---------------------#
#--------------------------------------------------------------------------------#

def CheckNeighborship(device,state):
    
    Devicename=Device_parser(device)
    s=Device_parser(device)
    log.step('check neighborship on '+Devicename+' for the state :'+state)
    log.info('running show ip bgp summary ')
    p=config_to_dict(s)
    #q=p[s][conf]
    #d = q.split('\n')
    s=Connect(device)
    s.sendline('show ip bgp summary')
    time.sleep(10)
    s.expect('#')
    o =s.before
    log.detail(o)
    pat = r'(\d+\.\d+\.\d+\.\d+)\s*(\d+)\s*\d+\s*\d+\s*\d+\:\d+\:\d+\s*(\w+)'
    #pat = r'(\d+\:\:\d+)\s*(\d+)\s*\d+\s*\d+\s*\d+\:\d+\:\d+\s*(\w+)'
    match = re.search(pat,o)
    if match:
        nehopip = match.group(1)
        neasnum = match.group(2)
        neighborship=match.group(3)
        if neighborship ==  state :
            #log.detail( "Nexthopip is ",nehopip," asnum is ",neasnum," neighborship is ",neighborship
            log.success('check neighborship on the device '+Devicename+' with the state :'+state+' is success')
            return True
        elif state != "Established" and (neighborship=="Active" or neighborship =="Idle" or neighborship =="Connect"):
	    log.success('check neighborship on the device '+Devicename+' with the state :'+state+' is success')
            return True
        else :
            log.detail( "Neighborship is not established")
            log.failure('check neighborship is unsuccess')
            return False
    else:
        return False

#--------------------------------------------------------------------------------#
#----------------------- Used to shutdown the interface -------------------------#  
#--------------------------------------------------------------------------------#

def shutdown_link(dev,int_no):

      ID=Device_parser(dev)
      log.step("Shutdown the interface "+int_no+" on "+ID)
      s=Connect(dev)
      s.sendline('conf t')
      s.expect('[#\$]')
      cmd="interface "+int_no
      s.sendline(cmd)
      s.expect('[#\$]')
      s.sendline('shutdown')
      s.expect('[#\$]')
      s.sendline("end")
      s.sendline("show interface "+int_no)
      s.expect('[#\$]')
      a = s.sendline("show run")
      s.expect('[#\$]')
      log.detail(a)
      log.success("the interface "+int_no+" has been shutdown on "+ID)

#--------------------------------------------------------------------------------#      
#--------------------- Used to bringup the interface  ---------------------------#
#--------------------------------------------------------------------------------#

def bringUpLink(dev,int_no):

      ID=Device_parser(dev)
      log.step("Bring the interface "+int_no+" up on "+ID )
      s=Connect(dev)
      cmd="interface "+int_no
      s.sendline("conf t")
      s.expect('[#\$]')
      s.sendline(cmd)
      s.expect('[#\$]')
      s.sendline('no shutdown')
      s.expect('[#\$]')
      s.sendline('end')
      s.expect('[#\$]')
      a = s.sendline("show run")
      s.expect('[#\$]')
      log.detail(a)
      log.success("the interface "+int_no+" has been brought up on "+ID)

#--------------------------------------------------------------------------------#      
#--------------------- Used to check the reachabilty of switches ----------------#
#--------------------------------------------------------------------------------#     

def Ping(device,device1):
     xml = open('OpenSwitch_FT_01.params').read()
     parsedInfo = xmldict.xml_to_dict(xml)
     IP=parsedInfo['TestCase']['ping']['destIP']
     ID=Device_parser(device)
     ID1=Device_parser(device1)
     log.step("Check for reachability between "+ID1+" and "+ID+" using PING.")
     log.info("Logging into :"+ID)
     child=Connect(device)
     command='ping '+IP
     log.info("pinging to IP :"+IP+" of "+ID1)
     child.sendline(command)
     child.expect('[#\$] ')
     log.detail(child.before)
     PingResults= child.before
     pat=re.compile(r'(\n*\s*(\d+)\s*\s+packets\stransmitted\,\s+(\d+)\s+received\,\s*(\d+)\%\s+packet\s+loss)',re.MULTILINE)
     match=re.search(pat,PingResults)
     if match:
	 PacketLoss=match.group(4)
	 if PacketLoss=='0':
	     log.success("Ping Successful!!No Packet Loss")
	 else:
             #log.detail( "PING UNSUCESSFUL"
             raise AssertionError("PING UNSUCESSFULL")
     else:
         #log.detail( "PING UNSUCESSFUL" 
         raise AssertionError("PING UNSUCESSFULL") 

#--------------------------------------------------------------------------------#
#--------------------- Used to Check IPV6 Neighborship state --------------------#
#--------------------------------------------------------------------------------#

def CheckIPV6Neighborship(device,state):
    DeviceName=Device_parser(device)
#    p=config_to_dict(s)
    log.step('check EBGP neighborship with IPV6 addressing on  Device:'+DeviceName+' for the state :'+state)
    displaytime(60)
    log.info("Logging into Device:"+DeviceName)	  
    Device_Name=Connect(device)
    log.info("running the show ip bgp summary")
    Device_Name.sendline('show ip bgp summary')
    Device_Name.expect('#')
    out=Device_Name.before
    log.detail(out)
    pat = r'(\d+\:\:\d+)\s*(\d+)\s*\d+\s*\d+\s*\d+\:\d+\:\d+\s*(\w+)'
    match = re.search(pat,out)
    nehopip = match.group(1)
    neasnum = match.group(2)
    neighborship=match.group(3)
    
    if neighborship ==  state :
        #log.detail( "Nexthopip is ",nehopip," asnum is ",neasnum," neighborship is ",neighborship
        log.success('check EBGP neighborship  with IPv6 addressing on the device '+DeviceName+' with the state :'+state+' is success')
        return True
        
    else :
        log.failure ("EBGP Neighborship with IPv6-addressing is not established")
        return False

#--------------------------------------------------------------------------------#
#--------------------- Used to Check Remove Private AS---------------------------#
#--------------------------------------------------------------------------------#

def Remove_Private(device):
    DeiveName=Device_parser(device)
    check=0
    xml = open('OpenSwitch_FT_01.params').read()
    parsedInfo = xmldict.xml_to_dict(xml)
    asnumFAB=parsedInfo['TestCase']['private']['asnumFAB']
    asnum=parsedInfo['TestCase']['private']['asnum1']
    IP=parsedInfo['TestCase']['private']['IP']
    loop=parsedInfo['TestCase']['private']['loop']
    log.step("Verify feature \"Remove Private AS\" for ASNUM "+asnumFAB+" should not present in path of loopback address on "+DeiveName)
    log.info("Logging into Device:"+DeiveName)
    Deive_Name = Connect(device)          
    log.info('check the BGP table for loopback address')
    #log.detail( "===================================="
    #log.detail( "PARSING THE PARAMFILE TO READ THE INFORMATION"
    
    #log.detail( "===================================="
    #log.detail( "CHECKING THE BGP INFORMATION FOR THE LOOPBACK ADDRESS IN DEVICE3"
    displaytime(120,'to get Neighbor state as established')
    log.info('running show ip bgp '+loop)
    Deive_Name.sendline('sh ip bgp '+loop)
    Deive_Name.expect('#')
    Deive_Name.sendline('sh ip bgp '+loop)
    Deive_Name.expect('#')
    actual=Deive_Name.before
    log.detail(actual)
    #log.detail( "===================================="
    #log.detail( "CHECKING THE EXPECTED RESULT WITH ACTUAL RESULT"

    actual=actual.replace(" ", "")
    
    actual=actual.split('\n')
    
    string1="""AS:"""+asnum+""""""
    string2=""""""+IP+"""from"""+IP+""""""
    string3="""OriginIGP,metric0,localpref0,weight32768,valid,external,best"""
    
   
    length = len(actual)
    currentline = 0
    while(currentline<length):
        if string1 in actual[currentline]:
            secondline = currentline+1
            
            if string2 in actual[secondline]:
                thirdline = currentline+2
                

                if string3 in actual[thirdline]:
                    check =1
                    
                    break
        currentline=currentline+1
    #log.detail( "==============================================="
    if check == 1:
        log.success(" Remove Private AS is verified on "+DeiveName)
        return True
        
    else:
        log.failure(" Remove Private AS is not verified on "+DeiveName)
        return False

#--------------------------------------------------------------------------------#
#------------------ Used to Check BGP Neighborship state ------------------------#
#--------------------------------------------------------------------------------#

def CheckNeighbor(device,state):
    Device_name=Device_parser(device)
    log.step('check neighborship on  Device:'+Device_name+' for the state :'+state)
    call_device=config_to_dict(Device_name)
    displaytime(60,'to get Neighbor state as established')
    Devicename=Connect(device)
    Devicename.sendline('show ip bgp summary')
    Devicename.expect('#')
    output =Devicename.before
    #log.detail( "output is :",output
    Devicename.sendline('show ip bgp summary')
    Devicename.expect('#')
    output = Devicename.before
    log.detail(output)
    fd = open("sample1.txt","w+")
    fd.write(output)
    fd.close()
    fd = open("sample1.txt","r")
    line = fd.readlines()
    for eachline in line :
        pattern = r'(\d+\.\d+\.\d+\.\d+)\s*(\d+)\s*\d+\s*\d+\s*\S*\s*(\w+)'
        match = re.search(pattern,eachline)
        if match:
            Neighbor_IP = match.group(1)
            Neighbor_AS = match.group(2)
            Check_State = match.group(3)
            if Check_State ==  state :
                log.success("Nexthopip is "+Neighbor_IP+" ASnum is "+Neighbor_AS+" neighborship state is: "+Check_State)
                os.remove("sample1.txt")
                return  True
            if Check_State ==  state :
                break
    
    else :
        os.remove("sample1.txt")
        log.failure( "Neighborship is not established on "+Device_name)
        return  False 

#--------------------------------------------------------------------------------# 
#---------- Used to Check BGP Neighborship state for loopback interfaces --------#
#--------------------------------------------------------------------------------#

def CheckNeighborshipWithLoopback(device):
    Device_name=Device_parser(device)
    call_device=config_to_dict(Device_name)
    Devicename=Connect(device)
    displaytime(10,'to get Neighbor state as established')
    log.detail( device)
    if device == "device1":
        displaytime(120,'to get Neighbor state as established')
        log.step("Check neighborship with loopback on "+Device_name)
        Devicename.sendline('show ip bgp 1.1.1.1')
        Devicename.expect('#')
        log.detail( Devicename.before)
        output =Devicename.before
        Devicename.sendline('show ip bgp 1.1.1.1')
        Devicename.expect('#')
        output = Devicename.before
        log.detail( output)
        fd = open("sample2.txt","w+")
        fd.write(output)
        fd.close()
        f = open("sample2.txt","r")
        line = f.readlines()
        for eachline in line :
            pattern1 = r'\s*AS\:\s*\d+\s*\d+'
            pattern2 = r'\s*(\d+\.\d+\.\d+\.\d+)\s*from\s*(\d+\.\d+\.\d+\.\d+)'
            pattern3 = r'\s*Origin\s*IGP\,\s*metric\s*\d+\,\s*localpref\s*\d+\,\s*weight\s*\d+\,\s*valid\,\s*external\,\s*best'
            match1 = re.search(pattern1,eachline)
            if match1:
                for each_line_1 in line:
                    match2 = re.search(pattern2,each_line_1)
                    #log.detail( match2
                    if match2 :
                        for each_line_2 in line :
                            match3 = re.search(pattern3,each_line_2)
                            #log.detail( match3
                            if match3 :
                                os.remove("sample2.txt")
                                log.success( "Best path found in device: "+Device_name)
                                return True
        

    elif device == "device2":
        displaytime(60,'to get Neighbor state as established')
        log.step("Check routemap is configured on "+Device_name)
        Devicename.sendline('show ip bgp 1.1.1.1')
        Devicename.expect('#')
        #log.detail( Devicename.before
        output =Devicename.before
        #log.detail( "sdkfhksdf",output
        Devicename.sendline('show ip bgp 1.1.1.1')
        Devicename.expect('#')
        output = Devicename.before
        log.detail( "output",output)
        fd = open("sample3.txt","w+")
        fd.write(output)
        fd.close()
        f = open("sample3.txt","r")
        line = f.readlines()
        for eachline in line :
                pattern1 = r'AS\:\s*\d+'
                pattern2 = r'\s*(\d+\.\d+\.\d+\.\d+)\s*from\s*(\d+\.\d+\.\d+\.\d+)'
                pattern3 = r'\s*Origin\s*IGP\,\s*metric\s*\d+\,\s*localpref\s*\d+\,\s*weight\s*\d+\,\s*valid\,\s*external\,\s*best'
                pattern4 = r'Community\:\s*no\-advertise'
                match1 = re.search(pattern1,eachline)
                if match1 :
                    for each_line_1 in line:
                        match2 = re.search(pattern2,each_line_1)
                        #log.detail( match2
                        if match2 :
                            for each_line_2 in line :
                                match3 = re.search(pattern3,each_line_2)
                                #log.detail( match3
                                if match3 :
                                   for each_line_3 in line :
                                       match4 = re.search(pattern4,each_line_3)
                                       #log.detail( match4
                                       if match4:
                                           os.remove("sample3.txt")
                                           #log.detail( match4
                                           log.success( "Route map is Successfully configured "+Device_name)
                                           return True
        
    else:
        log.failure( "configuration is not sucessful"+Device_name)
        return False

#--------------------------------------------------------------------------------#
#---------------------------- Used to Reset the BGP------------------------------#
#--------------------------------------------------------------------------------#

def ClearBGP(device):
    Devicename=Device_parser(device)
    log.step("Reset the  BGP process ")
    call_device=config_to_dict(Devicename)
    Devicename=Connect(device)
    log.detail("Running \"clear bgp * soft out\" and \"clear bgp * soft out\"")
    Devicename.sendline('clear bgp * soft out')
    Devicename.expect('#')
    Devicename.sendline('clear bgp * soft out')
    Devicename.expect('#')
    log.success("Resetting the BGP process is success")



#--------------------------------------------------------------------------------#  
#---------------------- Used to configure EBGP_neighbourship --------------------#
#--------------------------------------------------------------------------------#

def EBGP_neighbourship(device1,device4,device3):
           log.info('Establish EBGP neighbourship between FAB-CSW and CSW-ASW.')
	   LoadBaseconfigurations(device1,device4,device3)
           log.info('Establishing EBGP_neighbourship is success')

#--------------------------------------------------------------------------------#
#--------------verify log-neighbor-changes using "show running-config" in fab05--#
#--------------------------------------------------------------------------------#

def VerifyLogNeighbor(device1):
           expectedstring="bgp log-neighbor-changes"
           log.step('verify EBGP log neighborship states')
	   fab=Connect(device1)
           displaytime(5,'to get Neighbor state as established')
           fab.sendline('show running-config')
           fab.expect('#')
         
           data=fab.before
           log.detail( data)
           if expectedstring in data:
               log.success('verify Log neighbor changes is success')
               return True
           else:
               log.failure('verify Log neighbor changes is unsuccess')            
	       return False
	

#--------------------------------------------------------------------------------#
#-------Veirfy connection "Establishment" using "show ip bgp su" in  fab05.------#
#--------------------------------------------------------------------------------#

def showbgpsummary(device1):
           log.step('verify EBGP neighborship states')
           fab=Connect(device1)
           displaytime(10,'to get Neighbor state as established')
           fab.sendline('sh ip bgp summary')
           fab.expect('#')
           
	   data=fab.before
           log.detail( data)
           pat="Established"
           log.detail( data)
           if pat in data:
               log.success('verify EBGP neighborship is success')
               return pat
           else:
               log.failure('verify EBGP neighborship is failed') 
               return "idel state"


             
#--------------------------------------------------------------------------------#
#-----------------------Remove Neighbour FAB05 of CSW02--------------------------#
#--------------------------------------------------------------------------------#

def flapneighboursCSWO2(device2):
          xml = open('OpenSwitch_FT_01.params').read()
          parsedInfo = xmldict.xml_to_dict(xml)
          asnum=parsedInfo['TestCase']['LogNeighbor']['asnum']
          NextHopIP=parsedInfo['TestCase']['LogNeighbor']['NextHopIP']
          log.step('Flap  EBGP neighborship')
          cswswitch=Connect(device2)
          cswswitch.sendline('configure terminal')
          cswswitch.expect('#')
          log.detail( cswswitch.before)
          cswswitch.sendline('router bgp '+asnum)
          cswswitch.expect('#')
          cswswitch.sendline('neighbor '+NextHopIP+' shutdown')
          cswswitch.expect('#')
          displaytime(10,'to get Neighbor state as not established')
          cswswitch.sendline('do show ip bgp summary')
          cswswitch.expect('#')
	  data=cswswitch.before
          log.detail( data ) 
          state1="Connect"
          state2="Active"
          state3="Idle"
          if (state1 in data) or (state2 in data) or (state3 in data):
              log.success('Flap neighbor is success')
              return True 
          else:
              log.failure('Flap neighbor is unsuccess')
              return False            
          
#--------------------------------------------------------------------------------#
#---------------------Verify the EBGP nieghbors of CSW02-------------------------#
#state of FAB05 and ASW01 should be changed from Established to Connect/ActiveIdel#
#--------------------------------------------------------------------------------#

def verifyneighboursofCSW02(device1):
           log.step('verify EBGP neighbor FAB05 state After Flap')
           log.info('state should not be Established')
           fab=Connect(device1)
           displaytime(10,'to get Neighbor state as not established')
           fab.sendline('sh ip bgp summary')
           fab.expect('#')
           
	   data=fab.before
           log.detail( data)
           pat="Established"
           log.detail( data)
           if pat not in data:
               log.success('state in FAB05 is not Estalished')
               return True
           else:
               log.failure('state is Established in FAB05') 
               return False 

                   
#--------------------------------------------------------------------------------#          
#------------Configuring bgp and Enabling soft reconfiguration to FAB05 ---------#
#--------------------------------------------------------------------------------#

def Enablereconfig(device1,Expectedconfig):
           log.step('Enable soft re-config  to FAB05')
           log.info('Enable soft re-config on FAB05')
           fab=Connect(device1)
           displaytime(3,'to get Neighbor state as established')
           fab.sendline('sh bgp neighbors')
           fab.expect('#')
           data=fab.before
           log.detail( fab.before)
           if Expectedconfig in data:
               log.success('Enable soft re-config is success')
               return Expectedconfig
           else:
               log.failure('Enabling soft re-config is failed') 
               return "Disabled"


#--------------------------------------------------------------------------------#
#------------------------Checking for the idle state-----------------------------#
#--------------------------------------------------------------------------------#

def CheckBFDIdle(device,neigh,var):
    var=str(var)
    device_info=Device_parser(device)
    log.step("Checking for the idle state "+device_info)
    parse_info=calltestcaseparams('Neighbors')
    parse_detail=parse_info[neigh]
    parse_dict=config_to_dict(device_info)
    device_info=Connect(device)
    log.info("Checking for the bgp summary, to find Idle state is present for BFD configured Neighbor")
    device_info.sendline('show ip bgp summary')
    device_info.expect('#')
    output =device_info.before
    fd = open("sample.txt","w+")
    fd.write(output)
    fd.close()
    f = open("sample.txt","r")
    log.detail(output)
    line = f.readlines()
    for eachline in line :
        pattern = r'(\d+\.\d+\.\d+\.\d+)\s*\d+\s*\d+\s*\d+\s*\d+\:\d+\:\d+\s*(\S+)'
        match = re.search(pattern,eachline)
        if match:
            if match.group(1)==parse_detail and match.group(2)==var:
                log.success("Idle state is present after configuring BFD")
                os.remove("sample.txt")
		return True
                break  
            else:
                os.remove("sample.txt")
                log.fail("Idle state is not present")
		return False
#--------------------------------------------------------------------------------#
#----------------------------Checking for the BFD state--------------------------#
#--------------------------------------------------------------------------------#

def CheckBFDUp(device,cmd):
    device_info=Device_parser(device)
    log.step("Checking for the BFD state "+device_info)
    device_info=Connect(device)
    displaytime(30,'to get Neighbor state as established')
    device_info.sendline(cmd)
    device_info.expect('#')
    output = device_info.before
    log.info("Checking for Remote/Local in up/up state ")
    log.detail(output)
    fd = open("sample.txt","w+")
    fd.write(output)
    fd.close()
    f = open("sample.txt","r")
    line = f.readlines()
    x=0
    for eachline in line :
        pattern = r'\d+\.\d+\.\d+\.\d+\s*\d+\.\d+\.\d+\.\d+\s*up\/up\s*none\/none'
        match=re.search(pattern,eachline)
        if match:
             x=1
    if x==1 :
        os.remove("sample.txt")
        log.success("Both Remote/Local present as up/up state")
	return True
    else :
        os.remove("sample.txt")
        log.fail("Both Remote/Local not in up/up state")
	return False

#--------------------------------------------------------------------------------# 
#--------------------------Checking for the BFD state----------------------------#
#--------------------------------------------------------------------------------#
   
def CheckBFDDown(device,cmd):
    match=0
    device_info=Device_parser(device)
    log.step("Checking for the BFD state "+device_info)
    device_info=Connect(device)
    displaytime(30,'to get Remote/Local in up/Down state')
    device_info.sendline(cmd)
    device_info.expect('#')
    output = device_info.before
    log.info("Checking for Remote/Local in up/Down state ")
    log.detail(output)
    output=output.replace(" ", "")
    fd = open("sample.txt","w+")
    fd.write(output)
    fd.close()
    f = open("sample.txt","r")
    line = f.readlines()
    x=0
    for eachline in line :
        pattern1 = re.compile(r'(\n*\s*\d+.\d+.\d+.\d+.\d+.\d+.\d+up/downnone/control_detect_expired)',re.MULTILINE)
        match=re.search(pattern1,eachline)
    	if match:
        	x=1
    if x==1 :
        os.remove("sample.txt")
        log.success("Both Remote/Local present as up/Down state")
	return True    
    else:
        os.remove("sample.txt")
        log.fail("Both Remote/Local not in up/Down state")
	return False

#--------------------------------------------------------------------------------# 
#-------------------Checking for the Peer Group Neighborship---------------------#
#--------------------------------------------------------------------------------#
def CheckPeerGroupNeighborship(device,peergroupname=''):
    Devicename=Device_parser(device)
    log.step("check BGP is Configured with peer-group feature")
    call_device=config_to_dict(Devicename)
    Devicename=Connect(device)
    Devicename.sendline('show running-config')
    Devicename.expect('#')
    output =Devicename.before
    log.detail(output)
    fd = open("sample4.txt","w+")
    fd.write(output)
    fd.close()
    f = open("sample4.txt","r")
    line = f.readlines()
    for eachline in line :
        pattern1 = r'router\s*bgp\s*(\d+)'
        pattern2 = r'neighbor\s*(\w+)\s*peer\-group'
        pattern3= r'neighbor\s*\d+\.\d+\.\d+\.\d+\s*remote\-as\s*(\d+)'
        match1 =re.search(pattern1,eachline)          
        if match1 :
                for eachline_1 in line :
                    match2 =re.search(pattern2,eachline_1)          
                    if match2:
                        for eachline_2 in line :
                            match3 =re.search(pattern3,eachline_2)
                            #log.detail( match3
                            if match3:
                                asnum = match1.group(1)
                                #log.detail( asnum
                                peername = match2.group(1)
                                #log.detail( loopbackip
                                if peergroupname == peername :
                                    os.remove("sample4.txt")
                                    log.success( "PEER Group  Configuration is Done")
                                    return True
                                    break
                                else:
                                    os.remove("sample4.txt")
                                    log.failure( "PEER Group is not configured")
                                    return False
    
#--------------------------------------------------------------------------------# 
#-------------------------Removing the configuration-----------------------------#
#--------------------------------------------------------------------------------#

'''def RemoveConfig(device1='',device2='',device3='',device4=''):
    
    l=[]
    log.step("removing configuration on devices") 
    if device1!='':
        log.info( "Logging into Device:\""+Device_parser(device1)+"\" and resseting the previous configuration....")
        Configure(device1,'remove')
        l.append(Device_parser(device1))
    if device2!='':
        log.info( "Logging into Device:\""+Device_parser(device2)+"\" and resseting the previous configuration....")
        Configure(device2,'remove')
        l.append(Device_parser(device2))
    if device3!='':
        log.info( "Logging into Device:\""+Device_parser(device3)+"\" and resseting the previous configuration....")
        Configure(device3,'remove')
        l.append(Device_parser(device3))
    if device4!='':
        log.info( "Logging into Device:\""+Device_parser(device4)+"\" and resseting the previous configuration....")
        Configure(device4,'remove')
        l.append(Device_parser(device4))
    a=str(l)
    log.success("Removing Configuration on devices "+a+" is success")'''

def RemoveConfig(*device):
    log.step("removing configuration on devices")
    length = len(device)
    devices=[]
    for i in range(0,length):
        device_name  = device[i]
        log.info( "Logging into Device:\""+Device_parser(device_name)+"\" and resseting the previous configuration....")
        Configure(device_name,"remove")
        devices.append(Device_parser(device_name))
    devices = str(devices)
    log.success("Removing Configuration on devices "+devices+" is success")

#--------------------------------------------------------------------------------# 
#---------------------------Basic Configurations---------------------------------#
#--------------------------------------------------------------------------------#

''' LoadBaseconfigurations(device1='',device2='',device3='',device4=''):
    l=[]
    log.step("Load Base configurations") 
    if device1!='':
        log.info( "Logging into Device:\""+Device_parser(device1)+"\" and loading the basic configuration....")
        Configure(device1,'basic')
        l.append(Device_parser(device1))
    if device2!='':
        log.info( "Logging into Device:\""+Device_parser(device2)+"\" and loading the basic configuration....")
        Configure(device2,'basic')
        l.append(Device_parser(device2))
    if device3!='':
        log.info( "Logging into Device:\""+Device_parser(device3)+"\" and configuring the basic configuration....")
        Configure(device3,'basic')
        l.append(Device_parser(device3))
    if device4!='':
        log.info( "Logging into Device:\""+Device_parser(device4)+"\" and configuring the basic configuration....")
        Configure(device4,'basic')
        l.append(Device_parser(device4))
    a=str(l)

      
    log.success("Configuration on devices "+a+" is success")'''


def LoadBaseconfigurations(*device):
    log.step("Load Base configurations")
    length = len(device)
    devices=[]
    for i in range(0,length):
        device_name  = device[i]
        log.info( "Logging into Device:\""+Device_parser(device_name)+"\" and loading the basic configuration....")
        Configure(device_name,"basic")
        devices.append(Device_parser(device_name))
    devices = str(devices)
    log.success("Configuration on devices "+devices+" is success")

#--------------------------------------------------------------------------------# 
#-------------------Checking for the Vlan Established state----------------------#
#--------------------------------------------------------------------------------#

def CheckNeighborvlan(device,state):
    Device_name=Device_parser(device)
    log.step('check neighborship of neighbors on Device: '+Device_name+' for the state :'+state)
    call_device=config_to_dict(Device_name)
    Devicename=Connect(device)
    Devicename.sendline('show ip bgp summary')
    Devicename.expect('#')
    output =Devicename.before
    log.detail( "output is :",output)
    Devicename.sendline('show ip bgp summary')
    Devicename.expect('#')
    output =Devicename.before
    log.detail( "SECOND : output is :",output)
    fd = open("sample1.txt","w+")
    fd.write(output)
    fd.close()
    i=0
    fd = open("sample1.txt","r")
    line = fd.readlines()
    for eachline in line :
        pattern1 = r'(\d+\.\d+\.\d+\.\d+)\s*(\d+)\s*\d+\s*\d+\s*\S*\s*(\w+)'
        match1 = re.search(pattern1,eachline)
        pattern2 = r'(\d+::\d+)\s*(\d+)\s*\d+\s*\d+\s*\S*\s*(\w+)'
        match2 = re.search(pattern2,eachline)
        if match1 :
            Neighbor_IP = match1.group(1)
            Neighbor_AS = match1.group(2)
            Check_State = match1.group(3)
        else :
            if match2 :
                Neighbor_IP = match2.group(1)
                Neighbor_AS = match2.group(2)
                Check_State = match2.group(3)
        if match1 or match2:
            if Check_State ==  state :
                i=i+1
                log.success("Nexthopip is "+Neighbor_IP+" ASnum is "+Neighbor_AS+" neighborship state is: "+Check_State)
            else:
                
                log.failure( "Neighborship is not established on "+Device_name+"on nexthopip"+Neighbor_IP+" ASnum is "+Neighbor_AS) 
   # if device=="device1" or device=="device4":
   #     if i==4 :
   #         os.remove("sample1.txt")
   #         log.success("Neighborship is established"+Device_name)
    #        return True
    #    else :
#	    log.failure("Neighborship is established"+Device_name)
#            os.remove("sample1.txt")
#            return False 
    if i==2 :
        log.success("Neighborship is established on  Device: "+Device_name)
        os.remove("sample1.txt")
        return True
    else :
        log.failure("Neighborship is not established on Device: "+Device_name)
        os.remove("sample1.txt")
        return False   


#--------------------------------------------------------------------------------# 
#-------------------Checking for the Routemap Established state----------------------#
#--------------------------------------------------------------------------------#

   

def show_ip_bgp_bestpath(device,Network_IP,routemap=""):
    Device_name=Device_parser(device)
    call_device=config_to_dict(Device_name)       
    Devicename=Connect(device)
    displaytime(120,'to get Neighbor state as established')
    log.step(" Check for the Best-path to the network "+Network_IP+"  on "+Device_name)
    Devicename.sendline('show ip bgp '+Network_IP)
    Devicename.expect('#')
    log.detail( Devicename.before)
    output =Devicename.before
    Devicename.sendline('show ip bgp '+Network_IP)
    Devicename.expect('#')
    actual = Devicename.before
    log.detail( actual)
    actual=actual.replace(" ", "")
    actual=actual.split('\n')
    length = len(actual)
    currentline = 0
    check = 0
    check1 = 0

    if routemap == "":             
        while(currentline<length):
            if "external,best" in actual[currentline]:
                check =1
                ip_address=actual[currentline-1]
                pattern = r'\s*(\d+\.\d+\.\d+\.\d+)\s*from\s*(\d+\.\d+\.\d+\.\d+)'
                match = re.search(pattern,ip_address)
                break
            currentline=currentline+1
        if check == 1 :
            log.success("Best path without Route-Map "+match.group(1))
            return match.group(1)
        else :
            log.fail("No best path found")
            return 0
    
    if routemap == "localpreference" :
        currentline=0
        while(currentline<length):
            if "external,best" in actual[currentline]:
                check = 1
                ip_address=actual[currentline-1]
                pattern = r'\s*(\d+\.\d+\.\d+\.\d+)\s*from\s*(\d+\.\d+\.\d+\.\d+)'
                match = re.search(pattern,ip_address)
                break
            currentline=currentline+1
        currentline = 0
        while(currentline<length):
            if "external" in actual[currentline]:
                if "best" not in  actual[currentline]:
                    check1 = 2
                    ip_address=actual[currentline-1]
                    pattern1 = r'\s*(\d+\.\d+\.\d+\.\d+)\s*from\s*(\d+\.\d+\.\d+\.\d+)'
                    match1 = re.search(pattern1,ip_address)
                    break
            currentline=currentline+1
        if check == 1 and check1 ==2 :
            log.success("Best path : "+match.group(1))
            return match1.group(2)
        elif check != 2:
            log.fail("no alternate path found")
            return 0
        else: 
            log.fail("No best path found")
            return 0
    

def routemap_prepend(device,Network_IP,routemap_name) :
     Device_name=Device_parser(device)
     call_device=config_to_dict(Device_name)
     testname = BuiltIn().get_variable_value("${TEST_NAME}")
     Network_IP=call_device[Device_name][testname][Network_IP]         
     Devicename=Connect(device)
     parse_info=calltestcaseparams('routemap')
     routemap_name=parse_info[routemap_name]
#Calling show_ip_bgp_bestpath to find best path IP Address
     bestpath=show_ip_bgp_bestpath(device,Network_IP,"set AS-PATH  prepend")
     check =0
     log.detail( bestpath)
     if bestpath != 0:
         Devicename.sendline('show running-config')
         Devicename.expect('#')
         output =Devicename.before
         pattern1 = r'router\s*bgp\s*(\d+)'
         match1 = re.search(pattern1,output)
         log.step("Configuring Route-Control via set AS-PATH  prepend  on  "+Device_name)
         Devicename.sendline('configure terminal')
         Devicename.expect('#')	
         Devicename.sendline('router bgp '+match1.group(1))
         Devicename.expect('#')
         Devicename.sendline('neighbor '+bestpath+' route-map '+routemap_name)
         Devicename.expect('#')
         Devicename.sendline('do sh run')	
         Devicename.expect('#')
         out=Devicename.before
         log.detail( out)
         log.success("Routemap is configured \"set AS-PATH  prepend\" attribute")
#Calling ClearBGP for *soft in and *soft out command
         ClearBGP(device)
         displaytime(120,'to get Neighbor state as established')
         log.step("Check for the Best-path to the network "+Network_IP+" after applying the Route-Map on "+Device_name)
         Devicename.sendline('do show ip bgp '+Network_IP)
         Devicename.expect('#')
         log.detail( Devicename.before)
         output =Devicename.before
         Devicename.sendline('do show ip bgp '+Network_IP)
         Devicename.expect('#')
         actual = Devicename.before
         log.detail( actual)
         actual=actual.replace(" ", "")
         actual=actual.split('\n')
         length = len(actual)
         currentline=0
         while(currentline<length):
             if bestpath in actual[currentline]:
                 thirdline = currentline+1 
                 if "best" not in actual[thirdline]:
                     check =1
                     break
             currentline=currentline+1
         if check == 1 :
             log.info("Best path is not in "+bestpath)
         else :
             log.fail("Best path is not changed")
             return False
         currrentline = 0
         while(currentline<length):
             if "best" in actual[currentline]:
	         ip_address=actual[currentline-1]
                 pattern = r'\s*(\d+\.\d+\.\d+\.\d+)\s*from\s*(\d+\.\d+\.\d+\.\d+)'
                 match = re.search(pattern,ip_address)
                 if match.group(1) != bestpath :
                     check = 2
                     break 
             currentline=currentline+1
         if check == 2 :
             log.success("best path is changed as "+match.group(1))
             return True
         else :
             log.fail("best path not changed")
             return False
     else :
        log.fail("No best path found")
        return False
                  
def verifyroutemap(device,name):
    Device_name=Device_parser(device)
    log.step(" Verify Route-Map is created with "+name+" attribute on "+Device_name)
    Devicename=Connect(device)
    Devicename.sendline('sh run')
    Devicename.expect('#')
    actual=Devicename.before
    log.detail( actual)
    actual=actual.replace(" ", "")
    actual=actual.split('\n')
    length = len(actual)
    currentline=0
    check=0
    while(currentline<length): 
        if name in actual[currentline]:
            check =1
            break
        currentline=currentline+1
    if check == 1:
        log.success("Route-Map is created with "+name+" attribute on "+Device_name)
        return True
    else:
        log.failure(name+" is not created on "+Device_name)
        return False
     
     
    
def routemap_localpreference(device,Network_IP,routemap_name) :
     Device_name=Device_parser(device)
     call_device=config_to_dict(Device_name)
     testname = BuiltIn().get_variable_value("${TEST_NAME}")
     Network_IP=call_device[Device_name][testname][Network_IP]         
     Devicename=Connect(device)
     parse_info=calltestcaseparams('routemap')
     routemap_name=parse_info[routemap_name]
#Calling show_ip_bgp_bestpath to find best path IP Address
     bestpath=show_ip_bgp_bestpath(device,Network_IP,"localpreference")
     check =0
     #log.detail( bestpath)
     if bestpath != 0:
         Devicename.sendline('show running-config')
         Devicename.expect('#')
         output =Devicename.before
         pattern1 = r'router\s*bgp\s*(\d+)'
         match1 = re.search(pattern1,output)
         log.step("Apply Route-map with \"local-preference\" attribute on "+Device_name)
         Devicename.sendline('configure terminal')
         Devicename.expect('#')	
         Devicename.sendline('router bgp '+match1.group(1))
         Devicename.expect('#')
         Devicename.sendline('neighbor '+bestpath+' route-map '+routemap_name)
         Devicename.expect('#')
         Devicename.sendline('do sh run')	
         Devicename.expect('#')
         out=Devicename.before
         log.detail( out)
         log.success("Route-map with \"local-preference\" attribute is configured ")
         out=out.replace(" ", "")
         out=out.split('\n')
         length = len(out)
         currentline=0
         while(currentline <length):
             if "local-preference" in out[currentline]:
                 out2=out[currentline]
                 pattern =r'set\s*local-preference\s*(\d+)'
                 match1=re.search(pattern,out2)
                 if match1:
                     log.detail( match1.group(1))
             currentline=currentline+1
#Calling ClearBGP for *soft in and *soft out command
         ClearBGP(device)
         displaytime(120,'to get Neighbor state as established')
         log.step("Check for the Best-path to the network "+Network_IP+" after applying the Route-Map on "+Device_name)
         Devicename.sendline('do show ip bgp '+Network_IP)
         Devicename.expect('#')
         log.detail( Devicename.before)
         output =Devicename.before
         Devicename.sendline('do show ip bgp '+Network_IP)
         Devicename.expect('#')
         actual = Devicename.before
         log.detail( actual)
         actual=actual.replace(" ", "")
         actual=actual.split('\n')
         length = len(actual)
         currentline=0
         while(currentline<length):
             if bestpath in actual[currentline]:
                 thirdline = currentline+1 
                 if "best" in actual[thirdline]:
                     check =1
                     break
             currentline=currentline+1

         if check != 1:
             log.fail("Best path is not changed")
             return False
         currrentline = 0
         while(currentline<length):
             if "external,best" in actual[currentline]:
                 line = actual[currentline]
	         ip_address=actual[currentline-1]
                 pattern = r'\s*(\d+\.\d+\.\d+\.\d+)\s*from\s*(\d+\.\d+\.\d+\.\d+)'
                 pattern3 = r'\s*Origin\s*IGP\,\s*metric\s*\d+\,\s*localpref\s*(\d+)\,\s*weight\s*\d+\,\s*valid\,\s*external\,\s*best'
                 match = re.search(pattern,ip_address)
                 match2 = re.search(pattern3,line)
                 if match.group(1) == bestpath :
                     if match2.group(1) ==  match1.group(1): 
                         check = 2
                         break 
             currentline=currentline+1
         if check == 2 :
             log.success("best path is changed as "+match.group(1)+" and localpreference is verified" )
             return True
         else :
             log.fail("best path not changed")
             return False
     else :
        log.fail("No best path found")
        return False
                  

#--------------------------------------------------------------------------------# 
#-------------------Verify route map Community------------ ----------------------#
#--------------------------------------------------------------------------------#   
 
def verify_routemap_community(device1,community):
    device=Device_parser(device1)
    log.step("Verify Route-Map is created with \"set community\" attribute on "+device) 
    switchterminal=Connect(device1)
    switchterminal.sendline('show running-config')
    switchterminal.expect('#')
    configinfo=switchterminal.before
    #log.detail( configinfo
    if community in configinfo:
        log.success("Route-Map is created with \"set community\" attribute on  "+device +" : success")
        return True
    else:
        log.success("Route-Map is not created with \"set community\" attribute on  "+device +" : Unsuccess")
        return False


#--------------------------------------------------------------------------------# 
#-------------------Display best path before route map community-----------------#
#--------------------------------------------------------------------------------#   
def Bestpath_Before_Community_Routemap(device3,Network_IP):
    Device_name=Device_parser(device3)
    call_device=config_to_dict(Device_name)
    testname = BuiltIn().get_variable_value("${TEST_NAME}")
    Network_IP=call_device[Device_name][testname][Network_IP]
    log.step('Check for the Best-path to the network '+Network_IP+' before applying the Route-Map from '+Device_name)
    show_ip_bgp_bestpath1(device3,Network_IP)
    log.success('Check for best path before applying the Routemap from '+Device_name+' is success')



#--------------------------------------------------------------------------------# 
#-------------------Configure route map community to device----------------------#
#--------------------------------------------------------------------------------#  
def Configure_routemap(device1,community):
    Device_name=Device_parser(device1)
    log.step("Apply Route-map with \"set community\" attribute on "+Device_name) 
    switchterminal=Connect(device1)
    parseinfo=calltestcaseparams('community')
    bgp=parseinfo['bgp']
    neighborIP=parseinfo['neighborIP']
    routemapname=parseinfo['routemapname']
    traffic=parseinfo['traffic']
    switchterminal.sendline('configure terminal')
    switchterminal.expect('#')
    switchterminal.sendline(bgp)
    switchterminal.expect('#')
    switchterminal.sendline('neighbor '+neighborIP+' route-map '+routemapname+' '+traffic)
    switchterminal.expect('#')
    switchterminal.sendline('do show running-config')
    switchterminal.expect('#')
    data= switchterminal.before
    log.detail( data)
    log.success('configure route map with \"set community\" attribute on '+Device_name+' is success')
   


#--------------------------------------------------------------------------------# 
#------------------check route map community on neighbor device-----------------#
#--------------------------------------------------------------------------------#   

def Check_routemap_community(device2,Expectedroutemap,loopback):  
    Device_name=Device_parser(device2)
    ClearBGP(device2)
    displaytime(60,'wait for update')
    log.step("Check routemap \"community no-advertise \" on "+Device_name) 
    switchterminal=Connect(device2)
    displaytime(60,'wait for update')
    loopback=calltestcaseparams(loopback)
    switchterminal.sendline('show ip bgp '+loopback)
    switchterminal.expect('#')
    data= switchterminal.before
    switchterminal.sendline('show ip bgp '+loopback)
    switchterminal.expect('#')
    data= switchterminal.before
    log.detail( data)
    if Expectedroutemap in data:
        log.success("Check routemap \"community no-advertise on\" "+Device_name+" is success")
        return True 
    else:
        log.success("Check routemap \"community no-advertise on\" "+Device_name+" is unsuccess") 
        return False
    

#--------------------------------------------------------------------------------# 
#-------------------Display best path after route map community-----------------#
#--------------------------------------------------------------------------------#   
def Bestpath_After_Community_Routemap(device3,Network_IP):
    Device_name=Device_parser(device3)
    log.step('Check for best path after applying the Routemap with \"set community\" attribute from '+Device_name)
    call_device=config_to_dict(Device_name)
    testname = BuiltIn().get_variable_value("${TEST_NAME}")
    Network_IP=call_device[Device_name][testname][Network_IP]
    show_ip_bgp_bestpath1(device3,Network_IP)
    log.success('Check for best path after applying the Routemap with \"set community\" attribute from '+Device_name+' is success')


# System Testing APIs
#*********************************
#*********************************

#-----------------------------------------------------------------------------------------------------------------------------------------#
#       Description: The function opens the configuration file (device.cfg) of the input device and converts it into a dictionary         #
#-----------------------------------------------------------------------------------------------------------------------------------------#

def calldevices(device):
    xml = open(device+'.cfg').read()
    try :
        parsedInfo = xmldict.xml_to_dict(xml)
        return parsedInfo
    except :
        print "There is no such file to parse "
        print "file name is not correct"

#---------------------------------------------------------------------------------------------------------------------------------------------#
# Description:The function opens the file in which the device information is given and returns the values of the particular device in a list  #
#---------------------------------------------------------------------------------------------------------------------------------------------#

def Get_deviceInfo(device):
    deviceparam=open('device.params').read()
    deviceInfo=deviceparam.splitlines() 
    for value in deviceInfo:
        pattern=device
        match=re.search(pattern,value)
        if match:          
            deviceList=value.split(',')
            return deviceList

#-----------------------------------------------------------------------------------------------------------------------------------------#
#                                           Description:Connects to the particular device                                                 #
#-----------------------------------------------------------------------------------------------------------------------------------------#

def connect_device(device):
    device_name=Deviceparser(device)
    device_Info=Get_deviceInfo(device_name)
    # name=device_Info[0]
    ip_address=device_Info[1]
    port=device_Info[2]
    user=device_Info[3]
    password=device_Info[4]
    mode=device_Info[5]
    refused="ssh: connect to host " +ip_address+ " port 22: Connection refused"
    connectionInfo = pexpect.spawn('ssh -p '+port +' ' +user+'@'+ip_address,env={ "TERM": "xterm-mono" },maxread=50000 )
    expect = 7
    while expect == 7:
        expect =connectionInfo.expect( ['Are you sure you want to continue connecting','password:|Password:',pexpect.EOF,pexpect.TIMEOUT,refused,'>|#|\$','Host key verification failed.'],120 )  
        if expect == 0:  # Accept key, then expect either a password prompt or access
            connectionInfo.sendline( 'yes' )
            expect = 7  # Run the loop again
            continue
        if expect == 1:  # Password required                
            connectionInfo.sendline(password)
            connectionInfo.expect( '>|#|\$')
            if connectionInfo.expect:
                log.failure('Password for '+device_name+' is incorrect')
                raise testfail.testFailed('Password for '+device_name+' is incorrect')
                break
        elif expect == 2:
            log.failure('End of File Encountered while Connecting '+device_name)
            raise testfail.testFailed('End of File Encountered while Connecting '+device_name)
            break
        elif expect == 3:  # timeout
            log.failure('Timeout of the session encountered while connecting')
            raise testfail.testFailed('Timeout of the session encountered')
            break
        elif expect == 4:
            log.failure('Connection to '+device_name+' refused')
            raise testfail.testFailed('Connection to '+device_name+' refused')
            break
        elif expect == 5:
            pass
        elif expect == 6:
            cmd='ssh-keygen -R ['+ip_address+']:'+port
            os.system(cmd)
            connectionInfo = pexpect.spawn('ssh -p '+port +' ' +user+'@'+ip_address,env={ "TERM": "xterm-mono" },maxread=50000 )
            expect = 7
            continue
    connectionInfo.sendline("")
    connectionInfo.expect( '>|#|\$' )
    if mode=='OPS':
        connectionInfo.sendline('vtysh')
        connectionInfo.expect('>|#|\$')
    return connectionInfo

#-----------------------------------------------------------------------------------------------------------------------------------------#
#                                         Description:Parses the parameter file to get device name                                        #
#-----------------------------------------------------------------------------------------------------------------------------------------#


def Deviceparser(device="") :
    xml = open('OpenSwitch_ST_01.params').read()
    parsedInfo = xmldict.xml_to_dict(xml)
    if device!="":
        device=str(device)
        device_name=parsedInfo['TestCase']['Device'][device]
        return device_name
    else:
        device_name=parsedInfo['TestCase']['Device']
        return device_name

#-----------------------------------------------------------------------------------------------------------------------------------------#
#                                          Description:Parses the parameter file to get parameters                                        #
#-----------------------------------------------------------------------------------------------------------------------------------------#

def getTestCaseParams(testcase="",test=""):
	testcase=str(testcase)
	if test=="":
		xml = open('OpenSwitch_ST_01.params').read()
		tc=xmldict.xml_to_dict(xml)
		testcaseInfo=tc['TestCase'][testcase]
		return testcaseInfo
	elif test!="":
		xml = open('OpenSwitch_ST_01.params').read()
		tc=xmldict.xml_to_dict(xml)
		test_values=tc['TestCase'][testcase][test]
		return test_values 

#-----------------------------------------------------------------------------------------------------------------------------------------#
#                                        Description:Extracts the neighbor info                                                           #
#-----------------------------------------------------------------------------------------------------------------------------------------#

def Extract_neighbors(device):
	asnum=[]
	device_name=Deviceparser(device)
	config_Info=calldevices(device_name)
	bgpInfo=config_Info[device_name]['BGP']
    	bgpList = bgpInfo.split('\n')
    	for line in bgpList :
       		pattern=r'(neighbor\s+(\d+\.\d+\.\d+\.\d+)\s+remote-as\s+(\d+))'
		match=re.search(pattern,line)
		if match:
			asnum.append(match.group(2))
		else:
			pass
	return asnum

#-----------------------------------------------------------------------------------------------------------------------------------------#
#                                   Description:Checks the state whether it is established or not                                         #
#-----------------------------------------------------------------------------------------------------------------------------------------#

def Check_state(device,state):
    neighbours=0
    Established_neighbors=[]
    device_name=Deviceparser(device)
    config_Info=calldevices(device_name)
    log.step('Log-in into '+device_name+' to check '+state+' state')
    connectionInfo=connect_device(device)
    connectionInfo.sendline('show ip bgp summary')
    connectionInfo.expect('#')
    Output =connectionInfo.before
    log.info('checking that the device '+device_name+' is in '+state+' state or not')
    log.detail(Output)
    fd = open("sample.txt","w+")
    fd.write(Output)
    fd.close()
    f = open("sample.txt","r")
    line = f.readlines()
    for eachline in line :
        pattern = r'(\d+\.\d+\.\d+\.\d+)\s*\d+\s*\d+\s*\d+\s*\d+\:\d+\:\d+\s*(\S+)'
        match = re.search(pattern,eachline)
        if match:
            neighbours=neighbours+1
            if match.group(2)==state:
                Established_neighbors.append(match.group(1))
    os.remove("sample.txt")
    if neighbours==len(Established_neighbors):
        log.success('The required '+state+' state is achived in '+device_name+'\n')
    else:
        log.failure("The Required state is not achieved for all the IP's")
        raise testfail.testFailed("The Required state is not achieved for all the IP's")

#-----------------------------------------------------------------------------------------------------------------------------------------#
#                                    Description:creates and configures the loopback                                                      #
#-----------------------------------------------------------------------------------------------------------------------------------------#
          
def Create_loopback(device):
        loopback=[]
        device_name=Deviceparser(device)
        device_Info=calldevices(device_name)
	loopbackInfo=device_Info[device_name]['Loopback'];
        loopbackList=loopbackInfo.split('\n')
        bgpInfo=device_Info[device_name]['BGP']
        bgpList = bgpInfo.split('\n')
        for loopbackip in loopbackList:
            pat=r'ip\s+address\s+((\d+\.\d+\.\d+\.\d+)\/\d+)'
            match=re.search(pat,loopbackip)
            if match:
                loopback.append(match.group(1))
        log.step('Log-in into '+device_name+' and create loopback')
        connectionInfo=connect_device(device)
        connectionInfo.sendline('configure terminal')
        connectionInfo.expect('#')
        log.info("creating loopback for "+device_name+" with loopback ip "+loopback[0])
        for loopbackip in loopbackList: 
            connectionInfo.sendline(loopbackip)
            connectionInfo.expect('#')
	    log.detail(connectionInfo.before)
        log.info('loopback created successfully')
        connectionInfo.sendline('exit')
        connectionInfo.expect('#')
        connectionInfo.sendline(bgpList[0])
        connectionInfo.expect('#')
        for loopbackip in loopback:
            connectionInfo.sendline('network '+loopbackip)
            connectionInfo.expect('#')
	    log.info('Advertising ip '+loopbackip+' to neighbors')
	    log.detail(connectionInfo.before)
            
        connectionInfo.sendline('end')
        connectionInfo.expect('#')
        connectionInfo.sendline('exit')           
        connectionInfo.expect('$')
        for loopbackip in loopback:
            log.success('loopback created for '+device_name+" with loopback ip "+loopback[0] +"\n")
        return loopback[0]
           
#-----------------------------------------------------------------------------------------------------------------------------------------#
#                                    Description:checks for equal cost path between two devices
#-----------------------------------------------------------------------------------------------------------------------------------------#

def check_equalcost_path(device ,dest_device):
    loopback=[]
    client=Deviceparser(device)
    device_name=Deviceparser(dest_device)
    device_Info=calldevices(device_name)
    config_Info=device_Info[device_name]['Loopback'];
    configlist=config_Info.split('\n') 
    for value in configlist:
        pat=r'ip\s+address\s+((\d+\.\d+\.\d+\.\d+)\/\d+)'
        match=re.search(pat,value)
        if match:
            loopback.append(match.group(2))
    loopbackip=loopback[0]
    log.step('Check for Equal cost path from '+client+' to '+device_name)
    as_num=[]
    paths=0
    log.info('Log-in into '+client+' and check for Equal cost path')       
    connectionInfo=connect_device(device)
    connectionInfo.sendline('sh ip bgp '+loopbackip)
    expected_value=connectionInfo.expect(['% Network not in table','% No bgp router configured','#'])
    if expected_value == 0:
        raise testfail.testFailed('The given loopback ip is not in the table of '+client)
    if expected_value == 1:
        raise testfail.testFailed('The router of '+client+' is not Configured')
    if expected_value == 2: 
        connectionInfo.expect('#')
        Output=connectionInfo.before
	log.detail(Output)
        fd = open("sample.txt","w+")
        fd.write(Output)
        fd.close()
        fopen = open("sample.txt","r")
        line = fopen.readlines()
        for eachline in line :
            pat=r'AS:((\s+\d+)*)'
            match=re.search(pat,eachline)
            if match:
                as_num.append(match.group(1))
        first_equal_cost=as_num[0]
        for i in range(0,len(as_num)):
            if as_num[i]== first_equal_cost:
                paths=paths+1
        paths=str(paths)
        log.success('The loopback has '+paths+' equal cost path from '+device_name+' to '+client +'\n')

#-----------------------------------------------------------------------------------------------------------------------------------------#
#                          Description:To reset the neighbor relationships in both directions                                             #
#-----------------------------------------------------------------------------------------------------------------------------------------#

def ClearBGP(device):
    device_name=Deviceparser(device)
    connectionInfo=connect_device(device)
    log.step("clear the bgp for the device "+device_name)
    connectionInfo.sendline("clear bgp * in")
    connectionInfo.sendline("clear bgp * out")
    log.success('BGP cleared successfully for the device '+device_name +'\n')

#-----------------------------------------------------------------------------------------------------------------------------------------#
#                                       Description: Checks for the best path for given ip                                                #
#-----------------------------------------------------------------------------------------------------------------------------------------#

def checkBestPath(device,ip):
    device_name=Deviceparser(device)
    connectInfo=connect_device(device)
    ip1=ip.split("/")
    ip_address=ip1[0]
    log.step('Log-in into '+device_name+' and check for best path')
    log.info("checking best path from "+device_name+" to "+ip_address)
    #print "*******************************************************"*2
    #print "STEP : checking best path from "+device_name+" to "+ip_address
    #print "*******************************************************"*2
    connectInfo.sendline("sh ip bgp "+ip_address)
    pat='\w+\d+\#'
    connectInfo.expect(pat)
    result = connectInfo.before
    log.detail(result)

    pat=re.compile(r'(.*\d+\.\d+\.\d+\.\d+\s+from\s+)(\d+\.\d+\.\d+\.\d+)(\s+Origin \w*, metric \d+, localpref \d+, weight \d+, valid, external, best)',re.MULTILINE)
    try:
        match=re.search(pat,result)
        bestIP=match.group(2)
    except:
        bestIP=""
    if bestIP:
        log.success("Best path for "+device_name+" to "+ip_address+" is through the route "+bestIP +'\n')
	#print "-----------------------------------------------------------------------------------"
	#print "RESULT : Best path for "+device_name+" to "+ip_address+" is through the route "+bestIP +'\n'
	#print "-----------------------------------------------------------------------------------"
        return bestIP 
    else:
        return False
    

#-----------------------------------------------------------------------------------------------------------------------------------------#
#                           Testcase: Description: Verify IPv4 BGP on all devices                                                         #
#-----------------------------------------------------------------------------------------------------------------------------------------#

def ipv4_verification():
    switches=[]
    fabs=[]
    leaves=[]
    test_name = "Testcase1"
    total_fabs=getTestCaseParams(test_name,'fabs')
    total_leaves=getTestCaseParams(test_name,'leaves')
    list_of_fabs=total_fabs.split('\n')
    for device in list_of_fabs:
        device=device.strip()
        fabs.append(device)
    list_of_leaves=total_leaves.split('\n')
    for device in list_of_leaves:
        device=device.strip()
        leaves.append(device)
    switches.extend(leaves)
    switches.extend(fabs)
    for switch in switches:
        Check_state(switch,'Established')
    for leaf in leaves:
        lb=Create_loopback(leaf)
    for leaf in leaves:
        for fab in fabs:
            check_equalcost_path(fab,leaf)
    
      
#-----------------------------------------------------------------------------------------------------------------------------------------#
#                          Testcase: Description: clears BGP routing process and checks for system recovery                               #
#-----------------------------------------------------------------------------------------------------------------------------------------#

def ClearBGPRouting(device1,device2):
    device_name1=Deviceparser(device1)
    device_name2=Deviceparser(device2)
    test_name = "Testcase2"
    states=getTestCaseParams(test_name)
    s1=states['state']
    ip=Create_loopback(device2)
    bestIp1=checkBestPath(device1,ip)
    ClearBGP(device1)
    time.sleep(40)
    checkBGPState=Check_state(device1,s1)
    bestIp2=checkBestPath(device1,ip)
    log.step('check whether routing protocol is recovering or not')
    if bestIp2:
        log.info('Best path changed changed from '+bestIp1+' to '+bestIp2 +'\n')
        log.success('Routing protocol recovered successfully')
    else:
        raise testfail.testFailed('Routing protocol is not recovered')

#-----------------------------------------------------------------------------------------------------------------------------------------#
#                                  Testcase:Description: checks for lldp information for neighbor                                         #
#-----------------------------------------------------------------------------------------------------------------------------------------#
   
def ChecklldpNeighborInfo():
    devices = Deviceparser()
    Result=[]
    for device in devices:
        Result.append(lldpNeighborInfo(device))
    if "Fail" in Result:
        raise testfail.testFailed("LLDP neighbor information does not matches with the given information\n")
#-----------------------------------------------------------------------------------------------------------------------------------------#
#                                            Description:Gives the lldp information of neighbor                                           #
#-----------------------------------------------------------------------------------------------------------------------------------------#
    
def lldpNeighborInfo(device):
    connectionInfo=connect_device(device)
    test_name="Testcase5"      
    device_name=Deviceparser(device)
    device_params=getTestCaseParams(test_name,device_name)
    log.step('Checking LLDP neighbor information for the device: '+device_name)
    lldp_dict = ast.literal_eval(device_params)
    j=0
    for i in range(len(lldp_dict)):
        source=lldp_dict[i][j]
        dest=lldp_dict[i][j+1]
        source_params=source.split(':')
        dest_params=dest.split(':')
        source_name=source_params[0]
        source_port=source_params[1]
        dest_name=dest_params[0]
        dest_port=dest_params[1]
        connectionInfo.sendline('show lldp neighbor-info '+source_port)
        connectionInfo.expect('#')                  
        result= connectionInfo.before         
        connectionInfo.expect('#')
        result = result+connectionInfo.before
	log.detail(result)
        pattern1 = r'Neighbor\s*Port\-ID\s*\:\s*(\d+)'
        pattern2 = r'Neighbor\s*Chassis\-Name\s*\:\s*(\w+)'
        pattern3 = r'Port\s*\:\s*(\d+)'
        match =re.search(pattern1,result) 
        match1 = re.search(pattern2,result)
        match2 = re.search(pattern3,result)
        if match :
            neighborportid = match.group(1) 
        if match1 :
            chassisname = match1.group(1)
        if match2:
            portid = match2.group(1)
        if source_port==portid and dest_name==chassisname and dest_port==neighborportid:
            log.info("port "+portid+" of "+device_name+" is connected to port "+neighborportid+" of "+chassisname)
            i=1
        else:
            i=0
            break
           
    if i==1:
        log.success('LLDP neighbor information matched with the given information\n')
        return "Pass"
    else:
        log.failure('LLDP neighbor information does not matches with the given information\n')
        return "Fail"    
        
#--------------------------------------------------------------------------------------------------------------------------------------------#
#  TriggerLink_FailureRecovery  Input:: eg.device1,device13  Description:: 1. Creates Loopback in device13                                   #
#																		   2. Finds Best path in device1 for that Loopback					 #
#																		   3. Shutdowns the best path's interface in device1                 #
#																		   4. Ensures Whether it takes some other best path                  #
#--------------------------------------------------------------------------------------------------------------------------------------------#

def  TriggerLink_FailureRecovery (FAB,LEAF):
    success=0
    ShutdownInterfaces=[]
    LeafName=Deviceparser(LEAF)
    FabName=Deviceparser(FAB)
    connectionInfo=connect_device(FAB)
    test_name="Testcase3"	
    loopbackIp=Create_loopback(LEAF)
    while(1):
        bestIp=checkBestPath(FAB,loopbackIp)
        if bestIp:
            ip=bestIp.split('.')
            bestIPLastDigit=int(ip[3])
            BestIPNetwork=str(ip[0])+'.'+str(ip[1])+'.'+str(ip[2])+'.'
            bestIPLast=int(bestIPLastDigit)-1
            connectionInfo.sendline('show running-config')
            connectionInfo.expect('[#\$] ')
            showRunningConfig = connectionInfo.before
            pattern=re.compile(r'(\n*\s*interface (\d+)\n*\s*no shutdown\n*\s*ip address )'+BestIPNetwork+str(bestIPLast)+r'(/\d+)',re.MULTILINE)
            match=re.search(pattern,showRunningConfig)
            if match:
                State='down'
                log.step("Shut-down the BestPath from device "+FabName+" to desired network "+loopbackIp+ " .")
		#print "***"*45
		#print "Shut-down the BestPath from device "+FabName+" to desired network "+loopbackIp+ " ."
                ShutdownInterfaces.append(str(match.group(2)))
                InterfaceStateChange(FAB,str(match.group(2)),State) 
            success=1
        else:
            #log.success("Now there are no best paths for the device "+FabName+"\n")
            break
    if success==1:
        log.success("TriggerLink Failure Recovery Test has verified successfully\n")
    log.step("Bring up the shutdown interfaces")
    for ShutdownedInterface in ShutdownInterfaces:
        result=InterfaceStateChange(FAB,ShutdownedInterface,State='up')
    if result:
        log.success("Interfaces Brought up successfully\n")

#--------------------------------------------------------------------------------------------------------------------------------------------#
#     InterfaceStateChange  Input::eg.device1,2,up      Output:: Change the Interface state for the given device                             #
#--------------------------------------------------------------------------------------------------------------------------------------------#

def  InterfaceStateChange (Device,InterfaceName,State) :
    device_name=Deviceparser(Device)
    connectionInfo=connect_device(Device)
    log.info('changing the state of '+device_name+' interface to '+State)
    #print 'changing the state of '+device_name+' interface to '+State
    
    connectionInfo.sendline('configure terminal')
    connectionInfo.expect('[#\$] ')
    connectionInfo.sendline('interface '+InterfaceName)
    connectionInfo.expect('[#\$] ')
    log.detail(connectionInfo.before)
    if State == 'up':
        connectionInfo.sendline('no shutdown')
        connectionInfo.expect('[#\$] ')
	log.detail(connectionInfo.before)
        log.success("Interface "+InterfaceName+" of "+device_name+" has been Turned up\n")
	#print "Interface "+InterfaceName+" of "+device_name+" has been Turned up\n"
        return True
    elif State == 'down':
        connectionInfo.sendline('shutdown')
        connectionInfo.expect('[#\$] ')
	log.detail(connectionInfo.before)
        log.success("Interface "+InterfaceName+" of "+device_name+" has been shut down\n")
	#print "Interface "+InterfaceName+" of "+device_name+" has been shut down\n"
    connectionInfo.sendline('end')
    connectionInfo.expect('[#\$] ')
    #print connectionInfo.before

#-----------------------------------------------------------------------------------------------------------------------------------------#
#                     Testcase:Description:Adds Acl rules and checks whether they are added to respective interfaces                      #
#-----------------------------------------------------------------------------------------------------------------------------------------#


def ACLTest(FAB,LEAF):
    aclresult=0
    intresult=0
    connectionInfo=connect_device(FAB)
    LeafName=Deviceparser(LEAF)
    FabName=Deviceparser(FAB)
    loopbackIp=Create_loopback(LEAF)
    log.step("Create ACL rules with name ROUTE and apply in all interfaces "+FabName)
    device_Info=calldevices(FabName)
    ACLInfo=device_Info[FabName]['ACL']
    InterfaceInfo=device_Info[FabName]['Interface']
    ACLrules=ACLInfo.split('\n')
    Interfacelist=InterfaceInfo.split('\n')
    for ACLrule in ACLrules:
          connectionInfo.sendline(ACLrule)
          connectionInfo.expect('[#\$] ')
	  log.detail(connectionInfo.before)
          aclresult=1
    log.info("ACL rules are created with name 'ROUTE' successfully" )	
    for int1 in Interfacelist:
        connectionInfo.sendline(int1)
        connectionInfo.expect('[#\$] ')
	log.detail(connectionInfo.before)
        intresult=1
    log.info("ACL 'Route' is applied to all the interfaces" )
    if aclresult==1 and intresult==1:
        log.success("Creating and applying ACL rules with name ROUTE for device "+FabName+" has been done successfully\n")
    else:
        raise testfail.testFailed("Creating ACL rules failed")
    log.step("clear ACL hitcounts in "+FabName)
    connectionInfo.sendline("clear access-list hitcounts all")            
    connectionInfo.expect('[#\$] ')
    log.detail(connectionInfo.before)
    log.success("ACL Hitcounts are cleared in "+FabName+" successfully\n")
    log.step("start traffic in "+LeafName+" to generate hitcounts on "+FabName)
    connectionInfo1=connect_device(LEAF)
    connectionInfo1.sendline('ping '+loopbackIp)
    connectionInfo1.expect('[#\$] ')
    log.success("Ping Traffic generated successfully\n")
    log.step("show the hitcounts in "+FabName)
    connectionInfo.sendline("show access-list hitcounts ip ROUTE")            
    connectionInfo.expect('[#\$] ')
    log.detail(connectionInfo.before)
    log.info("Hit counts got changed")
    #print connectionInfo.before
    log.success("ACL Testcase is successful!!!\n")
	
 
