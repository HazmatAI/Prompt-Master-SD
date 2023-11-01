"""
Start the application.
"""
import tracemalloc

tracemalloc.start(25)

from src.main import Bot

if __name__ == "__main__":
    Bot().run()
