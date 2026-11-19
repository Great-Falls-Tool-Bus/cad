# cad

GFTB shelving and related CAD drawings for the Great Falls Tool Bus.
Mods follow the [VoronUsers](https://github.com/VoronDesign/VoronUsers) layout.

| Creator | Mod | Description | Vehicle | Last changed |
| --- | --- | --- | --- | --- |
| jesssullivan | [Port-side shelves](bus_mods/jesssullivan/port_side_shelves) | Stick-framed 2×4 / 2×6 shelving with ⅜″ ply decks, three stepped bays | bus-hybrid | 2026-09-14 |

```
bus_mods/<creator>/<mod>/
├─ .metadata.yml     title, description, file manifest
├─ README.md         what it is, materials, images
├─ CAD/              source (.f3d) and neutral (.step) exports
├─ images/           renderings
├─ docs/             build sheets: LaTeX sources, compiled by Bazel
└─ pdfs/             the compiled build sheets, checked in so nobody needs a toolchain to read them
```

Work from a fork. Enter the Nix shell with `nix develop` or `direnv allow`, then run `just setup` to install the shared Git hooks.
Use `just hooks-check` to compare them with the public organization mirror and `just hooks-test` to test them locally.

Documents are LaTeX compiled with [rules_tectonic](https://github.com/Jesssullivan/rules_tectonic). No TeX install is needed.

```sh
direnv allow                      # nix dev shell: bazelisk, tectonic, buildifier, uv
bazelisk build //:docs            # every PDF
bazelisk run //:buildifier.check  # lints the BUILD files
```

After a doc changes, rebuild it and copy the PDF into the mod's `pdfs/` so the checked-in copy matches its source.
