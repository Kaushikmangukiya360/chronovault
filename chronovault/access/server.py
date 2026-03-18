"""FastAPI server that validates link tokens and serves decrypted JSON."""

from __future__ import annotations

from fastapi import FastAPI, HTTPException, Request

from chronovault.access.linker import Linker


def build_app(linker: Linker, read_collection_data: callable) -> FastAPI:
    """Build FastAPI app for signed access links."""
    app = FastAPI(title="chronovault-access", version="1.0")

    @app.get("/access")
    def access_endpoint(t: str, request: Request) -> dict:
        source_ip = request.client.host if request.client else "127.0.0.1"
        try:
            payload = linker.validate_token(token=t, source_ip=source_ip)
            data = read_collection_data(payload["collection"])
            return {"collection": payload["collection"], "records": data}
        except Exception as exc:  # noqa: BLE001
            raise HTTPException(status_code=403, detail="access denied") from exc

    return app
