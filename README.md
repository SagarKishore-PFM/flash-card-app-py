# Flash Card App

Written entirely in Python 3.6.x, this customizable [GRE][gre] flashcard app uses the [Kivy][kivy] library for GUI, and [Oxford's REST API][oxford] to fetch definitions, example sentences, synonyms, and antonyms. Includes features to add new words and create and customize your own stacks.

[gre]: https://www.ets.org/gre
[kivy]: https://kivy.org/
[oxford]: https://developer.oxforddictionaries.com/

# Installation

- Please ensure you are using `python 3.6.x`

## Clone
- Clone this repo to your local machine using https://github.com/SagarKishore-PFM/flash-card-app-py.git

## Installing Requirements

- Create and activate a virtual environment. (Here is how you do it in [Anaconda][Anaconda], [Virtualenv][Venv], [Pipenv][Pipenv].)

[Anaconda]: https://uoa-eresearch.github.io/eresearch-cookbook/recipe/2014/11/20/conda/
[Venv]: https://virtualenv.pypa.io/en/latest/userguide/#usage
[Pipenv]: https://docs.pipenv.org/en/latest/install/#installing-pipenv

- Now install all the packages from the `requirements.txt` file

```shell
(your-venv)$ pip install -r requirements.txt
```

## Usage


- Once your virtual environment is activated and all the required packages are installed, run the file ```main.py``` in your terminal.

```shell
(your-venv)$ python3 ./main.py
```

- You should see a few preinstalled databases and an option to create your own. A Database here refers to an instance of the class `FCDataBase` which has a **unique** name, and a list of `Stacks` and `Words`.

- `FCDataBase` name, as mentioned before, must be unique, and cannot start with numbers or spaces and should not contain special characters (Only spaces and hyphens allowed, **case-sensitive**). 

- For your new `FCDataBase`, you can clone a `Word` database (*recommended*) from existing databases or start clean.
    > `Stack` databases will not be copied over. **Only** the selected `Word` database gets cloned.

![Exploring FCDatabase Screen](http://g.recordit.co/Vm7rWuPWMh.gif)

- Each Database contains links to the Stacks List screen and Words List screen.

  - Stack List screen allows you to **create/practice/edit/delete** a `Stack`.  Similarly, the Word List screen allows you to **add/view/delete** a `Word`.

- `Stack` names, like `FCDataBase` names, must be unique, and cannot start with numbers or spaces and should not contain special characters (Only spaces and hyphens allowed, **case-sensitive**).

- To practice, click on the chosen `Stack` and click on the `Practice Selected Stack` button. Here you can reset the Stack's progress if needed. 

- Example practice session...

![Example practice Session](http://g.recordit.co/eep1vVEN87.gif)

## Other notable features


- Saves progress on exit.
- Caches audio clips, downloaded from the net, for each session. Deletes the cached audio files upon closing the app.
- A search bar to search for `Words` in the Word List screen.
- *Add Word* functionality checks for existing and invalid words.

![Word List screen functionalities](http://g.recordit.co/GS2FuyY4TK.gif)

- Crude UI :grin:

## Contribute


- Report bugs and issues here on github.
- There are a few features such as -- adding a timer, tracking and reporting on progress over time, that could be added.
- Pull Requests are always welcome.


## License and Author Info

- Flash Card App is available under the MIT license. See [LICENSE][MIT] for more information.

[MIT]: LICENSE

## References and Acknowledgments


- [Magoosh GRE Vocabulary Flashcards][magoosh] (on which my app is based).
- [Barron's 333][333] list.


[magoosh]: https://gre.magoosh.com/flashcards/vocabulary/decks
[333]: https://quizlet.com/2832581/barrons-333-high-frequency-words-flash-cards/