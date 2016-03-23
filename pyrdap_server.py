from flask import Flask,jsonify,session
from ipwhois import IPWhois

app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False


@app.route('/rdap/ip/<ip>', methods=['GET'])
def get_rdap_ip(ip):
	try:	
		obj = IPWhois(ip)
		results_raw = obj.lookup_rdap(depth=1)
		status = 200
		results = jsonify(results_raw)
	except:
		results_raw = jsonify({'status': "not_found"}) 
		status = 404
		results = jsonify({'status': "not_found"})
	return results,status



if __name__ == '__main__':
	app.run(host='0.0.0.0',port=8006,debug=True,processes=10)
