#!/usr/bin/env python
# coding: utf-8
# Copyright 2014 Thomas Polasek
# Copyright 2013 Abram Hindle
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
import urllib
import urlparse

def help():
    print "httpclient.py [GET/POST] [URL]\n"

class HTTPRequest(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body
    
    def __str__(self):
        return "%s\n\n%s" %(str(self.code), str(self.body))

class HTTPClient(object):

    def connect(self, host, port):
        return socket.create_connection((host, port), 10)
    
    def get_code(self, data):
        return int(data.split()[1])
    
    def find_index(self,lines):
        i = 0
        for l in lines:
            if len(l) != 0: i += 1
            else: return i
        return i
    
    def get_headers(self,data):
        i = self.find_index(data.splitlines())
        return "\r\n".join(data.splitlines()[0:i-1])
    
    def get_body(self, data):
        lines = data.splitlines()
        i = self.find_index(lines)
        return "\r\n".join(lines[i:len(lines)])
    
    def recvall(self, sock):
        out = []
        while True:
            dat = sock.recv(9000)
            if dat: out += [dat]
            else: break
        return "".join(out)
            
    def getInfoUrl(self,url):
        url = "http://" + url if url[:7] != "http://" else url
        purl = urlparse.urlparse(url)
        sock = self.connect(purl.hostname if not None else "/",
                            purl.port if purl.port is not None else 80)
        return [sock,purl.path,
                purl.hostname if not None else "/"]

    def GET(self, url, args=None):
        sock,path,hostname = self.getInfoUrl(url)

        sock.sendall(("GET %s HTTP/1.1\r\n" % path) +
                     ("Host: %s\r\n" % hostname) +
                     ("\r\n"))
        data = self.recvall(sock)
        return HTTPRequest(self.get_code(data), self.get_body(data))
    
    def POST(self, url, args=None):
        sock,path,hostname = self.getInfoUrl(url)
        
        requstdat = "POST %s HTTP/1.1\r\nHost: %s\r\n" % (path, hostname)
        if args is not None:
            postdat = urllib.urlencode(args)
            requstdat += "Content-Length: %s\r\n\r\n" % len(postdat)
            requstdat += postdat
        else:
            requstdat += "\r\n"

        sock.sendall(requstdat)
        data = self.recvall(sock)
        return HTTPRequest(self.get_code(data), self.get_body(data))
    
    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST(url, args)
        else:
            return self.GET(url, args)

if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print client.command(sys.argv[2], sys.argv[1])
    
    else:
        print client.command(sys.argv[1], command)
