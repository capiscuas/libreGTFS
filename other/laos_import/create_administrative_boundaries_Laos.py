import xml.etree.cElementTree as ET
import xml.dom.minidom as minidom

input_filename = "distritos2.osm"
#input_filename = "test.osm"

output_filename = "final.osm"

# Parse the XML from the OSM file
tree = ET.ElementTree(file=input_filename)

# Get the root of the XML (the <osm> node)
r = tree.getroot()


# Get all of the individual nodes from the file into a dictionary,
# with the keys being the ids of the nodes
nodes = {}

# Put all nodes in a dictionary
for n in r.findall('node'):
	nodes[n.attrib['id']] = (float(n.attrib['lat']), float(n.attrib['lon']))

all_ways = {}

#Converting the Ways Tree XML elements into a python dictionary
for way in r.findall("way"):
    way_id = way.attrib['id']
    all_ways[way_id] = {'id':way_id,'tag':{},'nd':[]}
    for c in way.getchildren():
            if c.tag == "nd":
                 node_id = c.attrib['ref']
                 all_ways[way_id]['nd'].append(node_id)
            else:
                all_ways[way_id]['tag'][c.attrib['k']] = c.attrib['v']
                 
                
print 'all_ways: ',len(all_ways)

print 'Calculating node ocurrences'
#(how many ways contain each node), this will be useful when splitting the ways only at the intersections
node_ocurrences = {}

for idx,way in all_ways.items():
    for node_id in way['nd']: #Each of the way's node
                if  node_ocurrences.has_key(node_id): node_ocurrences[node_id] += 1
                else: node_ocurrences[node_id] =  1


level6_ways = {}
relations_level6 = {}

level4_ways = {}
relations_level4 = {}

splitted_way =  []
splitted_relation = []
splitted_ways_idx = {}
splitted_ways_idx_ocurrences = {}

now = False  
	  
print 'splitting all the nodes'
for idx,way in all_ways.items():
	# Look at all of the children of the <way> node
        previous_node_ocurrences = 0
        splitted_way =  []
        splitted_relation = []
        closed_way = way_is_completed = False
	for node_id in way['nd']:
                #if the node is intersected by 3 or more ways = relation intersects, let's split the way
                #For those external ways(the outter ways of the region) may be necessary add auxiliar way with JOSM to increase the
                # number of node interseccion to 3
                if node_ocurrences[node_id] >= 3 and len(splitted_way) > 0: 
                        way_is_completed = True
                        closed_way = False

                else: 
                        if node_id not in splitted_way:
                                splitted_way.append(node_id)
                                closed_way = False
                        else:
                            way_is_completed = True#End of the way, same initial point
                            closed_way = True
    
                if way_is_completed:
                    way_is_completed = False
                    splitted_way.append(node_id)
                   
                    #In order to avoid duplication, we index our splitted ways as [A to Z]
                    # that way if we split the other way that goes from Z to A, we will find it
                    # already indexed as [A to Z] and increase the number of ocurrences
                    idx_nodes_head = str(splitted_way[0])+","+str(splitted_way[-1])
                    idx_nodes_tail = str(splitted_way[-1])+","+str(splitted_way[0])
                    if splitted_ways_idx.has_key(idx_nodes_head):
                        splitted_relation.append(idx_nodes_head)
                        splitted_ways_idx_ocurrences[idx_nodes_head] += 1
                    elif splitted_ways_idx.has_key(idx_nodes_tail):
                        splitted_relation.append(idx_nodes_tail)
                        splitted_ways_idx_ocurrences[idx_nodes_tail] += 1
                    else:
                            splitted_ways_idx[idx_nodes_head] = splitted_way
                            splitted_ways_idx_ocurrences[idx_nodes_head] = 1
                            splitted_relation.append(idx_nodes_head)

                    if closed_way:   splitted_way = []
                    else: splitted_way = [node_id]
                    

                previous_node_ocurrences = node_ocurrences[node_id]

        all_ways[idx]['splitted_relation'] = splitted_relation


relation_ids_level6 = {}


#Now we have all the total_occurrences of each splitted_way so we can detect the borders of the administrative boundaries
#In this example we have ways with admin_level 9(which we can use to generate boundaries 9,8,7,6 and 5) and original ways with admin_level8
#(which we can use to generate boundaries 8,7,6,5).


for idx,way in all_ways.items():
    admin_level = 6 #Reseting the admin_level
    splitted_relation = way['splitted_relation']
    if way['tag'].has_key('PNAME'):
                #Extracting the names of the boundaries from level9 to level5
                #admin_level = int(way['tag']['admin_level'])
                if way['tag'].has_key('PNAME'):
                    level4_name = way['tag']['PNAME'].lower()
                
                tags = {}
                for k,v in way['tag'].items():
                    if k not in ['is_in:district','is_in:hamlet','id','is_in:province','is_in:subdistrict','name','admin_level','area','boundary','rw_number','rt_number']:
                        tags[k] = v
                        
                if admin_level == 6:
                    if way['tag'].has_key('DNAME'):
                        level6_name = way['tag']['DNAME']
                        
                    else:
                        print 'Missing DNAME way=', idx
                        
                    relations_level6[level6_name] = {'ways_idx':splitted_relation}
                    tags['name'] = level6_name
                    relations_level6[level6_name]['tag'] = tags

 
                for way_ref in splitted_relation:   
                    #Detecting relations of Level4
                    if level4_ways.has_key(way_ref):
                        neighbour_way_level4_name = level4_ways[way_ref]
                        if level4_name != neighbour_way_level4_name:
                                if relations_level4.has_key(level4_name): relations_level4[level4_name].append(way_ref)
                                else:  relations_level4[level4_name] = [way_ref]
                                if relations_level4.has_key(neighbour_way_level4_name): relations_level4[neighbour_way_level4_name].append(way_ref)
                                else:  relations_level4[neighbour_way_level4_name] = [way_ref]
                    else: 
                        level4_ways[way_ref] = level4_name
                        #Only those with ocurrences 1 are the outside way borders of the region of Jakarta
                        if splitted_ways_idx_ocurrences[way_ref] == 1 and len(splitted_relation) != 1: #if it's a border way
                            if relations_level4.has_key(level4_name): relations_level4[level4_name].append(way_ref)
                            else:  relations_level4[level4_name] = [way_ref]
                    
                    
                    

                            
