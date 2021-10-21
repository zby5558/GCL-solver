# GCL-solver

This project can derive gate control lists of TSN networks and then gernerate two xml files for the routing and GCL control, which can be used in the Nesting project https://omnetpp.org/download-items/NeSTiNg.html.

Two files are needed to create a TSN network. In this repo, we have an example of two files, which are testGCLPattern.txt and testGCLLink.txt. Note that two files should have the same prefix. If we want to create an example network called exmaple, the names of the two files should be examplePattern.txt and exampleLink.txt. We can run TSN_GCL_solver.py to generate two xml files. Each time we run TSN_GCL_solver.py, we should modify dirName and fileName1 so that it can choose the correct output folder and input files. 

The Pattern.txt files defines the hyperperiod, which is the least common multiple of all periods of all flows. Each flow has a flowID, a period whose unit is ms, a packet size whose unit is B, a path containing the source and destination, a Delay requirement, a jitter requirement, a host, which is the source of the flow, a mac address for the destination, which is used by the nesting project, and a queue, which must be 7. An example is shown below
FlowID: 1
Period: 150
Size: 1250
Path: source1-switchA-switchB-switchC-dest1
Delay-requirement: 50
Jitter-requirement: 50
Host: source1
Dest: 00-00-00-00-00-03
Queue: 7

The Link.txt files define the capacity of links. Each link should have a switch, which is the source of the link, a port, which should be compatiable with the port declared in the nesting project files, a link, which contains the two nodes of the link, a delay in unit ms, and a speed in unit Mbps. An example is shown below:
Switch: switchA
Port: 2
Link: switchA-switchB
Delay: 0
Speed: 1000

Note that if the source of a link is a host instead of a switch, the switch component of the link should be Null. An example is shown below:
Switch: Null
Port: 0
Link: source1-switchA
Delay: 0
Speed: 1000
