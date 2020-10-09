

# This is run by a crontab. 
# It accepts any arguments and passes them to the run.py script. 

PY="/usr/local/bin/python3.7"
# SCRIPT="run.py"
# pwd
SCRIPT="/home/acobb/weatherman/run.py"
LOG="logs/run.log"

if [ $# -eq 0 ]; then
    ARGS="-p"
else
    ARGS="$*"
fi

${PY} ${SCRIPT} ${ARGS}
