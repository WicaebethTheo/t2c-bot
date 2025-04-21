from .lancement import TeyLancement

async def setup(bot):
    await bot.add_cog(TeyLancement(bot))
