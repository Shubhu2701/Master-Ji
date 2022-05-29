import discord
from discord.ext import commands
import wavelink

class music(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.client.loop.create_task(self.node_connect())
        self.vc=None
        self.context=None
        
       
    async def node_connect(self):
        await self.client.wait_until_ready()
        await wavelink.NodePool.create_node(bot=self.client,host='lavalinkinc.ml',port=443,password='incognito',https=True)
    
    @commands.Cog.listener()
    async def on_wavelink_node_ready(self, node:wavelink.Node):
        print(f'Node {node.identifier} is ready.')
    
    @commands.Cog.listener()
    async def on_wavelink_track_end(self,player:wavelink.Player, track: wavelink.Track, reason):
        if self.vc.loop:
            return await self.vc.play(track)
        next_song=self.vc.queue.get()
        await self.vc.play(next_song)
        await self.context.send(embed=discord.Embed(title=f"Now Playing: {next_song.title}", color=discord.Color.from_rgb(255, 255, 255)))
        
    @commands.command(name='play',aliases=['p','PLAY','Play','P'],help='Plays the provided song from youtube.')
    async def play(self, ctx: commands.Context, *args):
        player = wavelink.NodePool.get_node().get_player(ctx.guild)
        self.context=ctx
        search=' '.join(args)
        joined=await self.join(ctx)
        if player is not None and len(search)==0:
            if self.vc.is_paused():
                await self.vc.resume()
                mbed = discord.Embed(title="Playback resumed.", color=discord.Color.from_rgb(255, 255, 255))
            return await ctx.send(embed=mbed)
        search = await wavelink.YouTubeTrack.search(query=search, return_first=True)
        player = wavelink.NodePool.get_node().get_player(ctx.guild)
        if self.vc.queue.is_empty and not player.is_playing():
            await self.vc.play(search)
            await ctx.send(embed=discord.Embed(title=f"Now Playing: {search.title}", color=discord.Color.from_rgb(255, 255, 255))) 
        else:
            await self.vc.queue.put_wait(search)
            await ctx.send(embed=discord.Embed(title=f"Added to the queue: {search}", color=discord.Color.from_rgb(255, 255, 255)))

    @commands.command(name='skip',aliases=['s','SKIP','Skip','S'],help='Skips the current song being playing.')
    async def skip(self,ctx:commands.Context):
        player=wavelink.NodePool.get_node().get_player(ctx.guild)
        if player is None:
            return await ctx.send(embed=discord.Embed(title=f"Not playing anything.", color=discord.Color.from_rgb(255, 255, 255)))
        elif not ctx.author.voice:
            return await ctx.send(embed=discord.Embed(title=f"Join a voice channel first.", color=discord.Color.from_rgb(255, 255, 255)))
        await self.vc.stop()
    
    @commands.command(name='loop',aliases=['l','LOOP','Loop','L'],help='Loops the song playing currently.')  
    async def loop(self,ctx:commands.Context):
        player = wavelink.NodePool.get_node().get_player(ctx.guild)
        if player is None:
            return await ctx.send(embed=discord.Embed(title=f"Not playing anything.", color=discord.Color.from_rgb(255, 255, 255)))
        elif not ctx.author.voice:
            return await ctx.send(embed=discord.Embed(title=f"Join a voice channel first.", color=discord.Color.from_rgb(255, 255, 255)))
        
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
        player = wavelink.NodePool.get_node().get_player(ctx.guild)
        if player is None:
            return await ctx.send(embed=discord.Embed(title=f"Not playing anything.", color=discord.Color.from_rgb(255, 255, 255)))
        elif not ctx.author.voice:
            return await ctx.send(embed=discord.Embed(title=f"Join a voice channel first.", color=discord.Color.from_rgb(255, 255, 255)))
        
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
        player = wavelink.NodePool.get_node().get_player(ctx.guild)
        if player is None:
            return await ctx.send(embed=discord.Embed(title=f"Not playing anything.", color=discord.Color.from_rgb(255, 255, 255)))
        elif not ctx.author.voice:
            return await ctx.send(embed=discord.Embed(title=f"Join a voice channel first.", color=discord.Color.from_rgb(255, 255, 255)))
        
        self.vc.queue.clear()
        return await ctx.send(embed=discord.Embed(title=f"Queue Cleared..", color=discord.Color.from_rgb(255, 255, 255)))
              
    @commands.command(name='join',aliases=['j','summon','JOIN','Join','Summon','SUMMON','Cum','cum','CUM'],help='Joins the voice channel.')
    async def join(self, ctx: commands.Context):
        player = wavelink.NodePool.get_node().get_player(ctx.guild)
        
        if player is not None:
            if player.is_paused():
                return
        try:
            channel=ctx.author.voice.channel
        except Exception:
            await ctx.send(embed=discord.Embed(title=f"Join a voice channel first.", color=discord.Color.from_rgb(255, 255, 255)))          
            return False
        if player is None:
            self.vc=await channel.connect(cls=wavelink.Player)
            setattr(self.vc, 'loop', False)
            # await ctx.send(embed=discord.Embed(title=f"Connected to {channel.name}", color=discord.Color.from_rgb(255, 255, 255)))
            return True
        if player is not None:
            if player.is_connected() and player.channel!=channel:
                await player.move_to(channel)
                setattr(self.vc, 'loop', False)
                # await ctx.send(embed=discord.Embed(title=f"Connected to {channel.name}", color=discord.Color.from_rgb(255, 255, 255)))
            return True
        if player is None:
            await ctx.send(embed=discord.Embed(title=f"Could not connect to the voice channel. Please try again", color=discord.Color.from_rgb(255, 255, 255)))
            return False

    @commands.command(name='leave',aliases=['dc','LEAVE','Leave','d','disconnect','DISCONNECT','D','Disconnect'],help='Kicks the bot from the voice channel.')
    async def leave(self, ctx: commands.Context):
        player = wavelink.NodePool.get_node().get_player(ctx.guild)

        if player is None:
            return await ctx.send(embed=discord.Embed(title="Master Ji isn't connected to any voice channel.", color=discord.Color.from_rgb(255, 255, 255)))
        
        await player.disconnect()
        mbed = discord.Embed(title="Disconnected", color=discord.Color.from_rgb(255, 255, 255))
        await ctx.send(embed=mbed)
    
    @commands.command(name='pause',aliases=['PAUSE','Pause'],help='Pauses the current song being playing.')
    async def pause(self, ctx: commands.Context):
        player = wavelink.NodePool.get_node().get_player(ctx.guild)

        if player is None:
            return await ctx.send(embed=discord.Embed(title="Master Ji isn't connected to any voice channel.", color=discord.Color.from_rgb(255, 255, 255)))
        
        if not player.is_paused():
            if player.is_playing():
                await player.pause()
                return await ctx.send(embed=discord.Embed(title="Playback Paused.", color=discord.Color.from_rgb(255, 255, 255)))
            else:
                return await ctx.send(embed=discord.Embed(title="Nothing Is playing right now.", color=discord.Color.from_rgb(255, 255, 255)))
    
    @commands.command(name='resume',aliases=['r','RESUME','Resume','R'],help='Resumes the current song being playing.')
    async def resume(self, ctx: commands.Context):
        player = wavelink.NodePool.get_node().get_player(ctx.guild)

        if player is None:
            return await ctx.send(embed=discord.Embed(title="Master Ji isn't connected to any voice channel.", color=discord.Color.from_rgb(255, 255, 255)))
        
        if player.is_paused():
            await player.resume()
            return await ctx.send(embed=discord.Embed(title="Playback resumed.", color=discord.Color.from_rgb(255, 255, 255)))
        else:
            return await ctx.send(embed=discord.Embed(title="Playback is not paused.", color=discord.Color.from_rgb(255, 255, 255)))
                

def setup(client):
    client.add_cog(music(client))
