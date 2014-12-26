from django.shortcuts import render, redirect
from django.http import HttpResponse
import proteinnetwork as pn
import requests 
from django.conf import settings
from utils.pdb_interact import get_pdb_name 

def home_page(request):
    if request.method == 'POST':
        request.session['pdb_id'] = request.POST['pdb_id']
        return redirect('/proteins/the-only-protein-in-the-world', )
    return render(request, 'home.html')

def protein_setup(request):
    pdb_id = request.session.get('pdb_id')
    if pdb_id:
        pdb_file_name = settings.MEDIA_ROOT + '/' + pdb_id + '.pdb'
        # Retrieve the PDB file from the RSC website and save in media folder
        with open(pdb_file_name, 'w') as f:
            pdb_file_url = 'http://www.rcsb.org/pdb/files/'+ pdb_id + '.pdb'
            pdb_file_text = requests.get(pdb_file_url)
            f.write(pdb_file_text.text)

        pdb_name = get_pdb_name(pdb_file_name)
        
        protein = pn.molecules.Protein()
        parser = pn.parsing.PDBParser(pdb_file_name)
        parser.parse(protein)
        
        return render(
            request, 
            'setup.html', 
            {'pdb_id' : request.session['pdb_id'], 'pdb_name' : pdb_name}
        )
        
    else:
        return redirect('/')
