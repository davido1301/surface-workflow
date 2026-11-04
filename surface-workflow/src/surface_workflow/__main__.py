from pathlib import Path 

from surface_workflow.config import load_config 
from surface_workflow.structures.slab  import gen_slab 
from surface_workflow.structures.cell import generate_cell, generate_basic_cell
from surface_workflow.io.cp2k.input import generate_new_cp2kinp 
from surface_workflow.io.cp2k.output import collect_energies
from surface_workflow.analysis.plotting import plot_energy_steps_scf, plot_convergence 
from surface_workflow.io.io import write_atoms 
from surface_workflow.structures.precursors import adsorb_molecule



import subprocess 
import os 
import shutil


def main(): 
    config_path = Path("configs/slab.yaml")
    config = load_config(config_path) 

    output_dir = Path(config["output"]["directory"])
    output_dir.mkdir(parents=True, exist_ok=True) 


    precursor_xyz = config["precursors"]["file"] 
    conv_criteria = config["slab"]["conv_criteria"]

    energies = [] 
    
    ## AD MOLECULE ENERGY 
    run_dir = Path(config["cp2k"]["workdir"]) / "ads_mol"
    run_dir.mkdir(parents=True, exist_ok=True) 
    cp2k_conf = run_dir / "cp2k_admol.inp"
    out_file = run_dir / "cp2k.out" 

    shutil.copy(precursor_xyz, run_dir) 

    generate_basic_cell(config["precursors"]["name"], run_dir=run_dir, conf_dir=config["cp2k"]["directory"])
    generate_new_cp2kinp(config_path, structure=config["precursors"]["name"], filename=cp2k_conf) 
    subprocess.run(
    [
        "srun",
        "cp2k.psmp",
        "-i", str(cp2k_conf.resolve()),
        "-o", str("cp2k.out")
        ], 
    cwd=run_dir,
    check=True, 
    ) 
    
    output = collect_energies(out_file) 
    ads_mol_e = output.final_energy 
    print(ads_mol_e, "ADS MOL E " ) 
    exit()
    


    # run cp2k calcs 
    for n_layers in range(1, config["slab"]["max_layers"]):
        run_dir = Path(config["cp2k"]["workdir"]) / f"slab_{n_layers}"
        cp2k_conf = run_dir / f"cp2k_{n_layers}.inp" 
        run_dir.mkdir(parents=True, exist_ok=True) 
        xyz_file = Path(run_dir / f"slab_{n_layers}.extxyz") 

        out_file = Path(run_dir / "cp2k.out").resolve()
        input_file = Path(cp2k_conf).resolve()
        bond_atom = config["precursors"]["bond_atom"]


        slab = gen_slab(config_path, n_layers, run_dir) 
        slab = adsorb_molecule(slab, precursor_xyz, bond_atom)  
        write_atoms(slab,xyz_file) 

        continue
        generate_cell(f"slab_{n_layers}.extxyz", run_dir = run_dir, conf_dir= config["cp2k"]["directory"] ) 
        generate_new_cp2kinp(config_path, structure=f"slab_{n_layers}.extxyz", filename =cp2k_conf) 
        
        # SUBPROCESS INTO CP2K and run calculation 
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
        output = collect_energies(out_file)
        energies.append(output.final_energy / float(output.data["atoms"][0][0])) 
        plot_energy_steps_scf(output.data["electronic_steps"][0], run_dir / f"scf_{n_layers}_steps.png") 

    ### Plot convergence 

        if len(energies) > 1: 
            delta = abs(energies[-1] - energies[-2])
            if delta < conv_criteria: 
                print("Converged?!")
                break 


    plot_convergence(energies, output_dir / "convergence_plots.png") 


    
        
if __name__ == "__main__": 
     main()
