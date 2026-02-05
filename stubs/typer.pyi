from typing import Any, Optional, Callable

class Typer:
    def __init__(self, **kwargs: Any) -> None: ...
    def command(self) -> Callable[[Callable[..., Any]], Callable[..., Any]]: ...

def Option(
    default: Any = ...,
    *,
    help: Optional[str] = ...,
    **kwargs: Any,
) -> Any: ...
