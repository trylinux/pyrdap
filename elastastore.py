from elasticsearch import Elasticsearch
import requests
import json
import argparse

def getargs():
	parser = argparse.ArgumentParser()
	parser.add_argument("-i","--ip", help="An Ip address")
	args = parser.parse_args()
	store_whois(str(args.ip))

def store_whois(ip):
	es = Elasticsearch()
	index_num = str(ip).replace(".","0")
	print index_num
	url = "http://hailey.opendnsbl.net:8006/whois/ip/%s" % ip
	ip_whois_record = requests.get(url)
	es.index(index='rwhois', doc_type='ipaddr', id=index_num, body=ip_whois_record.json())

if __name__ == '__main__':
	getargs()
