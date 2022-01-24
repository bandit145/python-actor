#!/bin/env python
import actor.system.network as network
import socketserver


srv = socketserver.TCPServer(
    (
        "127.0.0.1",
        9000,
    ),
    network.MsgHandler,
)
srv.serve_forever()
