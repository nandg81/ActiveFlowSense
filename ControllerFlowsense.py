'''
Team 9 Roll no : 2021H1030103P, 2021H1030105P, 2021H1030128P
Controller for FlowSense
'''

from pox.core import core
from pox.lib.util import dpid_to_str
import pox.openflow.libopenflow_01 as of
from pox.lib.recoco import Timer
import time

log = core.getLogger()
start_time=0
current_time=0

#The active_list data structure is for storing the list of active flows at every switch
active_list=[]
#The utilization_table data structure is for storing the list of checkpoints at every switch for every port
utilization_table=[]
'''
The mac_to_port data structure at the controller stores the mapping between mac address and port for every switch. It is actually a dictionary of dictionaries.
The key for the outer dictionary is the switch dpid. The value for the outer dictionary is another dictionary whose keys are mac addresses of hosts in the network.
The value for the inner dictionary is port through which we can reach the host having the mac address specified in the key from the switch mentioned in the key of outer dictionary.
eg: mac_to_port={5:{{40:10:40:10:40:10,2},{40:10:40:10:40:20,1}},4:{{40:10:40:10:40:10,6},{40:10:40:10:40:20,3}}}
In this example, first key of outer dictionary is 5. This is dpid of a switch. So, this means that to reach host with mac address 40:10:40:10:40:10 from switch 5, you have to forward to port 2.
To reach host with mac address 40:10:40:10:40:20 from switch 5, you have to forward to port 1.
To reach host with mac address 40:10:40:10:40:10 from switch 4, you have to forward to port 6
To reach host with mac address 40:10:40:10:40:20 from switch 4, you have to forward to port 3
'''
mac_to_port = {}
timeout_value = 0
hard_or_soft = 2

#fuction to create a timestamp and updating the current time
def get_the_time ():  
	global current_time
	flock = time.localtime()
	current_time=time.mktime(flock)-start_time
	then = "[%s-%s-%s" %(str(flock.tm_year),str(flock.tm_mon),str(flock.tm_mday))
  
	if int(flock.tm_hour)<10:
		hrs = "0%s" % (str(flock.tm_hour))
	else:
		hrs = str(flock.tm_hour)
	if int(flock.tm_min)<10:
		mins = "0%s" % (str(flock.tm_min))
	else:
		mins = str(flock.tm_min)
	if int(flock.tm_sec)<10:
		secs = "0%s" % (str(flock.tm_sec))
	else:
		secs = str(flock.tm_sec)
	then +="]%s.%s.%s" % (hrs,mins,secs)
	return then

#fuction to add a new flow to the active_list data structure	
def add_flow (event):
	global active_list,current_time
	flow={}
	flow['dpid']=event.connection.dpid
	flow['in_port']=event.port
	flow['dst']=event.parsed.dst
	flow['active']=1
	flow['timestamp']=get_the_time()
	flow['start_time']=current_time
	flow['end_time']=0
	if flow not in active_list:
		active_list.append(flow)
		file1 = open("output.txt","a")
		str1='Flow added'
		print(str1)
		file1.write(str1)
		file1.write("\n")
		str1=str(flow)
		print(str1)
		file1.write(str1)
		file1.write("\n")
		file1.close()
		return True
	else:
		return False

#fuction to add a new checkpoint to the utilization_table data structure	
def add_checkpoint (event,matching_flow):
	global current_time,active_list,utilization_table
	checkpoint={}
	checkpoint['dpid']=event.connection.dpid
	checkpoint['dst']=event.ofp.match.dl_dst
	checkpoint['time']=current_time
	checkpoint['flow_start_time']=matching_flow['start_time']
	duration=matching_flow['end_time']-matching_flow['start_time']
	checkpoint['utilization']=((event.ofp.byte_count*8.0)/1000)/duration #storing utilization in kbps
	remaining=0
	#check whether it is a partial utilization or not. If some flows are remaining, it is partial
	for flow in active_list:
		if checkpoint['dpid']==flow['dpid'] and checkpoint['dst']==flow['dst'] and flow['active']==1 and flow['start_time']<checkpoint['time']:
			remaining=remaining+1
	checkpoint['active']=remaining
	utilization_table.append(checkpoint)
	return checkpoint

