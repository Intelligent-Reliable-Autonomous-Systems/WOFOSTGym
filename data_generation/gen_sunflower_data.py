"""
Generates data for the sunflower experiments by calling the gen_data

Written by: Will Solow, 2024

To run: python3 -m data_generation.gen_sunflower_data --start_dir <path to directory>

"""

import subprocess
import os
import argparse


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--start_dir",
        type=str,
        default="experiments/ConstrainedMultiFarm/SunflowerMulti/",
        help="Path to data directory",
    )
    args = parser.parse_args()

    directories = [args.start_dir]
    pt_files = []

    for directory in directories:
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith(".pt"):
                    pt_files.append(os.path.join(root, file))

    for p in pt_files:
        # Get config
        config = p.removesuffix("agent.pt") + "config.yaml"
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
        run_str = f"python3 -m data_generation.gen_data --agro-file sunflower_agro.yaml --env-id multi-lnpkw-v0 --file-type npz --year-low 2005 --lat-low 40 --lat-high 40 --agent-path {p} --agent-type {ag_type} --save-folder experiments/data/sunflower/ --data-file sunflower_multi_{ag_type}_{num} --config-fpath {config}"
        run_str = run_str.split(" ")
        process = subprocess.Popen(run_str, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        stdout, stderr = process.communicate()
        print("STDOUT:", stdout)
        print("STDERR:", stderr)


if __name__ == "__main__":
    main()
