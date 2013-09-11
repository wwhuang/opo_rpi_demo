import sys
import urllib2
import json

packet = {}

while True:
    line = sys.stdin.readline()
    if ":" in line:
        s = line.split(":")
        if s[0].strip() == "RANGE":
            packet['RANGE'] = float(s[1].strip()) / 1000000.0
        elif s[0].strip() == "RX_ID":
            packet['RX_ID'] = int(s[1].strip(), 16)
        elif s[0].strip() == "TX_ID":
            packet['TX_ID'] = int(s[1].strip(), 16)
        elif s[0].strip() == "TIME":
            packet['TIME'] = int(s[1].strip())
            print packet
            data = json.dumps(packet)
            d_len = len(data)
            url = 'http://localhost:5000/receive_data'
            req = urllib2.Request(url, data, {'Content-Type': 'application/json',
                                              'Content-Length': d_len})
            try:
                r = urllib2.urlopen(req)
                print "Correct Packet"
                print str(r.read())
            except urllib2.HTTPError, e:
                print "HTTP ERROR"
                print "Code: " + str(e.code)
                print "Msg: " + str(e.msg)
                print "Hdrs: " + str(e.hdrs)
                print "fp: " + str(e.fp)

            packet = {}
