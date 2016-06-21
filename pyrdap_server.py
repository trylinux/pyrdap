from flask import Flask,jsonify,session
from ipwhois import IPWhois
import requests
import json
import elastastore
import sys
sys.path.append("/opt/pyrdap/whois")
import whois
from elasticsearch import Elasticsearch
app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False


@app.route('/rdap/ip/<ip>', methods=['GET'])
def get_rdap_ip(ip):
	es = Elasticsearch()
        does_exist = es.exists(index='rdap', doc_type='ipaddr', id = ip)
        print does_exist
        if does_exist is True:
                status = 200
                print "Found it!"
                get_record = es.get(index='rdap',doc_type='ipaddr', id = ip)
                results = jsonify(get_record['_source'])
	else:
		try:
			obj = IPWhois(ip)
			results_raw = obj.lookup_rdap(depth=1)
			status = 200
			results = jsonify(results_raw)
			es.index(index='rdap', doc_type='ipaddr', id=ip, body=json.dumps(results_raw))
		except Exception as e:
			print e
			results_raw = jsonify({'status': "not_found"}) 
			status = 404
			results = jsonify({'status': "not_found"})
	return results,status

@app.route('/rdap/asn/<asn>', methods=['GET'])
def get_rdap_asn(asn):
	es = Elasticsearch()
        does_exist = es.exists(index='whois', doc_type='asn_rdap', id = asn)
        print does_exist
        if does_exist is True:
                status = 200
                print "Found it!"
                get_record = es.get(index='rdap',doc_type='asn', id = asn)
                results = jsonify(get_record['_source'])
	else:
		try:
			url = 'http://hailey.opendnsbl.net:8080/rdapbootstrap/autnum/%s' % asn
			r = requests.get(url)
			status = 200
			b = r.json()
			#c = json.loads(b)
			#d = c['entities']
			#print d
			#e = json.dumps(c)
			#es.index(index='rwhois', doc_type='asn', id=asn, body=json.dumps(b))
			results = jsonify(b)
		except Exception as e:
			print e
			results_raw = jsonify({'status': "not_found"})
        	        status = 404
	                results = jsonify({'status': "not_found"})
	return results,status

@app.route('/whois/ip/<ip>', methods=['GET'])
@app.route('/whois/ip/<ip>/refresh/<refresh>', methods=['GET'])
def get_whois_ip(ip,refresh=None):
	es = Elasticsearch()
	print repr(ip)
	id_num = str(ip).replace(".","0")
	does_exist = es.exists(index='rwhois', doc_type='ipaddr', id = id_num)
	print does_exist
	if does_exist is True and refresh is None:
		status = 200
		print "Found it!"
		get_record = es.get(index='rwhois',doc_type='ipaddr', id = id_num)
		results = jsonify(get_record['_source'])
	elif does_exist is True and refresh is not None:
                status = 200
                print "Forcing refresh!"
                es.delete(index='rwhois', doc_type='ipaddr', id = id_num)
                try:
                        obj = IPWhois(ip)
                        try:
                                results_raw = obj.lookup(get_referral=True)
                        except:
                                results_raw = obj.lookup()

                        status = 200
                        results = jsonify(results_raw)
                        es.index(index='rwhois', doc_type='ipaddr', id=id_num, body=results_raw)

                except Exception as e:
                        print e
                        results = jsonify({'status': "not_found"})
                        status = 404


	
	else:
		try:
			obj = IPWhois(ip)
			try:
				results_raw = obj.lookup(get_referral=True)
			except:
				results_raw = obj.lookup()
			status = 200
			results = jsonify(results_raw)
			id_num = str(ip).replace(".","0")
			es.index(index='rwhois', doc_type='ipaddr', id=id_num, body=results_raw)
	
		except Exception as e:
        	        print e
                	results_raw = jsonify({'status': "not_found"})
	                status = 404
        	        results = jsonify({'status': "not_found"})
        return results,status

@app.route('/whois/search/<search>', methods=['GET'])
def get_search(search):
	es = Elasticsearch()
	a = str(search)
	try:
		b = es.search(index='rwhois',size='10000', body={"query": {"filtered": {"query":{ "query_string": { "query": a}}}}})
		status = 200
		results = jsonify(b)
	except Exception as e:
		print e
		results_raw = jsonify({'status': "not_found"})
                status = 404
                results = jsonify({'status': "not_found"})
        return results,status

@app.route('/whois/domain/<domain>', methods=['GET'])
@app.route('/whois/domain/<domain>/refresh/<refresh>', methods=['GET'])

def get_whois_domain(domain,refresh=None):
        es = Elasticsearch()
        id_num = domain
        does_exist = es.exists(index='domain', doc_type='domain', id = domain)
        print does_exist
        if does_exist is True and refresh is None:
                status = 200
                print "Found it!"
                get_record = es.get(index='domain',doc_type='domain', id = domain)
                results = jsonify(get_record['_source'])
	elif does_exist is True and refresh is not None:
		status = 200
		print "Forcing refresh!"
		es.delete(index='domain', doc_type='domain', id = domain)
                try:
                        obj = whois.whois(domain)
                        status = 200
                        results = jsonify(obj)
                        es.index(index='domain', doc_type='domain', id=domain, body=obj)

                except Exception as e:
                        print e
                        results_raw = jsonify({'status': "not_found"})
                        status = 404
	     	
		
        else:
                try:
                        obj = whois.whois(domain)
                        status = 200
                        results = jsonify(obj)
                        es.index(index='domain', doc_type='domain', id=domain, body=obj)

                except Exception as e:
                        print e
                        results_raw = jsonify({'status': "not_found"})
                        status = 404
                        results = jsonify({'status': "not_found"})
        return results,status

	
if __name__ == '__main__':
	app.run(host='0.0.0.0',port=8006,debug=True,threaded=True)
