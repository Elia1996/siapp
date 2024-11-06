# SIApp
Self Improvement Application

# Mnemotechnique
the memorization app will be written in kivy and python, it will have two possibilities in the menu:
- insertion: here it will be possible to create associations between the Information to remember and the related images according to the PAO ( character, action, object) method. There will be 4 fields (at least one field between Character, action and object must be filled):
    - Information (text)
    - Character( text + image)
    - Action ( text + image)
    - Object ( text + image)
- exercise: here the app will show the user randomly (without repetition until all associations have been tested) the associations in two ways:
    - The thing to memorize -> In this case the user has to remember the PAO association and when he remembers it press a button that shows the saved association ( Character, action, object), at the bottom there will be 3 buttons “right”, “wrong”, “difficult” referring to the association. The 'app saves the response time and the user's selection of right, wrong, difficult.
    - Character, Action or Object - > here the process is reverse and the user has to remember the Information associated with the Character, Action or Object.

During the exercises the app will associate each association with a score based on the response time in one direction (from Information to PAO) and the other ( from each element of PAO to Information). Based on the score and knowing the 1 1 1 rule ( one hour, one day, one week, one month) the app proposes a set of cards so as to maximize memorization by the user.

In particular the database will contain for each association:
- Information (text)
- Character (text + image)
- Action  (text + image)
- Object (text + image)
- Last Response time I to PAO (seconds, float)
- Last Response time PAO to I (seconds, float)
- Creation date (datetime)
- Last repetition date (datetime)
- Number of refresh (int)
- Difficulty (int)
- Retention index (float)

From the fields:
- Last repetition date (datetime)
- Number of refresh (int)
- Difficulty (int)
Will be calculated the retention index each time the user refresh the application or at least once a day.
To decide what to display the retention index will be calculated for each association, the associations will be ordered by retention index (first the lowest) and the first 20 will be displayed in the exercise menu.
If the user finish the 20 associations the app will show a message “You have finished the 20 associations, do you want to continue?” if the user press yes the app will recalculate the retention index and show again the first 20 associations.

The database will be managed with SQLModel and SQLite.