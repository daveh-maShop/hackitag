from mashop.microtoolkit import MicroRestServer

import os

server = MicroRestServer()
app = server.setup_app()

if __name__ == '__main__':
    server.start(app)
