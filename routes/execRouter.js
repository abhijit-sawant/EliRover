var express = require('express');
var bodyParser = require('body-parser');
var fs = require('fs');
var cp = require('child_process');
var proc = require('process');

var execRouter = express.Router();
execRouter.use(bodyParser.json());

execRouter.route('/')
.post(function(req, res, next){
	var pathFileCode = '/home/pi/EliRover/code.py';
	if (process.platform == 'win32')
		pathFileCode = 'C:/Users/Abhijit/Software/EliRover/code.py';
	var pathPyExe = 'python';
	if (process.platform == 'win32')
		pathPyExe = '"C:/Program Files/Anaconda3/python.exe"';
	var lstCode = req.body.code.split('\n');
	// lstCode.push('time.sleep(3)');
	for (var i = 0; i < lstCode.length; ++i) {
		lstCode[i] = '    ' + lstCode[i];
	}	
	var code = 'import time\nimport elirover\n\n'
	code += 'def exec_code():\n';
	code += '    rover = elirover.EliRover()\n';
	code += lstCode.join('\n') + '\n';
	code += "if __name__ == '__main__':\n";
	code += '    exec_code()\n\n'
	code += '#End of file:\n'
	fs.writeFile(pathFileCode, code, function(err) {
		if (err)
			return res.json({errMsg: 'Failed to write with error: ' + err}); 
		else {
			var subProcess = cp.exec(pathPyExe + ' ' + pathFileCode, function (err, stdout, stderr) {
				setProcStop(function(errStop) {
					if (err)
						return res.json({errMsg: 'Failed to launch process with error: ' + err});						
					
					var msg = null;
					if (stderr)
						msg = 'Got errors from process ' + stderr + '\n\n';
					if (errStop)
						msg += 'Failed to update data with error: ' + errStop;
					if (msg !== null)
						return res.json({errMsg: msg});

 					res.json({logMsg:'Got output from process ' + stdout});
				});			
			});
			if (subProcess !== null && subProcess.pid !== null)
				setProcRunning(subProcess.pid);
		}
	});	      
})

.delete(function(req, res, next){
	stopProc(function(err) {
		if (err)
		{
			msg = 'Failed to kill procee with error ' + err;
			return res.json({errMsg: msg});
		}
		return res.json({logMsg: 'Killed process'});
	});
})

var getPathFileData = function() {
	var pathFileData = '/home/pi/EliRover/data.json';
	if (process.platform == 'win32')
		pathFileData = 'C:/Users/Abhijit/knowledge/Blockly/data.json';
	return pathFileData;	
}

var setProcRunning = function(pid) {
	var procData = `{"isRunning":true, "pid": ${pid}}`;
	fs.writeFileSync(getPathFileData(), procData);	
}

var stopProc = function(callBack) {
	fs.readFile(getPathFileData(), 'utf-8', function(err, data) {
		if (err)
			return callBack(err);
		var procData = JSON.parse(data);
		if (procData.hasOwnProperty('isRunning') == true)
		{
			if (procData.pid !== null)
			{
				if (proc.kill(procData.pid, 0))
				{
					try 
					{
						proc.kill(procData.pid);
					}
					catch(e)
					{
						callBack(e);
					}
				}
			}
			procData.isRunning = false;
			procData.pid = null;			
			fs.writeFile(getPathFileData(), JSON.stringify(procData), function(errWrite) {
				if (errWrite)
					return callBack(errWrite);
				callBack(null);
			});
		}
	});
}

var setProcStop = function(callBack) {
	fs.readFile(getPathFileData(), 'utf-8', function(err, data) {
		if (err)
			return callBack(err);
		var procData = JSON.parse(data);
		if (procData.hasOwnProperty('isRunning') == true)
		{
			procData.isRunning = false;
			procData.pid = null;
			fs.writeFile(getPathFileData(), JSON.stringify(procData), function(errWrite) {
				if (errWrite)
					return callBack(errWrite);
				callBack(null);
			});
		}
	});
}	


module.exports = execRouter;
