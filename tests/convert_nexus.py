import time
from treelib import Tree
import h5py
import json


def create_nx_worker(h5f, tree, nid, md):
    """
    recursively create the structure using dfs;
    Args:
        h5f: the input nexus/hdf5 file handler, must be writable;
        tree: tree structure that represent the data structure;
        nid: the root path to begin with
        md: dictionary containing the data
    Return:
        None
    """
    # x is a Tree.Node type
    for x in tree.children(nid):
        if not x.is_leaf():
            h5f.create_group(x.identifier)
            create_nx_worker(h5f, tree, x.identifier, md=md)
        else:
            h5f.create_dataset(x.identifier, data=md[x.identifier])


def nexus_from_dictionary(output_fname, md, show_tree=False):
    """
    convert a dictionary to nexus fileformat;
    Args:
        output_fname: filename for the output file; it will overwrite
            any existing files;
        md: the dictionary that contains the data; the keys are defined in the
            nexus file format;
        show_tree: [True, False] to show the hierarch tree or not;
    Return:
        None

    """
    # deal with empty dictionary
    if not md:
        return

    nx_tree = Tree()
    nx_tree.create_node('root', '/')

    for key in md.keys():
        # parse the path and get ride of the starting empty string;
        temp = key.split('/')[1:]
        for n, x in enumerate(temp):
            idf = '/' + '/'.join(temp[:n + 1])
            parent = '/' + '/'.join(temp[:n])
            # create branch if it doesn't exist
            if idf not in nx_tree.is_branch(parent):
                nx_tree.create_node(x, idf, parent=parent)

    if show_tree:
        nx_tree.show()

    if len(output_fname) < 3 or \
            output_fname[-3:] not in ['.h5', 'hdf', '.nx']:
        output_fname += '.nx'

    with h5py.File(output_fname, 'w') as f:
        create_nx_worker(f, nx_tree, '/', md)


def example_1():
    """
    convert a dictionary to nexus format;
    """
    from nexus_map import md
    # open "nexus_map.py" to see the data inside the dictionary

    output_fname = "output_example_1.nx"
    nexus_from_dictionary(output_fname, md, show_tree=True)


def example_2():
    """
    convert an aps dataset to nexus; it read all the existing keys in the
    aps dataset, and export using the nexus key to the output file.
    """
    input_fname = "../testdata/A009_Silica100nm_00001_0001-0100.hdf"
    output_fname = "output_example_2.nx"

    # load the key_map
    with open('nexus_aps_map.json', 'r') as f:
        key_map = json.load(f)

    # read the keys in the input file;
    md = {}
    with h5py.File(input_fname, 'r') as fin:
        for key, val in key_map.items():
            if val in fin:
                md[key] = fin.get(val)[()]

    # export file;
    nexus_from_dictionary(output_fname, md, show_tree=True)


if __name__ == '__main__':
    example_1()
    # example_2()
