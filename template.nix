{ pkgs ? import <nixpkgs> {} }: # 

(pkgs.buildFHSUserEnv {
  
  name = "template-env";
  targetPkgs = pkgs: with pkgs; [
    coreutils git python35Full nix-index
  ];
  multiPkgs = pkgs: with pkgs; [

#output of de-generate
#$output_of_dee_generate

  ];
  runScript = "bash";
}).env
