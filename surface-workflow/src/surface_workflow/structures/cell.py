from ase.io import read 
from pathlib import Path 
from surface_workflow.config import load_config 


def generate_cell(config_path): 
    config = load_config(config_path)

    xyz_path = Path(config["output"]["directory"]) / "slab_1.extxyz" 
    output_path = Path(config["cp2k"]["directory"]) / "cell.inc" 

    atoms = read(xyz_path, format="extxyz")

    if atoms.cell.volume < 0.1: 
        raise ValueError(
                f"Cell volume close to zero: {atoms.cell.volume}"
                ) 
    with output_path.open("w") as f:
        for axis, vector in zip("ABC", atoms.cell):
            x, y, z = vector
            f.write(
                f"{axis} [angstrom] "
                f"{x:.12f} {y:.12f} {z:.12f}\n"
            )

    print(f"Cell written to: {output_path}")
    print(f"Cell lengths (Å): {atoms.cell.lengths()}")
    print(f"PBC: {atoms.pbc}")


