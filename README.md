# cad

GFTB shelving and related CAD drawings for the Great Falls Tool Bus.
Mods follow the [VoronUsers](https://github.com/VoronDesign/VoronUsers) layout. The index is [`bus_mods/README.md`](bus_mods/README.md).

```
bus_mods/<creator>/<mod>/
├─ .metadata.yml     title, description, file manifest
├─ README.md         what it is, materials, images
├─ CAD/              source (.f3d) and neutral (.step) exports
├─ images/           renderings
├─ docs/             build sheets: LaTeX sources, compiled by Bazel
└─ pdfs/             the compiled build sheets, checked in so nobody needs a toolchain to read them
```

Documents are LaTeX compiled with [rules_tectonic](https://github.com/Jesssullivan/rules_tectonic). No TeX install is needed.

```sh
direnv allow                      # nix dev shell: bazelisk, tectonic, buildifier, uv
bazelisk build //:docs            # every PDF
bazelisk run //:buildifier.check  # lints the BUILD files
```

After a doc changes, rebuild it and copy the PDF into the mod's `pdfs/` so the checked-in copy matches its source.
