#!/usr/bin/env python3
# Pre-process generated compile_commands.json to make it play nice with
# clangd. Mainly for use with RTEMS.

import json
import argparse
import subprocess


def get_compiler_include_paths(compiler: str) -> list[str]:
    """
    Returns a list of compiler built-in include paths
    """
    r = subprocess.run([compiler, '-E', '-Wp,-v', '-xc', '/dev/null'], capture_output=True)
    o = r.stderr.decode('utf-8').split('\n')
    out = []
    for l in o:
        if l.startswith(' '):
            out.append('-I' + l.removeprefix(' '))
    return out


# clangd can't understand these.
REMOVE_ARGS = ['-qrtems', '-specs', 'bsp_specs']

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', dest='FILE', type=str, required=True)
    parser.add_argument('-i', dest='INCLUDES', nargs='+', help='Add these directories as include paths')
    args = parser.parse_args()

    j = {}
    with open(args.FILE, 'r') as fp:
        j = json.load(fp)


    for f in j:
        for toremove in REMOVE_ARGS:
            try:
                f['arguments'].remove(toremove)
            except:
                pass

        for a in f['arguments']:
            if a.startswith('-B'):
                f['arguments'].append(a.replace('-B', '-I') + '/include')
                break
        if args.INCLUDES is None:
            args.INCLUDES = []
        f['arguments'] += ['-I' + x for x in args.INCLUDES]
        f['arguments'] += get_compiler_include_paths(f['arguments'][0])


    with open(args.FILE, 'w') as fp:
        json.dump(j, fp, indent=2)


if __name__ == '__main__':
    main()

