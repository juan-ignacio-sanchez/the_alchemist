import cProfile
import pstats
from pstats import SortKey

from src.TheAlchemist import main as real_main


if __name__ == "__main__":
    cProfile.run("real_main()", "profile.txt")

    p = pstats.Stats("profile.txt")
    p.strip_dirs().sort_stats(SortKey.TIME).print_stats(10)
