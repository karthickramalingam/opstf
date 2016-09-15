*** Settings ***
Documentation    Test Suite ID 		: 	LINKED_IN_ST_01
...
...              Test Suite Name 	: 	OpenSwitch_ST_01
...
...              Created 		:	24-Aug-2016
...
...              Status 		: 	Completed 
...
...              @authors		: 	TERRALOGIC TEAM
...
...              Abstract 		:       This test-suite examines the basic functionalities of OpenSwitch using "Dockers Setup"
...
...              Test-cases List 	:	1.Verify IPv4 BGP on all devices	
...              			: 	2.Manually clear BGP routing process. Measure convergence time and verify system status.
...              			: 	3.Trigger link failure and link recovery. Measure convergence time and verify system status.
...              			: 	4.Verify that all ACLs with required number of rules are assigned to port-based and SVI interfaces.
...              			: 	5.Verify lldp feature.

Library		../common/OpenSwitchCliDriver.py
Library		SSHLibrary
Library		String
Library 		Collections
Suite Teardown	Close All Connections

*** Test Cases ***

Testcase-1 : Verify IPv4 BGP on all devices 
    [Documentation]  Verifies IPv4 BGP for all devices
    IPv4_verification  

Testcase-2 : Verify clear BGP routing process
    [Documentation]  Clears BGPRouting and checks best path is established or not
	ClearBGPRouting  Device1  Device13

Testcase-3 : Verify Trigger link failure and link recovery
   [Documentation]  Checks whether the link failure is recovered or not
   TriggerLink_FailureRecovery   Device1  Device13

Testcase-4 : Verify ACL with 15 rules
   [Documentation]  Adds Acl rules and checks whether they are added to respective interfaces
   ACLTest  Device1  Device13

Testcase-5 : Verify lldp feature
    [Documentation]  Checks LLDP neighbor information with the given information
    ChecklldpNeighborInfo



