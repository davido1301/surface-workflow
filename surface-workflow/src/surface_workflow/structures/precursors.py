from pymatgen.core import Structure, Molecule
from pymatgen.core.surface import SlabGenerator 
import re
import numpy as np
from math import ceil
from ase.io import write
from pymatgen.io.ase import AseAtomsAdaptor
from scipy.spatial.transform import Rotation
import random 
from itertools import combinations



def insert_dma(slab, molecule_path, bond_atom, target_distance=2.45): 
    """ Replace one atom on top and insert DMA in place of a random surface atom in a given distance, 
    !!! For now also rotate it a bit so it fits a bit more nicely. Needs to be overworked""" 
    max_z = max(site.coords[2] for site in slab) 
    atoms_on_top = [] # Scanning for H atoms  
    for z,i in enumerate(slab): 
        if abs(i.coords[2] - max_z) < 0.1 and str(i.specie) == "H": 
            atoms_on_top.append([i, z]) 

    adsorb_molecule = Molecule.from_file(molecule_path)  # change for config 

    site = random.choice(atoms_on_top) 
    slab.remove_sites([site[1]])
    
    for i in range(0, len(adsorb_molecule)): 
                      if str(adsorb_molecule[i].specie) == bond_atom: 
                          bond_Al = adsorb_molecule[i].specie
                          bond_idx = i 

    site = site[0] 
    neighbors = slab.get_neighbors(site=site, r=1.5) # for H atom 
    distance_vec = site.coords - neighbors[0].coords 
    distance_vec = np.linalg.norm(distance_vec) 

    bond_atom_pos = distance_vec * target_distance + neighbors[0].coords
    dma = adsorb_molecule.copy() 

    # Rotation hardcoded for now 
    dma.rotate_sites(
            indices=list(range(len(dma))), 
            theta=np.deg2rad(-60),
            axis=[1,1,0],
            anchor=dma[bond_idx].coords 
        )

    for i in range(0, len(dma)): 
        slab.append(str(dma[i].species), bond_atom_pos + dma[i].coords - dma[bond_idx].coords, coords_are_cartesian=True) 
    

    return slab 


def adsorb_molecule(slab, molecule_path,bond_atom, target_dist = 2.5): 
    """ Place precursor molecule ontop of surface randomly in target distance""" 
    max_z = max(site.coords[2] for site in slab) 
    atoms_on_top = [] 
    for z,i in enumerate(slab): 
        if abs(i.coords[2] - max_z) < 0.1 and str(i.specie) == "H": 
            atoms_on_top.append([i,z])

    adsorb_molecule = Molecule.from_file(molecule_path) 
    
    for z,i in enumerate(adsorb_molecule): 
        if str(i.specie) == bond_atom: 
            bond_idx = z 
            break
    
    site = random.choice(atoms_on_top) 
    bond_atom_pos = site[0].coords + np.asarray([0, 0, target_dist])
    
    for i in range(0, len(adsorb_molecule)): 
        slab.append(str(adsorb_molecule[i].species), bond_atom_pos + adsorb_molecule[i].coords - adsorb_molecule[bond_idx].coords, coords_are_cartesian=True) 
    return slab 
    
