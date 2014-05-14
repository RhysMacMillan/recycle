"""A set of tools for use in integration tests."""
import os
from hashlib import sha1

import numpy as np
import tables

def hasher(x):
    return int(sha1(x).hexdigest(), 16)

def idx(h):
    ind = [None] * 5
    for i in range(4, -1, -1):
        h, ind[i] = divmod(h, 2**32)
    return tuple(ind)

sha1array = lambda x: np.array(idx(hasher(x)), np.uint32)

def table_exist(db, tables):
    """Checks if hdf5 database contains the specified tables.
    """
    return all([t in db.root for t in tables])

def find_ids(data, data_table, id_table):
    """Finds ids of the specified data located in the specified data_table,
    and extracts the corresponding id from the specified id_table.
    """
    ids = []
    for i, d in enumerate(data_table):
        if isinstance(d, np.ndarray) and isinstance(data, np.ndarray):
            if (d == data).all():
                ids.append(id_table[i])
        elif isinstance(d, np.ndarray) and not isinstance(data, np.ndarray):
            if (d == sha1array(data)).all():
                ids.append(id_table[i])
        elif d == data:
            ids.append(id_table[i])
    return ids

def exit_times(agent_id, exit_table):
    """Finds exit times of the specified agent from the exit table.
    """
    i = 0
    exit_times = []
    for index in exit_table["AgentId"]:
        if index == agent_id:
            exit_times.append(exit_table["ExitTime"][i])
        i += 1

    return exit_times

def create_sim_input(ref_input, k_factor_in, k_factor_out):
    """Creates xml input file from a reference xml input file.

    Changes k_factor_in_ and k_factor_out_ in a simulation input
    files for KFacility.

    Args:
        ref_input: A reference xml input file with k_factors.
        k_factor_in: A new k_factor for requests.
        k_factor_out: A new conversion factor for offers.

    Returns:
        A path to the created file. It is created in the same
        directory as the reference input file.
    """
    # File to be created
    fw_path = ref_input.split(".xml")[0] + "_" + str(k_factor_in) + \
              "_" + str(k_factor_out) + ".xml"
    fw = open(fw_path, "w")
    fr = open(ref_input, "r")
    for f in fr:
        if f.count("k_factor_in_"):
            f = f.split("<")[0] + "<k_factor_in_>" + str(k_factor_in) + \
                "</k_factor_in_>\n"
        elif f.count("k_factor_out_"):
            f = f.split("<")[0] + "<k_factor_out_>" + str(k_factor_out) + \
                "</k_factor_out_>\n"

        fw.write(f)

    # Closing open files
    fr.close()
    fw.close()

    return fw_path
