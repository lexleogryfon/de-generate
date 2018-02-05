#!/bin/env python
import os
import subprocess as sp
from pathlib import Path
from string import Template
# import ipdb

"""
pypy 3.5.3
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
# TODO refactor
# TODO try use raw package prefixes from nix-locate
# TODO add package.nix
# TODO add pyinstaller



# variables
files = set()
notfound_libraries = []
temp = set()

input = '../wingide/'



def scan(path_string):
    p = Path(path_string)
    for child in p.iterdir():
        if child.is_dir():
            scan(child)
        else:
            temp.add(child.name)
            if os.access(str(child), os.X_OK):
                try:
                    output = sp.check_output('ldd {} 2>&1 | grep "not found"'.format(child), shell=True, stderr=sp.STDOUT, universal_newlines=True)
                    output = output.splitlines()
                    notfound_libraries.extend(output)
                except OSError as e:
                    print(e)
                except sp.CalledProcessError:
                    # catches exitcode that not equal 0, common in our case
                    # do nothing because ldd usually spits non zero exit code when applied to non ELF\.so , and grep spits non zero exit code when did not found mathces (e.g. no output)
                    pass
    return notfound_libraries

                
n_l_after_return = scan(input)


# print(temp, len(temp), len(set(temp)))
print(notfound_libraries == n_l_after_return)
# for i in range(1, 10): print(type(notfound_libraries[i]), len(notfound_libraries), notfound_libraries[i])
exit()



# removing dublicates and split strings to leave only library filename
notfound_libraries = {i.split()[0] for i in notfound_libraries}


for i in notfound_libraries:
    print(i)

# print(len(i), type(notfound_libraries))


def remove_existing_libs(libs, files):
    non_existing_libs = set()
    for lib in libs:
        if lib in files:
        # print(lib + " is in folder")
            pass
        else:
            print(lib + " NOT in folder")
            non_existing_libs.add(lib)
    return non_existing_libs


print('\n\n')
notfound_libraries = remove_existing_libs(notfound_libraries, temp)
for i in notfound_libraries: print(i)


def guess_pkgs():
    pkgs = set()
    for lib in notfound_libraries:
        pkg = sp.check_output('nix-locate --top-level {} | grep " x "'.format(lib), shell=True, stderr=sp.STDOUT, universal_newlines=True).split()[0].split(".")[-2]
#        print(pkg)
        pkgs.add(pkg)
    return pkgs


print('\n\n')


print(guess_pkgs())
guessed_pkgs = guess_pkgs()
string_of_guessed_pkgs = " \n".join(guessed_pkgs)


def guess_prefixes(pkgs):
    # unimplemented, because of nix-env can't be run in FHS, error: Nix database directory ‘/nix/var/nix/db’ is not writable: Permission denied
    pkgs_with_prefixes = ()
    for pkg in pkgs:
        # try
        prefixed_pkg = sp.check_output('nix-env -qaPsc --description {}'.format(pkg),
                                       shell=True, stderr=sp.STDOUT,
                                       universal_newlines=True)  # .split()[0].split(".")[-2]
        print(prefixed_pkg)
    return pkgs_with_prefixes


# guess_prefixes(guessed_pkgs)


with open('template.nix', 'r') as file1, open('newenv.nix', 'w') as file2:
    tmplt = Template(file1.read())
    d = {'output_of_dee_generate': string_of_guessed_pkgs}
    result = tmplt.substitute(d)
#    print(result)
    file2.write(result)
