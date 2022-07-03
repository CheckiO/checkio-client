import os
import signal
import aiohttp
import asyncio
import aiohttp_cors
from aiohttp import web
from checkio_client.settings import conf

async def view_plugin(req):
    from checkio_client.web_plugin import Actions
    data = await req.json()
    
    return web.json_response(
        getattr(Actions, data['do'])(data)
    )

def start_server():
    domain_data = conf.default_domain_data

    web_app = web.Application()

    cors = aiohttp_cors.setup(web_app, defaults={
        "*": aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*",
            )
    })
    cors.add(web_app.router.add_post('/plugin/', view_plugin))
    web.run_app(web_app, port=8766, host='localhost')

def serverd():
    import daemon
    from pid import PidFile
    pidfile = PidFile(conf.serv_pidfile)
    with daemon.DaemonContext(pidfile=pidfile):
        start_server()

def main(args):
    if args.daemon:
        serverd()
    else:
        start_server()
    
def stop(args=None):
    try:
        with open(conf.serv_pidfile) as fh:
            os.kill(int(fh.read()), signal.SIGTERM)
    except FileNotFoundError:
        print('PIDFile "{}" not found. Server is not running now?'.format(conf.serv_pidfile))
    except ProcessLookupError:
        print('Process from PIDFile "{}" not found. Server is not running now?'.format(conf.serv_pidfile))

def restart(args):
    stop()
    serverd()
