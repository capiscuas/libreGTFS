import xml.etree.cElementTree as ET
import xml.dom.minidom as minidom

input_filename = "original_to_convert.osm"
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

level8_ways = {}
relations_level7_level8_level9 = {}

level7_ways = {}
relations_level7 = {}

level6_ways = {}
relations_level6 = {}

level5_ways = {}
relations_level5 = {}

splitted_way =  []
splitted_relation = []
splitted_ways_idx = {}
splitted_ways_idx_ocurrences = {}
kecamatan_ways = {}
relation_kecamatan = {}
kabupaten_ways = {}
relation_kabupaten = {}
relations_level7_level8 = {}
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


    
names_level7_level8 = {}
tags_level7_level8 = {}

relation_ids_level7_level8_level9 = {}
relation_ids_level7_level8 = {}
relation_ids_level7 = {}
relation_ids_level6 = {}


#Now we have all the total_occurrences of each splitted_way so we can detect the borders of the administrative boundaries
#In this example we have ways with admin_level 9(which we can use to generate boundaries 9,8,7,6 and 5) and original ways with admin_level8
#(which we can use to generate boundaries 8,7,6,5).


for idx,way in all_ways.items():
    admin_level = 0 #Reseting the admin_level
    splitted_relation = way['splitted_relation']
    if way['tag'].has_key('admin_level'):
                #Extracting the names of the boundaries from level9 to level5
                admin_level = int(way['tag']['admin_level'])
                if way['tag'].has_key('kel_name'):
                    level7_name = way['tag']['kel_name'].lower()
                if way['tag'].has_key('is_in:hamlet'):
                    level7_name = way['tag']['is_in:hamlet'].lower()
                    
                if way['tag'].has_key('kec_name'):
                    level6_name = way['tag']['kec_name'].lower()
                if way['tag'].has_key('is_in:subdistrict'):
                    level6_name = way['tag']['is_in:subdistrict'].lower()
                    
                if way['tag'].has_key('kab_name'):
                    level5_name = way['tag']['kab_name'].lower()
                if way['tag'].has_key('is_in:district'):
                    level5_name = way['tag']['is_in:district'].lower()
             
            
                if admin_level == 8:
                    if way['tag'].has_key('rw_number'):
                        level8 = way['tag']['rw_number']
                    elif way['tag'].has_key('name'):
                        level8 = way['tag']['name']
                        #print level8
                        if level8.startswith('RW '): #We get the number from 'RW XXX'
                            level8 = level8[3:]
                    else:
                        level8 = 'RW UNKNOWN'
                        
                if admin_level == 9:
                    level8 = ''
                    if way['tag'].has_key('rw_number'):
                        level8 = way['tag']['rw_number']
                        if level8.startswith('RW '):
                            level8 = level8[3:]
                    else:
                        level8 = 'RW UNKNOWN'
                        
                    if way['tag'].has_key('rt_number'):
                        level9 = way['tag']['rt_number']
                        if level9.startswith('RT '):
                            level9 = level9[3:]
                    elif way['tag'].has_key('name'):
                        level9 = way['tag']['name']
                    else:
                        level9 = 'RT UNKNOWN'

                    
                try:
                        level8_name = int(level8) #This would remove the zeros in case of string number 00X = X
                        formatted_level8_name = 'RW '+str(level8_name).zfill(2)
                except:
                        level8_name = level8
                        formatted_level8_name = level8
                level7_level8_name = level7_name + '_'+str(level8_name)

                names_level7_level8[level7_level8_name] = formatted_level8_name
                #print names_level7_level8[level7_level8_name]
                    

                
                if admin_level == 9:
                    try:
                            level9_name = int(level9) #This would remove the zeros in case of string number 00X = X
                            formatted_level9_name = 'RT '+str(level9_name).zfill(2)
                    except:
                            level9_name = level9
                            formatted_level9_name = level9
                    level7_level8_level9_name = level7_name + '_'+str(level8_name) + '_'+str(level9_name)
                    
                        
                #Used to detect duplicated level8 or from those generated
                if admin_level == 8:
                    if relations_level7_level8.has_key(level7_level8_name): #duplicated level8
                        try:
                            print 'DUPLICATED',way['tag']['OBJECTID'],level7_level8_name
                        except:
                            print 'DUPLICATED',level7_level8_name
                    
                
                tags = {}
                for k,v in way['tag'].items():
                    if k not in ['is_in:district','is_in:hamlet','id','is_in:province','is_in:subdistrict','name','admin_level','area','boundary','rw_number','rt_number']:
                        tags[k] = v
                        

                if admin_level == 8:
                    #Adding relations of Level8 directly
                    tags_level7_level8[level7_level8_name] = tags

                if admin_level == 9:
                     #Adding relations of Level9 directly
                     relations_level7_level8_level9[level7_level8_level9_name] = {'ways_idx':splitted_relation}
                     tags['name'] = formatted_level9_name
                     relations_level7_level8_level9[level7_level8_level9_name]['tag'] = tags
                     #deprecated since relation subarea are not used anymore
                     #addMember(father_level=8,father_name=level7_level8_name,children_name=level7_level8_level9_name)
                    
                     
                     
                for way_ref in splitted_relation:   
                    
                    #Detecting relations of Level8 generated from Level9
                    if level8_ways.has_key(way_ref):

                        neighbour_way_level7_level8_name = level8_ways[way_ref]
                        #print neighbour_way_level7_level8_name
                        if level7_level8_name != neighbour_way_level7_level8_name:

                                if relations_level7_level8.has_key(level7_level8_name): relations_level7_level8[level7_level8_name]['ways_idx'].append(way_ref)
                                else:  relations_level7_level8[level7_level8_name] = {'ways_idx':[way_ref],'name':formatted_level8_name}
                                if relations_level7_level8.has_key(neighbour_way_level7_level8_name): relations_level7_level8[neighbour_way_level7_level8_name]['ways_idx'].append(way_ref)
                                else: relations_level7_level8[neighbour_way_level7_level8_name] = {'ways_idx':[way_ref],'name':formatted_level8_name}

                    else:
                        
                        level8_ways[way_ref] = level7_level8_name
                        #Only those with ocurrences 1 are the outside way borders of the region of the file
                        if splitted_ways_idx_ocurrences[way_ref] == 1 and len(splitted_relation) != 1: #if it's a border way

                                if relations_level7_level8.has_key(level7_level8_name): relations_level7_level8[level7_level8_name]['ways_idx'].append(way_ref)
                                else: #Adding the name of the Level8 generated
                                    relations_level7_level8[level7_level8_name] = {'ways_idx':[way_ref],'name':formatted_level8_name}

                    #Detecting relations of Level7
                    if level7_ways.has_key(way_ref):
                        neighbour_way_level7_name = level7_ways[way_ref]
                        if level7_name != neighbour_way_level7_name:
                                if relations_level7.has_key(level7_name): relations_level7[level7_name].append(way_ref)
                                else: relations_level7[level7_name] = [way_ref]
                                if relations_level7.has_key(neighbour_way_level7_name): relations_level7[neighbour_way_level7_name].append(way_ref)
                                else: relations_level7[neighbour_way_level7_name] = [way_ref]
                    else: 
                        level7_ways[way_ref] = level7_name
                        #Only those with ocurrences 1 are the outside way borders of the region of the file
                        if splitted_ways_idx_ocurrences[way_ref] == 1 and len(splitted_relation) != 1: #if it's a border way
                            if relations_level7.has_key(level7_name): relations_level7[level7_name].append(way_ref)
                            else: relations_level7[level7_name] = [way_ref]
                            
                    #Detecting relations of Level6
                    if level6_ways.has_key(way_ref):
                        neighbour_way_level6_name = level6_ways[way_ref]
                        if level6_name != neighbour_way_level6_name:
                                if relations_level6.has_key(level6_name): relations_level6[level6_name].append(way_ref)
                                else:  relations_level6[level6_name] = [way_ref]
                                if relations_level6.has_key(neighbour_way_level6_name): relations_level6[neighbour_way_level6_name].append(way_ref)
                                else:  relations_level6[neighbour_way_level6_name] = [way_ref]
                    else: 
                        level6_ways[way_ref] = level6_name
                        #Only those with ocurrences 1 are the outside way borders of the region of Jakarta
                        if splitted_ways_idx_ocurrences[way_ref] == 1 and len(splitted_relation) != 1: #if it's a border way
                            if relations_level6.has_key(level6_name): relations_level6[level6_name].append(way_ref)
                            else:  relations_level6[level6_name] = [way_ref]
                    
                    #Detecting relations of Level5
                    if level5_ways.has_key(way_ref):
                        neighbour_way_level5_name = level5_ways[way_ref]
                        if level5_name != neighbour_way_level5_name:
                                if relations_level5.has_key(level5_name): relations_level5[level5_name].append(way_ref)
                                else: relations_level5[level5_name] = [way_ref]
                                if relations_level5.has_key(neighbour_way_level5_name): relations_level5[neighbour_way_level5_name].append(way_ref)
                                else: relations_level5[neighbour_way_level5_name] = [way_ref]
                    else: 
                        level5_ways[way_ref] = level5_name
                        #Only those with ocurrences 1 are the outside way borders of the region of Jakarta
                        if splitted_ways_idx_ocurrences[way_ref] == 1 and len(splitted_relation) != 1: #if it's a border way
                            if relations_level5.has_key(level5_name): relations_level5[level5_name].append(way_ref)
                            else: relations_level5[level5_name] = [way_ref]
                    
                    

                            
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
  xml_way.append(ET.Element('tag',{'k':'boundary','v':'administrative'}))
  
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


