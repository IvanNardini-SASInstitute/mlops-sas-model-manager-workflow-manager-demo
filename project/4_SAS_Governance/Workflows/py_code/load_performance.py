
#Libraries

import pandas as pd
import swat

# Session variable

_USERNAME = 'xxx'
_PASSWORD = 'xxx'
_CASLIB = 'xxx'


# Start CAS Session
cas_session = swat.CAS(caslib = _CASLIB)

# For each csv, load into caslib Public with 30 secs

# df = pd.DataFrame(data = [[1,1,1,'HomeImp','ProfExe',1,1,1,1,1,1,1],[_LOAN, _MORTDUE, _VALUE, _REASON, _JOB, _YOJ, _DEROG, _DELINQ, _CLAGE, _NINQ, _CLNO, _DEBTINC]], 
#   	columns = ["LOAN", "MORTDUE", "VALUE", "REASON", "JOB", "YOJ", "DEROG", "DELINQ", "CLAGE", "NINQ", "CLNO", "DEBTINC"])
#   scoretbl = cas_session.upload_frame(df, casout=dict(name="input",replace=True,caslib=cas_library))