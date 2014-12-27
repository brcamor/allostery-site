def get_pdb_name(pdb_file_loc):
    """ Extracts molecule names and corresponding chains from pdb
    file from the COMPND MOLECULE entries
    """
    names = []
    chains = []
    with open(pdb_file_loc, 'r') as f:
        for line in f:
            stripped_line = line.strip().split()
            if len(stripped_line) > 2 and stripped_line[2] == 'MOLECULE:':
                names.append(' '.join(stripped_line[3:])[:-1])
            if len(stripped_line) > 2 and stripped_line[2] == 'CHAIN:':
                chains.append(' '.join(stripped_line[3:])[:-1])
    
    chain_map = []
    for i, name in enumerate(names):
        chain_map.append((name, chains[i]))

    return chain_map