print '#RT Level9',len(relations_level7_level8_level9)
counter = 1
for name_level7_level8_level9, relation in relations_level7_level8_level9.items():
  xml = ET.Element('relation',{'id':'-'+str(counter), 'visible':'true'})
  
  
  #In order to mantain the original HOT ID tags in those ways for FLOOD control
  tags = {}
  if relation.has_key('tag'):
      tags = relation['tag']
  
  if tags:
    for k,v in tags.items():
            xml.append(ET.Element('tag',{'k':k,'v':v}))
  
  xml.append(ET.Element('tag',{'k':'boundary','v':'administrative'}))
  xml.append(ET.Element('tag',{'k':'admin_level','v':'9'}))
  xml.append(ET.Element('tag',{'k':'type','v':'boundary'}))
  #xml.append(ET.Element('tag',{'k':'natural','v':'water'}))
  
  for indexes in relation['ways_idx']:
      way_ref = indexes[1:indexes.find(',')] +  indexes[indexes.find(',')+2:] #we remove the , comma
      xml.append(ET.Element('member',{'type':'way','role':'outer','ref':'-'+way_ref}))
  r.append(xml)
  counter += 1
  
  
print '#RW Level8',len(relations_level7_level8)
counter = 100000
for name_level7_level8, relation in relations_level7_level8.items():
  xml = ET.Element('relation',{'id':'-'+str(counter), 'visible':'true'})
  
  tags = {}
  if relation.has_key('tag'):
      tags = relation['tag']
  if tags_level7_level8.has_key(name_level7_level8):
      tags = tags_level7_level8[name_level7_level8]
      
  if tags:
    for k,v in tags.items():
            xml.append(ET.Element('tag',{'k':k,'v':v}))
  
  xml.append(ET.Element('tag',{'k':'boundary','v':'administrative'}))
  xml.append(ET.Element('tag',{'k':'admin_level','v':'8'}))
  xml.append(ET.Element('tag',{'k':'type','v':'boundary'}))
  #xml.append(ET.Element('tag',{'k':'natural','v':'water'}))
  
  if names_level7_level8.has_key(name_level7_level8):
      formatted_level8_name = names_level7_level8[name_level7_level8]
      xml.append(ET.Element('tag',{'k':'name','v':formatted_level8_name}))
      

  for indexes in relation['ways_idx']:
      way_ref = indexes[1:indexes.find(',')] +  indexes[indexes.find(',')+2:] #we remove the , comma
      xml.append(ET.Element('member',{'type':'way','role':'outer','ref':'-'+way_ref}))
  r.append(xml)
  counter += 1



