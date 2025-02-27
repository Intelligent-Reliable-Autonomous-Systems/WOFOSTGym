import subprocess
import os
import time

#directories = ["data/Sunflower_Single_Cost"]
directories = ["data/Sunflower_Multi_Cost"]
pt_files = []

for directory in directories:
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.pt'):
                pt_files.append(os.path.join(root, file))

for p in pt_files:
    # Get config
    config = p.removesuffix("agent.pt")+"config.yaml"
    files = p.split("/")
    # Get agent type and number
    ag_type = ""
    num = 0
    for f in files:
        if f in ["DQN", "SAC", "PPO"]:
            ag_type = f
        try: 
            num = int(f)
        except:
            pass
    run_str = f"python3 gen_data.py --agro-file sunflower_agro.yaml --env-id multi-lnpkw-v0 --file-type npz --year-low 2005 --lat-low 40 --lat-high 40 --agent-path {p} --agent-type {ag_type} --save-folder data/runs/ --data-file sunflower_multi_{ag_type}_{num} --config-fpath {config}"
    run_str = run_str.split(" ")
    process = subprocess.Popen(run_str, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    stdout, stderr = process.communicate()
    print("STDOUT:", stdout)
    print("STDERR:", stderr)