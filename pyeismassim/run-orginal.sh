SERVER_DIR=/home/dgm/lidia-massim/massim-2011-1.0/massim/scripts/
SERVER_CMD='startServer.sh'
MONITOR_DIR=/home/dgm/lidia-massim/massim-2011-1.0/massim/scripts/
MONITOR_CMD='startMarsMonitor.sh'
PERCEPT_DIR=/home/dgm/lidia-massim/pyeismassim/perceptServer/
PERCEPT_CMD='PerceptServer.py 1 10000 31'
PYTHON=python
TERM_CMD=urxvtc

WD=$(pwd)
echo Working dir is:  $WD
echo Server path is:  $SERVER_DIR
echo Monitor path is: $MONITOR_DIR
echo Term command is: $TERM_CMD
echo Python command:  $PYTHON

# Run servero
echo Starting server.
cd $SERVER_DIR
$TERM_CMD -title 'MASSIM' -e $SERVER_CMD
cd $WD
sleep 10

# Run monitor
#echo Starting monitor.
#cd $MONITOR_DIR
#$TERM_CMD -name 'MONITOR' -e $MONITOR_CMD
#cd $WD
#sleep 10

# Run percept server
echo Starting percept server
cd $PERCEPT_DIR
$TERM_CMD -title 'PERCEPT' -e $PYTHON $PERCEPT_CMD
cd $WD
sleep 10

# Run agents
$TERM_CMD -title 'AGENT' -e $PYTHON Agent.py a1 1 -sh localhost -sp 10000
$TERM_CMD -title 'AGENT' -e $PYTHON Agent.py b1 1
