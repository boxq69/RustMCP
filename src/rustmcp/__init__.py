
import logging

from dotenv import load_dotenv

def main() -> None:
    load_dotenv()
    logging.basicConfig(level=logging.INFO)

    from rustmcp.server import mcp

    mcp.run(transport="stdio")