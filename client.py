#!/usr/bin/env python
# Copyright 2012-2013 inBloom, Inc. and its affiliates.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import json,sys,httplib2,urllib,yaml,traceback

class client(object):

    def __init__(self,host='127.0.0.0',port=8000,verbose=False):
        self.headers={}
        self.host=host
        self.port=port
        self.verbose=verbose
        self.errors = []
        self.connect()

    def connect(self):
        try:
            self.conn=httplib2.Http()
        except:
            self.errors.append("Failed to connect to server at host %s port %s." % (self.host,self.port))
            if self.verbose:
                print self.errors[-1]

    #def query(self,httpmode,command,q,opts,parse=True):
    def query(self, *args, **kwargs):
        if not kwargs:
            parse = True
        else:
            parse = kwargs['parse']
        if len(args) == 4:
            httpmode, command, q, opts = args[0], args[1], args[2], args[3]
        elif len(args) == 3:
            httpmode, command, q, opts = 'GET', args[0], args[1], args[2]
        uq=urllib.urlencode({"q":json.dumps(q)})
        uopts=urllib.urlencode({"opts":json.dumps(opts)})
        if httpmode == 'GET':
            url='http://'+self.host+':'+str(self.port)+'/'+command+'?'+uq+'&'+uopts
            resp,cont=self.conn.request(url,method='GET',headers=self.headers)
        elif httpmode == 'POST':
            url='http://'+self.host+':'+str(self.port)+'/'+command
            resp,cont=self.conn.request(url,method='POST',headers=self.headers,body='?'+uq+'&'+uopts)
        else:
            print "BAD HTTP MODE:",httpmode
            return None
            
        if self.verbose:
            print "REQUEST URL =",url
        if resp.status==200:
            if not parse:
                return cont
            if not opts.has_key("format") or opts["format"] == "json":
                j=json.loads(cont)
                return j
            elif opts.has_key("format"):
                if opts["format"] == "yaml":
                    return yaml.safe_load(cont)
                elif opts["format"] in ["xml","oldxml","johnxml"]:
                    return cont
        else:
            print resp,cont
        return None
    
        
if __name__=='__main__':
    c=client(host='192.168.1.22',port=9000)
    if len(sys.argv) < 3 or sys.argv[1]=='entity/search' and len(sys.argv) < 4:
        print len(sys.argv)
        print """
Usage examples:\n
./client.py GET entity/search '{"urn:lri:property_type:types":"urn:lri:entity_type:type"}' '{"details":true}'
./client.py GET entity/create '{"urn:lri:property_type:id":"MY_FQGUID","urn:lri:property_type:types":["urn:lri:entity_type:thing"]}' 
./client.py GET property/create '{"from":"MY_ENTITY_GUID","urn:lri:property_type:name":"THE NAME OF MY ENTITY"}' 
./client.py GET property/update '{"guid":"MY_PROPERTY_GUID","value":"MY NEW NAME"}' 

"""
    else:
        httpmode = sys.argv[1].upper()
        action = sys.argv[2]
        q = json.loads(sys.argv[3])
        if len(sys.argv) < 5:
            opts = {}
        else:
            opts = json.loads(sys.argv[4])

        response = c.query(httpmode,action,q,opts)
        if not opts.has_key("format") or opts["format"] == "json":
            print json.dumps(response,indent=3,sort_keys=True)
        else:
            print response





