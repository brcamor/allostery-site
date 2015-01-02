from django.shortcuts import render, redirect
from django.http import HttpResponse
import proteinnetwork as pn
import requests 
from django.conf import settings
from utils.pdb_interact import get_chains, get_hetatms
from proteinnetwork.molecules import AtomList, BondList

def home_page(request):

    if request.method == 'POST':
        pdb_id = request.POST['pdb_id']
        request.session['pdb_id'] = pdb_id
        return redirect('/chains')

    else:
        return render(request, 'home.html')

def chain_setup(request):

    if request.method == 'POST':
        included_chains = request.POST.getlist('chains')
        
        all_chains = request.session.get('all_chains')
        removed_chains = list(set(all_chains) - set(included_chains))

        request.session['included_chains'] = included_chains
        request.session['removed_chains'] = removed_chains
        
        return redirect('/hetatms')

    elif request.session.get('pdb_id'):
        pdb_id = request.session.get('pdb_id')
        if pdb_id:
            pdb_file_name = settings.MEDIA_ROOT + '/' + pdb_id + '.pdb'
            
            # Retrieve the PDB file from the RSC website and save in media folder
            with open(pdb_file_name, 'w') as f:
                pdb_file_url = 'http://www.rcsb.org/pdb/files/'+ pdb_id + '.pdb'
                pdb_file_text = requests.get(pdb_file_url)
                f.write(pdb_file_text.text)
                
                # Extract name of molecules in the PDB file    
                chain_map = get_chains(pdb_file_name)
                chains = [chain[1] for chain in chain_map] 
                request.session['all_chains'] = chains

                return render(
                    request, 
                    'chain_setup.html', 
                    {'pdb_id' : pdb_id, 'chain_map' : chain_map}
                )

    else:
        print "PDB ID not received"
        return redirect('/')

def hetatm_setup(request):
    
    if request.method == 'POST':

        hetatms = request.session['hetatms']
        hetatms = [[hetatm[2], hetatm[1]] for hetatm in hetatms]
        
        included_hetatms_idx = request.POST.getlist('hetatms')
        included_hetatms = []
        for idx in included_hetatms_idx:
            included_hetatms.append(hetatms[int(idx)])
        
        removed_hetatms = [hetatm for hetatm in hetatms
                           if hetatm not in included_hetatms]

        request.session['included_hetatms'] = included_hetatms
        request.session['removed_hetatms'] = removed_hetatms

        return redirect('/source')

    else:

        pdb_id = request.session.get('pdb_id')
        chains = request.session.get('all_chains')
        
        if pdb_id and chains:
            pdb_file_name = settings.MEDIA_ROOT + '/' + pdb_id + '.pdb'
            hetatms = get_hetatms(pdb_file_name, chains)
            request.session['hetatms'] = hetatms

            return render(
                request, 
                'hetatm_setup.html', 
                {'pdb_id' : pdb_id, 'hetatms' : hetatms}
            )
        
        else:
            print "pdb_id and chains not found"
            return redirect('/')

def source_setup(request):
    
    if request.method == 'POST':
        print "In source_setup POST"
        residues = request.session.get('residue_list')
        source_residues_idx = request.POST.getlist('residues')
        print 'Source residues idx: ' + str(source_residues_idx)
        source_residues = []
        for idx in source_residues_idx:
            source_residues.append(residues[int(idx)])
        request.session['source_residues'] = source_residues
        return redirect('/results')

    pdb_id = request.session.get('pdb_id')
    removed_hetatms = request.session.get('removed_hetatms', [])
    removed_chains = request.session.get('removed_chains', [])

    if pdb_id and removed_hetatms is not None and removed_chains is not None:
        pdb_file_name = settings.MEDIA_ROOT + '/' + pdb_id + '.pdb'
        
        protein = pn.molecules.Protein()
        parser = pn.parsing.PDBParser(pdb_file_name)
        parser.parse(
            protein, 
            strip={
                'res_name' : ['HOH'], 
                'residues' : removed_hetatms, 
                'chain' : removed_chains
            }
        )

        residue_list = sorted(
            protein.residues.keys(), 
            key=lambda element: (element[1], int(element[0][0:3])))
        request.session['residue_list'] = residue_list

        return render(
            request,
            'source_setup.html',
            {
                'pdb_id' : request.session['pdb_id'],
                'residues': residue_list,
            }
        )
    else:
        return redirect('/')

