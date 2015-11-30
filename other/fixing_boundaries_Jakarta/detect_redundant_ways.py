import xml.etree.cElementTree as ET


input_filename = "unique_nodes.osm"
output_filename = "ready_to_fix.osm"

# Parse the XML from the OSM file
tree = ET.ElementTree(file=input_filename)

#I tried to use the library OSMAPI to parse the OSM files into python structures
# but it hanged the laptop cause it took too much time
#from osmapi import OsmApi
#MyApi = OsmApi(username = u"xxxxxxx", password = u"*******")
#result = MyApi.ParseOsm(file(input_filename).read())

# Get the root of the XML (the <osm> node)
r = tree.getroot()

unique_rw = []
ways_level9 = []
ways_level8 = [] 
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
    

#Looping the all_ways dictionary to find out what level 8 ways are redundant because they could be generate from the smaller level 9.
#In order to do this, we extract the tag names for the admin_level=8, and admin_level=7 
# and we compare them when crawling the ways who have admin_level8...
#if that idx(level8+level7) already exists, it means that this way is redundant and can be generated with the ways of level9.

all_unique_rw = []
for idx,way in all_ways.items():
  #print way['tag']
  if way['tag'].has_key('admin_level'):
	  admin_level = int(way['tag']['admin_level'])
	  if admin_level == 9:
	      ways_level9.append(way)
	      if way['tag'].has_key('rw_number'):
                  try:
                      rw_number = int(way['tag']['rw_number'])
                  except:
                      continue
                  else:
                    if way['tag'].has_key('kel_name'):
                        desa = (way['tag']['kel_name']).lower().replace(" ", "")
                        #print "Level 9 RW=",rw_number, "Desa:",desa
                        all_unique_rw.append(str(rw_number)+'_'+desa)
	  elif admin_level == 8:
	      ways_level8.append(way)

ways_to_delete = []
for way in ways_level8:
    if way['tag'].has_key('name') or way['tag'].has_key('RW'):
            if way['tag'].has_key('name'): rwtag = way['tag']['name']
            else: rwtag = way['tag']['RW']
            if rwtag.startswith('RW'):
                try:
                        rw_number = int(rwtag[2:])
                except:
                        continue
                else:
                        desaname = ''
                        if way['tag'].has_key('is_in:hamlet'): desaname = way['tag']['is_in:hamlet']
                        if way['tag'].has_key('KEL_NAME') : desaname = way['tag']['KEL_NAME']
                        if desaname:
                            #We remove the spaces because we realized sometimes the tags from level9 and level8 didn't match bcs spaces.
                            desa = (desaname).lower().replace(" ", "")
                            rw8 = str(rw_number)+'_'+desa
                            if rw8 in all_unique_rw:
                                #print 'Redundant',rw8
                                ways_to_delete.append(way['id'])
                            #print "Level 8 RW=",rw_number, "Desa:",desa

print 'Colouring redundant ways, TOTAL: ',len(ways_to_delete)               
for way in r.findall("way"):
    way_id = way.attrib['id']
    if way_id in ways_to_delete:
        #We add this tag so we can have BLUE color in JOSM for easy debugging(comparing, deleting, etc)
        way.append(ET.Element('tag',{'k':'natural','v':'water'}))


print 'Saving'
tree.write(output_filename, encoding='utf-8', xml_declaration=True) 