rpdat=$1
cat $rpdat | awk '{print $3-$2"    " $0}' | sort -r -n
