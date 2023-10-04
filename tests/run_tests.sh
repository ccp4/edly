#!/bin/bash
function usage(){
  echo "Usage:
  serve.py [-h] [-r] [-R] [-e] [-l <lvl>] [-p <port>] [-i <ip>] [-a<address>] [-s <sec>] [-H]

  OPTIONS
  -------
      - h : show this help
      - r : shortcut for --address https://www.ccp4.ac.uk/edly/viewer
      - d : shortcut for --address http://130.246.214.80:8001
      - l : marker lvl (default 2)
      - p : port number (default 8020)
      - i : ip address (default localhost)
      - a : full address which prevails over ip,port(default 0)
      - e : email the report
      - R : tests report
      - C : code coverage report
      - H : headless mode (default False)
    "
  exit 1;
}


dir=$(realpath `dirname $0`)
env_bin=$(realpath $dir/../.env/bin)


date=$(date "+%y_%m_%d-%H_%M")

args=
lvl=2
address=
do_report=0
do_coverage=0
send_email=0
port=8020
port_report=8001
report_dir='report'
while getopts ":l:a:p:s:rdHReCh" arg; do
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
    e)
      send_email=1
      email_address='tarik.drevon@stfc.ac.uk'
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

########################################################################################
## launch the server (only in report mode at the moment )
########################################################################################
html=
if [ $do_report -eq 1 ];then
  port=$port_report
  report_dir+="/$date"
  if [ ! -d $dir/$report_dir ];then mkdir -p $dir/$report_dir ;fi;
  server_log="$report_dir/server.log"

  cd $dir/..
  echo 'Launching server for reporting'
  $env_bin/python3 serve.py -p $port &> 'tests/'$server_log &
  server_pid=$!
  html="--html=$dir/$report_dir/report.html --self-contained-html"
  cd $dir

  ##check the port is correct
  log_port=0
  i=0
  while [[ ! "$log_port" -eq "$port_report" && $i -lt 5 ]] ;do
    running_line=$( grep "Running on http" $server_log  | sed 's/[^0-9.:]//g')
    ip_address=$(echo $running_line | cut -d":" -f2)
    log_port=$(echo $running_line | cut -d":" -f3)
    i=$(($i+1))
    # echo $i
    # cat $server_log
    # echo "$running_line $ip_address $log_port"
    sleep 1
  done
  if [[ "$log_port" -eq "$port_report" ]];then
    echo "Server running on ip address : $ip_address:$log_port with process $server_pid"
  else
    echo 'Failed to start server. quitting'
    echo "output of $server_log"
    cat $server_log
    kill $server_pid
    exit
  fi
fi


########################################################################################
### code coverage stuffs
########################################################################################
if [ $do_coverage -eq 1 ];then
  coverage_log="$report_dir/coverage_server.log"
  cd $dir/..
  $env_bin/coverage run --data-file=$dir/report/.coverage serve.py &>  $coverage_log &
  pid_cov=$!
fi



########################################################################################
#### start pytest
########################################################################################
args+="--port=$port"
cd $dir
cmd="$env_bin/pytest -s  $html $dir/test_base.py $args"
if [ $do_report -eq 1 ];then
  echo "Runnning pytest"
  echo $cmd
  pytest_log="$report_dir/pytest.log"
  $cmd &> $pytest_log
else
  echo $cmd
  $cmd
fi


########################################################################################
## kill the server if it was launched through this tests
########################################################################################
if [ $do_report -eq 1 ];then
  echo "Shutting down server pytest"
  kill $server_pid
  if [ $send_email -eq 1 ];then
    echo "Sending email to $email_address"
    $env_bin/python3 report_mail.py $report_dir

  fi
fi

########################################################################################
## Do the code coverage analysis
########################################################################################
if [ $do_coverage -eq 1 ];then
  echo 'coverage analysis'
  # kill $pid_cov
  cd $dir/report
  $env_bin/coverage html -i -d coverage_html
fi
