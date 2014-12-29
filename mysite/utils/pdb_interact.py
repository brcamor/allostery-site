def get_chains(pdb_file_loc):
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
                chains.append(' '.join(stripped_line[3:])[:-1].split(', '))
    
    chain_map = []
    for i, name in enumerate(names):
        for chain in chains[i]:
            chain_map.append((name, chain))

    return chain_map

def get_hetatms(pdb_file_loc):
    hetatms= []
    with open(pdb_file_loc, 'r') as f:
        for line in f:
            if line.startswith('HETATM') and not (line[17:21].strip() == 'HOH'):
                hetatms.append((line[17:21].strip(), line[21], line[22:27].strip()))
    return list(set(hetatms))
