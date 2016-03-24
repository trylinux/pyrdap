from flask import Flask,jsonify,session
from ipwhois import IPWhois
import requests
from elasticsearch import Elasticsearch
app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False

@app.before_request
def _elastic_connect():
	es = Elasticsearch()


@app.route('/rdap/ip/<ip>', methods=['GET'])
def get_rdap_ip(ip):
	try:	
		obj = IPWhois(ip)
		results_raw = obj.lookup_rdap(depth=1)
		status = 200
		results = jsonify(results_raw)
	except Exception as e:
		print e
		results_raw = jsonify({'status': "not_found"}) 
		status = 404
		results = jsonify({'status': "not_found"})
	return results,status

@app.route('/rdap/asn/<asn>', methods=['GET'])
def get_rdap_asn(asn):
	try:
		url = 'http://hailey.opendnsbl.net:8080/rdapbootstrap/autnum/%s' % asn
		r = requests.get(url)
		status = 200
		results = jsonify(r.json())
	except Exception as e:
		print e
		results_raw = jsonify({'status': "not_found"})
                status = 404
                results = jsonify({'status': "not_found"})
	return results,status

@app.route('/whois/ip/<ip>', methods=['GET'])
def get_whois_ip(ip):
	es = Elasticsearch()
	id_num = str(ip).strip("\.")
	does_exist = es.exists(index='rwhois', doc_type='ipaddr', id = id_num)
	print does_exist
	if does_exist is True:
		status = 200
		get_record = es.search(index='rwhois', body={"query": {"filtered": {"query":{ "query_string": { "query": ip}}}}})
		results = jsonify(get_record)
	else:
		try:
			obj = IPWhois(ip)
			results_raw = obj.lookup(get_referral=True)
			status = 200
			results = jsonify(results_raw)
	
		except Exception as e:
        	        print e
                	results_raw = jsonify({'status': "not_found"})
	                status = 404
        	        results = jsonify({'status': "not_found"})
        return results,status

#@app.route('/whois/domain/<domain>', methods=['GET']
	
if __name__ == '__main__':
	app.run(host='0.0.0.0',port=8006,debug=True,processes=10)
