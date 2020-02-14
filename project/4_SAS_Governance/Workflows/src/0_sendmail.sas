filename logfile '/home/sasdemo/modelops_credit_scoring_docker/WFsendmail.log';

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
   "subject":"SAS Model Governance: Mail service - Model Registration",
   "content":[ 
      { 
         "type":"text/plain",
         "value":"The Candidate Champion is registred into the SAS Model Manager. You will receive an email with Model report!"
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
  
libname resp JSON fileref=resp; 