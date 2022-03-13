#Josh Muszka, Dec 2021 - Feb 2022
#A Discord bot for a private geography club server
#Memes, geography facts, inside jokes, trivia games, and more

#NAMES/PERSONAL INFO HAVE BEEN REPLACED WITH *****, AS WELL AS THE BOT TOKEN (for obvious reasons)

import discord
import random
import praw
import os
import asyncio
from time import time

reddit = praw.Reddit(client_id = "iQ-tTl7DjI-H9pxMqXJVnQ",
                    client_secret = "70YmKuAe7_ohob5OP_Qmo1MIU9X-gg",
                    username = "geoclubbot",
                    password = "brehemaJR67",
                    user_agent = "Geo Club Bot")


intents = discord.Intents.default()
intents.members = True

# Client (the bot)
client = discord.Client(intents=intents)


#GLOBAL VARIABLES

previous_fact = "" #for geo.trivia
previous_wisdom = "" #for geo.wisdom
correct_answer = "" #for geo.trivia
ghost_round_counter = 0 #for geo.trivia
triviaIsRunning = False #for geo.trivia

now = 0 #for gif cooldown
prev_time = 0

#for geo.trivia, to keep track of players in a trivia game
class TriviaUsers:
    user_name = ""
    score = 0
    hasScoredThisRound = False

u = TriviaUsers()
user_list = [] #list to hold TriviaUsers




#method to count lines in a text file
def line_count(file):
    line_counter = 0

    with open (file) as f:
        fact = f.readlines()

        for line in fact:
            line_counter+=1

        return (line_counter)



@client.event
async def on_ready(): #runs whenever the client goes online
    await client.change_presence(activity=discord.Game(name="winning"))
    ctx = client.get_channel(745484084041613342) 
    #await ctx.send("I am online")


