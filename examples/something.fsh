#! /usr/bin/env ./fsh.py -M fish  -v
# pick some hosts
on www1mc*
run readlink /rollout/active-release 
# save the ouput to this directory
save -i /tmp/current-deployments
