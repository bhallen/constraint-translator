#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import argparse

def read_features(f_file):
    """
    Read the feature file and return a nested dictionary of feature values.
    """
    f_dict = {}
    m = [line.split('\t') for line in f_file.read().rstrip().split('\n')]
    f_names = m[0][1:]
    for line in m[1:]:
        if line[0] != 'empty':
            seg_vals = {f: v for f,v in zip(f_names, line[1:])}
        f_dict[line[0]] = seg_vals
    return f_dict


def read_constraints(c_file):
    """
    Read the constraint file and return a list of the original constraint strings.
    """
    return [line.split('\t')[0] for line in c_file.read().rstrip().split('\n')]


def convert_constraints(constraints, f_dict):
    """
    Return a list of RE-enabled (segmental) constraints translated from the originals.
    """
    def natural_class(vals_features, f_dict):
        seg_list = [segment for segment in f_dict]
        for vf in vals_features:
            # Assumes that the first character of a feature specification is its value and that the rest is the feature name.
            the_val = vf[0]
            the_ft = vf[1:]
            for seg in f_dict:
                s_vals = f_dict.get(seg, str(seg) + ' not found in feature dict.')
                if s_vals[the_ft] != the_val:
                    if seg in seg_list:
                        seg_list.remove(seg)
        return '|'.join(seg_list)

    re_constraints = []
    for c in constraints:
        splitcon = re.split('([\[\]])',c)
        for i in range(1,len(splitcon)-1):
            if splitcon[i-1] == '[' and splitcon[i+1] == ']':
                if splitcon[i][0] == '^': # complementation operator
                    splitcon[i-1] = '[^('
                    splitcon[i+1] = ')]'
                    vals_features = splitcon[i][1:].split(',')
                else:
                    splitcon[i-1] = '('
                    splitcon[i+1] = ')'
                    vals_features = splitcon[i].split(',')
                splitcon[i] = natural_class(vals_features,f_dict)
        re_constraints.append(''.join(splitcon))
    return re_constraints



def main():

    parser = argparse.ArgumentParser(description = 'Featural constraint translator')
    parser.add_argument('constraint_file_name', help='Name of constraints file')
    parser.add_argument('feature_file_name', help='Name of feature file')
    parser.add_argument('outfile', help='Name of output file')

    args = parser.parse_args()

    with open(args.constraint_file_name) as c_file:
        with open(args.feature_file_name) as f_file:
            features = read_features(f_file)
            constraints = read_constraints(c_file)
            converted = convert_constraints(constraints, features)

            with open(args.outfile, 'w') as outfile:
                outfile.write('\n'.join(converted))

    print("Output file created.")
    return 0

if __name__ == '__main__':
    main()

