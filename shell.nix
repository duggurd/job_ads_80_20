let 
  pkgs = import <nixpkgs> {};
in pkgs.mkShell {
  packages = [
    pkgs.terraform
    pkgs.awscli2
    (pkgs.python312.withPackages(ps: [
      ps.sqlalchemy
      ps.pandas
      ps.beautifulsoup4
      ps.requests
    ]))
  ];
}

