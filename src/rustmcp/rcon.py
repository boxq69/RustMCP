"""Rust WebRCON client, one short connection per command."""

import asyncio
import json
import time
import logging

from websockets.asyncio.client import connect
from websockets.exceptions import ConnectionClosed, InvalidHandshake

from rustmcp.config import ServerConfig

logger = logging.getLogger(__name__)


CONNECTION_COOLDOWN = 1.1
REQUEST_ID = 1

_lock = asyncio.Lock() # one command at a time
_last_connect = 0.0

class RconError(Exception):
    """Readable error that the agent gets instead of a stack trace."""


class NoReplyError(RconError):
    """Connected, but the server never answered this command."""


async def send_command(
    config: ServerConfig,
    command: str,
    timeout: float = 10.0,
    collect: float = 0.0
) -> str:
    """Run one console command and return the server's reply.

    Args:
        command: Console command, e.g. "serverinfo".
        timeout: Seconds to wait for the connection and the reply.
        collect: After the reply, keep listening this many seconds and append
            every server message.
    """
    global _last_connect

    async with _lock:
        wait = CONNECTION_COOLDOWN - (time.monotonic() - _last_connect)
        if wait > 0:
            await asyncio.sleep(wait)
        _last_connect = time.monotonic()

        # the password is part of the URL, so this URL must never be logged
        url = f"ws://{config.host}:{config.port}/{config.password}"
        logger.info("RCON -> %s", command)

        try:
            async with connect(url, open_timeout=timeout, max_size=None) as ws:
                await ws.send(json.dumps(
                    {"Identifier": REQUEST_ID, "Message": command, "Name": "WebRcon"}
                ))
                lines = [await _wait_for_reply(ws, timeout)]
                if collect > 0:
                    lines += await _collect_messages(ws, collect)
                return "\n".join(line for line in lines if line)

        except InvalidHandshake:
            # Do not retry 5 wrong passwords get the IP banned
            raise RconError(
                "Server rejected the RCON connection. Check RCON_PASSWORD "
                "and that your IP is not banned from RCON."
            ) from None
        except TimeoutError:
            raise RconError(
                f"Timed out after {timeout}s, no connection or no reply from the server."
            ) from None
        except OSError:
            raise RconError(
                f"Cannot reach {config.host}:{config.port}. Is the server running "
                "and is rcon.web enabled?"
            )  from None
        except ConnectionClosed:
            raise RconError("RCON connection was closed by server.") from None

async def _wait_for_reply(ws, timeout: float) -> str:
    try:
        async with asyncio.timeout(timeout):
            async for raw in ws:
                message = json.loads(raw)
                # skip console logs that arrive before our reply
                if message.get("Identifier") == REQUEST_ID:
                    return message.get("Message", "")
    except TimeoutError:
        raise NoReplyError(f"Server did not answer within {timeout}s.") from None
    raise RconError("Connection closed before the server replied.")


async def _collect_messages(ws, seconds: float) -> list[str]:
    messages = []
    try:
        async with asyncio.timeout(seconds):
            async for raw in ws:
                messages.append(json.loads(raw).get("Message", ""))
    except TimeoutError:
        pass
    return messages