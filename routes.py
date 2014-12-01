#!/usr/bin/python
#Written by spegler on 251114

from flask import Flask, render_template, request, url_for
import requests
import json
from urlparse import urlparse

VARNISH = ""
AKAMAI = ""
AKAMAI_U = ""
AKAMAI_P = ""

app = Flask(__name__)

def clear(url):
    """Clears an item from all available caches."""

    host_header = {"Host": urlparse(url).hostname}
    purge_req = VARNISH + urlparse(url).path
    varreq = requests.request(method="PURGE", url=purge_req, headers=host_header)
    if varreq.status_code == 200:
        # Even if we get a 200 the item still might not be cleared, check X-Age header.
        res_age = requests.get(url=purge_req, headers=host_header).headers
        if res_age["X-Age"] >= 5:
            vresult = "Varnish: Item Cleared."
        else:
            vresult = """Varnish: Accepted request but item age is still old.
            Age is: %s""" % res_age["X-Age"]
    else:
        vresult = "Varnish: I'm sorry, Dave. I'm afraid I can't do that."
        # This is normally down to a Varnish ACL error.
    # Setup payload as a json object list.
    payload = json.dumps({"objects": [url]})
    # Post out to Akamai.
    akreq = requests.post(AKAMAI, auth=(AKAMAI_U, AKAMAI_P), headers={"Content-Type":"application/json"}, data=payload)
    # It would probably be a good idea to add a little more error checking on this.
    # A 200 out of Akamai should be good enough for the moment.
    if akreq.status_code == 201:
        aresult = "Akamai: Item cleared."
    else:
        aresult = "Akamai: I think we should stop."

    return vresult + " " + aresult

@app.route('/', methods=['GET', 'POST'])
def main():
    if request.method == 'POST':
    	url=request.form['url'] 
    	response=clear(url)
        return render_template('post_success.html', url=url, response=response)
    else:
    	return render_template('get_success.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0')
