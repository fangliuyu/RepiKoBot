from types import ModuleType
import typing
import importlib
import os
import traceback

from repiko.core.log import logger

def loadPlugins(path:str="repiko/plugin",reload:typing.Dict[str,ModuleType]=None) -> typing.Dict[str,ModuleType]:
    pkgName="repiko"
    plugins={}
    files=os.listdir(path)
    if path.startswith(pkgName):
        nameList=path.split("/")
        if nameList[0]!=pkgName:
            nameList=path.split("\\") # win?
        nameList.append("") # ["repiko","plugin",""]
    else:
        nameList=[""]
    for fn in files:
        if not fn.startswith("_") and fn.endswith(".py"): # 不以 _ 开头的 py 文件
            name,_=os.path.splitext(fn)
            nameList[-1]=name
            fullName=".".join(nameList)
            try:
                if reload and name in reload:
                    logger.info(f"重载 {fullName} ——")
                    plugins[name]=importlib.reload(reload[name])
                else:
                    logger.info(f"加载 {fullName} ——")
                    plugins[name]=importlib.import_module(fullName)
            except Exception as ex:
                traceback.print_exception(type(ex),ex,ex.__traceback__)
                logger.error(f">> {fullName} 载入失败！ <<")
    return plugins
