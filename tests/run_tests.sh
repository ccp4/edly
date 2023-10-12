#!/bin/bash
function usage(){
  echo "Usage:
  run_tests.sh [-h] [-r] [-R] [-e] [-l <lvl>] [-A \"<args>\"] [-m \"<selected_tests>\"] [-p <port>] [-i <ip>] [-a<address>] [-s <sec>] [-H]

  OPTIONS
  -------
  ----- pytest related
      - h : show this help
      - H : headless mode (default False)
      - s : seconds to sleep between widget manipulations
      - l : marker lvl (default 2)
      - A : any other arguments to pass to pytest
      - m : run selected tests, see examples (if not specified runs all tests)
            Note that login and close are added automatically
    ---- address related
      - p : port number (default 8020)
      - i : ip address (default localhost)
      - a : full address which prevails over ip,port(default None)
      - r : shortcut for --address https://www.ccp4.ac.uk/edly/viewer
      - d : shortcut for --address http://130.246.214.80:8001
    ---- reporting
      - e : email the report
      - R : make a html report **
      - C : code coverage report **

** only works when the server can be served locally

Examples:
--------
./run_tests.sh -a http://192.168.0.21:8000
  Runs tests for server at address http://192.168.0.21:8000

./run_tests.sh -l0 -R -e
  Runs only lvl0 tests, generate a report and send it by mail

./run_tests.sh -l1 -m 'frames'
  Runs only tests in test_frames.py with level not more than level 1
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
markers="all"
all_markers='login frames bloch rock close'
report_dir='report'
while getopts ":l:a:A:p:s:m:rdHReCh" arg; do
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
    m)
      markers="login $OPTARG close" #;echo "$markers"
      ;;
    A)
      args=" "$OPTARG" "
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

########################################################################################
## launch the server (only in report mode at the moment )
########################################################################################
html=
if [ $do_report -eq 1 ];then
  address= # disable full address to guarantee the port
  port=$port_report

  report_dir+="/$date"
  if [ ! -d $dir/$report_dir ];then mkdir -p $dir/$report_dir ;fi;

  report_log="$report_dir/run_tests.log"
  server_log="$report_dir/server.log"

  cd $dir/..
  echo 'Launching server for reporting' >> "tests/$report_log"; tail -n1 "tests/$report_log"
  $env_bin/python3 serve.py -p $port &> "tests/$server_log" &
  server_pid=$!
  html="--html=$dir/$report_dir/report.html --self-contained-html"
  cd $dir

  ##check the port is correct
  log_port=0
  i=0
  # If the server takes more than 60 seconds to lauch,increase this
  wait_for_server=60
  while [[ ! "$log_port" -eq "$port_report" && $i -lt $wait_for_server ]] ;do
    running_line=$( grep "Running on http" $server_log  | sed 's/[^0-9.:]//g')
    ip_address=$(echo $running_line | cut -d":" -f2)
    log_port=$(echo $running_line | cut -d":" -f3)
    i=$(($i+1))
    # echo $i
    # cat $server_log
    # echo "$running_line $ip_address $log_port"
    sleep 1
  done
  echo "launch time : $i seconds (max $wait_for_server)" >> $report_log; tail -n1 $report_log
  if [[ "$log_port" -eq "$port_report" ]];then
    echo "Server running on ip address : $ip_address:$log_port with process $server_pid" >> $report_log; tail -n1 $report_log
  else
    echo 'Failed to start server. quitting' >> $report_log; tail -n1 $report_log
    echo "Output of $server_log : "
    cat $server_log
    kill $server_pid
    exit
  fi
fi


########################################################################################
### code coverage stuffs
########################################################################################
if [ $do_coverage -eq 1 ];then
  if [ ! -d $dir/$report_dir ];then mkdir -p $dir/$report_dir ;fi;
  coverage_log="$report_dir/coverage_server.log"
  cd $dir/..
  echo 'Launching server for code coverage'
  $env_bin/coverage run --data-file=$dir/report/.coverage serve.py &>  $coverage_log &
  pid_cov=$!
fi



########################################################################################
#### start pytest
########################################################################################
args+=" --port=$port "
if [ $address ];then args+=" --address=$address ";fi
args+=" --lvl=$lvl "
#### tried to use pytest markers originally but this fails due to some weird behaviour
# of the pytest expression interpreter clashing with double quote characters
#echo "markers : $markers";
# pycmd="print( ' or '.join('$markers'.strip().split(' ')))  "
# markers_expr=$(python3 -c "$pycmd"  )
# args=" $markers_expr\" $args"
if [[ $markers == "all" ]];then markers=$all_markers;fi
files=
cd $dir
# for f in $markers;do files+=" $dir/test_$f.py";done
for f in $markers;do files+=" test_$f.py";done
cmd="$env_bin/pytest   $html $args -v -s $files"
if [ $do_report -eq 1 ];then
  echo "Runnning pytest" >> $report_log; tail -n1 $report_log
  echo $cmd              >> $report_log; tail -n1 $report_log
  pytest_log="$report_dir/pytest.log"
  ## put the output of pytest in pytest.log
  $cmd &> $pytest_log
else
  echo $cmd
  $cmd
fi


########################################################################################
## kill the server if it was launched through this tests
########################################################################################
if [ $do_report -eq 1 ];then
  echo "Shutting down server used for pytest" >> $report_log; tail -n1 $report_log
  kill $server_pid
  if [ $send_email -eq 1 ];then
    echo "Sending email to $email_address" >> $report_log; tail -n1 $report_log
    cmd="$env_bin/python3 email_report.py -f=$report_dir"
    echo $cmd >> $report_log; tail -n1 $report_log
    $cmd >> $report_log; tail -n1 $report_log

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
