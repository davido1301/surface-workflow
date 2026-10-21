from ase.io import read 
from pathlib import Path 
from surface_workflow.config import load_config 


def generate_cell(filename, run_dir, conf_dir): 

    xyz_path = Path(run_dir / filename)
    output_path = Path(conf_dir) / "cell.inc" 

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


