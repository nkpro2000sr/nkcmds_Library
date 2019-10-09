def nkhidef(path:"path of file or dir",show:"show flag"=False,
            strict:"strict path syntax"=False)->"(<code_num>,<result_string>)":
    """
It is used to hide file:
path may be path of file or directory,
if show is True then give path will be UNHIDE

| <code_num> =>     reason
``````````````````````````````````````````````````````
| 0 => no error given path is hided or unhided
|0.1 => given command is already done
| 1 => unknown error,
         error will be returned as <result_string>
| 2 => platform not supported. this works only for
         windows and linux platform
| 3 => given path is not an directory but file found
|-3 => same as 3 but path is hided or unhided anyway
|-3.1 => same as -3 but given commnad is already done
| 4 => given path is not an file but directory found
|-4 => same as 4 but path is hided or unhided anyway
|-4.1 => same as -4 but given command is already done
| 5 => given path not found
______________________________________________________
3,4 is returned if only strict path syntax is enabled
otherwise -3,-4 is returned and given work is done.
disableing strict may leads to errors.
%d%.0 only works properly on windows platform.
"""
    from os import popen,rename,path as Path
    from sys import platform,exc_info
    code = 0
    file = True
    if Path.isdir(path):
        file = False
        if Path.split(path)[1]=='':
            path=Path.split(path)[0]
        else:
            if strict:
                return (4,"there is no file "+path)
            else: code = -4
    elif Path.isfile(Path.split(path)[0]) or Path.isfile(path):
        if Path.split(path)[1]=='':
            if strict:
                return (3,"there is no directory "+path)
            else:
                code = -3
                path = Path.split(path)[0]
    else: return (5,"path not found "+path)
    
    if platform[:3]=="win":
        import stat as Stat
        from os import stat
        try:
            hiden = stat(path).st_file_attributes & Stat.FILE_ATTRIBUTE_HIDDEN
            if show:
                if hiden:
                    popen('attrib -h '+path).close()
                    return (code if code else 0,
                             "given >"+("file " if file else "dir ")+path+" is UNHIDED")
                else:
                    return ((code - 0.1) if code else 0.1,
                            "given >"+("file " if file else "dir ")+path+" is already not hiden")
            else:
                if not hiden:
                    popen('attrib +h '+path).close()
                    return (code if code else 0,
                          "given >"+("file " if file else "dir ")+path+" is HIDED")
                else:
                    return ((code - 0.1) if code else 0.1,
                            "given >"+("file " if file else "dir ")+path+" is already hiden")
        except: return (1,exc_info())
        
    elif platform[:3]=="lin":
        try:
            if show:
                if Path.split(path)[1][0]=='.':
                    rename(path,Path.split(path)[0]+Path.split(path)[1][1:])
                    return (code if code else 0,
                             "given >"+("file " if file else "dir ")+path+" is UNHIDED "+
                        "and new path is >"+Path.split(path)[0]+Path.split(path)[1][1:])
                else:
                    return ((code - 0.1) if code else 0.1,
                            "given >"+("file " if file else "dir ")+path+" is already not Hiden")
            else:
                rename(path,'.'.join(Path.split(path)))
                return (code if code else 0,
                             "given >"+("file " if file else "dir ")+path+" is HIDED "+
                        "and new path is >>"+'.'.join(Path.split(path)))
        except: return (1,exc_info())
    else: return (2,platform+" is not supported")
