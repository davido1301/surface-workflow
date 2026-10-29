from math import ceil 
from pathlib import Path 

from ase.io import write 
from pymatgen.core import Structure 
from pymatgen.core.surface import SlabGenerator 
from pymatgen.io.ase import AseAtomsAdaptor

from surface_workflow.config import load_config 

def reconstruct_2x1(): 
    pass 

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

    # only use first termination for now TODO 
    slab = slabs[0].copy() 
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