@client.event
async def on_message(message):
    ctx = message.channel

    #redeclaring globals for the trivia game feature, because python
    global user_list
    global correct_answer
    global u
    global ghost_round_counter

    global now
    global prev_time

    #GEO.HELP COMMAND
    if message.content == 'geo.help':

        #delete message sent by user
        await message.channel.purge(limit=1) 

        #Create an embed containing a list of all commands
        helpEmbed = discord.Embed(title="Commands", color=0xFAD900)
        helpEmbed.add_field(name=":earth_americas: geo.help", value="Brings up this panel containing all commands", inline="False")
        helpEmbed.add_field(name=":earth_americas: geo.fact", value="Learn a cool new geography fact", inline="False")
        helpEmbed.add_field(name=":earth_americas: geo.trivia", value="Play a game of geography trivia", inline="False")
        helpEmbed.add_field(name=":earth_americas: geo.wisdom", value="Only if you can handle pure knowledge", inline="False")
        helpEmbed.add_field(name=":earth_americas: geo.meme", value="haha funny but with geography", inline="False")
        helpEmbed.add_field(name=":earth_americas: geo.info", value="Geo Club information", inline="False")
        helpEmbed.add_field(name=":earth_americas: geo.moderation", value="List of commands for server moderation", inline="False")
        helpEmbed.set_footer(text="Geo Club winningest club")
        helpEmbed.set_author(name="Geo Club Bot")

        await ctx.send(embed=helpEmbed) #send embed


    #brings up a list of moderation commands
    if message.content == "geo.moderation":
        await message.channel.purge(limit=1) #delete message sent by user

        #create an embed containing a list of moderation commands
        modEmbed = discord.Embed(title="Server Moderation", color=0xFAD900)
        modEmbed.add_field(name="geo.clear n", value="Auto-clear n amount of messages", inline="False")
        modEmbed.set_author(name="Owner and admins may use these commands")

        await ctx.send(embed=modEmbed)
        

    #sends a random geography fact
    if message.content == 'geo.fact':

        #delete message sent by user
        await message.channel.purge(limit=1) 

        #open the text file containing the facts
        with open('facts.txt', 'r') as f:

            global previous_fact

            #add each fact to a list of facts
            fact_list = f.readlines()
            fact = fact_list[random.randint(0,line_count('facts.txt')-1)] #choose a random fact

            #so that facts don't repeat twice in a row
            while fact == previous_fact:
                fact = fact_list[random.randint(0,line_count('facts.txt')-1)]

            await ctx.send(fact)
            previous_fact = fact #remember the fact that was just sent, to avoid two of the same in a row next time




    #starts a trivia game, where it sends a question, an image, and four options (with one being the correct answer)
    #it keeps track of each player's score
    if message.content == 'geo.trivia':

        #delete message sent by user
        await message.channel.purge(limit=1) 

        global triviaIsRunning
        global user_list

        if triviaIsRunning:
            #so that two trivia games can't run at once (would be too confusing)
            await ctx.send("Trivia game already in progress")
        else:

            #function to count the number of files in the images folder
            def file_count(list):
                file_counter = 0
                for files in list:
                    file_counter+=1
                return file_counter

            
            triviaIsRunning = True #effectively starts the game

            await ctx.send("Get ready for some trivia! Use **geo.stoptrivia** to end trivia")

            u = TriviaUsers()
            u.user_name = message.author.name #add the user who initiated the game to the user list
            user_list.append(u)

            #trivia loop
            while triviaIsRunning:

                ghost_round_counter+=1
                #ghost_round_counter gets reset to 0 every time someone answers
                #so that if theres two rounds in a row where no one answers, game ends to avoid going on forever


                #each time the while loop iterates, a new "round" with a new question is displayed, so reset this to false
                for user in user_list:
                    user.hasScoredThisRound = False


                await asyncio.sleep(3)
                #get random image and parse number from file name
                path = "images"
                dir_list = os.listdir(path)
                trivia_number = dir_list[random.randint(0,file_count(dir_list)-1)] #choose a random image from the folder
                picture = "images/" + trivia_number #to save the file as reference for when it's embedded
                trivia_number = os.path.splitext(trivia_number)[0]



                #find corresponding information in triviaanswers.txt
                #ie. if image 2 is chosen, find question 2 in the text file

                with open("triviaanswers.txt") as f:
                    file = f.readlines()

                    file[0] = str.rstrip(file[0])
                    trivia_number = str(trivia_number)

                    #trivia info
                    question = ""
                    answer_a = ""
                    answer_b = ""
                    answer_c = ""
                    answer_d = ""

                    #go through each line until it finds the number
                    for index, lines in enumerate(file):

                        file[index] = str.rstrip(file[index])

                        if file[index] == trivia_number:
                            #fill in variables with appropriate data
                            question = file[index+1]
                            answer_a = file[index+2]
                            answer_b = file[index+3]
                            answer_c = file[index+4]
                            answer_d = file[index+5]
                            break

                    #the * is in the text file to let the program know it's the correct answer
                    global correct_answer

                    if answer_a[0] == "*":
                        answer_a = answer_a.strip("*")
                        correct_answer = "a"
                    if answer_b[0] == "*":
                        answer_b = answer_b.strip("*")
                        correct_answer = "b"
                    if answer_c[0] == "*":
                        answer_c = answer_c.strip("*")
                        correct_answer = "c"
                    if answer_d[0] == "*":
                        answer_d = answer_d.strip("*")
                        correct_answer = "d"


                #create an embed containing the question, image, and possible answers
                triviaEmbed = discord.Embed(title="Question:", color=0xFAD900)
                file = discord.File(picture, filename="image.png")
                triviaEmbed.set_image(url="attachment://image.png")

                triviaEmbed.add_field(name = question, value=("A. " + answer_a + "\nB. " + answer_b + "\nC. " + answer_c + "\nD. " + answer_d))

                await ctx.send(file = file, embed = triviaEmbed) #send the embed


                #wait 15 seconds to reveal correct answer
                await asyncio.sleep(15)
                await ctx.send("The correct answer is " + correct_answer + "!")

                #reset user answer checkers
                for user in user_list:
                    user.hasScoredThisRound = False

                #if 2 rounds without any answers
                if ghost_round_counter >= 2:
                    await ctx.send("Ending game due to inactivity. Use **geo.trivia** to start again")
                    triviaIsRunning = False #end game


        if triviaIsRunning == False:

            end_embed = discord.Embed(title="Trivia finished", color=0xFAD900)

            results = ""

            for user in user_list:
                results = results + "\n" + user.user_name + " - " + str(user.score)


            end_embed.add_field(name = "Final Scores:", value = results)

            await asyncio.sleep(3)
            await ctx.send(embed = end_embed)


            #remove users from user_list after trivia is done

            user_list.clear()
            



    #geo.stoptrivia
    if message.content == 'geo.stoptrivia':

        #delete message sent by user
        await message.channel.purge(limit=1) 

        if triviaIsRunning:
            triviaIsRunning = False #end game
        else:
            await ctx.send("No trivia game is currently active")



    #geo.wisdom
    if message.content == 'geo.wisdom':

        #delete message sent by user
        await message.channel.purge(limit=1) 

        #exact same procedure as geo.fact
        with open('wisdom.txt', 'r') as w:
            wisdom_list = w.readlines()
            global previous_wisdom

            wisdom = wisdom_list[random.randint(0,line_count("wisdom.txt")-1)]
            while wisdom == previous_wisdom:
                wisdom = wisdom_list[random.randint(0,line_count("wisdom.txt")-1)]

            await ctx.send(wisdom)
            previous_wisdom = wisdom






    #geo.meme, finds a random post from r/geographymemes on reddit
    if message.content == 'geo.meme':

        #delete message sent by user
        await message.channel.purge(limit=1) 

        subreddit = reddit.subreddit("geographymemes")
        all_subs = []


        hot = subreddit.hot(limit = 150)

        for submission in hot:
           all_subs.append(submission)

        random_sub = 0
        while random_sub == 0 or random_sub.is_self:
            random_sub = random.choice(all_subs)
        name = random_sub.title
        url = random_sub.url

        memeEmbed = discord.Embed(title = name)
        memeEmbed.set_image(url = url)

        await ctx.send(embed = memeEmbed)           


    #sends an embed containing our club's information (personal info has been censored)
    if message.content == 'geo.info':

        #delete message sent by user
        await message.channel.purge(limit=1) 

        infoEmbed = discord.Embed(title="Info", color=0xFAD900)
        infoEmbed.add_field(name="Club founder:", value="Ben Woodward (2015)", inline="False")
        infoEmbed.add_field(name="Current president:", value="Matthew Woodward", inline="false")
        infoEmbed.add_field(name="Former presidents:", value="Ben Woodward, Daniel Innes, Matthew Woodward", inline="false")
        infoEmbed.add_field(name="Geo Club Hall of Fame:", value="[Click here](https://docs.google.com/document/d/1rwhp_dL4SIHdHF-K-rFZLcnawzjrxWcNmQkxXyGV03g/edit?usp=sharing)", inline="False")
        infoEmbed.add_field(name="Bot created by:", value="Josh Muszka", inline="False")

        await ctx.send(embed=infoEmbed)




    #if someone enters a multiple choice answer while trivia is running
    if str.lower(message.content) == 'a' or str.lower(message.content) == 'b' or str.lower(message.content) == 'c' or str.lower(message.content) == 'd':
        
        if triviaIsRunning:

            ghost_round_counter = 0

            #add users to user_list
            if len(user_list) == 0: 
                u = TriviaUsers()
                u.user_name = message.author.name
                user_list.append(u)
            else:
                u = TriviaUsers()
                u.user_name = message.author.name
                user_list.append(u)
                for index, user in enumerate(user_list):

                    if index == len(user_list) - 1:
                        break

                    if message.author.name == user.user_name:
                        user_list.remove(u)
                        break
            


            #check if user has already answered, and award points accordingly
            for user in user_list:
                if user.hasScoredThisRound == False:                    
                    if str.lower(message.content) == correct_answer and message.author.name == user.user_name:
                        user.score+=10
                        break

            #so that the user can only score once
            for user in user_list:
                if message.author.name == user.user_name and user.hasScoredThisRound == False:
                    user.hasScoredThisRound = True
                    break



    #spam ping andrew command
    #andrew is a person in the server we like to mess with, so is some code that does just that
    if message.content == "geo.andrew":

        #delete message sent by user
        await message.channel.purge(limit=1)     

        for i in range(5):
            await ctx.send(f"<@{425705608923185152}> ", delete_after=1)
        
    #clear messages command
    if "geo.clear" in message.content:
        if (message.content).index("geo.clear") == 0:

            #if user is owner, or admin
            guild = ctx.guild
            owner = discord.utils.get(guild.roles, id=656967501724385280)
            admin = discord.utils.get(guild.roles, id=656968274399199232)

            if owner in message.author.roles or admin in message.author.roles:
                arguments = []
                arguments = (message.content).split(" ")    
                quantity = arguments[1]

                if len(arguments) == 1:
                    await ctx.send("Error, must specify number of messages to delete (ie. geo.clear 4)")
                if len(arguments) == 2:
                    if quantity.isnumeric():
                        quantity = int(quantity)
                        if quantity > 0 and quantity <= 100:
                            await message.channel.purge(limit=1)#delete message sent by user
                            await message.channel.purge(limit=quantity)#purge specified number of messages

                            if (quantity == 1): message = quantity + " message cleared"
                            else: message = str(quantity) + " messages cleared"
                            await ctx.send(message, delete_after=3) #send confirmation message
                            
                        else:
                            await ctx.send("Error, number must be between 1 and 100")
                    else: await ctx.send("Error, argument must be numeric")
                else: 
                    await ctx.send("Error, must specify number of messages to delete (ie. geo.clear 4)")
                if len(arguments) >= 3:
                    await ctx.send("Error, must specify number of messages to delete (ie. geo.clear 4)")
            else:
                await ctx.send("Error, you do not have permission to use this command")



    #ALL THESE GIFS ARE INSIDE JOKES OF THE SERVER
    #if someone sends a message containing a certain word, bot replies with a certain gif


    # now = time()
    # if now - prev_time >= 300: #if it has been 5 minutes since last gif was sent

    #     prev_time = time()

    #     #rock gif
    #     if str.casefold("sex") in str.casefold(message.content) or str.casefold("seggs") in str.casefold(message.content) or str.casefold("seck") in str.casefold(message.content) or str.casefold("cum") in str.casefold(message.content):
    #         await message.reply(file=discord.File('gifs/rock.gif'))

    #     #turkey gif
    #     if str.casefold("turkey") in str.casefold(message.content) or str.casefold("turbkey") in str.casefold(message.content) or str.casefold("turkiye") in str.casefold(message.content) or str.casefold("türkiye") in str.casefold(message.content):
    #         if not message.author.name == "Geo Club Bot":
    #             await message.reply(file=discord.File('gifs/turkey.gif'))

    #     #genshin gif
    #     if str.casefold("genshin") in str.casefold(message.content):
    #         await message.reply(file=discord.File('gifs/genshin.gif'))

    #     #turkey is european argument
    #     if str.casefold("turkey") in str.casefold(message.content) or str.casefold("türkiye") in str.casefold(message.content):

    #         if str.casefold("european") in str.casefold(message.content) or str.casefold("europe") in str.casefold(message.content):
    #             if not message.author.name == "Geo Club Bot":
    #                 await message.reply("TÜRKIYE IS NOT EUROPE :flag_tr::flag_tr::flag_tr::flag_tr::flag_tr::flag_tr:")
    #                 await message.channel.send("TÜRKIYE NUMBER ONE BESTEST COUNTRIE")

    #     #send ben shapiro gif
    #     if str.casefold("shapiro") in str.casefold(message.content) or str.casefold("liberal") in str.casefold(message.content) or str.casefold("libtard") in str.casefold(message.content) or str.casefold("fact") in str.casefold(message.content) or str.casefold("logic") in str.casefold(message.content):
    #         if not message.author.name == "Geo Club Bot":
    #             if not message.content == "geo.fact":
    #                 await message.reply(file=discord.File('gifs/shapiro.gif'))


    #if bot gets pinged
    mention = f'<@!{client.user.id}>'
    if mention in message.content:
        await message.channel.send(f"no u <@{message.author.id}>")

    #play command
    if "geo.play" in message.content:
        if (message.content).index("geo.play") == 0:
            args= []
            args = (message.content).split(" ")

            if len(args) >= 2:
                song = ""

                for i in range(len(args)):
                    if not i == 0:
                        song += args[i]
                        song+= " "

                msg = "Now playing " + song
                await message.channel.send(msg)

                voice_channel = discord.utils.get(ctx.guild.voice_channels, name="General")
                await voice_channel.connect()

            else: await message.channel.send("Error: Must enter a song title")

    #disconnect command
    if message.content == "geo.disconnect":
        await ctx.guild.voice_client.disconnect()

