

import requests,os,time

def FileDown(filepath,url):
    # 网络文件保存到本地
    r = requests.get(url,verify=False)
    if r.status_code == 200:
      with open(filepath, 'ab') as f:
        f.write(r.content)
        f.close()
      return filepath
    else:
        return None


def time_name(path):
    # 文件名称+时间重命名功能
    if os.path.exists(path):
        filepath,filename = os.path.split(path)
        name, dk = os.path.splitext(filename)
        name = '{0}{1}'.format(name,str(time.strftime(r'_%Y%m%d_%H_%M_%S',time.localtime())))
        newpath = os.path.join(filepath,name+dk)
        os.rename(path,newpath)
        return newpath
    else:
        return None

def number_name(oldpaths,a): 
    # 360数字重命名
    filepath,filename = os.path.split(oldpaths)
    name, dk = os.path.splitext(filename)
    oldpath= os.path.join(filepath,name+dk)  # 原始文件名称路径 
    newname = os.path.join(oldpaths,str(a).zfill(5)+dk) # 重命名文件名称路径
    os.rename(oldpath,newname) # 重命名文件
    # shutil.copyfile(oldpath,newname) #复制重命名
    return newname