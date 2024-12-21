let 
  pkgs = import <nixpkgs> {};
in pkgs.mkShell {
  packages = [
    (pkgs.python311.withPackages(ps: [
      ps.sqlalchemy
      ps.pandas
      ps.beautifulsoup4
      ps.requests
      ps.pgcli
      ps.psycopg2
      ps.requests-cache
      ps.build
      ps.ipykernel
      ps.ipython
      ps.jupyter
      ps.notebook
    ]))
  ];
}

