from django.shortcuts import render, redirect
from django.http import HttpResponse
import proteinnetwork as pn
import requests 
from django.conf import settings
from utils.pdb_interact import get_chains, get_hetatms
from proteinnetwork.molecules import AtomList, BondList
import pandas as pd

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
        pdb_file_name = settings.MEDIA_ROOT + '/' + pdb_id + '.pdb'
        chains = request.session.get('all_chains')
        removed_chains = request.session.get('removed_chains', [])

        protein = pn.molecules.Protein()
        parser = pn.parsing.PDBParser(pdb_file_name)
        parser.parse(
            protein, 
            strip={
                'res_name' : ['HOH'], 
                'chain' : removed_chains
            }
        )
        final_pdb_name = protein.pdb_id.split('/')[-1]

        if pdb_id and chains:
            pdb_file_name = settings.MEDIA_ROOT + '/' + pdb_id + '.pdb'
            hetatms = get_hetatms(pdb_file_name, chains)
            request.session['hetatms'] = hetatms

            return render(
                request, 
                'hetatm_setup.html', 
                {'pdb_id' : pdb_id, 'hetatms' : hetatms, 'pdb_file' : final_pdb_name}
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

        final_pdb_name = protein.pdb_id.split('/')[-1]

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
                'pdb_file' : final_pdb_name,
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

        source_residues_list = request.session['source_residues']
        source_residues = []
        for residue in source_residues_list:
            source_residues.append(tuple(residue))

        # Calculate perturbation propensities
        results = pn.edgeedge.edgeedge_run(protein, source_residues)
        results.calculate_bond_perturbation_propensities()
        results.bond_results.sort(columns=["pp"], ascending=[0], inplace=True)
        top_weak_bonds_pp = zip(results.bond_results[0:10]['bond_name'],
                                results.bond_results[0:10]['pp'])

        results.calculate_residue_perturbation_propensities()
        results.residue_results.sort(columns=['pp'], ascending=[0], inplace=True)
        top_residues_pp = zip(results.residue_results[0:10]['residue_name'],
                              results.residue_results[0:10]['pp'])
        
        bond_results_file = pdb_id + "_bond_results.csv"
        results.bond_results_to_csv(name=settings.BASE_DIR + '/edge/static/edge/' + 
                                    bond_results_file)

        residue_results_file = pdb_id + "_residue_results.csv"
        results.residue_results_to_csv(name=settings.BASE_DIR + '/edge/static/edge/' + 
                                    residue_results_file)
        return render(request,
                      'results.html',
                      {
                          'pdb_id' : pdb_id,
                          'source_residues' : source_residues,
                          'top_weak_bonds_pp': top_weak_bonds_pp,
                          'top_residues_pp' : top_residues_pp, 
                          'distance_bond_pp_file' : bond_results_file,
                          'distance_residue_pp_file' : residue_results_file,
                      }
        )

