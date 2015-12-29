#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xml.etree.cElementTree as ET
import sys

if not len(sys.argv) > 2:
    print 'Usage: python '+ sys.argv[0] +' input.osm output.osm'
    sys.exit(0)

input_filename = sys.argv[1]
output_filename = sys.argv[2]

ascii_to_lao = {}
ascii_to_lao[' '] = u' '
ascii_to_lao['|'] = u'\u0EDC' # ໜ     
ascii_to_lao[';'] = u'\u0EA7' # ວ  ;q ວົ  ;y ວີ  
ascii_to_lao['-'] = u'\u0E8A' # ຊ 
ascii_to_lao[','] = u'\u0EA1' #5 ມູ    , ມ   ,t ມັ ,h ມ້
ascii_to_lao['\''] = u'\u0E87' # ງ
ascii_to_lao['^'] = u'\u0EBC' #   ຫຼ  el sombrero es lo de abajo
ascii_to_lao['+'] = u'\u0ECD\u0EC8' #  ບໍ່ (el circulito)
ascii_to_lao['.'] = u'\u0EC3' # ໃ
ascii_to_lao['\\'] = u'\u0EDD' # ໝ

ascii_to_lao['0'] = u'\u0E82' # ຂ
#ascii_to_lao['1'] = u'\u' # ??????
ascii_to_lao['2'] = u'\u0E9F' #n ຟື      2 ຟ
ascii_to_lao['3'] = u'\u0EC2' # ໂ 
ascii_to_lao['4'] = u'\u0E96' # ຖ
ascii_to_lao['5'] = u'\u0EB8' #,5 ມູ  m5 ທຸ  v5 ອຸ 
ascii_to_lao['6'] = u'\u0EB9' #r6 ພູ   [6 ບຸ  $ູ
ascii_to_lao['7'] = u'\u0E84' #u ຄີ   7 ຄ 7q ຄົ
ascii_to_lao['8'] = u'\u0E95' # ຕ   8Q ຕົ້
ascii_to_lao['9'] = u'\u0E88' # ຈ  9e ຈຳ  9b ຈິ

ascii_to_lao['a'] = u'\u0EB1' #ra ພັ la ສັ  fa ດັ
ascii_to_lao['b'] = u'\u0EB4' #9b ຈິ , el semicirculo
ascii_to_lao['c'] = u'\u0EC1' # ແ
ascii_to_lao['d'] = u'\u0E81' # ກ
ascii_to_lao['e'] = u'\u0ECD' #9e ຈຳ   ຄໍາ  el circulito
ascii_to_lao['f'] = u'\u0E94' # ດ   fa ດັ
ascii_to_lao['g'] = u'\u0EC0' # ເ
ascii_to_lao['h'] = u'\u0EC9' #,h ມ້
#ascii_to_lao['i'] = u'\u' # ????
ascii_to_lao['j'] = u'\u0EC8' #mj ທ່  s^qj  ລົ່ (jota es el palo arriba)
ascii_to_lao['k'] = u'\u0EB2' # າ
ascii_to_lao['l'] = u'\u0EAA' # ສ la ສັ 
ascii_to_lao['m'] = u'\u0E97' #5 ທຸ  m ທ mj ທ່
ascii_to_lao['n'] = u'\u0EB7' #n2 ຟື   ,n ມື
ascii_to_lao['o'] = u'\u0E99' # ນ
ascii_to_lao['p'] = u'\u0E8D' # ຍ 
ascii_to_lao['q'] = u'\u0EBB' #7q ຄົ    ;q ວົ  s^q  ລົ່
ascii_to_lao['r'] = u'\u0E9E' # ພ    r6 ພູ   [6 ບຸ ra ພັ  ry ພີ
ascii_to_lao['s'] = u'\u0EAB' # ຫ  
ascii_to_lao['t'] = u'\u0EB0' # ະ 
ascii_to_lao['u'] = u'\u0EB5' #7u ຄີ     ]u ລີ
ascii_to_lao['v'] = u'\u0EAD' # ອ v5 ອຸ 
ascii_to_lao['w'] = u'\u0EC4' # ໄ
ascii_to_lao['x'] = u'\u0E9B' # ປ
ascii_to_lao['y'] = u'\u0EB5' #ry ພີ  ;y ວີ  puede q sea el circulo solo
ascii_to_lao['z'] = u'\u0E9C' # ຜ zY ຜິ້ 

