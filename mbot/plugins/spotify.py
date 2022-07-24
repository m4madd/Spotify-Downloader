"""MIT License

Copyright (c) 2022 Daniel

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
from asyncio import sleep
#from mbot.utils.progress import progress
from mbot import AUTH_CHATS, LOGGER, Mbot,LOG_GROUP
from pyrogram import filters
from mbot.utils.mainhelper import parse_spotify_url,fetch_spotify_track,download_songs,thumb_down,copy,forward 
from mbot.utils.ytdl import getIds,ytdl_down,audio_opt
import spotipy
from os import mkdir
import os
import shutil
from random import randint
import random
#import eyed3 
from mutagen import File
from mutagen.flac import FLAC ,Picture
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
client = spotipy.Spotify(auth_manager=spotipy.oauth2.SpotifyClientCredentials())
#PICS = ("mbot/1162775.jpg mbot/danny-howe-bn-D2bCvpik-unsplash.jpg mbot/saurabh-gill-38RthwbB3nE-unsplash.jpg").split()
BUG = "" #put your log group id here for error logs 
@Mbot.on_message(filters.regex(r'https?://open.spotify.com[^\s]+') & filters.incoming &  ~filters.edited | filters.regex(r'https?://open.spotify.com[^\s]+') & filters.command(["spotify","spotdl"]) | filters.incoming & ~filters.edited & filters.regex(r"spotify:") & filters.chat(AUTH_CHATS))
async def spotify_dl(_,message):
    link = message.matches[0].group(0)
    #seep = await sleep (0.9)
    m = await message.reply_text(f"⏳")
    n = await message.reply_chat_action("typing")

    try:
        parsed_item = await parse_spotify_url(link)
        item_type, item_id = parsed_item[0],parsed_item[1]
        randomdir = f"/tmp/{str(randint(1,100000000))}"
        mkdir(randomdir)
        if item_type in ["show", "episode"]:
            items = await getIds(link)
            for item in items:
                cForChat = await message.reply_chat_action("record_audio")
                sleeeps = await sleep (0.9)
                PForCopy = await message.reply_photo(item[5],caption=f"✔️ نام اپیزود : `{item[3]}`\n🕔 مدت زمان : {item[4]//60}:{item[4]%60}")
                fileLink = await ytdl_down(audio_opt(randomdir,item[2]),f"https://open.spotify.com/episode/{item[0]}")
                thumbnail = await thumb_down(item[5],item[0])
                sleeping  = await sleep(2.0)
                DForChat =  await message.reply_chat_action("upload_audio")
                #reply = await message.reply_text(f"با عرض پوزش ما پشتیبانی از این قسمت را حذف کرده ایم 😔")
                AForCopy = await message.reply_audio(fileLink,title=item[3].replace("_"," "),performer="Spotify",duration=int(item[4]),caption=f"[{item[3]}](https://open.spotify.com/episode/{item[0]})",thumb=thumbnail,parse_mode="markdown",quote=True)
                shutil.rmtree(randomdir)
                if LOG_GROUP:
                    await sleep(3.5)
                    await copy(PForCopy,AForCopy)
            return await m.delete()
        elif item_type == "track":
            song = await fetch_spotify_track(client,item_id)
            cForChat = await message.reply_chat_action("record_audio")
            #sleeeps = await sleep (0.9)
            PForCopy = await message.reply_photo(song.get('cover'),caption=f"🎧 عنوان : `{song['name']}`\n🎤 هنرمند : `{song['artist']}`\n💽 آلبوم : `{song['album']}`\n🗓 سال انتشار : `{song['year']}`")
            path = await download_songs(song,randomdir)
            thumbnail = await thumb_down(song.get('cover'),song.get('deezer_id'))
            dForChat = await message.reply_chat_action("upload_audio")
            audio = FLAC(path)
            audio["YEAR_OF_RELEASE"] = song.get('year')
            audio["WEBSITE"] = "https://t.me/Spowtifybot"
            audio["GEEK_SCORE"] = "9"
            audio["ARTIST"] = song.get('artist')                                                                            
            audio["ALBUM"] = song.get('album')
            audio.save()
            audi = File(path)
            image = Picture()
            image.type = 3
            if thumbnail.endswith('png'):
               mime = 'image/png'
            else:
                 mime = 'image/jpeg'
            image.desc = 'front cover'
            with open(thumbnail, 'rb') as f: # better than open(albumart, 'rb').read() ?
                  image.data = f.read()

            audi.add_picture(image)
            audi.save()
            AForCopy = await message.reply_audio(path,performer=f"{song.get('artist')}",title=f"{song.get('name')} - {song.get('artist')}",caption=f"[{song.get('name')}](https://open.spotify.com/track/{song.get('deezer_id')}) | {song.get('album')} - {song.get('artist')}",thumb=thumbnail, parse_mode="markdown",quote=True)
            feedback = await message.reply_text(f"انجام شد✅",   
             reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="Feedback", callback_data="feed")]]))
            shutil.rmtree(randomdir)
            if LOG_GROUP:
                await sleep(2.5)
                await copy(PForCopy,AForCopy)
            return await m.delete()
        elif item_type == "playlist":
            tracks = client.playlist_items(playlist_id=item_id,additional_types=['track'], limit=40, offset=0, market=None)
            total_tracks = tracks.get('total')
            for track in tracks['items']:
                song = await fetch_spotify_track(client,track.get('track').get('id'))
                cForChat = await message.reply_chat_action("record_audio")
               #sleeeps = await sleep (0.9)
                PForCopy = await message.reply_photo(song.get('cover'),caption=f"🎧 عنوان : `{song['name']}`\n🎤 هنرمند : `{song['artist']}`\n💽 آلبوم : `{song['album']}`\n🗓 سال انتشار : `{song['year']}`\n🔢 Track No: `{song['playlist_num']}`\n🔢 Total Track: `{total_tracks}`")
                path = await download_songs(song,randomdir)
                thumbnail = await thumb_down(song.get('cover'),song.get('deezer_id'))
                cForChat = await message.reply_chat_action("upload_audio")
                sleeping  = await sleep(0.8)
                audio = FLAC(path)
                audio["YEAR_OF_RELEASE"] = song.get('year')
                audio["WEBSITE"] = "https://t.me/Spowtifybot"
                audio["GEEK_SCORE"] = "9"
                audio["ARTIST"] = song.get('artist')                                                                           
                audio["ALBUM"] = song.get('album')
                audio.save()
                audi = File(path)
                image = Picture()
                image.type = 3
                if thumbnail.endswith('png'):
                    mime = 'image/png'
                else:
                    mime = 'image/jpeg'
                image.desc = 'front cover'
                with open(thumbnail, 'rb') as f: # better than open(albumart, 'rb').read() ?
                   image.data = f.read()

                audi.add_picture(image)
                audi.save()
                AForCopy = await message.reply_audio(path,performer=song.get('artist'),title=f"{song.get('name')} - {song.get('artist')}",caption=f"[{song.get('name')}](https://open.spotify.com/track/{song.get('deezer_id')}) | {song.get('album')} - {song.get('artist')}",thumb=thumbnail,parse_mode="markdown",quote=True)
                feedback = await message.reply_text(f"انجام شد✅",   
                 reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="بازخورد", callback_data="feed")]]))
                shutil.rmtree(randomdir)
                if LOG_GROUP:
                    await sleep(2.5)
                    await copy(PForCopy,AForCopy)
            return await m.delete()
        elif item_type == "album":
            tracks = client.album_tracks(album_id=item_id, limit=40, offset=0, market=None)
            for track in tracks['items']:
                song = await fetch_spotify_track(client,track.get('id'))
               #sleeeps = await sleep (0.9)
                PForCopy = await message.reply_photo(song.get('cover'),caption=f"🎧 عنوان : `{song['name']}`\n🎤 هنرمند : `{song['artist']}`\n💽 آلبوم : `{song['album']}`\nq🗓 سال انتشار: `{song['year']}`")
                path = await download_songs(song,randomdir)
                thumbnail = await thumb_down(song.get('cover'),song.get('deezer_id'))
                sleeping  = await sleep(0.8)
                audio = FLAC(path)
                audio["YEAR_OF_RELEASE"] = song.get('year')
                audio["WEBSITE"] = "https://t.me/Spowtifybott"
                audio["GEEK_SCORE"] = "9"
                audio["ARTIST"] = song.get('artist')                                                                         
                audio["ALBUM"] = song.get('album')
                audio.save()
                audi = File(path)
                image = Picture()
                image.type = 3
                if thumbnail.endswith('png'):
                   mime = 'image/png'
                else:
                    mime = 'image/jpeg'
                image.desc = 'front cover'
                with open(thumbnail, 'rb') as f: # better than open(albumart, 'rb').read() ?
                   image.data = f.read()

                audi.add_picture(image)
                audi.save()
                AForCopy = await message.reply_audio(path,performer=song.get('artist'),title=f"{song.get('name')} - {song.get('artist')}",caption=f"[{song.get('name')}](https://open.spotify.com/track/{song.get('deezer_id')}) | {song.get('album')} - {song.get('artist')}",thumb=thumbnail,parse_mode="markdown",quote=True)
                feedback = await message.reply_text(f"انجام شد✅",   
                  reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="بازخورد", callback_data="feed")]]))
                shutil.rmtree(randomdir)
                if LOG_GROUP:
                    await sleep(2.5)
                    await copy(PForCopy,AForCopy)
            return await m.delete()
                   
    except Exception as e:
        LOGGER.error(e)
        K = await m.edit_text(e)
        H = await message.reply_text(f"انجام شد✅",   
             reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="خطا شناسایی شد", callback_data="bug")]]))
        await message.reply_text(f"😛فایل با موفقیت آپلود شد")
        await forward(K,H)

@Mbot.on_callback_query(filters.regex(r"feed"))
async def feedback(_,query):
      await query.message.edit(f"بازخورد 🏴‍☠️",
                  reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="Press here", url="https://t.me/dailychannelsbot?start=spotify_downloa_bot")]]))

@Mbot.on_callback_query(filters.regex(r"bug"))                                                                                                          
async def bug(_,query):                                                                                                                                  
      await query.message.edit(f"لطفا با پیام خطای بالا به من گزارش دهید😶‍🌫️")
      await sleep(2.3)
      await query.message.edit(f"گزارش باگ 🪲",
                  reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="❤️‍🔥گزارش به من ", url="https://t.me/MMd_6")]]))
