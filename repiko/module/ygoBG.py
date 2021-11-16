import json

from urllib import parse
import httpx
from bs4 import BeautifulSoup
from bs4.element import PageElement, Tag
from typing import List
# try:
#     from bs4.element import TemplateString #新版bs4需要
# except:
#     TemplateString=NavigableString

from .ygo.card import Card,CardAttribute,CardRace,CardType,LinkMark

class BaiGe:

    link="https://ygocdb.com/"

    linkmark={
        "↙":LinkMark.BottomLeft,
        "↓":LinkMark.Bottom,
        "↘":LinkMark.BottomRight,
        "←":LinkMark.Left,
        "→":LinkMark.Right,
        "↖":LinkMark.TopLeft,
        "↑":LinkMark.Top,
        "↗":LinkMark.TopRight
    }

    @staticmethod
    def dealInt(text:str):
        if text.isdigit():
            return int(text)
        else:
            return text

    def getHTML(self,url):
        res=httpx.get(url)
        return res.text

    async def asyncGetHTML(self,url):
        async with httpx.AsyncClient() as client:
            res=await client.get(url)
        return res.text

    def html2Card(self,html,cardPage=False):
        html=BeautifulSoup(html,"lxml")
        if cardPage:
            divs=html.find_all("div",{"class":"row card detail"}) 
        else:
            divs=html.find_all("div",{"class":"row card result"})
        if not divs:
            return None
        cards=[]
        for div in divs:
            info:List[Tag]=div.find_all("div",limit=3)
            if cardPage:
                info[2]=info[2].parent
            types=None
            data=None
            desc=""
            state="type"
            for child in info[2].div.children: #效果文本
                if state=="type":
                    if isinstance(child,str):
                        child=child.strip()
                        if child:
                            types,*data=child.split()
                            types=types[1:-1].split("|") # [魔法|永续]
                            state="data"
                elif state=="data":
                    if isinstance(child,Tag):
                        if child.name=="hr":
                            state="desc"
                    elif isinstance(child,str):
                        child=child.strip()
                        if child:
                            data= (data or []) + child.split()
                elif state=="desc":
                    if isinstance(child,Tag):
                        if child.name=="br":
                            desc+="\n"
                        elif child.name=="hr" and "灵摆" in types:
                            desc=desc.rstrip()
                            desc+="\n{p}"
                        else:
                            child=child.text
                    if isinstance(child,str):
                        desc+=child
            c=Card(types)
            c.name=info[1].h2.text
            extras=info[1].find_all("h3")
            # print(extras)
            c.id=extras.pop().text
            
            if len(extras)<2:
                if extras[-1].text.isascii():
                    c.enname=extras.pop().text
                else:
                    c.jpname=extras.pop().text
            else:
                c.enname=extras.pop().text
                c.jpname=extras.pop().text
            c.database,c.QA,c.wiki,c.yugipedia,c.ygorg,c.ourocg,c.script,c.ocgRule=[
                a.get("href") for a in info[1].find_all("a")]
            c.img=info[0].img.get("data-original")
            if isinstance(c.img,str) and c.img.endswith("!half"):
                c.img=c.img[:-5]
            if c.isMonster:
                race,attribute=data.pop(0).split("/") # 恐龙/地
                c.race=CardRace.fromStr(race)
                c.attribute=CardAttribute.fromStr(attribute)
                lv=""
                for char in data.pop(0): # [★2] [☆4] [LINK-3]
                    if char.isdigit():
                        lv+=char
                lv=BaiGe.dealInt(lv)
                c.level=lv
                attack,defence=data.pop(0).split("/") # 1400/1200
                c.attack=BaiGe.dealInt(attack)
                c.defence=BaiGe.dealInt(defence)
                if c.isXyz:
                    c.rank=lv
                if c.isLink:
                    c.linknum=lv
                    c.defence=None
                    marks=data.pop(0).split("]") # [↑][←][→][↙][↓][↘]
                    for m in marks:
                        m=m.strip("[")
                        if m:
                            c.linkmark.add(BaiGe.linkmark[m])
                if c.isP:
                    marks=data.pop(0).split("/") # 4/4
                    c.Pmark=[ BaiGe.dealInt(m) for m in marks ]
                    desc=f"←{marks[0]} 【灵摆】 {marks[1]}→"+desc
                    if CardType.Normal in c.cardType:
                        desc=desc.format(p="【怪兽描述】")
                    else:
                        desc=desc.format(p="【怪兽效果】")
            c.effect=desc.strip()
            cards.append(c)

            return c # 先只找一张卡

    def search(self,text,byID=False):
        if byID:
            url=f"{self.link}card/{text}" # text是卡号
        else:
            url=f"{self.link}?search={text}"
        html=self.getHTML(url)
        return self.html2Card(html,cardPage=byID)

    async def asyncSearch(self,text,byID=False):
        if byID:
            url=f"{self.link}card/{text}" # text是卡号
        else:
            url=f"{self.link}?search={text}"
        html=await self.asyncGetHTML(url)
        return self.html2Card(html,cardPage=byID)

if __name__ == "__main__":
    
    async def main():
        text=input()
        a=BaiGe()
        print(await a.asyncSearch(text))

    import asyncio
    asyncio.run(main())
