import xml.etree.cElementTree as ET

input_filename = "original.osm"
output_filename = "final.osm"

# Parse the XML from the OSM file
tree = ET.ElementTree(file=input_filename)

# Get the root of the XML (the <osm> node)
r = tree.getroot()


# Get all of the individual points from the file into a dictionary,
# with the keys being the ids of the nodes
unique_nodes_bycoords = {}
nodes_to_uniquenodes_by_ids = {}
unique_nodes_by_ids = {}

# Put all nodes in a dictionary and create a non duplicate nodes list to use later while looping the ways
for n in r.findall('node'):
        node_id = n.attrib['id']
	lat_lon = n.attrib['lat'] + "," + n.attrib['lon']
	
	    
	if not unique_nodes_bycoords.has_key(lat_lon): 
	    unique_nodes_bycoords[lat_lon] = node_id
	    unique_nodes_by_ids[node_id] = (n.attrib['lat'], n.attrib['lon'])
	    nodes_to_uniquenodes_by_ids[node_id] = node_id
	else:
	    unique_node_id = unique_nodes_bycoords[lat_lon]
	    nodes_to_uniquenodes_by_ids[node_id] = unique_node_id
            print node_id, "lat="+ n.attrib['lat'] + " lon=" + n.attrib['lon'] #to display which ones are the duplicate nods
	    
print 'Total Nodes:',len(nodes_to_uniquenodes_by_ids)
print 'Total Unique nodes:',len(unique_nodes_bycoords)
#print lat_lon, unique_nodes_bycoords.has_key(lat_lon)

#Looping the ways and its node members and replacing the id of the nodes with the unique node ids
for way in r.findall("way"):
	# Look at all of the children of the <way> node
	for c in way.getchildren():
	    if c.tag == "nd":
                node_id = c.attrib['ref']
                if nodes_to_uniquenodes_by_ids.has_key(node_id):

		    unique_node_id = nodes_to_uniquenodes_by_ids[node_id]
		    c.attrib['ref'] = unique_node_id
                
print 'Removing old nodes from the XML tree'
for i in r.findall("node"):
  r.remove(i)

print 'Adding no duplicated nodes to the XML tree'
for node_id,coords in unique_nodes_by_ids.items():
  xml_node = ET.Element('node',{'id':node_id, 'visible':'true','lat':coords[1] ,'lon':coords[0]})
  #Optionaly you can add the following line to visualize in JOSM the id of the node as the name, for debugging purposes.
  #xml_node.append(ET.Element('tag',{'k':'name','v':node_id}))
  r.append(xml_node)
  
  
print 'Saving'
tree.write(output_filename, encoding='utf-8', xml_declaration=True)