def results(request):

    if request.method == 'POST':
        return render(request, 'results.html')
    else:
        pdb_id = request.session.get('pdb_id')
        pdb_file_name = settings.MEDIA_ROOT + '/' + pdb_id + '.pdb'
        removed_hetatms = request.session.get('removed_hetatms', [])
        removed_chains = request.session.get('removed_chains', [])
    
        # Load the protein
        protein = pn.molecules.Protein()
        parser = pn.parsing.PDBParser(pdb_file_name)
        parser.parse(
            protein, 
            strip={
                'res_name' : ['HOH'], 
                'residues' : removed_hetatms, 
                'chain' : removed_chains
            }
        )
        ngenerator = pn.parsing.generate_network_FIRST()
        ngenerator.generate_network(protein, 
                                    bond_files_path=settings.MEDIA_ROOT)

        # Calculate perturbation propensities
        source_residues_list = request.session['source_residues']
        source_residues = []
        for residue in source_residues_list:
            source_residues.append(tuple(residue))
        
        source_atoms = protein.get_atoms(source_residues)
        source_bonds = pn.helpers.weak_bonds(source_atoms, protein.bonds)

        pp = pn.edgeedge.perturbation_propensity (protein.network, 
                                                  source_bonds,
                                                  protein.bonds)

        weak_bonds = BondList([bond for bond in protein.bonds if bond.weight < 2000])
        pp_weak = {bond.id:pp[bond.id] for bond in weak_bonds}
        pp_weak_ordered_idx = sorted(pp_weak.keys(), 
                                     key=lambda element:pp_weak[element], 
                                     reverse=True)
        
        # Get info on top bonds
        top_weak_bonds_pp = []
        for i in range(10):
            top_bond = protein.bonds[pp_weak_ordered_idx[i]]
            atom1_string = (top_bond.atom1.res_name + ' ' + 
                            top_bond.atom1.res_num + ' ' + 
                            top_bond.atom1.name)
            atom2_string = (top_bond.atom2.res_name + ' ' + 
                            top_bond.atom2.res_num + ' ' + 
                            top_bond.atom2.name)
            bond_pp = pp_weak[pp_weak_ordered_idx[i]]
            top_weak_bonds_pp.append([atom1_string, atom2_string, bond_pp])

        # Get info on top residues
        pp_residues = pn.edgeedge.residue_pp(protein.residues.keys(), 
                                             weak_bonds, 
                                             pp_weak) 
        pp_residues_sorted = sorted(pp_residues.keys(), 
                                    key=lambda element:pp_residues[element],
                                    reverse=True)
        top_residues_pp = []
        for i in range(10):
            top_residues_pp.append([pp_residues_sorted[i], 
                                    pp_residues[pp_residues_sorted[i]]])

        # Calculate distances of bonds and residues from the source residues
        distance_weak = pn.helpers.distance_between(source_bonds, 
                                                    weak_bonds).min(axis=0)

        import matplotlib
        matplotlib.use('Agg') # Must be before importing matplotlib.pyplot or pylab!
        import matplotlib.pyplot as plt
        
        plt.scatter(distance_weak, pp_weak.values())
        plot_filename = pdb_id + '_bond_pp.svg'
        plt.savefig(settings.BASE_DIR + '/edge/static/edge/' + plot_filename, format='svg')

        return render(request,
                      'results.html',
                      {
                          'pdb_id' : pdb_id,
                          'source_residues' : source_residues,
                          'top_weak_bonds_pp': top_weak_bonds_pp,
                          'top_residues_pp' : top_residues_pp, 
                          'distance_bond_pp_plot_file' : plot_filename,
                      }
        )

