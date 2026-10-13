from pathlib import Path 

from surface_workflow.config import load_config 
from surface_workflow.structures.slab  import gen_slabs 
from surface_workflow.structures.cell import generate_cell
from surface_workflow.io.cp2k.input import generate_new_cp2kinp 

import subprocess 
import os 

def main(): 
    config_path = Path("configs/slab.yaml")
    config = load_config(config_path) 

    cp2k_conf = Path(config["cp2k"]["directory"]) / "cp2k.inp" 
    output_dir = Path(config["output"]["directory"]) 

    # Generate candidate slabs
    gen_slabs(config_path)
    
    # Generate cell for CP2K 
    generate_cell(config_path) 

    # LOOP create INPUT CP2K -> SUBPROCESS OUTPUT -> COLLECT ENERGIES PLOT CONV 
    # BATCHED FOR NOW 

    for n_layers in range(1, len(config["slab"]["layers"])+1):
        generate_new_cp2kinp(config_path, structure= output_dir / f"slab_{n_layers}.extxyz", filename = cp2k_conf) 
        # Next SUBPROCESS INTO CP2K and run calculation 
        subprocess.run(
            ["cp2k.psmp", "-i", cp2k_conf, "-o", Path(config["cp2k"]["workdir"]) / f"slab_{n_layers}.out"],
            check=True
        )

if __name__ == "__main__": 
     main()
