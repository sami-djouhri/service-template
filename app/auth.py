import ipaddress

from fastapi import HTTPException, Request, status
from pydantic import BaseModel

from app.config import settings
from app.logging_config import get_logger

log = get_logger(__name__)


class Principal(BaseModel):
    username: str
    groups: list[str] = []
    source: str = "forward-auth"


def _peer_trusted(request: Request) -> bool:
    """Prüft, ob der direkte TCP-Peer (der Reverse-Proxy) vertrauenswürdig ist.

    Forward-auth-Header (Remote-User/-Groups) dürfen NUR akzeptiert werden, wenn
    die Verbindung vom authentifizierenden Proxy kommt, sonst kann jeder Client,
    der den Dienst direkt erreicht, die Header fälschen und Auth umgehen.
    """
    client = request.client
    if client is None:
        return False
    try:
        peer = ipaddress.ip_address(client.host)
    except ValueError:
        return False
    for entry in settings.auth_trusted_proxies:
        try:
            if "/" in entry:
                if peer in ipaddress.ip_network(entry, strict=False):
                    return True
            elif peer == ipaddress.ip_address(entry):
                return True
        except ValueError:
            continue
    return False


async def current_user(request: Request) -> Principal:
    """
    Erwartet Authelia/Nginx forward-auth Header (konfigurierbar via
    auth_header_user/auth_header_groups), ABER nur von einem vertrauenswürdigen
    Proxy-Peer (auth_trusted_proxies). Wenn auth_required=False: anonymous.
    """
    if not settings.auth_required:
        return Principal(username="anonymous", source="disabled")

    if not _peer_trusted(request):
        log.warning(
            "auth.untrusted_peer",
            path=str(request.url.path),
            peer=request.client.host if request.client else None,
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Direkter Zugriff nicht erlaubt, Anfragen müssen über den authentifizierenden Reverse-Proxy laufen",
        )

    remote_user = request.headers.get(settings.auth_header_user)
    if not remote_user:
        log.warning("auth.missing_header", path=str(request.url.path))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )

    raw_groups = request.headers.get(settings.auth_header_groups, "")
    groups = [g.strip() for g in raw_groups.split(",") if g.strip()]
    return Principal(username=remote_user, groups=groups)


def require_group(group: str):
    async def _check(principal: Principal) -> Principal:
        if group not in principal.groups:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Group '{group}' required",
            )
        return principal

    return _check
