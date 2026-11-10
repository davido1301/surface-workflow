from ase.io import write 
from surface_workflow.structures.cell import generate_basic_cell 
import numpy as np
from pathlib import Path 
from ase import Atoms

def make_isolated_atoms(slab, run_dir, box_length=10): 

    run_dir = Path(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True) 
    elems = [] 

    for i in range(0, len(slab)): 
        elems.append(slab[i].specie.symbol) 
    unique = np.unique(elems) 

    for _ in unique: 
        symbol = str(_) 
        filename = f"{symbol}.extxyz" 
        atoms = Atoms(
                symbols = [symbol],
                positions = [[box_length/2]*3],
                pbc = False
                )
        atoms.write(run_dir / filename)  
