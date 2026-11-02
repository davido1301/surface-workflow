from math import ceil 
from pathlib import Path 

from ase.io import write 
from pymatgen.core import Structure 
from pymatgen.core.surface import SlabGenerator 
from pymatgen.io.ase import AseAtomsAdaptor

from surface_workflow.config import load_config 
import numpy as np 
from itertools import combinations 

def reconstruct_2x1(config_path, slab): 
    """ CREATE A 2x1 RECONSTRUCTION 
    ON TOP OF THE SURFACE 
    TESTED ON Si ( 1 0 0 ) WITH H TERMINATION """ 
    config = load_config(config_path) 
    h_dist = config["reconstruction"]["h_dist"] 
    target_dist = config["reconstruction"]["target_dist"] 
    cutoff = config["reconstruction"]["cutoff"]

    reconstructed = slab.copy() 
    a, b, c = reconstructed.lattice.matrix 
    normal = np.cross(a,b) 
    normal /= np.linalg.norm(normal) 
    height = reconstructed.cart_coords @ normal 
    max_height = height.max() 

    center_indices, neighbor_indices, offsets, distances = ( 
        reconstructed.get_neighbor_list(r=cutoff)
        ) 
    CN = np.bincount(center_indices, minlength = len(slab)) 
    
    candidates = [] 
    for i, cn in enumerate(CN): 
        if abs(reconstructed.cart_coords[i][2] - max_height) < 0.2: 
            candidates.append(i) 

    dimers = [] 
    for i, j in combinations(candidates, 2): 
        distance = reconstructed.get_distance(i, j) 
        dimers.append((distance, i, j)) 
    dimers.sort() # greedy search
    used_atoms = set() 
    dimer_pairs = [] 

    for distance, i, j in dimers: 
        if i in used_atoms or j in used_atoms: 
            continue 
        dimer_pairs.append((i,j)) 
        used_atoms.update([i,j]) 

    for i, j in dimer_pairs: 
        distance, image = reconstructed[i].distance_and_image(reconstructed[j])
        r_i = reconstructed[i].coords 
        r_j = reconstructed[j].coords 
        r_j_image = r_j + np.dot(image, reconstructed.lattice.matrix) 

        direction = (r_j_image - r_i) / distance 
        shift = (distance - target_dist) / 2 

        reconstructed.translate_sites(
                [i], shift * direction, frac_coords=False
                ) 
        reconstructed.translate_sites(
                [j], -shift*direction, frac_coords=False
                )
        # SATURATION OF DANG BONDS ON RECONSTRUCTED AREA 
    H_positions = []
    for i in list(used_atoms): 
        site = reconstructed[i] 
        site_coord = site.coords 
        neighbors = reconstructed.get_neighbors(site=site, r=cutoff) 

        H_vec = np.zeros(3) 

        for neighbor in neighbors: 
            dist_vec = site_coord - neighbor.coords 
            dist_vec /= np.linalg.norm(dist_vec) 
            H_vec += dist_vec 

        H_vec /= np.linalg.norm(H_vec) 
        H_pos = H_vec * h_dist + site_coord 
        H_positions.append(H_pos) 

    for pos in H_positions: 
        reconstructed.append("H", pos, coords_are_cartesian=True) 

    return reconstructed 


