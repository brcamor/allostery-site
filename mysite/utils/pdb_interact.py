def get_pdb_name(pdb_file_loc):
    """ Extracts name from pdb file from the COMPND MOLECULE entries
    """
    names = []
    with open(pdb_file_loc, 'r') as f:
        for line in f:
            stripped_line = line.strip().split()
            if len(stripped_line) > 2 and stripped_line[2] == 'MOLECULE:':
                names.append(stripped_line[3][:-1])
    
    return names
