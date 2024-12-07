# Deployment

To build the application by yourself, you needs to be in a Linux environment. You can use a virtual machine or a container to build the application.

These are the steps to build the application:

1. Clone the repository:
```bash
git clone https://github.com/Elia1996/siapp
```
2. Change to the project directory:
```bash
cd siapp
```
3. Create the python env and install the dependencies (you need to have [poetry](https://python-poetry.org/) installed):
```bash
poetry install
poetry shell
```
4. Install [Buildozer](https://buildozer.readthedocs.io/en/latest/installation.html):
```bash
python -m pip install buildozer
```
5. Build the application:
```bash
buildozer -v android debug
```
6. The APK will be in the `bin` directory.

If you have to rebuild the application, you should use the `clean` command before building:
```bash
buildozer -v android clean
buildozer -v android debug
```
