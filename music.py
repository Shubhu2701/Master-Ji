import discord
from discord.ext import commands
import youtube_dl

class music(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.playing=False
        self.paused=False
        self.queue=[]
        self.FFMPEG_OPTIONS={
			'before_options':'-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
			'options':'-vn'
		}
        self.YDL_OPTIONS = {'format':'bestaudio','noplaylist':'True'}
        self.vc=None
    
    def search_yt(self,item):
        with youtube_dl.YoutubeDL(self.YDL_OPTIONS) as ydl:
            try:
                info=ydl.extract_info('ytsearch:%s'%item,download=False)['entries'][0]
                raise Failed()
            except Failed:
                info=ydl.extract_info(item,download=False)
            except Exception:
                return False
        return {'source': info['formats'][0]['url'],'title':info['title']}
    
    
    async def nexxt(self):
        if len(self.queue)>0:
            self.playing=True
            curr_url=self.queue[0][0]['source']
            await self.send('Playing '+self.queue[0][0]['title'])
            self.queue.pop(0)
            self.vc.play(discord.FFmpegOpusAudio.from_probe(curr_url,**self.FFMPEG_OPTIONS),after=lambda x:self.nexxt())
        else:
            self.playing=False

    async def moozic(self,ctx):
        if len(self.queue)>0:
            self.playing=True
            curr_url=self.queue[0][0]['source']
            if self.vc == None or not self.vc.is_connected():
                self.vc = await self.queue[0][1].connect()
                if self.vc==None:
                    await ctx.send("Could not connect to the voice channel.")
                    return
            else:
                await self.vc.move_to(self.queue[0][1])
    
            self.queue.pop(0)
            self.vc.play(discord.FFmpegOpusAudio.from_probe(curr_url,**self.FFMPEG_OPTIONS),after=lambda x:self.nexxt())
        else:
            self.playing=False
            
    @commands.command(name='play',aliases=['p','PLAY','Play','P'],help='Plays the provided song from youtube.')
    async def play(self,ctx,*args):
        url=' '.join(args)
        try:
            voice_channel=ctx.author.voice.channel
        except Exception:
            await ctx.send('Join a voice channel!')
            return
            
        if self.paused:
            self.vc.resume()
        else:
            song=self.search_yt(url)
            if type(song)==type(True):
                await ctx.send('Couldn\'t play the song, Incorrect format or url.')
            else:
                await ctx.send('Song added to the queue.'+'\n'+'`'+song['title']+'`')
                self.queue.append([song,voice_channel])
                if self.playing==False:
                    await self.moozic(ctx)

    @commands.command(name='pause',aliases=['PAUSE','Pause'],help='Pauses the current song being playing.')
    async def pause(self,ctx,*args):
        if self.playing:
            self.playing=False
            self.paused=True
            self.vc.pause()
            await ctx.send('Paused ⏸')
        elif self.paused:
            self.playing=True
            self.paused=False
            self.vc.resume()
            await ctx.send('Playing ▶')
            
    @commands.command(name='resume',aliases=['r','RESUME','Resume','R'],help='Resumes the current song being playing.')
    async def resume(self,ctx,*args):
        if self.paused:
            self.playing=True
            self.paused=False
            self.vc.resume()
            await ctx.send('Playing ▶') 
            
    @commands.command(name='skip',aliases=['s','SKIP','Skip','S'],help='Skips the current song being playing.')
    async def skip(self,ctx,*args):
        if self.vc!=None and self.vc:
            self.vc.stop()
            await self.moozic(ctx)          
            
    @commands.command(name='queue',aliases=['q','QUEUE','Queue','Q'],help='Displays all the songs left in the queue.')
    async def queue(self,ctx,*args):
        string=''
        for i in range(0,len(self.queue)):
            if i>10: break
            string+='`'+self.queue[i][0]['title']+'`'+'\n'
        
        if string!='':
            await ctx.send(string)
        else:
            await ctx.send('The queue is empty, Use ~play command to play some songs')

    @commands.command(name='clear',aliases=['c','CLEAR','Clear','C'],help='Clears the queue.')
    async def clear(self,ctx,*args):
        if self.vc!=None and self.playing:
            self.vc.stop()
        self.queue=[]
        await ctx.send('Queue cleared!')

    @commands.command(name='leave',aliases=['l','L','LEAVE','Leave','d','disconnect','DISCONNECT','D','Disconnect'],help='Kicks the bot from the voice channel')
    async def leave(self,ctx):
        self.playing=False
        self.paused=False
        await self.vc.disconnect()
        
def setup(client):
    client.add_cog(music(client))