print 'Total splitted ways:',len(splitted_ways_idx)
##splitting all the nodes into ways when encountering an interesection of >2 


####EXPORTING TO THE XML######


print 'Erase all nodes from the XML tree'
for i in r.findall("node"):
  r.remove(i)

print 'Erase all the ways from the XML Tree'
for way in r.findall("way"):
  r.remove(way)
  
print 'Adding no duplicated nodes to the XML tree'
for node_id,coords in nodes.items():
  xml_node = ET.Element('node',{'id':node_id, 'visible':'true','lat':str(coords[0]) ,'lon':str(coords[1])})
  
  ##Optionaly you can add the following line to visualize in JOSM the id of the node as the name and its ocurrences(for debuging)
  #try:
    #ocurrences = node_ocurrences[node_id]
  #except:
      #ocurrences = 0
  #tag_name = node_id + ' ('+ str(ocurrences) +')'
  #xml_node.append(ET.Element('tag',{'k':'name','v':tag_name}))
  
  r.append(xml_node)
  



print 'Adding new splitted ways in OSM format to the XML tree'
#i = 0
for indexes, nodes in splitted_ways_idx.items():
  #i += 1
  way_ref = indexes[1:indexes.find(',')] +  indexes[indexes.find(',')+2:] #we remove the , comma
  #print int(way_ref)
  xml_way = ET.Element('way',{'id':'-'+way_ref, 'visible':'true'})
  
  if splitted_ways_idx_ocurrences.has_key(indexes):
      total_occurrences = splitted_ways_idx_ocurrences[indexes]

  #This is useful for debug purposes so we can read what node ids is the splitted way uniting and how many ocurrences
  #name_way = str(total_occurrences) +" "+ indexes
  #if total_occurrences <= 1:
        #xml_way.append(ET.Element('tag',{'k':'highway','v':'living_street'}))
  #else: 
        #xml_way.append(ET.Element('tag',{'k':'highway','v':'residential'}))
  #xml_way.append(ET.Element('tag',{'k':'name','v':name_way}))
  for node in nodes:
      xml_way.append(ET.Element('nd',{'ref':node}))
  r.append(xml_way)


print '#Level6',len(relations_level6)
counter = 1
for name_level6, relation in relations_level6.items():
  xml = ET.Element('relation',{'id':'-'+str(counter), 'visible':'true'})
  
  
  #In order to mantain the original HOT ID tags in those ways for FLOOD control
  tags = {}
  if relation.has_key('tag'):
      tags = relation['tag']
  
  if tags:
    for k,v in tags.items():
            xml.append(ET.Element('tag',{'k':k,'v':v}))
  
  xml.append(ET.Element('tag',{'k':'boundary','v':'administrative'}))
  xml.append(ET.Element('tag',{'k':'admin_level','v':'6'}))
  xml.append(ET.Element('tag',{'k':'type','v':'boundary'}))
  xml.append(ET.Element('tag',{'k':'natural','v':'water'}))
  
  for indexes in relation['ways_idx']:
      way_ref = indexes[1:indexes.find(',')] +  indexes[indexes.find(',')+2:] #we remove the , comma
      xml.append(ET.Element('member',{'type':'way','role':'outer','ref':'-'+way_ref}))
  r.append(xml)
  counter += 1
  
  
print '#Level4',len(relations_level4)

counter = 400000
for name_level4, ways_idx in relations_level4.items():
  xml = ET.Element('relation',{'id':'-'+str(counter), 'visible':'true'})
  xml.append(ET.Element('tag',{'k':'name','v':name_level4.title()}))
  xml.append(ET.Element('tag',{'k':'boundary','v':'administrative'}))
  xml.append(ET.Element('tag',{'k':'admin_level','v':'4'}))
  xml.append(ET.Element('tag',{'k':'natural','v':'water'}))
  xml.append(ET.Element('tag',{'k':'type','v':'boundary'}))
  xml.append(ET.Element('tag',{'k':'natural','v':'water'}))

      

  for indexes in ways_idx:
      way_ref = indexes[1:indexes.find(',')] +  indexes[indexes.find(',')+2:] #we remove the , comma
      xml.append(ET.Element('member',{'type':'way','role':'outer','ref':'-'+way_ref}))
  r.append(xml)
  counter += 1

print 'Saving'
tree.write(output_filename, encoding='utf-8', xml_declaration=True) 

#Printing the XML for debug purpose with pretty format
#xmlstr = minidom.parseString(ET.tostring(r)).toprettyxml(indent="   ")
#with open(output_filename, "w") as f:
   #f.write(xmlstr)
