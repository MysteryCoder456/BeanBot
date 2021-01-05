import json
from datetime import datetime
import discord
from discord.ext import commands

from data import UserData


class Jobs(commands.Cog):
    def __init__(self, bot, theme_color):
        self.bot = bot
        self.theme_color = theme_color
        self.date = datetime.now().day

        with open("bot/data/jobs_data.json", "r") as jobs_file:
            self.jobs_data = json.load(jobs_file)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Member):
        current_date = datetime.now().day

        if current_date > self.date:
            print("Resetting worked today flags for all users...")
            UserData.c.execute("UPDATE users SET worked_today = 0")
            UserData.conn.commit()
            self.date = current_date

    @commands.command(name="myjob", aliases=["mj"], help="Shows your current job", brief="Shows your current job")
    async def myjob(self, ctx):
        UserData.check_user_entry(ctx.author)

        # Get the user's job_id
        UserData.c.execute("SELECT job_id FROM users WHERE id = :user_id", {"user_id": ctx.author.id})
        job_id = UserData.c.fetchone()[0]

        if job_id == 0:
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
            if self.jobs_data.index(job) > 0:
                job_name = job["name"]
                job_salary = job["salary"]
                job_requirement = job["streak_requirement"]
                jobs_embed.add_field(name=job_name, value=f"Salary: **{job_salary} beans**, Work Streak Required: **{job_requirement} days**")

        await ctx.send(embed=jobs_embed)

    @commands.command(name="takejob", aliases=["tj"], help="Take up an available job", brief="Take up a job")
    async def takejob(self, ctx, *, job_name: str):
        UserData.check_user_entry(ctx.author)

        jn = None
        js = None
        jr = None

        # Get current work streak
        UserData.c.execute("SELECT job_streak FROM users WHERE id = :user_id", {"user_id": ctx.author.id})
        current_streak = UserData.c.fetchone()[0]

        for (job_id, job) in enumerate(self.jobs_data):
            if job["name"].lower() == job_name.lower():
                jn = job["name"]
                js = job["salary"]
                jr = job["streak_requirement"]

                if current_streak < jr:
                    await ctx.send(f"You need a **{jr} day** streak to get this job! You're currently on a **{current_streak} day** streak.")
                    return

                # Set user's job_id to specified job
                UserData.c.execute("UPDATE users SET job_id = :job_id WHERE id = :user_id", {"job_id": job_id, "user_id": ctx.author.id})
                UserData.conn.commit()
                break

        if jn is None or js is None or jr is None:
            return

        embed = discord.Embed(title=f"You have become a {jn}!", color=self.theme_color)
        embed.add_field(name="You will earn", value=f"{js} beans per hour")

        await ctx.send(embed=embed)

    @commands.command(name="work", aliases=["w"], help="Go to work and earn beans. Usable once per day", brief="Earn some beans")
    async def work(self, ctx):
        UserData.check_user_entry(ctx.author)

        UserData.c.execute("SELECT wallet, job_id, job_streak, worked_today FROM users WHERE id = :user_id", {"user_id": ctx.author.id})
        data = UserData.c.fetchone()

        current_balance = data[0]
        job_id = data[1]
        current_streak = data[2]
        worked_today = bool(data[3])

        # Check if the user worked today
        if worked_today:
            await ctx.send("You've done enough work for today, give yourself a break...")
            return

        if job_id == 0:
            await ctx.send("You're unemployed bro. Get a job...")
            return

        salary = self.jobs_data[job_id]["salary"]
        new_streak = current_streak + 1

        UserData.c.execute(
            "UPDATE users SET wallet = :new_amount, job_streak = :new_streak, worked_today = 1 WHERE id = :user_id",
            {
                "new_amount": current_balance + salary,
                "new_streak": new_streak,
                "user_id": ctx.author.id
            }
        )
        UserData.conn.commit()

        await ctx.send(f"You finished a day's worth of work and feel satisfied! You earned **{salary} beans** and you're on a **{new_streak} day** streak!")
