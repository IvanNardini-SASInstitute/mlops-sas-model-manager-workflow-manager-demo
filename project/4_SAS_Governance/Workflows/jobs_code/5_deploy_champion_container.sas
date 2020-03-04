filename logfile '/home/sasdemo/modelops_credit_scoring_docker/jobs/docker_run.log';

proc printto log=logfile;
run;

data _null_;
call system ('/home/sasdemo/modelops_credit_scoring_docker/jobs/docker_run.sh');
run;
