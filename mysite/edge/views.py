from django.shortcuts import render, redirect
from django.http import HttpResponse
import proteinnetwork as pn
import requests 
from django.conf import settings
from utils.pdb_interact import get_chains, get_hetatms

def home_page(request):
    if request.method == 'POST':
        pdb_id = request.POST['pdb_id']
        request.session['pdb_id'] = pdb_id
        return redirect('/chains')
    else:
        return render(request, 'home.html')

def chain_setup(request):
    if request.method == 'POST':
        request.session['chains'] = request.POST.getlist('chains')
        return redirect('/hetatms')
    else:
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
                
                return render(
                    request, 
                    'chain_setup.html', 
                    {'pdb_id' : pdb_id, 'chain_map' : chain_map}
                )
        else:
            return redirect('/')

def hetatm_setup(request):
    
    if request.method == 'POST':
        hetatms = request.session['hetatms']
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
        chains = request.session.get('chains')

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
            return redirect('/')

def source_setup(request):
    
    if request.method == 'POST':
        residues = request.session.get('residue_list')
        source_residues_idx = request.POST.getlist('residues')
        source_residues = []
        for idx in source_residues_idx:
            source_residues.append(residues[int(idx)])
        request.session['source_residues'] = source_residues

        return redirect('/results')

    else:
        pdb_id = request.session.get('pdb_id')
        chains = request.session.get('chains')
        pdb_file_name = settings.MEDIA_ROOT + '/' + pdb_id + '.pdb'

        protein = pn.molecules.Protein()
        parser = pn.parsing.PDBParser(pdb_file_name)
        parser.parse(protein, strip=('HOH',), chain=chains)
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

def results(request):
    pass
