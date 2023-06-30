#!/bin/bash
function usage(){
  echo "Usage:
  serve.py [-h] [-r] [-R] [-l <lvl>] [-p <port>] [-i <ip>] [-a<address>] [-s <sec>] [-H]

  OPTIONS
  -------
      - h : show this help
      - r : shortcut for --address https://www.ccp4.ac.uk/edly/viewer
      - d : shortcut for --address http://130.246.214.80:8001
      - l : marker lvl (default 2)
      - p : port number (default 8020)
      - i : ip address (default localhost)
      - a : full address which prevails over ip,port(default 0)
      - R : tests report
      - C : code coverage report
      - H : headless mode (default False)
    "
  exit 1;
}


dir=$(realpath `dirname $0`)
env_bin=$(realpath $dir/../.env/bin)

args=
lvl=2
address=
do_report=0
do_coverage=0
report_dir='report'
while getopts ":l:a:p:s:rdHRCh" arg; do
  case $arg in
    h) usage;;
    l)
      lvl=$OPTARG
      ;;
    a)
      report_dir='report_custom'
      address=$OPTARG
      ;;
    p)
      port=$OPTARG
      args+="--port=$port"
      ;;
    i)
      report_dir='report_custom'
      ip=$OPTARG
      args+="--ip=$ip"
      ;;
    s)
      sleep=$OPTARG
      args+="--sleep=$sleep"
      ;;
    r)
      report_dir='report_rel'
      address='https://www.ccp4.ac.uk/edly/viewer'
      ;;
    d)
      report_dir='report_dev'
      address='http://130.246.214.80:8001'
      ;;
    H)
      args+='--headless'
      ;;
    R)
      do_report=1
      ;;
    C)
      do_coverage=1
      ;;
  esac
done


if [ $address ];then args+=" --address=$address ";fi
args+=" --lvl=$lvl "

if [ $do_report -eq 1 ];then
  if [ ! -d $dir/$report_dir ];then mkdir $dir/$report_dir ;fi;
  args+="--html=$dir/$report_dir/report.html --self-contained-html"
fi


if [ $do_coverage -eq 1 ];then
  echo 'launching server for code coverage'
  cd $dir/..
  $env_bin/coverage run --data-file=$dir/report/.coverage serve.py &> $dir/report/server.log &
  pid_cov=$!
fi


# cmd="$dir/../.env/bin/pytest -s  $dir/test_base.py --lvl=$lvl ${args[@]}"
cd $dir
cmd="$env_bin/pytest -s  $dir/test_base.py $args"
echo $cmd
$cmd


if [ $do_coverage -eq 1 ];then
  echo 'coverage analysis'
  # kill $pid_cov
  cd $dir/report
  $env_bin/coverage html -i -d coverage_html
fi