'''
handle flowRemoved : 
Fired when a flow expires at a switch
'''
def _handle_FlowRemoved (event):
	global current_time,active_list,utilization_table
	timestamp=get_the_time()
	matching_flow={}
	#find the matching flow in the active_list	
	for flow in active_list:
		if flow['dpid']==event.connection.dpid and flow['dst']==event.ofp.match.dl_dst and flow['in_port']==event.ofp.match.in_port and flow['active']==1:
			flow['active']=0
			flow['end_time']=flow['start_time']+event.ofp.duration_sec
			if event.idleTimeout:
				flow['end_time']=flow['end_time']-event.ofp.idle_timeout
				current_time=current_time-event.ofp.idle_timeout
			matching_flow=flow
			break
	if matching_flow['end_time']-matching_flow['start_time']>0:
		checkpoint=add_checkpoint(event,matching_flow)
		file1 = open("output.txt","a")
		str1="Time: "+str(timestamp)+ " Checkpoint: "+str(current_time)+" Utilization on link from switch "+str(event.connection.dpid)+" through port "+ str(mac_to_port[event.connection.dpid][event.ofp.match.dl_dst]) + " = "+ str(checkpoint['utilization']) + " kbps Flows remaining: "+ str(checkpoint['active'])
		print(str1)
		file1.write(str1)
		file1.write("\n")
		#check for any previous checkpoints with partial utilization values
		for cp in utilization_table:
			if cp['dpid']==event.connection.dpid and cp['dst']==event.ofp.match.dl_dst and cp['active']>0 and cp['time']>matching_flow['start_time'] and cp['time']<checkpoint['time']:
				cp['utilization']=cp['utilization']+checkpoint['utilization']
				cp['active']=cp['active']-1
				str1="Checkpoint: "+str(cp['time'])+" Utilization on link from switch "+str(event.connection.dpid)+" through port "+ str(mac_to_port[event.connection.dpid][event.ofp.match.dl_dst]) + " = "+ str(cp['utilization']) + " kbps Flows remaining: "+ str(cp['active'])
				print(str1)
				file1.write(str1)
				file1.write("\n")
		file1.close()
	

'''
handle ConnectionUp :
fired in response to the establishment of a new control channel with a switch.
'''
def _handle_ConnectionUp(event):
	global mac_to_port, start_time
	if start_time==0:
		start_time=time.mktime(time.localtime())
	#initialise the outer dictionary with key values as switch dpids as the connection with switch gets established and with empty values
	mac_to_port[event.connection.dpid]={}
	print("Switch ",event.connection.dpid)
	print(dpid_to_str(event.connection.dpid))
	for swprt in event.connection.features.ports:
		if swprt.port_no != 65534:
			print(swprt.name)

'''
handle packetIn : 
Fired when the controller receives an OpenFlow packet-in messagefrom a switch, 
which indicates that a packet arriving at a switch port has either failed to match all entries in the table, 
or the matching entry included an action specifying to send the packet to the controller.
'''
def _handle_PacketIn(event):
	global mac_to_port,timeout_value
	dpid = event.connection.dpid
	inport = event.port
	packet = event.parsed
	if not packet.parsed:
		log.warning("%i %i ignoring unparsed packet", dpid, inport)
	
	#We need to fill up the mac_to_port data structure as new packets come in
	#If a packet from a particular source comes to switch through a particular port, we know that in the future, if we want to reach that particular source in the future, we can forward to this port
	#Store this information in mac_to_port if its not already there
	if packet.src not in mac_to_port[dpid]:
		mac_to_port[dpid][packet.src] = event.ofp.in_port
	#If the packet's destination mac address is there in the inner dictionary corresponding to this switch, add flow rule to forward the packet to the port in the dictionary
	if packet.dst in mac_to_port[dpid]:
		if add_flow(event):
			#flow_mod is for adding the flow rule
			msg = of.ofp_flow_mod()
			msg.match.in_port = inport
			msg.match.dl_dst = packet.dst
			msg.actions.append(of.ofp_action_output(port=mac_to_port[dpid][packet.dst]))
			if(hard_or_soft==1):
				msg.hard_timeout = timeout_value
			else:
				msg.idle_timeout = timeout_value
			msg.flags=of.OFPFF_SEND_FLOW_REM
			event.connection.send(msg)
			#The following lines are needed because the packet that causes the flow rule to be installed doesnt actually follow the flow rules
			#Only the subsequent packets follow the flow rules
			#So in order for the first packet to not be dropped, the controller needs to explicitly the packet_out for this packet to the same output port that the flow rule was installed
			msg = of.ofp_packet_out(data=event.ofp)
			msg.actions.append(of.ofp_action_output(port=mac_to_port[dpid][packet.dst]))
			event.connection.send(msg)
	#If the packet's destination mac address is not there in the inner dictionary corresponding to this switch, we just flood the packet	
	else:
		msg = of.ofp_packet_out(data=event.ofp)
		msg.actions.append(of.ofp_action_output(port=of.OFPP_ALL))
		event.connection.send(msg)


'''
launch :
Its the main method
'''			
def launch():
	global timeout_value
	hard_or_soft=int(input("Enter 1 for hard timeout, 2 for soft timeout "))
	timeout_value=int(input("Enter the timeout value: "))
	core.openflow.addListenerByName("ConnectionUp",_handle_ConnectionUp)
	core.openflow.addListenerByName("PacketIn",_handle_PacketIn)
	core.openflow.addListenerByName("FlowRemoved",_handle_FlowRemoved)
