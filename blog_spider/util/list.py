#!
# __author__ = 'valseek'
# __create_time__ = '2020/5/3 5:44 AM'



def resize(arr:list,size = None,default_value = 0):
    if size is None :
        return arr
    while len(arr) < size :
        arr.append(default_value)
    return arr



