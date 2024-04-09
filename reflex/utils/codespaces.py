from __future__ import annotations

import os

from fastapi.responses import HTMLResponse

from reflex.components.base.script import Script
from reflex.components.el.elements.media import Iframe
from reflex.components.component import Component
from reflex.constants import Endpoint

redirect_script = """
const thisUrl = new URL(window.location.href);
const params = new URLSearchParams(thisUrl.search)

function doRedirect(url) {
    if (!window.sessionStorage.getItem("authenticated_github_codespaces")) {
        const a = document.createElement("a");
        if (params.has("redirect_to")) {
            a.href = params.get("redirect_to")
        } else if (!window.location.href.startsWith(url)) {
            a.href = url + `?redirect_to=${window.location.href}`
        } else {
            return
        }
        a.hidden = true;
        a.click();
        a.remove();
        window.sessionStorage.setItem("authenticated_github_codespaces", "true")
    }
}
doRedirect("%s")
""" % Endpoint.AUTH_CODESPACE.get_url()


def codespaces_port_forwarding_domain() -> str | None:
    GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN = os.getenv(
        "GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN"
    )
    return GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN


def is_running_in_codespaces() -> bool:
    return codespaces_port_forwarding_domain() is not None


def codespaces_auto_redirect() -> list[Component]:
    if is_running_in_codespaces():
        return [Script.create(redirect_script)]
    return []


async def auth_codespace() -> HTMLResponse:
    """Page automatically redirecting back to the app after authenticating a codespace port forward.
    
    Returns:
        An HTML response with an embedded script to redirect back to the app.
    """
    return HTMLResponse("""
    <html>
        <head>
            <title>Reflex Github Codespace Forward Successfully Authenticated</title>
        </head>
        <body>
            <center>
                <h2>Successfully Authenticated</h2>
            </center>
            <script language="javascript">
                %s
            </script>
        </body>
    </html>
    """ % redirect_script)