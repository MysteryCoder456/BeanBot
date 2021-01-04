import json
import discord
from discord.ext import commands

from data import UserData


class Jobs(commands.Cog):
    def __init__(self, bot, theme_color):
        self.bot = bot
        self.theme_color = theme_color

        with open("bot/data/jobs_data.json", "r") as jobs_file:
            self.jobs_data = json.load(jobs_file)

    def check_user_entry(self, user):
        if str(user.id) not in UserData.user_data:
            UserData.create_new_data(user)

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
            jobs_embed.add_field(name=job_name, value=f"Salary: {job_salary}")

        await ctx.send(embed=jobs_embed)

    @commands.command(name="takejob", aliases=["tj"], help="Take up an available job", brief="Take up a job")
    async def takejob(self, ctx, *, job_name: str):
        self.check_user_entry(ctx.author)

        jn = None
        js = None

        for (job_id, job) in enumerate(self.jobs_data):
            if job["name"].lower() == job_name.lower():
                UserData.set_data(ctx.author, "job_id", job_id)
                jn = job["name"]
                js = job["salary"]
                break

        if jn is None or js is None:
            return

        embed = discord.Embed(title=f"You have become a {jn}!", color=self.theme_color)
        embed.add_field(name="You will earn", value=f"{js} beans per hour")

        await ctx.send(embed=embed)
