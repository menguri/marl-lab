# scripts/run_from_yaml.py (요약)
import yaml, sys, subprocess, os, json
from pathlib import Path

def to_with_args(d):
    out = []
    for k,v in d.items():
        out.append(f'{k}="{v}"' if isinstance(v,str) else f"{k}={v}")
    return out

if __name__ == "__main__":
    cfg_path = sys.argv[1]
    cfg = yaml.safe_load(open(cfg_path))
    cmd = ["python", "scripts/run_once.py", cfg["algo"], cfg["env"]]
    os.environ["EXP_CONFIG"] = json.dumps(cfg)   # 필요 시 내부에 전달
    # run_once.py를 algo/env/with_args CLI로 받도록 조금만 확장해도 OK
