import json
from datetime import datetime
import discord
from discord.ext import commands

from data import UserData


class Jobs(commands.Cog):
    def __init__(self, bot, theme_color):
        self.bot = bot
        self.theme_color = theme_color

        with open("bot/data/jobs_data.json", "r") as jobs_file:
            self.jobs_data = json.load(jobs_file)

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
        embed.add_field(name="You earn", value=f"{job_salary} beans per day")

        await ctx.send(embed=embed)

    @commands.command(name="joblist", aliases=["jl", "jobs"], help="List the jobs that you can take", brief="List available jobs")
    async def jobslist(self, ctx):
        jobs_embed = discord.Embed(title="Available Jobs", color=self.theme_color)

        for job in self.jobs_data:
            if self.jobs_data.index(job) > 0:
                job_name = job["name"]
                job_salary = job["salary"]
                job_requirement = job["streak_requirement"]
                jobs_embed.add_field(name=job_name, value=f"Salary: **{job_salary} beans**\nWork Streak Required: **{job_requirement} days**")

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

        UserData.c.execute("SELECT wallet, job_id, job_streak, last_work_date FROM users WHERE id = :user_id", {"user_id": ctx.author.id})
        data = UserData.c.fetchone()

        current_balance = data[0]
        job_id = data[1]
        current_streak = data[2]
        last_work_date = datetime.strptime(data[3], "%Y-%m-%d %H:%M")
        today = datetime.now()

        if job_id == 0:
            await ctx.send("You're unemployed bro. Get a job...")
            return

        salary = self.jobs_data[job_id]["salary"]
        new_streak = current_streak + 1

        time_diff = (today - last_work_date)

        if time_diff.days > 2:
            new_streak = 1
            await ctx.send("You didn't show up to work yesterday. Your work streak has been reset!")

        elif time_diff.days < 1:
            time_left = 24 - time_diff.total_seconds() / 3600

            if time_left > 1:
                await ctx.send(f"You've done enough work for today, try again in {int(time_left)} hours...")
            else:
                time_left = time_left * 60
                await ctx.send(f"You've done enough work for today, try again in {int(time_left)} minutes...")

            return

        UserData.c.execute(
            "UPDATE users SET wallet = :new_amount, job_streak = :new_streak, last_work_date = :new_lwd WHERE id = :user_id",
            {
                "new_amount": current_balance + salary,
                "new_streak": new_streak,
                "new_lwd": today.strftime("%Y-%m-%d %H:%M"),
                "user_id": ctx.author.id
            }
        )

        UserData.conn.commit()
        await ctx.send(f"You finished a day's worth of work and feel satisfied! You earned **{salary} beans** and you're on a **{new_streak} day** streak!")
