from django.shortcuts import render, redirect
from django.http import HttpResponse
#import proteinnetwork as pn
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
        pass

    else:
        pdb_id = request.session.get('pdb_id')
        chains = request.session.get('chains')

        if pdb_id and chains:
            pdb_file_name = settings.MEDIA_ROOT + '/' + pdb_id + '.pdb'
            hetatms = get_hetatms(pdb_file_name)
            request.session['hetatms'] = hetatms

            return render(
                request, 
                'hetatm_setup.html', 
                {'pdb_id' : pdb_id, 'hetatms' : hetatms}
            )
        
        else:
            return redirect('/')
