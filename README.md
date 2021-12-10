# ActiveFlowSense

FlowSense algorithm is combined with active probing so as to increase the frequency at which we get utilization values. 

Various existing active and passive network utilization measurement methods require overhead and infrastructure respectively. [1] defines the FlowSense algorithm, which uses an approach wherein the existing control messages in the network are used to measure the utilization. Hence, there is no additional overhead or infrastructure requirements. But this method has various limitations such as in the case of long flows, proactive rules etc. The limitations can be overcome by combining the active probing method with the FlowSense. In cases when a flow duration is greater than a specified value or the time since the last utilization calculation is greater than a specified value, active probing can be done. Therefore, by combining active probing and FlowSense, we get a network utilization measurement mechanism that requires minimal overhead and infrastructure and high accuracy. We have implemented the aforementioned combination in this project and titled it “ActiveFlowSense”.

Instructions:

1. The code files are provided as such:
i. ControllerFlowSense .py : Only FlowSense algorithm is implemented in this controller file.
ii. ControllerActive .py : ActiveFlowSense algorithm is implemented in this controller file.
iii. ControllerActiveZero .py : ActiveFlowSense algorithm is implemented in this controller file and 0 utilization is printed when there is no matching flow for a link.
iv. TopologyFirst .py : Topology involving 3 hosts and 2
v. TopologySecond .py : Topology involving 5 hosts and 3 switches.
2. The code was implemented and tested on Mininet 2.3.0 and POX controller installed on Ubuntu 18.04 on VirtualBox. So first, Mininet and POX needs to be installed in VirtualBox.
3. To run the controller file, place it in the misc folder in po x (other folders are also fine, but misc is given as an example)
ie, place the controller file in ~/pox/pox/misc
Open terminal, and use the following commands
cd ~/pox
./pox.py log.level
DEBUG misc. ControllerActive
The user is required to enter whether it is soft or hard timeout, timeout value and timer value (only for ControllerActive and ControllerActiveZero)
4. To run the topology file, place it the custom folder in mininet (again, custom folder is just taken as an example)
ie, place the topolog y file in ~/mininet/custom
Open another terminal, and use the following commands
cd ~/mininet/custom
sudo python3
TopologyFirst .py
5. After that, most commands required, like ping etc. can be run on the topology terminal.
6. All the output is displayed on the terminal and written to a file “output.txt” in the pox folder.

References:

[1] Yu C, Lumezanu C, Zhang Y et al (2013) FlowSense: monitoring network utilization with zero measurement cost. In: Proceedings of PANM’13, 2013, pp 31–41
[2] Jamal Hamad, Diyar & Yalda, Kherota & Okumus, Ibrahim Taner. (2015). Getting traffic statistics from network devices in an SDN environment using OpenFlow. 
[3] OpenFlow specification 
https://opennetworking.org/wp-content/uploads/2014/10/openflow-switch-v1.5.1.pdf
[4] McKeown, Nick & Anderson, Tom & Balakrishnan, Hari & Parulkar, Guru & Peterson, Larry & Rexford, Jennifer & Shenker, Scott & Turner, Jonathan. (2008). OpenFlow: Enabling innovation in campus networks. Computer Communication Review. 38. 69-74. 10.1145/1355734.1355746. 
