# sanne-middleware

Best-fit sizing and DXF file service for the Sanne order-to-pattern workflow. n8n Cloud calls
this service as tools. It is the only component that talks to the Azure PostgreSQL database
and the private Blob storage.

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| GET | `/healthz` | Health check (no key) |
| POST | `/v1/best-fit` | Base size and decision: standard, alteration or custom |
| GET | `/v1/products/{product_id}/base-dxf?size=M` | Approved base DXF for a size |
| POST | `/v1/dxf/validate` | Check a DXF before the pattern team sees it |

Every endpoint except `/healthz` needs the header `x-api-key`.

## Configuration

| Variable | Where it comes from |
|---|---|
| `DATABASE_URL` | Container App secret (Key Vault reference). Format: `postgresql://user:pass@host/sanne_staging?sslmode=require` |
| `SERVICE_API_KEY` | Container App secret (Key Vault reference) |
| `STORAGE_ACCOUNT_URL` | Container App setting, e.g. `https://<account>.blob.core.windows.net` |
| `STORAGE_CONTAINER` | Container App setting, default `dxf-files` |
| `ALTERATION_LIMIT_CM` | Container App setting, default `3` (pending pattern team sign-off) |

No local database is needed. Tests run without one.

## Run the tests

```bash
python -m venv .venv
. .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pytest -q
```

## Database setup (Azure)

```bash
DATABASE_URL="postgresql://…/sanne_staging?sslmode=require" python scripts/migrate.py
```

Run against `sanne_staging` first. Run against `sanne_prod` only after staging is signed off.

## Deploy

1. Merge to `main`. GitHub Actions runs the tests.
2. On success, it builds the image in Azure Container Registry and updates the Container App
   on the `staging` environment.
3. Promote to production by repeating the deploy step against the production Container App
   after Sanne signs off.

GitHub repository variables needed: `AZURE_RESOURCE_GROUP`, `AZURE_ACR_NAME`, `CONTAINER_APP_NAME`.
GitHub secrets needed: `AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_SUBSCRIPTION_ID`
(federated OIDC login, no stored passwords).

## Status

Sizing rules are a working draft. Tolerances and alteration limits must be confirmed by the
pattern team using the golden cases in `tests/test_sizing.py`.
