from django.shortcuts import render, redirect
from django.http import HttpResponse
#import proteinnetwork as pn
import requests 
from django.conf import settings
from utils.pdb_interact import get_pdb_name 

def home_page(request):
    if request.method == 'POST':
        pdb_id = request.POST['pdb_id']
        request.session['pdb_id'] = pdb_id
        return redirect('/proteins/' + pdb_id + '/chains')
    return render(request, 'home.html')

def chain_setup(request):
    pdb_id = request.session.get('pdb_id')
    if pdb_id:
        pdb_file_name = settings.MEDIA_ROOT + '/' + pdb_id + '.pdb'
        
        # Retrieve the PDB file from the RSC website and save in media folder
        with open(pdb_file_name, 'w') as f:
            pdb_file_url = 'http://www.rcsb.org/pdb/files/'+ pdb_id + '.pdb'
            pdb_file_text = requests.get(pdb_file_url)
            f.write(pdb_file_text.text)

        # Extract name of molecules in the PDB file    
        chain_map = get_pdb_name(pdb_file_name)

        return render(
            request, 
            'chain_setup.html', 
            {'pdb_id' : pdb_id, 'chain_map' : chain_map}
        )
        
    else:
        return redirect('/')
