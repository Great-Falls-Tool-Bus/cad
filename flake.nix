{
  description = "GFTB cad: shelving and related CAD for the Great Falls Tool Bus";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs =
    { nixpkgs, flake-utils, ... }:
    flake-utils.lib.eachDefaultSystem (
      system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
      in
      {
        devShells.default = pkgs.mkShell {
          buildInputs = with pkgs; [
            bazelisk
            buildifier
            tectonic
            git
            gh
            jq
            uv
          ];
          shellHook = ''
            echo "gftb cad dev shell"
            echo "  bazelisk  $(bazelisk version 2>/dev/null | head -1)"
            echo "  tectonic  $(tectonic --version 2>/dev/null | head -1)"
            echo "  build the cut list: bazelisk build //bus_mods/jesssullivan/port_side_shelves/docs:cut_list"
          '';
        };
      }
    );
}
