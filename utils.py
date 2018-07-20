import math

def digits(num, digit):
    site = pow(10, digit)
    return math.floor(num*site)/site

def s2f(data):
    if data == None or isinstance(data, int) or len(data) == 0:
        return data
    if isinstance(data, float):
        return digits(data, 6)
    #print("enter s2f data:", data)
    if isinstance(data, str):
        data = digits(float(data),6)
    elif isinstance(data,list):
        m=0
        for i in data:            
            if isinstance(i,str):
                data[m] = digits(float(i),6)
            elif isinstance(i,list):
                data[m] = s2f(i)
            else:
                print("unknown data type1!", type(i), i)
            m+=1
    elif isinstance(data, dict):
        for k,v in data.items():
            data[k] = s2f(v)
    else:
        print("unknown data type2!", type(data), data)
    #print("exit s2f data:", data)
    return data

