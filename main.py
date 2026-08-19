import asyncio
import signal
import uvicorn
from src.cli import parse_args, run_cli_loop, run_monitor, setup_logging
from src.config import get_config
from src.api import app, set_manager

async def run_api(manager, port: int):
    set_manager(manager)
    config = uvicorn.Config(app, host="0.0.0.0", port=port, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()

async def main_async(args):
    config = get_config(args)
    setup_logging(config)
    manager = await run_monitor(config)
    if manager is None:
        return
    if args.api_port:
        api_task = asyncio.create_task(run_api(manager, args.api_port))
        cli_task = asyncio.create_task(run_cli_loop(manager, config))
        await asyncio.gather(api_task, cli_task)
    else:
        await run_cli_loop(manager, config)

def main():
    args = parse_args()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    def shutdown():
        print("\nShutdown requested. Exiting gracefully.")
        loop.stop()
    try:
        loop.add_signal_handler(signal.SIGINT, shutdown)
        loop.add_signal_handler(signal.SIGTERM, shutdown)
    except NotImplementedError:
        pass
    try:
        loop.run_until_complete(main_async(args))
    except KeyboardInterrupt:
        pass
    finally:
        loop.close()

if __name__ == "__main__":
    main()
