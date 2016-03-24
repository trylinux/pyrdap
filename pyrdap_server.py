from flask import Flask,jsonify,session
from ipwhois import IPWhois
import requests
app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False


@app.route('/rdap/ip/<ip>', methods=['GET'])
def get_rdap_ip(ip):
	try:	
		obj = IPWhois(ip)
		results_raw = obj.lookup_rdap()
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

if __name__ == '__main__':
	app.run(host='0.0.0.0',port=8006,debug=True,processes=10)
