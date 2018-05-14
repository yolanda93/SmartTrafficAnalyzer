#!/usr/bin/env bash

VENV="venv"
CPU_LOC="https://storage.googleapis.com/tensorflow/linux/cpu/tensorflow-0.5.0-cp27-none-linux_x86_64.whl"
GPU_LOC="https://storage.googleapis.com/tensorflow/linux/gpu/tensorflow-0.5.0-cp27-none-linux_x86_64.whl"
GPU=0

function usage
{
    echo "Usage: sudo setup_tensorflow [--gpu]"
    echo ""
    echo "Help: setup_tensorflow --help"
}

if [ $# -gt 0 ]; then
    case $1 in
            -g | --gpu )            shift
                                    GPU=1
                                    ;;
            -h | --help )           usage
                                    exit
                                    ;;
            * )                     usage
                                    exit 1
        esac
        shift
fi
LOC="$CPU_LOC"
if [ "$GPU" -eq 1 ]; then
    LOC="$GPU_LOC"
fi

sudo apt-get install python-pip python-dev python-virtualenv

virtualenv --system-site-packages "$VENV"
source "$VENV/bin/activate"
#pip install -r requirements.txt
pip install --upgrade "$LOC"
