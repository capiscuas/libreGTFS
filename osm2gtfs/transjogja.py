#!/usr/bin/env python
# -*- coding: utf-8 -*-

#Python script to download from OSM the created bus routes in Yogyakarta and create a GTFS file
from osmapi import OsmApi
MyApi = OsmApi()

#Fixes Routes of TransJogja
#TODO: create a web javascript framework to let anybody create the GTFS trough web.
routes = [5332612,5334914,1913445,1761302,5334915,5334916,5334918,5334917]
platforms_id = {}
unique_platforms_id = set()
routes_info = {}
for route_id in routes:
        platforms_id[route_id] = []
        print 'Getting route ',route_id
        relation = MyApi.RelationGet(route_id)
        routes_info[route_id] = relation['tag']
        for a in relation['member']:
                if a['role'] == 'platform':
	              platforms_id[route_id].append(a['ref'])
                      unique_platforms_id.add(a['ref'])
	print platforms_id[route_id]
        

import transitfeed
schedule = transitfeed.Schedule()
schedule.AddAgency("Transjogja", "http://iflyagency.com",
                   "Indonesia/Yogyakarta")

service_period = schedule.GetDefaultServicePeriod()
service_period.SetStartDate("20150101")
service_period.SetEndDate("20160101")
service_period.SetWeekdayService(True)
#service_period.SetDateHasService('20070704', False)

stops_transit = {}
nodes = MyApi.NodesGet(unique_platforms_id)
for node_id,node in nodes.items():
  platform_name = node['tag']['name']
  stops_transit[node_id] = schedule.AddStop(lng=node['lon'], lat=node['lat'], name=platform_name)
  print 'Adding Stop',platform_name

#Adding Routes in GTFS
import datetime
for route_id in routes:
        route_name = routes_info[route_id]['name']
        print '\n\nAdding Trip', route_name
        route_ref = routes_info[route_id]['ref']
        route_colour = routes_info[route_id]['colour']
        route = schedule.AddRoute(short_name= route_ref, long_name=route_name,route_type="Bus")
        
        arrival_time = datetime.datetime(2008, 11, 22, 6, 0, 0) #Starts Stop at 09:00:00

        for i in range(8):
                trip = route.AddTrip(schedule)
                for p_id in platforms_id[route_id]:
                        stop = stops_transit[p_id]
                        print 'Adding stop in ',stop, 'at ', arrival_time.strftime("%H:%M:%S")   
                        departure_time = arrival_time + datetime.timedelta(0,10)
                        trip.AddStopTime(stop, arrival_time=arrival_time.strftime("%H:%M:%S"), departure_time=departure_time.strftime("%H:%M:%S"))
                        arrival_time = departure_time + datetime.timedelta(0,5*30) #Adding 5min between stops

schedule.Validate()
schedule.WriteGoogleTransitFeed('google_transit.zip')
