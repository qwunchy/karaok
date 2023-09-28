# This example requires the 'message_content' intent.

import discord
import time
import subprocess
import os
import signal
import string
from yt_dlp import YoutubeDL
from discord.ext import tasks, commands
intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

plays = {}
titles = {}
p=[1]
songq = [-3600]
flag=[True]
x = [0]
content=""
txtput=""
temp = ""
fsong = [0]
y = [0]
delet = -1
num=0
def get_length(filename):
    result = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                             "format=duration", "-of",
                             "default=noprint_wrappers=1:nokey=1", filename],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT)
    return int(float(result.stdout))


@tasks.loop(seconds = 1) # repeat after every 10 seconds
async def myLoop():
    if flag[0] and songq[0]>0:
        if songq[1].find("cdn.discordapp.com")==-1:
            p[0]=subprocess.Popen(["mpv","-fs","-pause","--ytdl-raw-options=format-sort=res:1080", songq[1]])
        else:
            p[0]=subprocess.Popen("ffmpeg -i '"+songq[1]+"' -f matroska - | mpv -fs -pause --force-window=yes -", shell=True)        

        plays[str(songq[2])]=plays[str(songq[2])]-1
        x[0]=songq[0]
        flag[0]=False 
    
    elif p[0].poll()==None:
        if x[0]>0: 
            x[0]-=1
        return
    elif songq[0]>0:
        songq.pop(0)
        songq.pop(0)
        songq.pop(0)
        if songq[0]>0:
            if songq[1].find(".youtube.com/")!=-1  or songq[1].find("/youtu.be/")!=-1:
                 p[0]=subprocess.Popen(["mpv","-fs","-pause","--ytdl-raw-options=format-sort=res:1080", songq[1]])

            else:
                p[0]=subprocess.Popen("ffmpeg -i '"+songq[1]+"' -f matroska - | mpv -fs -pause --force-window=yes -", shell=True)
            fsong[0]+=1
            x[0]=songq[0]
            channel = await client.create_dm(songq[2])
            await channel.send("Your song is up!")
            plays[str(songq[2])]=plays[str(songq[2])]-1
            if songq[3]>0:
                channel = await client.create_dm(songq[5])
                await channel.send("One more song until your turn!")

    else:
        x[0]=0
        flag[0]=True
        return
        

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    

@client.event
async def on_message(message):
    channel = await client.create_dm(message.author)
    if message.author == client.user:
        return

    if message.content.lower().startswith("$addsong"):
        if str(message.author) in plays:
            plays[str(message.author)]=plays[str(message.author)]+1
        else:
            plays[str(message.author)]=1
        if plays[str(message.author)]>10:
            await channel.send("You have too many songs queued")
        else:
            

            if message.content[9:].find("&list")!=-1:
                content=message.content[9:message.content[9:].find("&list")+9]
            else:
                content=message.content[9:]

            try:
                output = str(subprocess.check_output(["yt-dlp", "--get-duration", content]).decode("UTF-8"))
                output=int(output[:output.find(":")])*60+int(output[output.find(":")+1:-1]) 
                print(output)
                total=0
                for i in range(int(len(songq)/3)):
                    total+=songq[int(i)*3]+20
                 
                
                if int(songq[0])>0 or x[0]!=0:
                    await channel.send("Your song is expected to play in: "+str(int((total+x[0]-songq[0])/60))+"m "+str(int((total+x[0]-songq[0])%60))+"s")
                else:
                    await channel.send("Your song is up first")
                songq.pop(-1)
                
                songq.append(output)               
                              
                songq.append(content)
                songq.append(message.author)
                songq.append(-3600)
                titles[content]=subprocess.check_output(["yt-dlp", "--get-title", "--restrict-filenames",  content]).decode("UTF-8")[:-1] 
                
                                
                if not myLoop.is_running():
                    myLoop.start()
            
            except subprocess.CalledProcessError as e:
                plays[str(message.author)]=plays[str(message.author)]-1
                print(e)
                await channel.send("There seems to be an error. Did you enter the link correctly?")
                        
    


    elif message.content.lower().startswith("$addfile"):
        if str(message.author) in plays:
            plays[str(message.author)]=plays[str(message.author)]+1
        else:
            plays[str(message.author)]=1
        
        
        total=0
        for i in range(int(len(songq)/3)):
            total+=songq[int(i)*3]+20
        
        if plays[str(message.author)]>10:
            await channel.send("You have too many songs queued")
        else: 
            if int(songq[0])>0 or x[0]!=0:
                await channel.send("Your song is expected to play in: "+str(int((total+x[0]-songq[0])/60))+"m "+str(int((total+x[0]-songq[0])%60))+"s")
            else:
                await channel.send("Your song is up first")
            temp=str(message.attachments[-1])
            titles[temp]=temp[temp.rfind("/")+1:temp.rfind("?")]
            songq.pop(-1)
            songq.append(get_length(str(message.attachments[-1])))
            songq.append(str(message.attachments[-1]))
            songq.append(message.author)
            songq.append(-3600)
            total=0
            for i in range(int(len(songq)/3)):
                total+=songq[int(i)*3]+20
            
            if not myLoop.is_running():
                myLoop.start()

    
    elif message.content.lower().startswith("$qtime"):
        total=0
        for i in range(int(len(songq)/3)):
            total+=songq[int(i)*3]+20
        await channel.send(str(int((total+x[0]-songq[0])/60))+"m "+str(int((total+x[0]-songq[0]))%60)+"s")
    



    elif message.content.lower().startswith("$nextsong"):
        total=0
        for i in range(int(len(songq)/3)):
            if songq[int(i)*3+2]==message.author:
                break
            else:
                total+=songq[int(i)*3]+20
        total+=x[0]-songq[0]
        await channel.send(str(int(total/60))+"m "+str(total%60)+"s")
    
    

    elif message.content.lower().startswith("$showlist"):
        txtput=""
        y[0]=0
        for i in range(int(len(songq)/3)):
            y[0]+=1
            txtput+=str(y[0]+fsong[0])+" "
            txtput+=(str(songq[i*3+2].display_name)+" - ")
            txtput+=(titles[str(songq[i*3+1])]+'\n')
 
        await channel.send(txtput)
    

    
    elif message.content.lower().startswith("$remove"):
        num = int(message.content[8])
        print(num)
        if num >1:
            num+=fsong[0]-1          
            del songq[num*3]
            del songq[num*3]
            del songq[num*3]

    elif message.content.lower().startswith("$addl"):
        num = int(message.content[8])
        print(num)
        if num >1:
            num+=fsong[0]-1          
            del songq[num*3]
            del songq[num*3]
            del songq[num*3]

    elif message.content.lower().startswith("$adda"):
        num = int(message.content[8])
        print(num)
        if num >1:
            num+=fsong[0]-1          
            del songq[num*3]
            del songq[num*3]
            del songq[num*3]

            
    
client.run('MTE1NjY4MjUwMTcxMzAzOTQ1MQ.G-kEU4.GktzR7x23j0NaZG4VmwXg8MDsrSpnm4VKGTnn4')


