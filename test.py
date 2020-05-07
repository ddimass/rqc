import qboard
import uvicorn
import numpy as np
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse

Q = np.random.rand(30, 30) - 0.5

solver = qboard.solver(mode="bf")


async def cb(dic):
    if dic["cb_type"] == qboard.constants.CB_TYPE_NEW_SOLUTION:
        energy_ = dic["energy"]
        spins_ = dic["spins"]
        print("New solution found, energy %f, result vector %s" % (energy_, spins_))
        return energy_
    if dic["cb_type"] == qboard.constants.CB_TYPE_INTERRUPT_TIMEOUT:
        print("Solver interrupted by timeout")
    if dic["cb_type"] == qboard.constants.CB_TYPE_INTERRUPT_TARGET:
        print("Solver interrupted by target")


app = FastAPI()


@app.get("/")
async def get():
    return HTMLResponse(html)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message text was: {data}")

app = FastAPI()

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
    return HTMLResponse(html)

ws: WebSocket

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    solver.solve_qubo(Q, callback=cb, timeout=30, verbosity=0)
    await websocket.send_text(f"Message text was: {energy}")


if __name__ == '__main__':
    #
    uvicorn.run("test:app", host="0.0.0.0", port=8000, log_level='info', reload=True)