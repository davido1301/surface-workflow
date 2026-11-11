import subprocess 
from pathlib import Path 

def run_cp2k(cp2k_conf: Path, run_dir: Path, output_name: str = "cp2k.out"): 
    """ Run CP2K via slurm srun""" 

    cp2k_conf = Path(cp2k_conf).resolve() 
    run_dir = Path(run_dir).resolve() 

    if not cp2k_conf.is_file():
        raise FileNotFoundError(
                f"CP2K input file does not exist: {cp2k_conf}"
                ) 
    run_dir.mkdir(parents=True, exist_ok=True) 

    subprocess.run(
        [
            "srun",
            "cp2k.psmp",
            "-i", str(cp2k_conf),
            "-o", output_name,
        ],
        cwd=run_dir,
        check=True,
    )

    return run_dir / output_name