print '#Desa Level7',len(relations_level7)

counter = 200000
for name_level7, ways_idx in relations_level7.items():
  xml = ET.Element('relation',{'id':'-'+str(counter), 'visible':'true'})
  xml.append(ET.Element('tag',{'k':'name','v':name_level7.title()}))
  xml.append(ET.Element('tag',{'k':'boundary','v':'administrative'}))
  xml.append(ET.Element('tag',{'k':'admin_level','v':'7'}))
  xml.append(ET.Element('tag',{'k':'type','v':'boundary'}))
  #xml.append(ET.Element('tag',{'k':'natural','v':'water'}))
  
  for indexes in ways_idx:
      way_ref = indexes[1:indexes.find(',')] +  indexes[indexes.find(',')+2:] #we remove the , comma
      xml.append(ET.Element('member',{'type':'way','role':'outer','ref':'-'+way_ref}))
  r.append(xml)
  counter += 1
  
  

print '#Kecamatan Level6',len(relations_level6)

counter = 300000
for name_level6, ways_idx in relations_level6.items():
  xml = ET.Element('relation',{'id':'-'+str(counter), 'visible':'true'})
  xml.append(ET.Element('tag',{'k':'name','v':name_level6.title()}))
  xml.append(ET.Element('tag',{'k':'boundary','v':'administrative'}))
  xml.append(ET.Element('tag',{'k':'admin_level','v':'6'}))
  xml.append(ET.Element('tag',{'k':'type','v':'boundary'}))
  #xml.append(ET.Element('tag',{'k':'natural','v':'water'}))

  for indexes in ways_idx:
      way_ref = indexes[1:indexes.find(',')] +  indexes[indexes.find(',')+2:] #we remove the , comma
      xml.append(ET.Element('member',{'type':'way','role':'outer','ref':'-'+way_ref}))
  r.append(xml)
  counter += 1

print '#Kabupaten Level5',len(relations_level5)

counter = 400000
for name_level5, ways_idx in relations_level5.items():
  xml = ET.Element('relation',{'id':'-'+str(counter), 'visible':'true'})
  xml.append(ET.Element('tag',{'k':'name','v':name_level5.title()}))
  xml.append(ET.Element('tag',{'k':'boundary','v':'administrative'}))
  xml.append(ET.Element('tag',{'k':'admin_level','v':'5'}))
  xml.append(ET.Element('tag',{'k':'type','v':'boundary'}))
  #xml.append(ET.Element('tag',{'k':'natural','v':'water'}))
  #Obsolete, boundary relation subareas are deprecated according the OSM Wiki
  #if members_level5.has_key(name_level5):
      #print 'Members of ',name_level5
      #for member in members_level5[name_level5]:
          #print relation_ids_level6[member]
      

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
