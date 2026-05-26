# fal-cdn

Asset store provider for fal CDN using `fal_client.upload_file()` for uploads
and plain HTTP download for generated media URLs.

fal CDN 的素材存储 provider，使用 `fal_client.upload_file()` 上传文件，并通过普通 HTTP
下载生成的媒体 URL。

## Provider Key / Provider 配置键

```env
MAGICDUB_ASSET_STORE_PROVIDER=fal-cdn
```

## Configuration / 配置

The provider reads configuration from the process environment and
`providers/asset_store/fal_cdn/.env` when present. The root `.env` only selects
the active provider.

该 provider 会从进程环境变量读取配置；如果存在
`providers/asset_store/fal_cdn/.env`，也会读取其中的配置。根目录 `.env` 只负责选择当前启用的
provider。

Install provider dependencies with:

使用以下命令安装该 provider 的依赖：

```bash
magicdub provider install asset_store/fal-cdn
```

Required:

必填：

- `FAL_KEY` in `providers/asset_store/fal_cdn/.env`
- `providers/asset_store/fal_cdn/.env` 中的 `FAL_KEY`

## Interface / 接口

Implements `AssetStoreProvider.upload()` and `AssetStoreProvider.download()`.

实现 `AssetStoreProvider.upload()` 和 `AssetStoreProvider.download()`。

## Documentation / 文档

- https://fal.ai/docs/documentation/model-apis/fal-cdn
