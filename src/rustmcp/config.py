
import os
from dataclasses import dataclass, field


REQUIRED_VARS = ("RCON_HOST", "RCON_PORT", "RCON_PASSWORD")

@dataclass(frozen=True)
class ServerConfig:
    """Settings for connecting to Rust server."""

    host: str
    port: int
    password: str = field(repr=False) # never show password in logs
    allow_raw_commands: bool = False # off by default: players can prompt-inject via chat 
    

    @classmethod
    def from_env(cls) -> "ServerConfig":
        """Read settings from environment variables.
        
        Raises: 
            ValueError: If a variable is missing or has a wrong value.
        """

        env = {name: os.getenv(name) for name in REQUIRED_VARS}
        missing = [name for name, value in env.items() if not value]
        if missing:
            raise ValueError(f"Missing env variables: {', '.join(missing)}")

        try:
            port = int(env["RCON_PORT"])
        except ValueError:
            raise ValueError(f"RCON_PORT must be a number, got {env['RCON_PORT']!r}") from None
        
        return cls(
            host=env["RCON_HOST"],
            port=port,
            password=env["RCON_PASSWORD"],
            allow_raw_commands=os.getenv("ALLOW_RAW_COMMANDS", "false").lower() == "true"
        )
