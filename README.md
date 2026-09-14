# cad

GFTB shelving and related CAD drawings for the Great Falls Tool Bus.

## Layout

Follows the [VoronUsers](https://github.com/VoronDesign/VoronUsers) mods layout: one directory per creator, one per mod, each self-describing.

```
bus_mods/<creator>/<mod>/
├─ .metadata.yml     title, description, file manifest
├─ README.md         what it is, materials, images
├─ CAD/              source (.f3d) and neutral (.step) exports
├─ images/           renderings
├─ docs/             build sheets — LaTeX sources, compiled by Bazel
└─ pdfs/             the compiled build sheets, checked in so nobody needs a toolchain to read them
```

Index: [`bus_mods/README.md`](bus_mods/README.md).

## Building documents

Documents are LaTeX compiled with [rules_tectonic](https://github.com/Jesssullivan/rules_tectonic); no TeX install needed.

```sh
direnv allow                 # nix dev shell: bazelisk, tectonic, buildifier, uv
bazelisk build //:docs       # every PDF, or one target:
bazelisk build //bus_mods/jesssullivan/port_side_shelves/docs:cut_list
open bazel-bin/bus_mods/jesssullivan/port_side_shelves/docs/cut_list.pdf
```

After a doc changes, rebuild and copy the PDF into the mod's `pdfs/` so the checked-in copy matches its source.

`bazelisk run //:buildifier.check` lints the BUILD files.
