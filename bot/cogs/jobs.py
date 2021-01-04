import json
from datetime import datetime
import discord
from discord.ext import commands

from data import UserData


class Jobs(commands.Cog):
    def __init__(self, bot, theme_color):
        self.bot = bot
        self.theme_color = theme_color
        self.worked_today = {}
        self.date = datetime.now().day

        with open("bot/data/jobs_data.json", "r") as jobs_file:
            self.jobs_data = json.load(jobs_file)

    def check_user_entry(self, user):
        if str(user.id) not in UserData.user_data:
            UserData.create_new_data(user)

        if str(user.id) not in self.worked_today:
            self.worked_today[str(user.id)] = False

    @commands.Cog.listener()
    async def on_message(self, message: discord.Member):
        current_date = datetime.now().day

        if current_date > self.date:
            print("Resetting worked today flags for all users...")

            for key in self.worked_today:
                self.worked_today[key] = False

            self.date = current_date

    @commands.command(name="myjob", aliases=["mj"], help="Shows your current job", brief="Shows your current job")
    async def myjob(self, ctx):
        self.check_user_entry(ctx.author)

        job_id = UserData.get_data(ctx.author, "job_id")

        if job_id is None:
            await ctx.send("You're unemployed bro. Get a job...")
            return

        current_job = self.jobs_data[job_id]

        job_name = current_job["name"]
        job_salary = current_job["salary"]

        embed = discord.Embed(title=f"You are a {job_name}.", color=self.theme_color)
        embed.add_field(name="You earn", value=f"{job_salary} beans per hour")

        await ctx.send(embed=embed)

    @commands.command(name="jobslist", aliases=["jl", "jobs"], help="List the jobs that you can take", brief="List available jobs")
    async def jobslist(self, ctx):
        jobs_embed = discord.Embed(title="Available Jobs", color=self.theme_color)

        for job in self.jobs_data:
            job_name = job["name"]
            job_salary = job["salary"]
            job_requirement = job["streak_requirement"]
            jobs_embed.add_field(name=job_name, value=f"Salary: **{job_salary} beans**, Work Streak Required: **{job_requirement} days**")

        await ctx.send(embed=jobs_embed)

    @commands.command(name="takejob", aliases=["tj"], help="Take up an available job", brief="Take up a job")
    async def takejob(self, ctx, *, job_name: str):
        self.check_user_entry(ctx.author)

        jn = None
        js = None
        jr = None
        current_streak = UserData.get_data(ctx.author, "job_streak")

        for (job_id, job) in enumerate(self.jobs_data):
            if job["name"].lower() == job_name.lower():
                jn = job["name"]
                js = job["salary"]
                jr = job["streak_requirement"]

                if current_streak < jr:
                    await ctx.send(f"You need a **{jr} day** streak to get this job! You're currently on a **{current_streak} day** streak.")
                    return

                UserData.set_data(ctx.author, "job_id", job_id)
                break

        if jn is None or js is None or jr is None:
            return

        embed = discord.Embed(title=f"You have become a {jn}!", color=self.theme_color)
        embed.add_field(name="You will earn", value=f"{js} beans per hour")

        await ctx.send(embed=embed)

    @commands.command(name="work", aliases=["w"], help="Go to work and earn beans. Usable once per day", brief="Earn some beans")
    async def work(self, ctx):
        self.check_user_entry(ctx.author)

        if self.worked_today[str(ctx.author.id)]:
            await ctx.send("You've done enough work for today, give yourself a break...")
            return

        job_id = UserData.get_data(ctx.author, "job_id")

        if job_id is None:
            await ctx.send("You're unemployed bro. Get a job...")
            return

        salary = self.jobs_data[job_id]["salary"]
        UserData.add_data(ctx.author, "wallet", salary)

        self.worked_today[str(ctx.author.id)] = True
        UserData.add_data(ctx.author, "job_streak", 1)
        job_streak = UserData.get_data(ctx.author, "job_streak")

        await ctx.send(f"You finished a day's worth of work and feel satisfied! You earned **{salary} beans** and you're on a **{job_streak} day** streak!")
