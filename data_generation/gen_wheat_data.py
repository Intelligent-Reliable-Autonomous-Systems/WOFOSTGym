"""
Generates data for the wheat experiments by calling the gen_data

Written by: Will Solow, 2024

To run: python3 -m data_generation.gen_wheat_data --start_dir <path to directory>

"""

import subprocess
import os
import argparse

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("--start_dir", type=str, default="experiments/ConstrainedControl/Wheat/", help="Path to data directory")
    args = parser.parse_args()
    directories = [args.start_dir]
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
        #run_str = f"python3 -m data_generation.gen_data --agro-file wheat_agro.yaml --npk.intvn-interval 7 --file-type npz --year-low 2005 --agent-path {p} --agent-type {ag_type} --save-folder experiments/data/wheat/ --data-file wheat_threshold_wk_{ag_type} --env-reward RewardFertilizationThresholdWrapper --max-n 20 --max-p 20 --max-k 20 --max-w 20"
        run_str = f"python3 -m data_generation.gen_data --agro-file pear_agro.yaml --npk.intvn-interval 14  --file-type npz --year-low 2005 --agent-path {p} --agent-type {ag_type} --save-folder experiments/data/pear/ --data-file pear_threshold_wk_{ag_type} --env-reward RewardFertilizationThresholdWrapper --max-n 80 --max-p 80 --max-k 80 --max-w 40 --env-id perennial-lnpkw-v0"
        run_str = run_str.split(" ")
        process = subprocess.Popen(run_str, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        stdout, stderr = process.communicate()
        print("STDOUT:", stdout)
        print("STDERR:", stderr)

if __name__ == "__main__":
    main()
