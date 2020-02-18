filename logfile '/home/sasdemo/modelops_credit_scoring_docker/WFsendmail4.log';

proc printto log=logfile;
run;

/* Server and Credentials */
%let protocol=https;
%let server=api.sendgrid.com;
%let mailUri=v3/mail/send;
%let AuthToken=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;


filename resp TEMP;  
filename jsinput TEMP;

data _null_;
file jsinput;
input;
put _infile_;
datalines;
{ 
   "personalizations":[ 
      { 
         "to":[ 
            { 
               "email":"ivan.nardini92@gmail.com"
            }
         ]
      }
   ],
   "from":{ 
      "email":"sas_workflow_manager@sas.com"
   },
   "subject":"SAS Model Governance: Mail service - Retrain Model service",
   "content":[ 
      { 
         "type":"text/plain",
         "value":"value":" The Champion model is underperforming! Please contact Analytics Leader!"
      }
   ]
}
;
run; 

proc http
    method="POST"
    url="&protocol.://&server./&mailUri."
	in=jsinput
    out=resp;
    headers
    "Authorization"="bearer &AuthToken."
    "Content-Type"="application/json";
  run;
  
libname resps JSON fileref=resp; 

/* data _null_; */
/* set resps.ROOT; */
/* call symputx( "statusId", status); */
/* run; */
/*  */
/* data _null_; */
/* put "&statusId."; */
/* run; */
/*  */
/* filename resp clear; */