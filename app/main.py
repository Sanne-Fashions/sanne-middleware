"""sanne-middleware HTTP API. n8n calls these endpoints as tools."""

import secrets

from fastapi import Depends, FastAPI, Header, HTTPException, Query, Response
from pydantic import BaseModel, Field

from app.config import Settings, load_settings
from app.db import Database
from app.dxf import validate_dxf
from app.sizing import best_fit


class BestFitRequest(BaseModel):
    product_id: str = Field(min_length=1, max_length=64)
    measurements: dict[str, float] = Field(
        description="Body measurements in cm, keyed by measure name, e.g. bust, waist, hip."
    )


class DxfValidateRequest(BaseModel):
    dxf_text: str = Field(min_length=1, max_length=5_000_000)


def create_app(settings: Settings | None = None, db=None, storage=None) -> FastAPI:
    settings = settings or load_settings()
    db = db or Database(settings.database_url)
    if storage is None and settings.storage_account_url:
        from app.storage import BlobStore
        storage = BlobStore(settings.storage_account_url, settings.storage_container)

    app = FastAPI(
        title="sanne-middleware",
        version="0.1.0",
        description="Best-fit sizing and DXF file service for the Sanne order-to-pattern workflow.",
    )

    def require_api_key(x_api_key: str | None = Header(default=None)) -> None:
        if x_api_key is None or not secrets.compare_digest(x_api_key, settings.api_key):
            raise HTTPException(status_code=401, detail="invalid or missing API key")

    @app.get("/healthz")
    def healthz() -> dict:
        return {"status": "ok"}

    @app.post("/v1/best-fit", dependencies=[Depends(require_api_key)])
    def best_fit_endpoint(req: BestFitRequest) -> dict:
        """Return the base size and decision (standard, alteration or custom) for a customer."""
        chart = db.fetch_chart(req.product_id)
        if not chart:
            raise HTTPException(status_code=404, detail="no size chart for this product")
        try:
            result = best_fit(req.measurements, chart, settings.alteration_limit_cm)
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc))
        return {
            "base_size": result.base_size,
            "decision": result.decision,
            "alterations": result.alterations,
            "notes": result.notes,
        }

    @app.get(
        "/v1/products/{product_id}/base-dxf",
        dependencies=[Depends(require_api_key)],
        responses={200: {"content": {"application/dxf": {}}}},
    )
    def base_dxf(product_id: str, size: str = Query(min_length=1, max_length=16)) -> Response:
        """Return the approved base-size DXF file for a product."""
        if storage is None:
            raise HTTPException(status_code=503, detail="file storage is not configured")
        data = storage.get_base_dxf(product_id, size)
        if data is None:
            raise HTTPException(status_code=404, detail="no approved DXF for this size")
        return Response(content=data, media_type="application/dxf")

    @app.post("/v1/dxf/validate", dependencies=[Depends(require_api_key)])
    def validate(req: DxfValidateRequest) -> dict:
        """Check a DXF before it goes to the pattern team."""
        errors = validate_dxf(req.dxf_text)
        return {"valid": not errors, "errors": errors}

    return app


def get_app() -> FastAPI:
    """Entry point for uvicorn: uvicorn app.main:get_app --factory"""
    return create_app()
