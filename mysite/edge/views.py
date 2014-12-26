from django.shortcuts import render, redirect
from django.http import HttpResponse
#import proteinnetwork as pn
import requests 
from django.conf import settings

def home_page(request):
    if request.method == 'POST':
        request.session['pdb_id'] = request.POST['pdb_id']
        return redirect('/proteins/the-only-protein-in-the-world', )
    return render(request, 'home.html')

def protein_setup(request):
    pdb_id = request.session.get('pdb_id')
    if pdb_id:
        file_name = settings.MEDIA_ROOT + '/' + pdb_id + '.pdb'
        # Retrieve the PDB file from the RSC website and save in media folder
        with open(file_name, 'w') as f:
            f.write(requests.get('http://www.rcsb.org/pdb/files/'+ pdb_id + '.pdb').text)

        #protein = pn.molecules.Protein()
        #parser = pn.parsing.PDBparser(file_name)
        #parser.parsePDB(protein)
        
        return render(request, 'setup.html', {'pdb_id' : request.session['pdb_id']})
    else:
        return redirect('/')
