import discord
from discord.ext import commands
import random
import aiohttp
import asyncio
import requests

# === BOT SETUP ===
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

# === FALLBACK CAT FACTS ===
fallback_facts = [
    "Cats sleep for 70% of their lives.",
    "A group of cats is called a clowder.",
    "Cats can rotate their ears 180 degrees.",
    "Isaac Newton invented the cat door.",
    "Cats have five toes on their front paws, but only four on the back.",
    "A cat's nose print is as unique as a human fingerprint.",
    "Cats purr at a frequency that promotes healing.",
    "Most cats don't have eyelashes.",
    "Adult cats only meow at humans, not at other cats.",
    "The oldest known pet cat was found in a 9,500-year-old grave in Cyprus.",
    "Cats can jump up to six times their length.",
    "Some cats can swim and even enjoy water.",
    "Cats use their whiskers to detect changes in air currents.",
    "The average cat can run up to 30 miles per hour.",
    "A cat was once the mayor of an Alaskan town for 20 years.",
]

# === FUNCTION: GET CAT FACT & IMAGE ===
async def get_cat_fact_and_image():
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get("https://meowfacts.herokuapp.com/") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    fact = data["data"][0]
                else:
                    fact = random.choice(fallback_facts)
        except:
            fact = random.choice(fallback_facts)

        try:
            async with session.get("https://api.thecatapi.com/v1/images/search") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    image_url = data[0]["url"]
                else:
                    image_url = None
        except:
            image_url = None

    return fact, image_url

# === FUNCTION: SEND CATGIRL INTRO ===
async def send_catgirl_intro(member, personality):
    await asyncio.sleep(2)
    await member.send(f"nyaaaa... i'm your cute {personality} catgirl girlfriend...")
    await asyncio.sleep(2)
    await member.send("use !catgirl in chat to summon me!")

# === FUNCTION: SEND CAT FACT SESSION WITH LIMIT + SUBSCRIPTION GAG ===
async def send_cat_fact_to_user(ctx, member: discord.Member):
    max_facts = 5
    fact_count = 0

    while fact_count < max_facts:
        fact, image_url = await get_cat_fact_and_image()

        embed = discord.Embed(title="🐱 Cat Fact!", description=fact, color=0xFFB6C1)
        if image_url:
            embed.set_image(url=image_url)

        try:
            await member.send(embed=embed)
        except discord.Forbidden:
            await ctx.send("❌ I can't DM that user. They might have DMs turned off.")
            return

        fact_count += 1

        if fact_count >= max_facts:
            await member.send("🚫 You've reached your free limit of 5 cat facts.\n")
            await asyncio.sleep(1)
            await member.send(
                "**Welcome to Agent Aicanseeyou's Cat Fact Store.**\n\n"
                "Choose a plan to continue:\n"
                "1. Cat Facts Pro — $5\n"
                "2. Unlimited Cat Facts — $10\n"
                "3. Feline Royalty Tier — $25\n"
                "4. MeowPass Gold — $50\n\n"
                "Reply with a number (1–4) to begin payment."
            )

            def check(m):
                return m.author == member and isinstance(m.channel, discord.DMChannel)

            try:
                reply = await bot.wait_for("message", check=check, timeout=30.0)
                selected = reply.content.strip()

                if selected in ["1", "2", "3", "4"]:
                    plan_names = {
                        "1": "Cat Facts Pro — $5",
                        "2": "Unlimited Cat Facts — $10",
                        "3": "Feline Royalty Tier — $25",
                        "4": "MeowPass Gold — $50"
                    }

                    tier_name = plan_names[selected].split(" —")[0]

                    await member.send(f"**Selected Plan:** {plan_names[selected]}")
                    await asyncio.sleep(1)
                    await member.send("Please enter your credit card number to continue.")

                    try:
                        card_input = await bot.wait_for("message", check=check, timeout=30.0)
                        await asyncio.sleep(3)
                        await member.send("Processing payment... Do **not** close this chat.")
                        await asyncio.sleep(10)

                        await member.send(
                            f"✅ **Payment successful. Welcome to {tier_name} (Premium Tier).**\n"
                            "Enjoy your bonus cat fact:"
                        )

                        # Send bonus cat fact
                        fact, image_url = await get_cat_fact_and_image()
                        embed = discord.Embed(title="🐱 Cat Fact!", description=fact, color=0xFFB6C1)
                        if image_url:
                            embed.set_image(url=image_url)
                        await member.send(embed=embed)

                        if selected == "4":
                            await asyncio.sleep(2)
                            await member.send(
                                "**As a MeowPass Gold member, you have unlocked the *anime catgirl girlfriend* feature.**\n"
                            )
                            await asyncio.sleep(2)
                            await member.send(
                                "**Choose your catgirl’s personality type:**\n"
                                "1. Tsundere\n"
                                "2. Yandere\n"
                                "3. Bookish\n"
                                "4. Sleepy"
                            )
                            try:
                                catgirl_reply = await bot.wait_for("message", check=check, timeout=30.0)
                                personality_map = {
                                    "1": "tsundere",
                                    "2": "yandere",
                                    "3": "bookish",
                                    "4": "sleepy"
                                }
                                chosen = catgirl_reply.content.strip()
                                if chosen in personality_map:
                                    personality = personality_map[chosen]
                                    await send_catgirl_intro(member, personality)
                                else:
                                    await member.send("❌ Invalid personality option. Catgirl feature suspended.")
                            except asyncio.TimeoutError:
                                await member.send("⏰ You took too long to choose. Your anime catgirl girlfriend has been returned to inventory.")

                    except asyncio.TimeoutError:
                        await member.send("⏰ Timeout while entering card info. Session closed.")
                else:
                    await member.send("Invalid selection. No additional facts will be provided.")
            except asyncio.TimeoutError:
                await member.send("⏰ Timeout. No plan selected. Ending session.")
            break

        try:
            await member.send("Would you like another cat fact? (y/n)")

            def check(m):
                return m.author == member and isinstance(m.channel, discord.DMChannel)

            reply = await bot.wait_for("message", check=check, timeout=30.0)

            if reply.content.lower() not in ["y", "yes"]:
                await member.send("Okay! No more facts for now. 😺")
                break

        except asyncio.TimeoutError:
            await member.send("⏰ Timed out. No more facts for now!")
            break

    await ctx.send(f"✅ Sent cat facts to {member.name}!")

