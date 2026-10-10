from pathlib import Path 
import yaml 

def load_config(path: Str | Path) -> dict: 
    path = Path(path) 
    with path.open("r") as f: 
        config = yaml.safe_load(f) 
    
    required_sections = [
            "structure", 
            "slab",
            "supercell", 
            "output"
            ] 

    for section in required_sections: 
        if section not in config: 
            raise ValueError(
                    f"Missing configuration section: {section}"
                    )
    return config
