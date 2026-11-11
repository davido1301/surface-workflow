from pathlib import Path 

from surface_workflow.config import load_config 
from surface_workflow.structures.slab  import gen_slab 
from surface_workflow.structures.cell import generate_cell, generate_basic_cell
from surface_workflow.io.cp2k.input import generate_new_cp2kinp 
from surface_workflow.io.cp2k.output import collect_energies, extract_opt_structure
from surface_workflow.io.cp2k.cp2k import run_cp2k
from surface_workflow.analysis.plotting import plot_energy_steps_scf, plot_convergence 
from surface_workflow.io.io import write_atoms 
from surface_workflow.structures.precursors import adsorb_molecule
from surface_workflow.structures.isolated import make_isolated_atoms



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

    ENERGIES_SLAB = [] 
    ENERGIES_SLAB_ADS = [] 

    ## AD MOLECULE ENERGY 
    run_dir = Path(config["cp2k"]["workdir"]) / "ads_mol"
    run_dir.mkdir(parents=True, exist_ok=True) 
    cp2k_conf = run_dir / "cp2k_admol.inp"

    shutil.copy(precursor_xyz, run_dir) 

    generate_basic_cell(config["precursors"]["name"], run_dir=run_dir)

    generate_new_cp2kinp(config_path, structure=config["precursors"]["name"], filename=cp2k_conf, run_type="GEO_OPT")
    run_cp2k(cp2k_conf, run_dir)
    opt_structure = extract_opt_structure(config["precursors"]["name"], output_dir = run_dir).name
    print(opt_structure, "here is opt_structure.name?")

    generate_new_cp2kinp(config_path, structure=opt_structure, filename=cp2k_conf) 
    output = run_cp2k(cp2k_conf, run_dir)
    E_OUT = collect_energies(output) 
    MOLECULE_ISOLATED_ENERGY = E_OUT.final_energy 
    print(MOLECULE_ISOLATED_ENERGY, "Isolated Energy") 
    exit()
    #### 


    # run cp2k calcs 
    for n_layers in range(1, config["slab"]["max_layers"]):

        run_dir = Path(config["cp2k"]["workdir"]) / f"slab_{n_layers}"
        cp2k_conf = run_dir / f"cp2k_{n_layers}.inp" 
        run_dir.mkdir(parents=True, exist_ok=True) 

        xyz_file = Path(run_dir / f"slab_{n_layers}.extxyz") 
        ads_xyz_file = Path(run_dir / f"ads_slab_{n_layers}.extxyz") 
        bond_atom = config["precursors"]["bond_atom"]

        out_file = Path(run_dir / "cp2k.out").resolve()
        input_file = Path(cp2k_conf).resolve()

        # Compute energy for slab without ads. molecule
        slab = gen_slab(config_path, n_layers, run_dir) 
        continue
        write_atoms(slab,xyz_file) 
        generate_cell(f"slab_{n_layers}.extxyz", run_dir = run_dir, conf_dir= config["cp2k"]["directory"] ) 
        generate_new_cp2kinp(config_path, structure=f"slab_{n_layers}.extxyz", filename =cp2k_conf) 
        
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
        output = collect_energies(out_file)
        ENERGIES_SLAB.append(output.final_energy) 
        plot_energy_steps_scf(output.data["electronic_steps"][0], run_dir / f"scf_{n_layers}_steps.png") 

        # Compute energy for slab with ads. molecule
        slab = adsorb_molecule(slab, precursor_xyz, bond_atom)  
        write_atoms(slab,ads_xyz_file) 
        generate_cell(f"slab_{n_layers}.extxyz", run_dir = run_dir, conf_dir= config["cp2k"]["directory"] ) 
        generate_new_cp2kinp(config_path, structure=f"ads_slab_{n_layers}.extxyz", filename =cp2k_conf) 
        
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
        output = collect_energies(out_file)
        ENERGIES_SLAB_ADS.append(output.final_energy) 
        plot_energy_steps_scf(output.data["electronic_steps"][0], run_dir / f"scf_ads_{n_layers}_steps.png") 


        
        # KONV CRIT
        if len(ENERGIES_SLAB) > 1 and len(ENERGIES_SLAB_ADS) > 1: 
            delta = (ENERGIES_SLAB_ADS[-2] - ENERGIES_SLAB[-2] - MOLECULE_ISOLATED_ENERGY) - (ENERGIES_SLAB_ADS[-1] - ENERGIES_SLAB[-1] - MOLECULE_ISOLATED_ENERGY) 
            if abs(delta) < conv_criteria: 
                print(f"Converged?! {delta:.5f}")
                break 

    
    ## isolated atoms 
    dic_E0s = [] 
    run_dir = Path(config["E0s"]["run_dir"])
    make_isolated_atoms(slab, run_dir=run_dir)
    for file in run_dir.glob("*.extxyz"):
        generate_basic_cell(file.name, run_dir=config["E0s"]["run_dir"])
        generate_new_cp2kinp(config_path, structure=file.name, filename=run_dir / f"{file.stem}.inp", isolated=True) 
        subprocess.run(
            [
                "srun",
                "cp2k.psmp",
                "-i", str(f"{file.stem}.inp"),
                "-o", str(f"{file.stem}_cp2k.out") 
            ], 
            cwd=run_dir,
            check=True,
            )
        energy0 = collect_energies(run_dir / f"{file.stem}_cp2k.out") 
        dic_E0s.append((file.stem, energy0.final_energy))
    
    print(dic_E0s, "HERE E0s!!!!!!!!!!!")
    plot_convergence(ENERGIES_SLAB, output_dir / "convergence_plots.png") 
    plot_convergence(ENERGIES_SLAB_ADS, output_dir / "convergence_plots_ads.png") 

     

        
if __name__ == "__main__": 
     main()
