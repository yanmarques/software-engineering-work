#!/bin/sh
set -e

branch="${GIT_BRANCH:-dev}"

# global log file
log_file="/var/log/build.log"

method="${1:?}"

job() {
    git clone https://github.com/yanmarques/software-engineering-work.git -b "$branch"
    
    # change to project directory
    cd software-engineering-work
    
    # do the thing
    python3 setup.py "$method"

    # copy target result to mountpoint
    cp -a ./dist* /dist/

    echo "Build done. Waiting for shutdown!"
}

# start background job and log all output
job >> "$log_file" 2>&1 &

# keep processing
tail -f "$log_file"