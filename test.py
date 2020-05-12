from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware
import qboard
import uvicorn
import numpy as np
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
import threading

Q = np.random.rand(30, 30) - 0.5

solver = qboard.solver(mode="bf")


count = 0
def cb(dic):
    if dic["cb_type"] == qboard.constants.CB_TYPE_NEW_SOLUTION:
        energy_ = dic["energy"]
        spins_ = dic["spins"]
        print("New solution found, energy %f, result vector %s" % (energy_, spins_))
        count += 1
        ws.add_message({'dat': count, 'mess': energy_})
    if dic["cb_type"] == qboard.constants.CB_TYPE_INTERRUPT_TIMEOUT:
        print("Solver interrupted by timeout")
        ws.active = False

    if dic["cb_type"] == qboard.constants.CB_TYPE_INTERRUPT_TARGET:
        print("Solver interrupted by target")
        ws.active = False


class Ws:
    def __init__(self):
        self.sockets = []
        self.messages = []
        self.active = True
        self.count = 0

    def add_mess(self, dic):
        if dic["cb_type"] == qboard.constants.CB_TYPE_NEW_SOLUTION:
            energy_ = dic["energy"]
            spins_ = dic["spins"]
            print("New solution found, energy %f, result vector %s" % (energy_, spins_))
            self.count += 1
            self.messages.append({'dat': self.count, 'mess': energy_})
        if dic["cb_type"] == qboard.constants.CB_TYPE_INTERRUPT_TIMEOUT:
            print("Solver interrupted by timeout")
            self.active = False
            self.count = 0

        if dic["cb_type"] == qboard.constants.CB_TYPE_INTERRUPT_TARGET:
            print("Solver interrupted by target")
            self.active = False
            self.count = 0


    def add_message(self, message):
        self.messages.append(message)

    def add_client(self, ws_):
        if ws_ not in self.sockets:
            self.sockets.append(ws_)

    async def send_message(self):
        if self.messages:
            for ws_ in self.sockets:
                txt = await ws_.receive_text()
                print(txt)
                mess = self.messages.pop()
                await ws_.send_text(f'{{"dat": {mess["dat"]}, "mess": {mess["mess"]} }}')


ws = Ws()


app = FastAPI()
app.mount("/react", StaticFiles(directory="./react/build", html=True))
app.add_middleware(CORSMiddleware, allow_origins=['*'])

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var ws = new WebSocket("ws://localhost:8000/ws");
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""


@app.get("/")
async def get():
    return HTMLResponse(react)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    ws.active = True
    await websocket.accept()
    ws.add_client(websocket)
    tr = threading.Thread(target=solver.solve_qubo, args=(Q,), kwargs={'callback': ws.add_mess, 'timeout': 30, 'verbosity': 0})
    tr.start()
    while ws.active:
        await ws.send_message()
    tr.join()
    ws.sockets = []


if __name__ == '__main__':
    uvicorn.run("test:app", host="0.0.0.0", port=8000, log_level='info', reload=True)


react = '''
<!doctype html><html lang="en"><head><meta charset="utf-8"/><link rel="icon" href="/favicon.ico"/><meta name="viewport" content="width=device-width,initial-scale=1"/><meta name="theme-color" content="#000000"/><meta name="description" content="Web site created using create-react-app"/><link rel="apple-touch-icon" href="/logo192.png"/><link rel="manifest" href="/static/manifest.json"/><title>React App</title><link href="/static/css/main.d1b05096.chunk.css" rel="stylesheet"></head><body><noscript>You need to enable JavaScript to run this app.</noscript><div id="root"></div><script>!function(e){function r(r){for(var n,a,i=r[0],c=r[1],l=r[2],s=0,p=[];s<i.length;s++)a=i[s],Object.prototype.hasOwnProperty.call(o,a)&&o[a]&&p.push(o[a][0]),o[a]=0;for(n in c)Object.prototype.hasOwnProperty.call(c,n)&&(e[n]=c[n]);for(f&&f(r);p.length;)p.shift()();return u.push.apply(u,l||[]),t()}function t(){for(var e,r=0;r<u.length;r++){for(var t=u[r],n=!0,i=1;i<t.length;i++){var c=t[i];0!==o[c]&&(n=!1)}n&&(u.splice(r--,1),e=a(a.s=t[0]))}return e}var n={},o={1:0},u=[];function a(r){if(n[r])return n[r].exports;var t=n[r]={i:r,l:!1,exports:{}};return e[r].call(t.exports,t,t.exports,a),t.l=!0,t.exports}a.e=function(e){var r=[],t=o[e];if(0!==t)if(t)r.push(t[2]);else{var n=new Promise((function(r,n){t=o[e]=[r,n]}));r.push(t[2]=n);var u,i=document.createElement("script");i.charset="utf-8",i.timeout=120,a.nc&&i.setAttribute("nonce",a.nc),i.src=function(e){return a.p+"static/js/"+({2:"xlsx"}[e]||e)+"."+{2:"51a5d2ca",3:"0ef2bb3f",5:"8af65051",6:"0b87346a"}[e]+".chunk.js"}(e);var c=new Error;u=function(r){i.onerror=i.onload=null,clearTimeout(l);var t=o[e];if(0!==t){if(t){var n=r&&("load"===r.type?"missing":r.type),u=r&&r.target&&r.target.src;c.message="Loading chunk "+e+" failed.\n("+n+": "+u+")",c.name="ChunkLoadError",c.type=n,c.request=u,t[1](c)}o[e]=void 0}};var l=setTimeout((function(){u({type:"timeout",target:i})}),12e4);i.onerror=i.onload=u,document.head.appendChild(i)}return Promise.all(r)},a.m=e,a.c=n,a.d=function(e,r,t){a.o(e,r)||Object.defineProperty(e,r,{enumerable:!0,get:t})},a.r=function(e){"undefined"!=typeof Symbol&&Symbol.toStringTag&&Object.defineProperty(e,Symbol.toStringTag,{value:"Module"}),Object.defineProperty(e,"__esModule",{value:!0})},a.t=function(e,r){if(1&r&&(e=a(e)),8&r)return e;if(4&r&&"object"==typeof e&&e&&e.__esModule)return e;var t=Object.create(null);if(a.r(t),Object.defineProperty(t,"default",{enumerable:!0,value:e}),2&r&&"string"!=typeof e)for(var n in e)a.d(t,n,function(r){return e[r]}.bind(null,n));return t},a.n=function(e){var r=e&&e.__esModule?function(){return e.default}:function(){return e};return a.d(r,"a",r),r},a.o=function(e,r){return Object.prototype.hasOwnProperty.call(e,r)},a.p="/",a.oe=function(e){throw console.error(e),e};var i=this.webpackJsonpreact=this.webpackJsonpreact||[],c=i.push.bind(i);i.push=r,i=i.slice();for(var l=0;l<i.length;l++)r(i[l]);var f=c;t()}([])</script><script src="/static/js/4.42a866a7.chunk.js"></script><script src="/static/js/main.bdf87f67.chunk.js"></script></body></html>
'''
