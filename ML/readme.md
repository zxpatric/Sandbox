#bug fix
'''
For those having tried to solve the "!! Submission failed: Error using submitWithConfiguration>validateResponse (line 158)" error unsuccessfully, here is what worked for me (Matlab R2016b on Windows 7 Enterprise SP1 x64) :

1) if curl is not installed, install it from https://curl.haxx.se/download.html), add it to the env path, and then check that is well found with the following command from Matlab: system('curl -V')

2) disable the default progressmeter setting in curl. Namely, go into 'submitWithConfiguration.m' and add a '-s' after the POST instruction in lines 131 and 134 like that

json_command = sprintf('echo jsonBody=%s | curl -k -X POST -s -d @- %s', body, url);

I add to do step 2 for each exercise but it worked perfectly
'''

#Reference
'''
https://github.com/everpeace/ml-class-assignments.git
'''