#!/bin/bash
function usage(){
  echo "Usage:
  serve.py [-h] [-r] [--port <port>] [--ip<ip>] [--address<address>] [--sleep <sec>] [--headless]

  OPTIONS
  -------
      - h : show this help
      - r : shortcut for --address https://www.ccp4.ac.uk/edly/viewer
      -- port     : port number (default 8020)
      -- ip       : ip address (default localhost)
      -- address  : full address which prevails over ip,port(default 0)
      -- headless : headless mode (default False)
    "
  exit 1;
}
args=()
for arg in "$@"; do
  args+=("$arg")
done

if [ $# -ge 1 ];then
  if [[ $1 == '-h' ]];then
    usage
  elif [[ $1 == '-r' ]];then
    unset args[0]
    args+=(' --address https://www.ccp4.ac.uk/edly/viewer')
  fi
fi
# echo "${args[@]}"

dir=`dirname $0`
cmd="$dir/../.env/bin/pytest -s $dir/test_base.py ${args[@]}"
echo $cmd
$cmd
