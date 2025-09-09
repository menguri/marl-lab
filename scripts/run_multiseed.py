# scripts/run_multiseed.py
import subprocess, sys

SEEDS = [1,2,3,4,5]

def main():
    for s in SEEDS:
        cmd = ["python", "scripts/run_once.py"]
        # run_once.py 내부에서 seed를 with_args로 받게 바꾸고 싶다면 인자 전달해도 됨
        env = dict(**os.environ)
        env["PYTHONHASHSEED"] = str(s)
        print(f"[seed={s}]")
        subprocess.run(cmd, check=True, env=env)

if __name__ == "__main__":
    import os; main()
