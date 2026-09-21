#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from synthetic_environment import SyntheticDGFEnvironment

class Handler(BaseHTTPRequestHandler):
    env=None
    def _send(self,status,obj):
        body=json.dumps(obj,ensure_ascii=False,indent=2).encode()
        self.send_response(status); self.send_header('Content-Type','application/json'); self.send_header('Content-Length',str(len(body))); self.end_headers(); self.wfile.write(body)
    def do_GET(self):
        if self.path=='/tools': self._send(200,{"tools":[x for x in dir(self.env) if not x.startswith('_') and callable(getattr(self.env,x)) and x not in ('call',)]})
        else: self._send(404,{"error":"not found"})
    def do_POST(self):
        if not self.path.startswith('/tool/'):
            return self._send(404,{"error":"not found"})
        tool=self.path.split('/tool/',1)[1]
        try:
            length=int(self.headers.get('Content-Length','0')); data=json.loads(self.rfile.read(length) or b'{}')
            self._send(200,self.env.call(tool,data))
        except Exception as e:
            self._send(400,{"error":str(e)})
    def log_message(self,fmt,*args): pass

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--case',type=Path,required=True); ap.add_argument('--phase',default=None); ap.add_argument('--host',default='127.0.0.1'); ap.add_argument('--port',type=int,default=8765)
    ns=ap.parse_args(); Handler.env=SyntheticDGFEnvironment(ns.case,ns.phase); srv=HTTPServer((ns.host,ns.port),Handler); print(f'http://{ns.host}:{ns.port}'); srv.serve_forever()
if __name__=='__main__': main()
