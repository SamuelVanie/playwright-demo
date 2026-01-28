{
  description = "A playwright demo for the afrolink project";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-25.11";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs {
          inherit system;
        };
      in
        {
          devShell = pkgs.mkShell {
            buildInputs = with pkgs; [ python313Packages.playwright python313Packages.python python313Packages.opencv4 python313Packages.numpy ];
          };
        });
}
