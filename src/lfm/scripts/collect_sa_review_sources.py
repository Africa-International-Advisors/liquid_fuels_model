"""Preserve approved-review source documents without changing forecast inputs."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
from urllib.request import Request, urlopen

from lfm.config import Paths


def main():
    root = Paths.default().repo_root
    sources = json.loads((root / 'workstreams/WS1_data_validation/sa_review_sources_2026_10_07.json').read_text())['sources']
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    out = root / 'external/data/raw' / f'sa_review_{stamp}'
    out.mkdir(parents=True, exist_ok=False)

    def fetch(source):
        record = dict(source, retrieved_at=datetime.now(timezone.utc).isoformat())
        try:
            request = Request(source['url'], headers={'User-Agent': 'Mozilla/5.0 (liquid fuels source research)'})
            with urlopen(request, timeout=45) as response:
                data = response.read()
                record['resolved_url'] = response.url
            if source['format'] == 'pdf' and not data.startswith(b'%PDF'):
                raise ValueError('Expected PDF, received another content type')
            if source['format'] == 'json':
                json.loads(data)
            path = out / f"{source['id']}.{source['format']}"
            path.write_bytes(data)
            record.update(file=path.relative_to(root).as_posix(), sha256=hashlib.sha256(data).hexdigest(), bytes=len(data), status='preserved; not independently verified')
        except Exception as exc:
            record.update(status='download failed; do not treat as preserved', error=str(exc))
        print(source['id'], record['status'], flush=True)
        return record

    with ThreadPoolExecutor(max_workers=4) as pool:
        records = list(pool.map(fetch, sources))
    (out / 'manifest.json').write_text(json.dumps(records, indent=2), encoding='utf-8')
    print(out)


if __name__ == '__main__':
    main()
