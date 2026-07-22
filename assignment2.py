#!/usr/bin/env python3

'''
OPS445 Assignment 2 - Fall 2025
Program: assignment2.py 
Author: "jahmmed"
The python code in this file is original work written by
"jahmmed". No code in this file is copied from any other source 
except those provided by the course instructor, including any person, 
textbook, or on-line resource. I have not shared this python script 
with anyone or anything except for submission for grading.  
I understand that the Academic Honesty Policy will be enforced and 
violators will be reported and appropriate action will be taken.

Description: This script displays system memory usage and per-process
RSS memory using bar graphs. It reads from /proc/meminfo and /proc/PID/smaps.

Date: 2026-07-14
'''

import argparse
import os, sys

def parse_command_args() -> object:
    "Set up argparse here. Call this function inside main."
    parser = argparse.ArgumentParser(description="Memory Visualiser -- See Memory Usage Report with bar charts",epilog="Copyright 2023")
    parser.add_argument("-H", "--human-readable", action="store_true", help="Prints sizes in human readable format")
    parser.add_argument("-l", "--length", type=int, default=20, help="Specify the length of the graph. Default is 20.")
    parser.add_argument("program", type=str, nargs='?', help="if a program is specified, show memory use of all associated processes. Show only total use if not.")
    args = parser.parse_args()
    return args

def percent_to_graph(percent: float, length: int=20) -> str:
    """
    Turns a percent 0.0 - 1.0 into a bar graph string.
    
    The graph is made of '#' characters representing the percentage
    and spaces filling the remainder. The total length of the string
    always equals the length argument.
    """
    # Calculate number of hash symbols from the percentage
    num_hashes = round(percent * length)
    # Remaining characters are spaces
    num_spaces = length - num_hashes
    # Build and return the bar graph string
    return '#' * num_hashes + ' ' * num_spaces

def get_sys_mem() -> int:
    """
    Return total system memory in kB.
    
    Opens /proc/meminfo with explicit 'r' mode, finds the MemTotal line,
    and returns the numeric value as an integer.
    """
    # Open the system memory info file in read mode
    with open('/proc/meminfo', 'r') as f:
        # Iterate through each line to find MemTotal
        for line in f:
            if line.startswith('MemTotal:'):
                # Extract the numeric value and convert to int
                return int(line.split()[1])
    # Return 0 if MemTotal is not found
    return 0

def get_avail_mem() -> int:
    """
    Return total memory that is currently available in kB.
    
    Opens /proc/meminfo with explicit 'r' mode and looks for MemAvailable.
    If MemAvailable is missing (common on WSL), it falls back to
    MemFree + SwapFree.
    """
    mem_free = 0
    swap_free = 0
    mem_available = None
    
    # Open the system memory info file in read mode
    with open('/proc/meminfo', 'r') as f:
        for line in f:
            # Check for MemAvailable first (preferred value)
            if line.startswith('MemAvailable:'):
                mem_available = int(line.split()[1])
            # Store MemFree in case we need the fallback
            elif line.startswith('MemFree:'):
                mem_free = int(line.split()[1])
            # Store SwapFree in case we need the fallback
            elif line.startswith('SwapFree:'):
                swap_free = int(line.split()[1])
    
    # Return MemAvailable if it exists, otherwise use the WSL fallback
    if mem_available is not None:
        return mem_available
    return mem_free + swap_free

def pids_of_prog(app_name: str) -> list:
    """
    Given an app name, return all pids associated with app.
    
    Uses os.popen to call the 'pidof' command and returns
    the output as a list of PID strings.
    """
    # Use os.popen to run the pidof command for the given app name
    cmd = os.popen(f'pidof {app_name}')
    # Read the output and strip whitespace
    output = cmd.read().strip()
    # Close the pipe
    cmd.close()
    # If pidof returns nothing, return an empty list
    if not output:
        return []
    # Split the output string into a list of PID strings
    return output.split()

def rss_mem_of_pid(proc_id: str) -> int:
    """
    Given a process id, return the Resident memory used.
    
    Opens /proc/<pid>/smaps and sums all Rss values.
    """
    total_rss = 0
    # Open the smaps file for the given process ID
    with open(f'/proc/{proc_id}/smaps', 'r') as f:
        for line in f:
            # Check if line starts with Rss
            if line.startswith('Rss'):
                # Add the numeric value to the total
                total_rss += int(line.split()[1])
    return total_rss

def bytes_to_human_r(kibibytes: int, decimal_places: int=2) -> str:
    "turn 1,024 into 1 MiB, for example"
    suffixes = ['KiB', 'MiB', 'GiB', 'TiB', 'PiB']
    suf_count = 0
    result = kibibytes 
    while result > 1024 and suf_count < len(suffixes):
        result /= 1024
        suf_count += 1
    str_result = f'{result:.{decimal_places}f} '
    str_result += suffixes[suf_count]
    return str_result

if __name__ == "__main__":
    args = parse_command_args()
    if not args.program:
        total = get_sys_mem()
        avail = get_avail_mem()
        used = total - avail
        percent = used / total
        graph = percent_to_graph(percent, args.length)
        print(f"Memory         [{graph}| {percent:.0%}] {used}/{total}")
    else:
        pass
