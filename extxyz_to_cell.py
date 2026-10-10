import argparse
from pathlib import Path

from ase.io import read


def generate_cell(extxyz_path: Path, output_path: Path):
    atoms = read(extxyz_path, format="extxyz")

    if atoms.cell.volume < 1e-6:
        raise ValueError("Invalid cell: volume is zero.")

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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Extract CP2K cell vectors from EXTXYZ."
    )

    parser.add_argument(
        "extxyz",
        type=Path,
        help="Input EXTXYZ structure file"
    )

    parser.add_argument(
        "-o", "--output",
        type=Path,
        default=Path("cell.inc"),
        help="Output CP2K cell file (default: cell.inc)"
    )

    args = parser.parse_args()

    generate_cell(args.extxyz, args.output)

