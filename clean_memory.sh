#!/bin/bash

echo "🧹 Cleaning RAM cache and swap memory..."

# Ensure the script is run as root
if [[ $EUID -ne 0 ]]; then
    echo "❌ Please run this script as root (e.g. with sudo)."
    exit 1
fi

# Show memory usage before cleanup
echo -e "\n🔍 Memory and Swap BEFORE cleanup:"
free -h

# Kill processes using more than 4GB of RAM
echo -e "\n⚠️ Killing processes using more than 4GB of memory:"
ps -eo pid,comm,rss --sort=-rss | awk '$3 > 4000000 {print $0}' | while read pid comm rss; do
    echo "Killing PID $pid ($comm) using $((rss/1024)) MB..."
    kill -9 $pid
done

# Sync filesystem buffers
sync

# Drop caches (pagecache, dentries, and inodes)
echo 3 > /proc/sys/vm/drop_caches

# Optional: Compact memory
echo 1 > /proc/sys/vm/compact_memory

# Turn off and back on swap to flush it
swapoff -a
swapon -a

# Show memory usage after cleanup
echo -e "\n✅ Memory and Swap AFTER cleanup:"
free -h

echo -e "\n✔️ Done."
