<!--
Copyright (c) 2024 Elia Ribaldone.

This file is part of SiApp 
(see https://github.com/Elia1996/siapp).

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.-->
# SIApp
Self Improvement Application, here it is the [documentation](https://elia1996.github.io/siapp/).

# Time Management

- ✅ Hourslog:  The app is able to record your work hours using a check-in/out button.
 For each day are calculated the work, lunch and break hours.
 
 ![alt text](resources/image.png)


# Mnemotechnique
The Mnemotechnique part is composed of two sections at the moment:

- ✅ **PAO Insertion**: The user can insert a Person-Action-Object (PAO) triplet and the corresponding information to associate with it. Both for the triplet and the information is possible to add an image.
- ✅ **PAO Base Training**: In this screen the app will display an element of a random PAO triplet or a random information associated with a PAO triplet. The user can then try to remember the other elements and when he is ready he can check if he was right. The response time is saved and used to assign a score to each association, this score is used to decide which association to show next according to the [Forgetting Curve](https://en.wikipedia.org/wiki/Forgetting_curve).

- ✅ **PAO Training**: Here is the real training which has this process:
    - A sequence of informations is proposed to the user (the number of informations is decided by the app depending on the user's performance).
    - The user has to memorize the sequence.
    - When he is ready he can write down the sequence and check if he was right.
    - The response time is saved and used to modify the score of each association used in the sequence.

- 🛠️ **PAO Stats**: Statistics about the training, this data are in a specific screen to avoid distraction to user while training.

# Plan 
- PAO Insertion:
    - ✅ 
- PAO Base Training:
    - ✅ Show the mean, min and max time on the top. 
- PAO Stats:
    - 🛠️ Create the page
    - 🛠️ Display min, max and mean response time divided by I to PAO and PAO to I.
    - 🛠️ Graph of the mean response time during past training day.

# License
This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.
I used this command to add the license header to all the files:
```bash
licenseheaders -t lgplv3 -o "Elia Ribaldone" -y 2024 -n SiApp -u "https://github.com/Elia1996/siapp" -d siapp
```

# Github Workflow

The workflow is in the [.github/workflows](.github/workflows) folder.

At the moment github workflow doesn't work due to some problems with buildozer in the pipeline. I've still to figure out how to solve this problem.