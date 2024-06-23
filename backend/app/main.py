import os
import multiprocessing

import click
import uvicorn

from core.config import config
from consumer import start_consumer


@click.command()
@click.option(
    "--env",
    type=click.Choice(["dev", "prod"], case_sensitive=False),
    default="dev",
)
@click.option(
    "--debug",
    type=click.BOOL,
    is_flag=True,
    default=False,
)
def main(env: str, debug: bool):
    os.environ["ENV"] = env
    print(os.environ["ENV"])
    os.environ["DEBUG"] = str(debug)
    uvicorn.run(
        app="app:app",
        host=config.APP_HOST,
        port=config.APP_PORT,
        reload=True if env != "prod" else False,
    )


if __name__ == "__main__":
    process = multiprocessing.Process(target=start_consumer)
    process.start()
    main()
    process.join()
