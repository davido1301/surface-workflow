from pymatgen.io.cp2k.outputs import Cp2kOutput 
from pathlib import Path
from ase.io import read, write
import numpy as np

def collect_energies(cp2koutput_file): 
    output = Cp2kOutput(cp2koutput_file) 

    # COLLECT ENERGIES 
    output.parse_scf_opt() 
    output.parse_energies() 
    # COLLECT N ATOMS 
    output.parse_total_numbers() 

    return output 


def extract_opt_structure(structure, output_dir): 
    """ Take the last frame of geo_opt and print it out.""" 
    structure = Path(structure) 
    output_dir = Path(output_dir) 
    trajectory = output_dir / f"{structure.stem}-pos-1.xyz" 
    optimized = output_dir / f"{structure.stem}_optimized.extxyz"
    if not trajectory.is_file(): 
        raise FileNotFoundError(f"CP2k trajectory not found: {trajectory}") 
    atoms = read(trajectory, index=-1, format="extxyz")

    original_atoms = read(output_dir / structure.name, format="extxyz") 
    atoms.set_cell(original_atoms.cell) 
    atoms.set_pbc(original_atoms.pbc) 

    print(atoms.cell, "atoms cell") 
    print(atoms.pbc, "atoms pbc") 

    # Save final geometry
    write(optimized, atoms, format="extxyz")
    
    return optimized
