# Detect the folder name and start the bot
__import__(
    (lambda path: 
        getattr(path, 'basename')(getattr(path, 'dirname')(__file__))
    )(__import__('os.path', fromlist=['dirname', 'basename']).os.path)
).bot.run()

# TL;DR
# import <botname>
# <botname>.bot.run()
