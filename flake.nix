{
  description = "Python environment for python-pfhub";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-23.05";
    utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, utils}: (utils.lib.eachSystem ["x86_64-linux" ] (system:
    let
      pkgs = nixpkgs.legacyPackages.${system};
      pypkgs = pkgs.python310Packages;

      pypkgs-build-requirements = {
        attrs = [ "hatchling" ];
        urllib3 = [ "hatchling" ];
        hbreader = [ "setuptools" ];
        pytrie = [ "setuptools" ];
        url-normalize = [ "poetry-core" ];
        cfgraph = [ "setuptools" ];
        pytest-logging = [ "setuptools" ];
      };

      p2n-overrides = pkgs.poetry2nix.defaultPoetryOverrides.extend (self: super:
        builtins.mapAttrs (package: build-requirements:
          (builtins.getAttr package super).overridePythonAttrs (old: {
            buildInputs = (old.buildInputs or [ ]) ++ (builtins.map (pkg: if builtins.isString pkg then builtins.getAttr pkg super else pkg) build-requirements);
          })
        ) pypkgs-build-requirements
      );

      pfhubenv = pkgs.poetry2nix.mkPoetryEnv {
        editablePackageSources = {

        };
        projectDir = ./.;
        preferWheels = true;
        overrides = p2n-overrides;
      };

      pfhub = pkgs.poetry2nix.mkPoetryApplication {
        projectDir = ./.;
        preferWheels = true;
        overrides = p2n-overrides;
      };
   in
     {
       devShells.default = pfhubenv.env;
       packages.pfhub = pfhub;
       packages.default = self.packages.${system}.pfhub;
      }
    )
  );
}
