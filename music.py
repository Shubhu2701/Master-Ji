import discord
from discord.ext import commands
from wavelink.ext import spotify
import wavelink
import datetime

class music(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.client.loop.create_task(self.node_connect())
        self.vc=None
        self.context=None
        self.player=None
       
    async def node_connect(self):
        await self.client.wait_until_ready()
        await wavelink.NodePool.create_node(bot=self.client,host='lavalinkinc.ml',port=443,password='incognito',https=True,spotify_client=spotify.SpotifyClient(client_id='CLIENT_ID',client_secret='CLIENT_SECRET'))
    
    @commands.Cog.listener()
    async def on_wavelink_node_ready(self, node:wavelink.Node):
        print(f'Node {node.identifier} is ready.')
        
    
    @commands.Cog.listener()
    async def on_wavelink_track_end(self,player:wavelink.Player, track: wavelink.Track, reason):
        if self.vc.loop:
            return await self.vc.play(track)
        next_song=self.vc.queue.get()
        await self.vc.play(next_song)
        mbed=discord.Embed(title=f'Now Playing:\n{next_song.title}', description=f'Artist: {next_song.author}')
        mbed.add_field(name='Duration',value=f"`{datetime.timedelta(seconds=next_song.length)}`")
        mbed.url=next_song.uri
        await self.context.send(embed=mbed) 
    
    async def check_vc(self,ctx:commands.Context):
        if self.player is None:
            await ctx.send(embed=discord.Embed(title=f"Master Ji isn't connected to any voice channel.", color=discord.Color.from_rgb(255, 255, 255)))
            return False
        elif not ctx.author.voice:
            await ctx.send(embed=discord.Embed(title=f"Join a voice channel first.", color=discord.Color.from_rgb(255, 255, 255)))
            return False        
        
    @commands.command(name='play',aliases=['p','PLAY','Play','P'],help='Plays the provided song from youtube.')
    async def play(self, ctx: commands.Context, *args):
        self.context=ctx
        search=' '.join(args)
        joined=await self.join(ctx)
        if self.player is not None and len(search)==0:
            if self.vc.is_paused():
                await self.vc.resume()
                mbed = discord.Embed(title="Playback resumed.", color=discord.Color.from_rgb(255, 255, 255))
            return await ctx.send(embed=mbed)
        try:
            search=await spotify.SpotifyTrack.search(query=search,return_first=True)
            print('spotify search')
            print(search.title) 
        except Exception:
            search=await wavelink.YouTubeTrack.search(query=search, return_first=True)
            print('youtube search')
            
        self.player = wavelink.NodePool.get_node().get_player(ctx.guild)
        if self.vc.queue.is_empty and not self.player.is_playing():
            await self.vc.play(search)
            mbed=discord.Embed(title=f'Now Playing:\n{search.title}', description=f'Artist: {search.author}')
            mbed.add_field(name='Duration',value=f"`{datetime.timedelta(seconds=search.length)}`")
            mbed.url=search.uri
            await ctx.send(embed=mbed) 
        else:
            await self.vc.queue.put_wait(search)
            await ctx.send(embed=discord.Embed(title=f"Added to the queue:\n{search}", color=discord.Color.from_rgb(255, 255, 255)))

    @commands.command(name='skip',aliases=['s','SKIP','Skip','S'],help='Skips the current song being playing.')
    async def skip(self,ctx:commands.Context):
        
        await self.vc.stop()
    
    @commands.command(name='loop',aliases=['l','LOOP','Loop','L'],help='Loops the song playing currently.')  
    async def loop(self,ctx:commands.Context):
        check=self.check_vc(ctx)
        if not check:
            return  
        try:
            self.vc.loop^=True
        except Exception:
            setattr(self.vc, 'loop', False)
        
        if self.vc.loop:
            return await  ctx.send(embed=discord.Embed(title=f"Loop On.", color=discord.Color.from_rgb(255, 255, 255)))
        else:
            return await ctx.send(embed=discord.Embed(title=f"Loop Off.", color=discord.Color.from_rgb(255, 255, 255)))
    
    @commands.command(name='queue',aliases=['q','QUEUE','Queue','Q'],help='Displays all the songs left in the queue.')
    async def queue(self,ctx:commands.Context):
        self.player = wavelink.NodePool.get_node().get_player(ctx.guild)
        check=self.check_vc(ctx)
        if not check:
            return
        
        if self.vc.queue.is_empty:
            return await ctx.send(embed=discord.Embed(title=f"Queue is empty.", color=discord.Color.from_rgb(255, 255, 255)))
        
        mbed=discord.Embed()
        queue=self.vc.queue.copy()
        song_count=0
        for song in queue:
            song_count+=1
            mbed.add_field(name=f'{song_count}', value =f'{song.title}')
        mbed.title=(f'Total songs in queue: {song_count}\n')
        return await ctx.send(embed=mbed)
    
    @commands.command(name='clear',aliases=['c','CLEAR','Clear','C'],help='Clears the queue.')
    async def clear(self,ctx:commands.Context):
        self.player = wavelink.NodePool.get_node().get_player(ctx.guild)
        check=self.check_vc(ctx)
        if not check:
            return
        
        self.vc.queue.clear()
        return await ctx.send(embed=discord.Embed(title=f"Queue Cleared..", color=discord.Color.from_rgb(255, 255, 255)))
              
    @commands.command(name='join',aliases=['j','summon','JOIN','Join','Summon','SUMMON','Cum','cum','CUM'],help='Joins the voice channel.')
    async def join(self, ctx: commands.Context):
        self.player = wavelink.NodePool.get_node().get_player(ctx.guild)       
        if self.player is not None:
            if self.player.is_paused():
                return
        try:
            channel=ctx.author.voice.channel
        except Exception:
            await ctx.send(embed=discord.Embed(title=f"Join a voice channel first.", color=discord.Color.from_rgb(255, 255, 255)))          
            return False
        if self.player is None:
            self.vc=await channel.connect(cls=wavelink.Player)
            setattr(self.vc, 'loop', False)
            # await ctx.send(embed=discord.Embed(title=f"Connected to {channel.name}", color=discord.Color.from_rgb(255, 255, 255)))
            return True
        if self.player is not None:
            if self.player.is_connected() and self.player.channel!=channel:
                await self.player.move_to(channel)
                setattr(self.vc, 'loop', False)
                # await ctx.send(embed=discord.Embed(title=f"Connected to {channel.name}", color=discord.Color.from_rgb(255, 255, 255)))
            return True
        if self.player is None:
            await ctx.send(embed=discord.Embed(title=f"Could not connect to the voice channel. Please try again", color=discord.Color.from_rgb(255, 255, 255)))
            return False

    @commands.command(name='leave',aliases=['dc','LEAVE','Leave','d','disconnect','DISCONNECT','D','Disconnect'],help='Kicks the bot from the voice channel.')
    async def leave(self, ctx: commands.Context):
        check=self.check_vc(ctx)
        if not check:
            return
        
        await self.player.disconnect()
        mbed = discord.Embed(title="Disconnected", color=discord.Color.from_rgb(255, 255, 255))
        await ctx.send(embed=mbed)
    
    @commands.command(name='pause',aliases=['PAUSE','Pause'],help='Pauses the current song being playing.')
    async def pause(self, ctx: commands.Context):
        check=self.check_vc(ctx)
        if not check:
            return
        if not self.player.is_paused():
            if self.player.is_playing():
                await self.player.pause()
                return await ctx.send(embed=discord.Embed(title="Playback Paused.", color=discord.Color.from_rgb(255, 255, 255)))
            else:
                return await ctx.send(embed=discord.Embed(title="Nothing Is playing right now.", color=discord.Color.from_rgb(255, 255, 255)))
    
    @commands.command(name='resume',aliases=['r','RESUME','Resume','R'],help='Resumes the current song being playing.')
    async def resume(self, ctx: commands.Context):
        check=self.check_vc(ctx)
        if not check:
            return
        if self.player.is_paused():
            await self.player.resume()
            return await ctx.send(embed=discord.Embed(title="Playback resumed.", color=discord.Color.from_rgb(255, 255, 255)))
        else:
            return await ctx.send(embed=discord.Embed(title="Playback is not paused.", color=discord.Color.from_rgb(255, 255, 255)))
         
    # @commands.command(name='volume')
    # async def volume(self,ctx:commands.Context, volume:int):
    #     check=self.check_vc(ctx)
    #     if not check:
    #         return
    #     if volume>100:
    #         volume=100
    #     elif volume<0:
    #         volume=0
    #     await self.vc.set_volume(volume)
    #     return await ctx.send(embed=discord.Embed(title=f"Volume : {volume}", color=discord.Color.from_rgb(255, 255, 255))) 
        
    
    @commands.command(name='now',aliases=['n','NOW','Now','N','current','playing'],help='Displays the song playing currently.')
    async def now_playing(self, ctx:commands.Context):
        check=self.check_vc(ctx)
        if not check:
            return
        
        if not self.vc.is_playing():
            return await ctx.send(embed=discord.Embed(title=f"Not playing anything.", color=discord.Color.from_rgb(255, 255, 255)))
        
        mbed=discord.Embed(title=f'Now Playing: {self.vc.track.title}', description=f'Artist: {self.vc.track.author}')
        mbed.add_field(name='Duration',value=f"`{datetime.timedelta(seconds=self.vc.track.length)}`")
        mbed.url=self.vc.track.uri
        return await ctx.send(embed=mbed)
    
def setup(client):
    client.add_cog(music(client))
