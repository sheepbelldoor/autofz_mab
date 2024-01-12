#!/bin/bash
echo "" > /proc/sys/kernel/core_pattern
echo 0 > /proc/sys/kernel/core_uses_pid
echo performance | tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor
echo 0 > /proc/sys/kernel/yama/ptrace_scope
echo 1 > /proc/sys/kernel/sched_child_runs_first
echo 0 > /proc/sys/kernel/randomize_va_space

# get container id
CPU_CGROUP_PATH=$(cat /proc/1/cpuset)
CID=$(basename ${CPU_CGROUP_PATH})

set -x
# create subgroup
cgcreate -t autofz -a autofz -g cpu:/autofz

# gdb and pwndbg for debug
apt-get install -y gdb
cd ~
wget https://github.com/pwndbg/pwndbg/releases/download/2023.07.17-pkgs/pwndbg_2023.07.17_amd64.tar.gz
tar -v -xf ./pwndbg_2023.07.17_amd64.tar.gz
cp -r /d/p/aflasan .
rm -rf pwndbg_2023.07.17_amd64.tar.gz
mkdir crashes

# zsh
apt-get install -y zsh
sh -c "$(curl -fsSL https://raw.githubusercontent.com/robbyrussell/oh-my-zsh/master/tools/install.sh)"

