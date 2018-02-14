#!/bin/env python
import os, sys
import subprocess as sp
from pathlib import Path
from string import Template
# import ipdb

"""
made with emacs, elpy, color-theme-ld-dark,  pypy3.5.3
"""

# DONE check if file is executable before calling ldd
# DONE get initial list of libs that can't be found by ldd
# DONE  use subprocess https://docs.python.org/3/library/subprocess.html#replacing-shell-pipeline ; 
# DONE check for files that _do not exits in directory_, because otherwise those who exists could be dynamically linked during runtime by overriding LD LIB PATH
# DONE install nix-index to locate dependecies based on files
# DONE call nix-locate --top-level  libgstinterfaces-0.10.so.0  | grep " x "
# option nix-locate is case sensitive , so call for both cases?
# option handle multi string output from nix-locate
# DONE guess proper package names
# DONE generate text output file
# DONE refactor
# DONE try use raw package prefixes from nix-locate
# option add package.nix : won't implement due complexity
# option add reStructuredText docstrings
# option add pyinstaller
# BUG what if file.so does not have +x permission?

# DONE make template.nix look a like FHSsmall.nix
# DONE write readme.md
# DONE clear out input variable
# DONE comment nixOs.wiki

def scan(path_string, libs=[], all_files_param=set()):
    """
    return set of libraries that can't be linked by ldd AND set of all_files
    """
    all_files = all_files_param
    notfound_libraries = libs
    p = Path(path_string)
    for child in p.iterdir():
        if child.is_dir():
            scan(child, libs=notfound_libraries)
        else:
            all_files.add(child.name)
            if os.access(str(child), os.X_OK):
                try:
                    output = sp.check_output('ldd {} 2>&1 | grep "not found"'.format(child), shell=True, stderr=sp.STDOUT, universal_newlines=True)
                    output = output.splitlines()
                    notfound_libraries.extend(output)
                except OSError as e:
                    # trying to catch unclosed pipe > ulimit
                    print(e)
                except sp.CalledProcessError:
                    # catches exitcode that not equal 0, common in our case
                    # do nothing because ldd usually spits non zero exit code when applied to non ELF\.so , and grep spits non zero exit code when did not found mathces (e.g. no output)
                    pass

    # removing dublicates and split strings to leave only library filename
    notfound_libraries = {i.split()[0] for i in notfound_libraries}

    return notfound_libraries, all_files


def remove_existing_libs(libs, files):
    non_existing_libs = set()
    for lib in libs:
        if lib in files:
            # print(lib + " is in folder")
            pass
        else:
            # print(lib + " NOT in folder")
            non_existing_libs.add(lib)
    return non_existing_libs


def guess_pkgs(libs, output_prefixes=False):
    pkgs = set()

    if output_prefixes:
        for lib in libs:
            # pkg = sp.check_output('nix-locate --top-level {} | grep " x "'.format(lib), shell=True, stderr=sp.STDOUT, universal_newlines=True).split()[0]
            output = sp.check_output('nix-locate --top-level {}'.format(lib), shell=True, stderr=sp.STDOUT, universal_newlines=True).splitlines()
            for line in output:
                pkg = line.split()[0]
                # print(pkg)
                pkgs.add(pkg)        
    else:
        for lib in libs:
            pkg = sp.check_output('nix-locate --top-level {} | grep " x "'.format(lib), shell=True, stderr=sp.STDOUT, universal_newlines=True).split()[0].split(".")[-2]
    #        print(pkg)
            pkgs.add(pkg)
    return pkgs



def generate_nix(pkgs):
    """
    pkgs : accept raw string_of_guessed_pkgs (with \n separators)
    substitute $output_of_dee_generate in template.nix and produces newenv.nix
    """

    string_of_guessed_pkgs = pkgs
    with open('template.nix', 'r') as file1, open('newenv.nix', 'w') as file2:
        tmplt = Template(file1.read())
        d = {'output_of_dee_generate': string_of_guessed_pkgs}
        result = tmplt.substitute(d)
        # print(result)
        file2.write(result)


def main(argv):

    input = '/home/usr/path/to/folder_with_executables'
    notfound_libraries, files = scan(input)
    print('libraries that cannot be found by ldd')
    for i in notfound_libraries: print(i)
    print(len(i), type(notfound_libraries))
    print('\n\n')

    notfound_libraries = remove_existing_libs(notfound_libraries, files)
    print('\n\n')
    print('libraries that are not in the folder')
    for i in notfound_libraries: print(i)
    print(len(notfound_libraries))

    print('\n\n')
    print(guess_pkgs(notfound_libraries, output_prefixes=True))
    guessed_pkgs = guess_pkgs(notfound_libraries, output_prefixes=True)
    string_of_guessed_pkgs = " \n".join(guessed_pkgs)
#    exit()
    generate_nix(string_of_guessed_pkgs)
    exit(0)


if __name__ == "__main__":
    main(sys.argv)