def sature_tetraedic_2h(config_path, slab): 
    """ Saturate the bottom layer in a tetraedic coordination 
    ATM: also move the slab a little so it does not look awkward
    Tested on Si( 1 0 0 ) """ 
    config = load_config(config_path) 
    h_dist = config["reconstruction"]["h_dist"] 
    cutoff = config["reconstruction"]["cutoff"] 

    center_indices, neighbor_indices, offsets, distances = (
            slab.get_neighbor_list(r=cutoff) 
        )

    CN = np.bincount(center_indices, minlength = len(slab)) 
    candidates = [] 
    for i, cn in enumerate(CN): 
        if cn == 2 and slab.cart_coords[i][2] < 1: # CN must be 2 / only works if slab is centered at the bottom atm 
            candidates.append(i) 

    hydrogen_pos = [] 
    for i in candidates: 
        site = slab[i]
        site_coord = site.coords 
        neighbors = slab.get_neighbors(site=site, r=cutoff) 
        
        u_vec = neighbors[0].coords - site_coord 
        v_vec = neighbors[1].coords - site_coord 

        u_vec /= np.linalg.norm(u_vec) 
        v_vec /= np.linalg.norm(v_vec) 
                    
        normal = np.cross(u_vec, v_vec) 
        normal /= np.linalg.norm(normal) 
    
        cos_angle = np.dot(u_vec, v_vec) 

        plane_vec = u_vec + v_vec 
        plane_vec /= np.linalg.norm(plane_vec) 
    
        theta = np.deg2rad(109.47) 
        
        # d_vec = - p*plane + q * normal -> Vec to H atom 
        p = -(np.cos(theta)/np.cos(np.arccos(cos_angle)/2)) 

        d_vec = - p*plane_vec + (np.sqrt(1-p**2))*normal 
        e_vec = - p*plane_vec - (np.sqrt(1-p**2))*normal 

        h1_pos = d_vec * h_dist + site_coord 
        h2_pos = e_vec * h_dist + site_coord 

        hydrogen_pos.append(h1_pos) 
        hydrogen_pos.append(h2_pos) 

    for _ in hydrogen_pos: 
        slab.append("H", _, coords_are_cartesian=True) 

    slab.translate_sites(
            indices=range(len(slab)),
            vector=[0,0,h_dist],
            frac_coords=False
        )
    return slab 
    
    

    

def gen_slab(config_path: str, n_layer: int, run_dir): 
    config = load_config(config_path) 
    structure = Structure.from_file(
            config["structure"]["file"]
            ) 
    miller_index = config["structure"]["miller_index"] 
    vacuum = config["slab"]["vacuum"] 
    
    min_lateral_size = config["supercell"]["min_lateral_size"] 

    slabgen = SlabGenerator(
        initial_structure=structure, 
        miller_index=miller_index, 
        min_slab_size=n_layer, 
        min_vacuum_size=vacuum,
        in_unit_planes=True, # NOTE also affects vacuum: size is layers stacked ontop 
        )

    slabs = slabgen.get_slabs() 

    if not slabs: 
        raise ValueError(
                f"no slabs were generated for {n_layer} planes"
                ) 

    slab = slabs[0].copy()
    
    if config["reconstruction"]["2x1"]: 
        slab.make_supercell([2,2,1]) # for 2x1 reconstruction
        slab = reconstruct_2x1(config_path, slab) 
        slab = sature_tetraedic_2h(config_path, slab) 


    a, b, c = slab.lattice.abc 
    n_a = max(1, ceil(min_lateral_size / a)) 
    n_b = max(1, ceil(min_lateral_size/b)) 
    slab.make_supercell([n_a, n_b, 1]) 
    
    if config["slab"]["center"]: 
        # CENTER THE SLAB along Z 
        z_coords = slab.cart_coords[:,2] 
        slab_center = (z_coords.min() + z_coords.max()) / 2 
        cell_center = slab.lattice.matrix[2,2] / 2 
        dz = cell_center - slab_center 

        slab.translate_sites(
                indices=range(len(slab)), 
                vector=[0,0,dz], 
                frac_coords=False, 
                to_unit_cell=False
                ) 
    
    # TO ASE ATOMS -> WRITE EXTXYZ 
    atoms = AseAtomsAdaptor.get_atoms(slab) 
    atoms.pbc = [True, True, False] # Vacuum direction not periodic 
        
    output_file = run_dir / f"slab_{n_layer}.extxyz"
    write(output_file, atoms) 

    print(f"Generated: {output_file}") 


