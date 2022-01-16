import random
from collections import Counter

风牌="🀀🀁🀂🀃"
三元牌="🀄🀅🀆"
万="🀇🀈🀉🀊🀋🀌🀍🀎🀏"
条="🀐🀑🀒🀓🀔🀕🀖🀗🀘"
饼="🀙🀚🀛🀜🀝🀞🀟🀠🀡"
花="🀢🀣🀤🀥🀦🀧🀨🀩"
特殊="🀫🀪"

def 牌山():
    牌=[风牌,三元牌,万,条,饼]*4
    return "".join(牌)

山="".join(sorted(牌山()))

def 抽(num:int=14):
    牌=[*山]
    random.shuffle(牌)
    return "".join(sorted(牌[:num]))

def 和():
    牌堆=Counter(山)
    num=random.randint(1,100000)
    和牌=""
    if num<=252: # 2.52%
        和牌=七对(牌堆)
    elif num>99957: # 0.043%
        和牌=国士无双()
    else:
        for _ in range(4):
            和牌+=面(牌堆)
        和牌+=对(牌堆)
    return "".join(sorted(和牌))

def 刻(牌堆:dict):
    num=random.randint(1,100)
    if num==42 or num==84: # 2%
        return 至少抽(牌堆,4) # 杠
    return 至少抽(牌堆,3)     # 刻

数牌=[万,条,饼]

def 顺(牌堆:dict):
    花色=random.randint(0,2)
    下标=random.randint(1,7)
    前,中,后=数牌[花色][下标-1:下标+2]
    while not(牌堆[前] and 牌堆[中] and 牌堆[后]):  # 牌不够时可能死循环
        花色=random.randint(0,2)
        下标=random.randint(1,7)
        前,中,后=数牌[花色][下标-1:下标+2]
    牌堆[前]-=1
    牌堆[中]-=1
    牌堆[后]-=1
    if 牌堆[前]<=0:
        del 牌堆[前]
    if 牌堆[中]<=0:
        del 牌堆[中]
    if 牌堆[后]<=0:
        del 牌堆[后]
    return f"{前}{中}{后}"

def 面(牌堆:dict):
    num=random.randint(1,100) # 大约 顺:刻=9:1
    if num>90:
        return 刻(牌堆)
    else:
        return 顺(牌堆)

def 对(牌堆:dict):
    return 至少抽(牌堆,2)

def 七对(牌堆:dict):
    return "".join(对(牌堆) for _ in range(7))
        
def 国士无双():
    幺九="🀀🀁🀂🀃🀄🀅🀆🀇🀏🀐🀘🀙🀡"
    单张=random.choice(幺九)
    return 幺九+单张
    
def 至少抽(牌堆:dict,num=2):
    剩余=[*牌堆.keys()]
    单张=random.choice(剩余)
    while 牌堆[单张]<num:   # 牌不够时可能死循环
        单张=random.choice(剩余)
    牌堆[单张]-=num
    if 牌堆[单张]<=0:
        del 牌堆[单张]
    return 单张*num