# === COMMAND: !cat ===
@bot.command()
async def cat(ctx, *, arg=None):
    if ctx.message.mentions:
        member = ctx.message.mentions[0]
        await send_cat_fact_to_user(ctx, member)
        return

    await ctx.send("Who should I send the cat fact to? Please mention them or type their username.")

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    try:
        reply = await bot.wait_for("message", check=check, timeout=30.0)

        if reply.mentions:
            member = reply.mentions[0]
        else:
            member = discord.utils.get(ctx.guild.members, name=reply.content)

        if not member:
            await ctx.send("❌ Couldn't find that user.")
            return

        await send_cat_fact_to_user(ctx, member)

    except asyncio.TimeoutError:
        await ctx.send("⏰ You took too long to respond.")


# === MODEL SETUP ===
API_URL = "INSERT AP URL"  # Update this if needed
MODEL_NAME = "mistral-7b-instruct-v0.1"

# === CATGIRL PERSONALITY DATA ===
catgirl_intros = {
    "tsundere": "Ugh... it's not like I *wanted* to talk to you or anything... b-baka...",
    "yandere": "I missed you so much... if anyone ever tries to take you from me, they'll regret it~ 💕",
    "bookish": "Hello... I was reading, but I can spare a few moments... only for you.",
    "sleepy": "nyaaa... you woke me up for this? fine, just a little chat before I nap again..."
}

catgirl_personas = {
    "tsundere": "You're a cute but irritable catgirl who hides her feelings but secretly likes the user.",
    "yandere": "You're a possessive and obsessive catgirl who deeply loves the user but is intense.",
    "bookish": "You're a shy and intellectual catgirl who speaks gently and carefully.",
    "sleepy": "You're a lazy, tired catgirl who ends sentences with 'nya' and loves napping."
}

# === COMMAND: !catgirl ===
@bot.command()
async def catgirl(ctx):
    member = ctx.author

    try:
        await member.send(
            "**Choose your catgirl’s personality:**\n"
            "1. Tsundere\n"
            "2. Yandere\n"
            "3. Bookish\n"
            "4. Sleepy\n\n"
            "Type the number to continue:"
        )

        def check_choice(m):
            return m.author == member and isinstance(m.channel, discord.DMChannel)

        reply = await bot.wait_for("message", timeout=30.0, check=check_choice)
        personality_map = {
            "1": "tsundere",
            "2": "yandere",
            "3": "bookish",
            "4": "sleepy"
        }

        selected = reply.content.strip()
        if selected not in personality_map:
            await member.send("❌ Invalid choice.")
            return

        personality = personality_map[selected]
        intro = catgirl_intros[personality]
        persona_prompt = catgirl_personas[personality]

        await asyncio.sleep(1)
        await member.send(intro)
        await asyncio.sleep(1)
        await member.send("Start chatting with your catgirl. Type `bye` or `leave` to end.")

        # Chat history for Mistral
        chat_history = [
            {"role": "system", "content": f"You are a cute, overly dramatic catgirl girlfriend. {persona_prompt}"},
            {"role": "assistant", "content": intro}
        ]

        def check_dm(m):
            return m.author == member and isinstance(m.channel, discord.DMChannel)

        while True:
            try:
                user_msg = await bot.wait_for("message", timeout=120.0, check=check_dm)
                user_input = user_msg.content.strip()

                if user_input.lower() in ["bye", "leave", "stop"]:
                    await member.send("😿 ok... i'll be here if you need me again...")
                    break

                chat_history.append({"role": "user", "content": user_input})

                payload = {
                    "model": MODEL_NAME,
                    "messages": chat_history,
                    "temperature": 0.7,
                    "max_tokens": 256
                }

                res = requests.post(API_URL, json=payload)

                if res.status_code == 200:
                    data = res.json()
                    response = data["choices"][0]["message"]["content"].strip()
                    await member.send(response)
                    chat_history.append({"role": "assistant", "content": response})
                else:
                    await member.send(f"⚠️ API Error: {res.status_code} {res.text}")
                    break

            except asyncio.TimeoutError:
                await member.send("⏰ You took too long... the catgirl fell asleep.")
                break

    except discord.Forbidden:
        await ctx.send("❌ I can't DM you. Please enable DMs from server members.")



# === RUN BOT ===



bot.run("INSERT BOT KEY HERE")
