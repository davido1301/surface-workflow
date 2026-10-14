from pathlib import Path 

from surface_workflow.config import load_config 
from surface_workflow.structures.slab  import gen_slabs 
from surface_workflow.structures.cell import generate_cell
from surface_workflow.io.cp2k.input import generate_new_cp2kinp 

import subprocess 
import os 
import shutil 


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

    # create cp2k.inp before 
    for n_layers in config["slab"]["layers"]: 
        cp2k_conf = Path(config["cp2k"]["directory"]) / f"cp2k_{n_layers}.inp" 
        generate_new_cp2kinp(config_path, structure=f"slab_{n_layers}.extxyz", filename = cp2k_conf) 


    # run cp2k calcs 
    for n_layers in config["slab"]["layers"]:
        run_dir = Path(config["cp2k"]["workdir"]) / f"slab_{n_layers}"
        run_dir.mkdir(parents=True, exist_ok=True) 
        cp2k_conf = Path(config["cp2k"]["directory"]) / f"cp2k_{n_layers}.inp" 
        input_file = Path(cp2k_conf).resolve()
        out_file = Path(run_dir / "cp2k.out").resolve()


        shutil.copy2(
                Path(config["cp2k"]["directory"]) / "cell.inc",
                run_dir / "cell.inc", 
                )
        
        shutil.copy2(
                Path(output_dir) / f"slab_{n_layers}.extxyz",
                run_dir 
                ) 


        # Next SUBPROCESS INTO CP2K and run calculation 
        subprocess.run(
        [
            "srun",
            "cp2k.psmp",
            "-i", str(input_file),
            "-o", str("cp2k.out") 
                        ], 
        cwd=run_dir,
        check=True,
        )

        # plots inside the run dir  // Store energies for conv? 

if __name__ == "__main__": 
     main()
