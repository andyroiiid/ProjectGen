# Copyright 2025 Andrew Huang. All Rights Reserved.

import subprocess
from argparse import ArgumentParser
from pathlib import Path
from os import environ

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument("-r", "--release", action="store_true")
    args = parser.parse_args()

    vswhere_path = Path(environ["ProgramFiles(x86)"]) / "Microsoft Visual Studio" / "Installer" / "vswhere.exe"
    vswhere_args = [
        vswhere_path,
        "-latest",
        "-requires",
        "Microsoft.Component.MSBuild",
        "-find",
        "MSBuild/**/Bin/MSBuild.exe"
    ]
    vswhere_output = subprocess.run(vswhere_args, capture_output=True, check=True, text=True).stdout.strip()
    print(f"Found msbuild at {vswhere_output}")

    msbuild_path = Path(vswhere_output)
    msbuild_args = [
        msbuild_path,
        "-t:Build",
        f"-p:Configuration={"Release" if args.release else "Debug"}",
    ]
    subprocess.run(msbuild_args)