ascii_to_lao['['] = u'\u0E9A' #ບ
ascii_to_lao[']'] = u'\u0EA5' #ລ
ascii_to_lao['Q'] = u'\u0EBB\u0EC9' #ຕົ້ (convertir a 2 unicodes)
ascii_to_lao['Y'] = u'\u0EB4\u0EC9' #ຜິ້
ascii_to_lao['P'] = u'\u0EBD' #ຽ
ascii_to_lao['I'] = u'\u0EAE' #ຮ
ascii_to_lao['E'] = u'\u0EB3\u0EC9' #oE ນ້ຳ
ascii_to_lao['U'] = u'\u0EB4\u0EC9'  #ງເຜິ້ງ
ascii_to_lao['='] = u'\u0ECD' 
 
#numbers
 
ascii_to_lao['W'] = u'\u0ED0'  #0
ascii_to_lao['!'] = u'\u0ED1'  #1 
ascii_to_lao['@'] = u'\u0ED2'  #2 
ascii_to_lao['#'] = u'\u0ED3'  #3 
ascii_to_lao['$'] = u'\u0ED4'  #4
ascii_to_lao['&'] = u'\u0ED5'  #5 
ascii_to_lao['*'] = u'\u0ED6'  #6 

ascii_to_lao['('] = u'\u0ED7'  #7
ascii_to_lao[')'] = u'\u0ED8'  #8
#ascii_to_lao[''] = u'\u0ED9'  #9
# Parse the XML from the OSM file
tree = ET.ElementTree(file=input_filename)

# Get the root of the XML (the <osm> node)
r = tree.getroot()

#Converting the Ways Tree XML elements into a python dictionary
count = 0
for way in r.findall("node"): #or it could be way
    
    for c in way.getchildren():
                way_id = way.attrib['id']
                name_laos = ''
                missing = False
                
                if c.attrib.has_key('k') and c.attrib['k'] == 'DNAMELAO':
                    name_laos = c.attrib['v'].replace('&apos;','\'')
                elif c.attrib.has_key('k') and c.attrib['k'] == 'LAO_NAME':
                    name_laos = c.attrib['v'].replace('&apos;','\'')
                elif c.attrib.has_key('k') and c.attrib['k'] == 'VNAMELAO1':
                    name_laos = c.attrib['v'].replace('&apos;','\'')
                elif c.attrib.has_key('k') and c.attrib['k'] == 'VNAMEENG':
                    name_eng = c.attrib['v'].title()
                    c.attrib['v'] = name_eng
                
                if name_laos:    
                    converted_name = ''
                    for l in name_laos:
                        if ascii_to_lao.has_key(l):
                            converted_name += ascii_to_lao[l]
                        else:
                            print 'Not found ',l, way_id
                            converted_name += l
                            
                            missing = True
                            #continue
                            for c in way.getchildren():
                                if c.attrib.has_key('k') and c.attrib['k'] == 'ENGLISH_NA':
                                    name_eng = c.attrib['v']
                                elif c.attrib.has_key('k') and c.attrib['k'] == 'VNAMEENG':
                                    name_eng = c.attrib['v']
                                    print name_eng
                                    print name_laos
                                

                    if missing:
                        count += 1
                        print converted_name
                    c.attrib['v'] = converted_name
                 
print 'Total notfound', count
print 'Saving'
tree.write(output_filename, encoding='utf-8', xml_declaration=True) 