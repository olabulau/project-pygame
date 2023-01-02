# Minesweeper in Pygame

Originally written in MonkeyX for my A level project, now recreated in Python with the Pygame library.

![Screenshot of game](https://marleysudbury.github.io/minesweeper/screen1.png)

## Improvements on the original

* The leaderboard actually works
* You can right click twice to put a question mark
* Cross platform (MonkeyX is supposed to be cross-platform, but it was always glitchy/broken on MacOS)

## Requires

* Python 3.6.1
* Pygame 2.0.1

## Installation

Once Python 3.6.1 is installed onto your system, navigate to the directory where you want to install the game, then clone the repoistory with `git clone https://github.com/marleysudbury/minesweeper-pygame` (if you don't have git, you can download the repository as a .zip). Then go into the folder (`cd minesweeper-pygame`) and create virtual environment (venv) with `python3 -m venv venv`.

Activate the venv with `source venv/bin/activate` on MacOS or `venv\Scripts\activate.bat` on Windows. Install Pygame in the venv with `pip install pygame`.

## Running

Whilst in the venv, run the command `python3 game.py`. For quickstart, try `python3 game.py -quick`, `python3 game.py -quick medium` or `python3 game.py -quick hard`. For touchscreen compatability (WIP), try `python3 game.py -touch`.

## Other

To see the page about this on my website, click [here](https://marleysudbury.github.io/minesweeper).

For original click [here](https://github.com/marleysudbury/Minesweeper).

This version is not yet fully complete (see [issues](https://github.com/marleysudbury/minesweeper-pygame/issues)), but should be soon.
