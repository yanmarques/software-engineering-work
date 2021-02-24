#!/bin/sh
set -e

branch="${GIT_BRANCH:-dev}"

# global log file
log_file="/var/log/build.log"

method="${1:?}"

name() {
    # shellcheck disable=SC1091
    . /etc/os-release

    # recognizes the machine name 
    echo "$ID-$VERSION_ID"
}

# runtime host volume.
host_volume_dir=/dist/"$(name)"

case "$method" in
    rpm)
        build_method="custom_rpm"
        target_directory="dist/"
        ;;
    deb)
        build_method="custom_deb"
        target_directory="deb_dist/"
        ;;
    *)
        echo "[-] unknow method $method"
        exit 1
        ;;
esac

job() {
    git clone https://github.com/yanmarques/software-engineering-work.git -b "$branch"
    
    # change to project directory
    cd software-engineering-work
    
    # do the thing
    python3 setup.py "$build_method"

    mkdir -p "$host_volume_dir"

    # copy target result to mountpoint
    cp -a ./"${target_directory%/}"/* "$host_volume_dir"

    echo "Build done. Waiting for shutdown!"
}

# start background job and log all output
job >> "$log_file" 2>&1 &

# keep processing
tail -f "$log_file"