#send a welcome message (inside jokes again)
@client.event
async def on_member_join(member):
    geochannel = client.get_channel(656668781535428618)
    await geochannel.send(file=discord.File('gifs/jungle.gif'))
    await asyncio.sleep(3)

    await geochannel.send(f"Hello <@{member.id}>, let me tell you about how geo club is a lifestyle. Its not just a club, it becomes you. Every day oyu will have to get up at 6am and list of all the nations alphabetically. You will soon also be seeing vision of shitty alt history maps in your head, and arguing with turkish nationalists online if turkey is European or not. You will know more useless trivia then you ever needed to. But why, why do we do this? We do this to win, this club is shouldn't be called geo club, it should be called the dub's club cause of how many fat dubs we get.  I dont even need to call this the winingiest team because unlike beta cuck reach, or sigma hosa or whatever the fuck is around now,  gigachad geo club does not need to prove anything to anybody. Welcom, have a sick time, and thany you for listening to my ted talk. -Daniel Innes to Winnes")


#if andrew starts typing a message in the server
@client.event
async def on_typing(ctx, user, when):
    if user.id == 425705608923185152:
        await ctx.send("STFU ANDREW DON'T EVEN FINISH TYPING", delete_after=4)

# Run the client on the server
client.run(TOKEN) #bot token, censored
