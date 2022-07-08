# ring-selector-relay-protocols

1.	Ring Communication (protocol used : TCP)
  a.	This module is implemented using CommNode 
2.	Node Selector (protocol used : UDP)
  a.	This module is implemented using 2 classes named : UDPNode  and UDPSelector
3.	Relay Nodes (protocol used : TCP)
  a.	This module is implemented using RelayNode 

There is a main function in the program that takes one parameter named mode ("RING" , "NODE_SEL", "RELAY")
You can choose any of the module to run but one at time.
