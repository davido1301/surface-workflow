from math import ceil 
from pathlib import Path 

from ase.io import write 
from pymatgen.core import Structure 
from pymatgen.core.surface import SlabGenerator 
from pymatgen.io.ase import AseAtomsAdaptor

from surface_workflow.config import load_config 


def gen_slabs(config_path: str): 
    config = load_config(config_path) 
    structure = Structure.from_file(
            config["structure"]["file"]
            ) 
    miller_index = config["structure"]["miller_index"] 

    layers = config["slab"]["layers"]
    vacuum = config["slab"]["vacuum"] 
    
    min_lateral_size = config["supercell"]["min_lateral_size"] 

    output_dir = Path(config["output"]["directory"])
    output_dir.mkdir(parents=True, exist_ok=True) 

    for n_layers in layers: 
        slabgen = SlabGenerator(
                initial_structure=structure, 
                miller_index=miller_index, 
                min_slab_size=n_layers, 
                min_vacuum_size=vacuum,
                in_unit_planes=True, # NOTE also affects vacuum: size is layers stacked ontop 
                )

        slabs = slabgen.get_slabs() 

        if not slabs: 
            raise ValueError(
                    f"no slabs were generated for {n_layers} planes"
                    ) 

        # only use first termination for now TODO 
        slab = slabs[0].copy() 
        a, b, c = slab.lattice.abc 
        n_a = max(1, ceil(min_lateral_size / a)) 
        n_b = max(1, ceil(min_lateral_size/b)) 
        
        
        slab.make_supercell([n_a, n_b, 1]) 


        # TO ASE ATOMS -> WRITE EXTXYZ 
        atoms = AseAtomsAdaptor.get_atoms(slab) 
        atoms.pbc = [True, True, False] # Vacuum direction not periodic 
        
        output_file = output_dir / f"slab_{n_layers}.extxyz"
        write(output_file, atoms) 

        print(f"Generated: {output_file}") 


