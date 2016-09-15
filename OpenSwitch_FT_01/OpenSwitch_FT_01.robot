*** Settings ***
Documentation    Test Suite ID 		: 	LINKED_IN_FT_01
...
...              Test Suite Name 	: 	OpenSwitch_FT_01
...
...              Created 		:	24-Aug-2016
...
...              Status 		: 	Completed 
...
...              @authors		: 	TERRALOGIC TEAM
...
...              Abstract 		:       This test suite examines the basic functionalities of OpenSwitch using "Dockers Setup"
...
...              Test-cases List 	:	1.Verify the functionality of Static Routing.	
...              			: 	2.Verify the functionality of BGP Timers.
...              			: 	3.Verify the IPV6 EGBP neighbor.
...              			: 	4.Verify the functionality of Remove-private AS.
...              			: 	5.Verify BGP Authentication .
...              			: 	7.Verify neighbour state changes using "log-neighbor-changes".
...              			: 	8.Verify "Soft-reconfiguration inbound always".
...              			: 	9.Verify the BFD setup with multiple BFD timers.
...					:	10.Verify EBGP PeerGroup configuration
...					:	11.Verify IPV4 VLAN with EBGP Configuration 
...					:	13.Verify the BGP Route Control with LOCALPREFERENCE attribute

Library   ../common/OpenSwitchCliDriver.py
Library   SSHLibrary
Library   OperatingSystem

#---------------------------------------5-NODES-OpenSwitch TOPOLOGY----------------------
#
# 	NODES : #FAB05, #FAB06, #CSW01, #CSW02, #ASW01
#
#
#
#				 	1.1.1.1/32
#						|   # 64700
#                                              FAB05--------------FAB06
#	10.0.20.0/31			    .0|    |.2			10.0.20.2/31
#  				|--------------    -----------------
#			      .1|				    |.3
#                  #64850     CSW01                                CSW02  #64850
#			     .0	|				     |.0
#				|				     |
#				----------------     ----------------
#	10.0.4.0/31			     .1	|    | .1		10.0.5.0/31
#						 ASW01   #64900
#
#-----------------------------------------------------------------------------------------

*** Variables ***
${expectedinfo1}   community no-advertise
${expectedinfo2}   Community: no-advertise
${expectedstate}            Established
${Expectedconfigstate}      inbound_soft_reconfiguration: Enabled
${flag0}                    1
*** Testcases ***
#TestCase11
#        [Documentation]  Verify IPV4 and VLAN with EBGP Configuration  
#        RemoveConfig  device1  device2 
#        LoadBaseconfigurations  device1  device2  device3  device4 
#        displaytime  100  to get neighborship in Established state     
#      Sleep  120
#        Check Neighborship for vlan     
#        Configure  device1  removevlan
#        Configure  device2  removevlan
#        Configure  device3  removevlan
#        Configure  device4  removevlan
#        RemoveConfig  device3  device4  device1  device2


TestCase1

         [Documentation]  Verify the functionality of Static Routing    
         LoadBaseconfigurations  device1  device3          
         Ping  device3  device1

TestCase2
         [Documentation]  Verify the functionality of BGP Timers
         RemoveConfig  device1  device3
         LoadBaseconfigurations  device1  device2  
         displaytime  120 	  
#         Sleep  120
	 Check BGP Neighborship state

TestCase3

         [Documentation]  Verify EBGP neighborship with IPV6 addressing
         RemoveConfig  device1  device2       
         LoadBaseconfigurations  device1  device2     
         ${neighborstateof_fab05}=  CheckIPV6Neighborship  device1  ${expectedstate}
         Should Be True  ${neighborstateof_fab05}     


TestCase4

         [Documentation]  Verify the functionality of Remove-private AS
         RemoveConfig  device1  device2         
         LoadBaseconfigurations  device1  device2  device3         
         ${out1}  Remove_Private  device3
         Should Be True  ${out1}

TestCase5
         [Documentation]  Verify BGP Authentication
         RemoveConfig  device1  device2  device3                
         LoadBaseconfigurations  device1  device2  device3
	 Check BGP Neighborship

#TestCase7

#         [Documentation]  Verify neighbour state changes using "log-neighbor-changes"
#         RemoveConfig  device1  device2  device3  device4
#         Establish EBGP neighbourship between FAB-CSW and CSW-ASW.
#         Verify "log-neighbor-changes" in FAB05
#         Veirfy "show ip bgp summary" in FAB05 and its status should be Established
#         Flap the neighborships of CSW02        
#         Verify neighbour of CSW02 After Flap

