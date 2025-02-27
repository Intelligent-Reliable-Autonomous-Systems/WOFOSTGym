import subprocess
import os
import time
import sys

#directories = ["data/Sunflower_Single_Cost"]
directories = ["data/Wheat_Threshold_WK_Rand"]
#directories = ["data/Pear_Threshold_WK_Rand"]
pt_files = []

for directory in directories:
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.pt'):
                pt_files.append(os.path.join(root, file))

for i,p in enumerate(pt_files):
    # Get config
    config = p.removesuffix("agent.pt")+"config.yaml"
    files = p.split("/")
    # Get agent type and number
    ag_type = ""
    num = 0
    for f in files:
        if f in ["DQN", "SAC", "PPO", "BC", "GAIL", "AIRL"]:
            ag_type = f
        try: 
            num = int(f)
        except:
            pass
    run_str = f"python3 gen_data.py --agro-file wheat_agro.yaml --npk.intvn-interval 7 --file-type npz --year-low 2005 --agent-path {p} --agent-type {ag_type} --save-folder data/runs/ --data-file wheat_threshold_wk_{ag_type} --env-reward RewardFertilizationThresholdWrapper --max-n 20 --max-p 20 --max-k 20 --max-w 20"
    #run_str = f"python3 gen_data.py --env-id perennial-lnpkw-v0 --agro-file pear_agro.yaml --npk.intvn-interval 14 --file-type npz --lat-low 40 --lat-high 40 --year-low 2005 --agent-path {p} --agent-type {ag_type} --save-folder data/runs/ --data-file pear_threshold_wk_{ag_type} --env-reward RewardFertilizationThresholdWrapper --max-n 80 --max-p 80 --max-k 80 --max-w 40"
    run_str = run_str.split(" ")
    process = subprocess.Popen(run_str, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    stdout, stderr = process.communicate()
    print("STDOUT:", stdout)
    print("STDERR:", stderr)
