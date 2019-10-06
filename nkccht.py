def nkccht(msg:"str"="hello ",timeout:"int_sec"=-1,
           path:"temp dir path"=None,close:"terminal"=True
           ) -> "(int_errorcode,string_return)":
    """
msg = message to user
path = temporary directory with write permission
timeout = timeout for reading input from file
replay = message typed from user.
to show the message and get replay from user without own window.
this may help from not identifying which process show this message
..................................................................
| errorcode => reason                                            |
``````````````````````````````````````````````````````````````````
| 0 => no error ( reply in string_return )
| 1 => unknown error ( sys.exc_info is in string_return )
| 2 => given path not foung
| 3 => given path is file but dir needed
| 4 => permission error in given directory path
| 5 => platform not supported (only windows and linus supported)
| 6 => teminal terminated by user
| 7 => timeout
------------------------------------------------------------------
if close is set False terminal not terminated after timeout and
the temp file created won't deleted if user replyed after timeout.
"""
    import sys,os,time,threading,psutil
    
    if sys.platform[:3] == 'win':
        try:
            if path == None :
                try: path = os.environ['HOME']+"\\AppData\\Local"
                except: path = os.environ['HOMEDRIVE']+os.environ['HOMEPATH']+"\\AppData\\Local"
            if not os.path.exists(path): return (2,path+" not found")
            if not os.path.isdir(path): return (3,path+" is file but directory required")
            if not os.access(path,os.R_OK) or not os.access(path,os.W_OK):
                return (4,"permission denied to read or write in "+path)
            else:   # sometimes in windows os.access won't works so this is necessary
                try : f=open(os.path.join(path,'check'),'w');f.close()
                except PermissionError:
                    return (4,"permission denied to read or write in "+path)
                else :
                    try: os.remove(os.path.join(path,'check'))
                    except: pass

            path = os.path.join(path,str(os.getpid())+"reply"+str(threading.get_ident()))
        
            try: os.remove(path)
            except FileNotFoundError: pass

            pids=psutil.pids()
            os.popen(r'start /wait cmd /V /C "set /P nk= '+msg.replace('"',"''")+r' && echo !nk! > '+path+r'"')
            pids=[i for i in psutil.pids() if i not in pids]
            pid=pids[0]

            flag = 0;s_time=time.time()

            while timeout == -1 or time.time()-s_time < timeout :
                if os.path.exists(path):
                    flag = 1
                    break
                if pid not in psutil.pids():
                    if os.path.exists(path):
                        flag = 2
                        break
                    else:
                        flag = 3
                        break
                time.sleep(0.3)

            if flag == 0:
                if close :
                    os.popen('TASKKILL /PID '+str(pid)+' /T /F')
                retrn = (7,"waited for "+str(timeout)+" seconds "+("and closed terminal" if close else ""))
            elif flag == 3:
                retrn = (6,"terminal closed by user before timeout")
            elif flag == 1 or flag == 2:
                file=open(path,'r')
                retrn=(0,file.read())
                file.close()

            try: os.remove(path)
            except: pass

            return retrn

        except : return (1,sys.exc_info())
 
    elif sys.platform[:3]=='lin':
        try: 
            if path == None :
                try : path = os.environ['HOME']+"/.local"
                except: path = os.environ['HOMEDRIVE']+os.environ['HOMEPATH']+"./local"
            if not os.path.exists(path): return (2,path+" not found")
            if not os.path.isdir(path): return (3,path+" is file but directory required")
            if not os.access(path,os.R_OK) or not os.access(path,os.W_OK):
                return (4,"permission denied to read or write in "+path)

            path = os.path.join(path,'.'+str(os.getpid())+"reply"+str(threading.get_ident()))
            pidpath = path.replace('reply','pid')

            try : os.remove(path)
            except FileNotFoundError : pass

            cmd = "gnome-terminal -e 'bash -c \"ps > "+pidpath
            cmd += ";read -p \\\""+msg.replace("'",'`').replace('"','`')+"\\\" nk;"+"echo $nk > "+path+"\"'"
            os.popen(cmd)

            try: os.remove(pidpath)
            except FileNotFoundError : pass
            while 5: 
                try:
                    pidfile = open(pidpath)
                    pid = eval(pidfile.read().split('\n')[1].split(' ')[0])
                    pidfile.close()
                except: time.sleep(0.5)
                else: break
            try : os.remove(pidpath)
            except : pass

            flag = 0;s_time=time.time()

            while timeout == -1 or time.time()-s_time < timeout :
                if os.path.exists(path):
                    flag = 1
                    break
                if not psutil.pid_exists(pid):
                    if os.path.exists(path):
                        flag = 2
                        break
                    else:
                        flag = 3
                        break
                time.sleep(0.3)
    
            if flag == 0:
                if close :
                    os.popen('kill '+str(pid))
                retrn = (7,"waited for "+str(timeout)+" seconds "+("and closed terminal" if close else ""))
            elif flag == 3:
                retrn = (6,"terminal closed by user before timeout")
            elif flag == 1 or flag == 2:
                file=open(path,'r')
                retrn=(0,file.read())
                file.close()

            try: os.remove(path)
            except: pass
   
            return retrn
        except : return (1,sys.exc_info())
    
    else :
        return (5,sys.platform+" is not supported only windows and linux currently supported")
