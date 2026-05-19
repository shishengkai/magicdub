# fal-cdn

Asset store provider for fal CDN using `fal_client.upload_file()` for uploads
and plain HTTP download for generated media URLs.

## Provider Key

```env
MAGICDUB_ASSET_STORE_PROVIDER=fal-cdn
```

## Configuration

The provider reads configuration from the process environment and
`providers/asset_store/fal_cdn/.env` when present. The root `.env` only selects
the active provider.

Install provider dependencies with:

```bash
magicdub provider install asset_store/fal-cdn
```

Required:

- `FAL_KEY` in `providers/asset_store/fal_cdn/.env`

## Interface

Implements `AssetStoreProvider.upload()` and `AssetStoreProvider.download()`.

## Documentation

- https://fal.ai/docs/documentation/model-apis/fal-cdn
