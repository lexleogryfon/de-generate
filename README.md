# De-generate

Dependency generator for prebuilt binaries and shared libraries in NixOS.

## How?

    git clone https://github.com/lexleogryfon/de-generate.git
    cd ./de-generate
    nix-shell template.nix
    # edit nix-de-generate, assign path string to input variable inside main()
    # e.g. input = '/home/usr/path/to/folder_with_executables'
    ./nix-de-generate
    # a file newenv.nix should appear in current directory
    # with list of packages to satisfy dependency requirements.

## Why?

Due current state of the art NixOS design, you can't just run downloaded dynamically linked portable application outside of nixpkgs repo and expect it to work. When you attempt to run such app inside pkgs.buildFHSUserEnv, you may see that it couldn't find some libraries.
Previously you might be forced to find package for each lib manually with nix-locate, fortunately now you could just execute nix-de-generate against target directory and it will generate newenv.nix with possible dependencies. Theoretically project could be scaled to resolve dependecies in other distros too, such as Arch or Fedora.


https://nixos.wiki/wiki/FAQ#I.27ve_downloaded_a_binary.2C_but_I_can.27t_run_it.2C_what_can_I_do.3F

https://nixos.wiki/wiki/Packaging_Binaries#Extra_Dynamic_Libraries