TestCase8 

         [Documentation]  Verify "Soft-reconfiguration inbound always"
         RemoveConfig  device1  device3  device4
         Establish EBGP neighbourship between FAB-CSW and CSW-ASW.
         Enable "soft-reconfiguration inbound always" BGP command
         Flap the neighborships of CSW02
         Verify neighbour of CSW02 After Flap 

TestCase9

        [Documentation]  Verify the BFD setup with multiple BFD timers      
        LoadBaseconfigurations  device2  device5
        check BFD 
        bringUpLink  device5  2
        RemoveConfig  device2  device5

TestCase10
        [Documentation]  Verify EBGP PeerGroup configuration
        RemoveConfig  device1  device3  device4 
        LoadBaseconfigurations  device1  device2       
    	${out} =  CheckNeighbor  device1  Established
    	Should Be True  ${out} 
    	${out} =  CheckPeerGroupNeighborship  device1  PEERGROUP
    	Should Be True  ${out}
        RemoveConfig  device1  device2

TestCase13

         [Documentation]  Verify the BGP Route Control with LOCALPREFERENCE attribute
         RemoveConfig  device1  device2  device3  device4
	 LoadBaseconfigurations  device1  device2  device3  device4
         ${out1}=  verifyroutemap  device3  setlocal-preference 
	 Should Be True  ${out1}
         ${out1}=  routemap_localpreference  device3  Network_IP  localpreference
	 Should Be True  ${out1}         
         RemoveConfig  device1  device2  device3  device4



*** Keywords ***
##----------EBGP neighbourship------------------##
Check BGP Neighborship state
         ${out}  CheckNeighborship  device2  Established
         Should Be True  ${out}
         shutdown_link  device2  1
         displaytime  10  to get Neighbor state Established	    
#         Sleep  15  
         ${out1}  CheckNeighborship  device1  Established
         Should Be True  ${out1}    
         displaytime  15  to get Neighbor state Established	        
#         Sleep  120
         ${out2}  CheckNeighborship  device1  Idle
         Should Be True  ${out2}

Check BGP Neighborship          
         ConfigureRoute  device1  bgppassword
   	 ${out} =  CheckNeighbor  device2  Connect
    	 Should Be True  ${out}
    	 ConfigureRoute  device2  bgppassword
    	 ${out} =  CheckNeighbor  device2  Established
    	 Should Be True  ${out}
    	 ConfigureRoute  device2  password
    	 ${out} =  CheckNeighbor  device3  Connect
    	 Should Be True  ${out}
    	 ConfigureRoute  device3  bgppassword
    	 ${out} =  CheckNeighbor  device3  Established
    	 Should Be True  ${out}

Establish EBGP neighbourship between FAB-CSW and CSW-ASW.

       [Tags]   Establish EBGP neighbourship between FAB-CSW and CSW-ASW.
       EBGP_neighbourship    device1  device4    device3

Veirfy "show ip bgp summary" in FAB05 and its status should be Established

       [Tags]  Checking for Connection Establishment 
       ${recivestate}=  showbgpsummary  device1
       Should Be Equal   ${expectedstate}   ${recivestate}

Flap the neighborships of CSW02

       [Tags]   Removing Neighbourship of CSW02  
       ${out}=  flapneighboursCSWO2  device4
       Should Be True  ${out}
  
Verify "log-neighbor-changes" in FAB05

        [Tags]  Verify "log-neighbor-changes" in FAB05  After Flap
	${out}=  VerifyLogNeighbor  device1 
        Should Be True  ${out}

Verify neighbour of CSW02 After Flap

       [Tags]   Verify the EBGP nieghborship states 
       ${flag1}=  verifyneighboursofCSW02   device1
       Should Be True  ${flag1}

Enable "soft-reconfiguration inbound always" BGP command

       [Tags]  Enabling soft reconfiguration to FAB05 
       ${recivestate}=  Enablereconfig   device1  ${Expectedconfigstate}
       Should Be Equal   ${Expectedconfigstate}   ${recivestate}

Check Neighborship for vlan
        ${out} =  CheckNeighborvlan  device1  Established
        Should Be True  ${out} 
        ${out} =  CheckNeighborvlan  device2  Established
        Should Be True  ${out}      
        ${out} =  CheckNeighborvlan  device3  Established
        Should Be True  ${out}
        ${out} =  CheckNeighborvlan  device4  Established
        Should Be True  ${out}    

check BFD
        ${out} =  CheckBFDUp  device5  sh bfd neighbors
   	Should Be True  ${out} 
        shutdown_link  device5  2
        ${out} =  CheckBFDIdle  device5  ngh1   Idle
  	Should Be True  ${out} 
	${out} =  CheckBFDDown  device5  sh bfd neighbors
   	Should Be True  ${out} 
