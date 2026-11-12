# ERDI Docs: developer documentation for laser rangefinder modules

Source of the documentation site at **https://erdilrf.com/docs/**: UART protocols, wiring, code examples (Python, Arduino, ESPHome, ROS 2, ArduPilot Lua), a compatibility matrix with evidence links, and a **browser serial monitor** (Web Serial) for ERDI 905 nm laser rangefinder modules. Built with [Docusaurus](https://docusaurus.io/) 3.

- Docs home: <https://erdilrf.com/docs/>
- Serial monitor: <https://erdilrf.com/docs/tools/serial-monitor/>, works in Chrome and Edge on desktop, no install
- Models with a published protocol: 22 (13 in family A `55 AA`, 9 in family B `5C`)

## What is in this repository

| Path | Content |
|---|---|
| `docs/` | Pages. `docs/models/*.mdx`, `docs/compatibility/_matrix.md` and the partials are generated, the rest is hand-written or synced |
| `scripts/gen_models.py` | Generates model pages from the ERDI product database (`kb.json`). Cross-checks baud, frame length, unit and out-of-range marker against the erdi-lrf table and fails on any difference. Never writes prices |
| `scripts/sync_repo_docs.py` | Copies protocol and guide pages from [erdi-lrf-drivers](https://github.com/ErdiTech/erdi-lrf-drivers) so there is one source |
| `scripts/make_fixtures.py` | Builds the per-model wire table and golden test frames from erdi-lrf 0.1.4 (`vendor/`) |
| `src/lib/erdi-protocol.mjs` | JavaScript frame codec (port of the Python package), used by the serial monitor |
| `src/components/SerialMonitor/` | The Web Serial monitor (React), chart by [uPlot](https://github.com/leeoniya/uPlot) |
| `test/protocol.test.mjs`, `fixtures/` | Unit tests: golden frames for all 22 models, frames rebuilt from two real factory capture logs, noisy and chunked streams |
| `static/evidence/lua-sitl/` | Logs of the ArduPilot SITL run behind the Verified (SITL) matrix cells |

## Develop

```bash
npm install
npm test          # decoder unit tests (Node 20+)
npm start         # dev server at http://localhost:3000/docs/
npm run build     # static site in build/
```

The generated pages are committed, so CI needs neither the product database nor Python. To regenerate them you need the database checkout: `ERDI_KB_DIR=/path/to/erdi-kb npm run gen`.

## Deploy

The site is static. `scripts/deploy.sh` uploads `build/` as a new release directory and repoints a `current` symlink, so a rollback is one command (`scripts/deploy.sh rollback`). nginx serves it with:

```nginx
location = /docs { return 301 /docs/; }
location ^~ /docs/ {
    root /var/www/erdilrf-docs/current;
    if (-d $request_filename) { rewrite ^(.*[^/])$ $1/ permanent; }
    try_files $uri $uri/index.html =404;
    error_page 404 /docs/404.html;
    add_header Cache-Control "public, max-age=600" always;
}
location ^~ /docs/assets/ {
    root /var/www/erdilrf-docs/current;
    try_files $uri =404;
    add_header Cache-Control "public, max-age=31536000, immutable" always;
}
```

## Rules for contributors

- A number goes on a model page only if the product database has it. No source, no field.
- A matrix cell may say Verified only with evidence you can open. Everything else says Untested or No driver yet.
- No prices in the docs. The buy button links to the shop.

## Support

tommy@erdimail.com, +86 133 0819 5790, <https://erdilrf.com/contact/>

## License

Code: MIT, see [LICENSE](LICENSE). Documentation text: CC BY 4.0. The model specifications come from ERDI datasheets.
Copyright (c) 2026 ERDI TECH LTD.
