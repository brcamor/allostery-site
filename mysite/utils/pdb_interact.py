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
    
    if len(chains) == 0:
        # If no chains then COMPND records likely missing 
        # (e.g. in Bio files), so get chains from ATOM/HETATM records
        chains = set()
        with open(pdb_file_loc, 'r') as f:
            for line in f:
                if line.startswith('ATOM') or line.startswith('HETATM'):
                    chains.add(line[21])

    chain_map = []
    if len(names) > 0:
        for i, name in enumerate(names):
            for chain in chains[i]:
                chain_map.append((name, chain))
    else:
        for chain in chains:
            chain_map.append(('UNKNOWN', chain))

    return chain_map

def get_hetatms(pdb_file_loc, chains):
    hetatms= []
    with open(pdb_file_loc, 'r') as f:
        for line in f:
            if (line.startswith('HETATM') 
                and not (line[17:21].strip() == 'HOH')
                and line[21] in chains):
                hetatms.append((line[17:21].strip(), line[21], line[22:27].strip()))
    return list(set(hetatms))
