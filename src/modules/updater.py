import os
import subprocess
import requests
import json
import zipfile
import shutil
from queue import Queue
from threading import Thread

from .view import addText
from .utility import getenv, getTime
from .store import getGameState

# ----- Main Functions ----- #
def start(app, ctk, lockable, textbox, options):
    addText(f"", textbox)
    addText(f"[INFO] Beginning process at {getTime()}.", textbox)

    # Lock user input
    addText(f"[INFO] Locking user input.", textbox)
    lock = lockElements(lockable)
    lock(True)

    # Bundling all variables to pass them around throughout the script
    gameState = getGameState()
    variables = {
        "app": app,
        "ctk": ctk,
        "exepath": gameState['executable'],
        "instpath": gameState['instance'],
        "options": options,
        "root": getenv("nazpath"),
        "tmp": os.path.join(getenv("nazpath"), "_update_tmp"),
        "textbox": textbox,
        "version": getLatestVersion("1.20.1"),
        "lock": lock,
    }

    # Error Handling
    if (handleErrors(variables)):
        addText(f"[INFO] Unlocking user input.", textbox)
        lock(False)
        addText(f"[INFO] Finished process at {getTime()}.", textbox)
        return
    
    # Skip updating process if nuver is equal to latest ver
    if (onLatestVersion(variables)):
        finalize(variables)
        return

    # Clean up temp directory
    cleanUpdateDirectories(variables)

    # Download latest modpack version
    downloadModpack(variables)

    # Unzip update to temp directory
    extractModpack(variables)

    # Retrieve all of the mod files
    retrieveMods(variables)


# The update is split into multiple functions to allow for all of the mods to be retrieved
# before installing the actual update.
def resume_update(variables):
    # Install the update into the instance
    installUpdate(variables)

    # Store update's version number
    storeVersionNumber(variables)

    # Run the final bit of code
    finalize(variables)


# This is split so that it can be ran after resume_update finishes or before updating (if nuver is equal to
# latest ver)
def finalize(vars_):
    options, textbox, lock, exepath, app = [
        vars_["options"],
        vars_["textbox"],
        vars_["lock"],
        vars_["exepath"],
        vars_["app"]
    ]

    # Unlock the program
    addText(f"[INFO] Unlocking user input.", textbox)
    lock(False)

    # Debug mode stops exe from launching
    if (not options["debug"]):
        executed = executeLauncher(textbox=textbox, exepath=exepath)
        if (not executed):
            return
    else:
        addText("[INFO] The executable is not launched whilst in debug mode.", textbox)

                    
    addText(f"[INFO] Finished process at {getTime()}.", textbox)

    # Check if auto close is enabled; close if so
    if (options["autoclose"]):
        addText("[INFO] Auto close is enabled; closing app.", textbox)
        app.quit()


# ----- Helper Functions ----- #
def lockElements(elements):
    def lock(lock):
        if lock:
            for element in elements:
                element.configure(state="disabled")
        else:
            for element in elements:
                element.configure(state="normal")

    return lock


def handleErrors(vars_):
    textbox, exepath, instpath = [
        vars_["textbox"],
        vars_["exepath"],
        vars_["instpath"]
    ]
    error = False

    addText("[INFO] Validating the provided executable and instance paths.", textbox)

    # Ensure the path was provided.
    if instpath == "":
        addText("[ERROR] Please provide a path to your Minecraft instance.", textbox)
        error = True
    else:
        # Ensure the path is valid.
        if not os.path.exists(instpath):
            addText("[ERROR] The provided path to your Minecraft instance doesn't exist.", textbox)
            error = True

    # Ensure the path was provided.
    if exepath == "":
        addText("[ERROR] Please provide a path to your launcher's executable.", textbox)
        error= True
    else:
        # Ensure the path is valid.
        if not os.path.isfile(exepath):
            addText("[ERROR] The provided path to your launcher doesn't exist.", textbox)
            error =  True
        
    
    return error


def cleanUpdateDirectories(vars_):
    tmp, textbox = [
        vars_["tmp"],
        vars_["textbox"]
    ]
    # Delete any existing tmp directory
    if os.path.exists(tmp):
        addText("[INFO] Pruning old tmp directory.", textbox)
        shutil.rmtree(tmp)
    else:
        addText("[INFO] Creating tmp directory.", textbox)

    # Create clean tmp directory
    os.mkdir(tmp)


def getLatestVersion(version):
    def parseJson(obj):
        return {
            "name": obj["name"],
            "url": obj["files"][0]["url"]
        }
    
    req = requests.get(f"https://api.modrinth.com/v2/project/nazarick-smp/version?game_versions=[\"{version}\"]")
    data = json.loads(req.text)
    parsed = list(map(parseJson, data))
    return parsed[0]


def onLatestVersion(vars_):
    version_name, instpath = [
        vars_["version"]["name"],
        vars_["instpath"]
    ]
    nuver_path = os.path.join(instpath, "nuver")

    # Handle existing install
    if (os.path.exists(nuver_path)):
        with open(os.path.join(instpath, "nuver"), "rb") as f:
            last_version_name = f.read().decode("UTF-8")
            if (version_name == last_version_name):
                addText(f"[INFO] You are already on the latest version ({version_name}); skipping update.", vars_["textbox"])
                return True
            
    # Handle first install
    else:
        addText("[INFO] Sanitizing instance for initial install.", vars_["textbox"])
        instconfigpath = os.path.join(instpath, "config")
        if (os.path.exists(instconfigpath)):
            shutil.rmtree(instconfigpath)
            os.mkdir(instconfigpath)
        return False


def storeVersionNumber(vars_):
    version_name, textbox, instpath = [
        vars_["version"]["name"],
        vars_["textbox"],
        vars_["instpath"]
    ]

    addText(f"[INFO] Storing new version ID for future ref: {version_name}.", textbox)
    open(os.path.join(instpath, "nuver"), "w").write(version_name)


def downloadModpack(vars_):
    textbox, tmp, version = [
        vars_["textbox"],
        vars_["tmp"],
        vars_["version"]
    ]

    addText(f"[INFO] Downloading latest version: {version['name']}.", textbox)

    # Download the mrpack as .zip
    req = requests.get(version["url"], allow_redirects=True)
    open(os.path.join(tmp, "update.zip"), "wb").write(req.content)


def extractModpack(vars_):
    textbox, tmp = [
        vars_["textbox"],
        vars_["tmp"]
    ]

    addText("[INFO] Extracting the modpack zip.", textbox)
    with zipfile.ZipFile(os.path.join(tmp, "update.zip"), "r") as ref:
        ref.extractall(tmp)


def retrieveMods(vars_):
    tmp, textbox, debug = [
        vars_["tmp"],
        vars_["textbox"],
        vars_["options"]["debug"]
    ]

    # read modrinth.index.json
    with open(os.path.join(tmp, "modrinth.index.json"), "rb") as f:
        mods = json.loads(f.read().decode("UTF-8"))["files"]

        addText("[INFO] Retrieving any mods not present in the modpack zip:", textbox)

        # Create a queue and set max amount of threads
        queue = Queue(maxsize=0)
        num_threads = 2
        stop_threads = False

        # Keeps the thread alive while they do work
        def keep_alive(queue, stop):
          while True:
            # Kill thread flag handling
            if stop():
                break

            # Get the values for the task
            items = queue.get()
            func = items[0]
            args = items[1:]

            # Run the task and mark it as done
            func(*args)
            queue.task_done()
            
        # Initialize the threads
        for i in range(num_threads):
            if (debug):
                addText(f"[INFO] Creating thread #{i + 1}.", textbox)
            worker = Thread(target=keep_alive, args=(queue, lambda: stop_threads))
            worker.setDaemon(True)
            worker.start()

        # Populate the queue with tasks
        for mod in mods:
            queue.put([retrieve, mod, vars_])

        # This allows for joining all the threads in a non-blocking manner (so the GUI can
        # update). It signifies the end of the queue.
        def join(queue, variables):
            queue.join()

            # Stop threads
            if (debug):
                addText("[INFO] Stopping all threads.", textbox)
            nonlocal stop_threads
            stop_threads = True

            # Continue updating
            addText("[INFO] Finished retrieving missing mods.", textbox)
            resume_update(variables)
            return

        # Start up queue.join monitoring thread
        joiner = Thread(target=join, args=(queue, vars_))
        joiner.setDaemon(True)
        joiner.start()


def retrieve(mod, vars_):
    _, name = os.path.split(mod["path"])
    textbox, instpath, tmp = [
        vars_["textbox"],
        vars_["instpath"],
        vars_["tmp"]
    ]

    # Split path to get mod name and join with instpath
    localpath = os.path.join(instpath, "mods", name)
    destination = os.path.join(tmp, "overrides", "mods", name)

    # Copy file if it exists locally; otherwise, download it.
    if os.path.isfile(localpath):
        addText(f"[INFO] (C) {name.split('.jar')[0]}.", textbox)
        shutil.copyfile(localpath, destination)
    else:
        addText(f"[INFO] (D) {name.split('.jar')[0]}.", textbox)
        req = requests.get(mod["downloads"][0], allow_redirects=True)
        open(destination, "wb").write(req.content)


def installUpdate(vars_):
    instpath, tmp, textbox = [
        vars_["instpath"],
        vars_["tmp"],
        vars_["textbox"]
    ]

    # Paths
    modsdest = os.path.join(instpath, "mods")
    configdest = os.path.join(instpath, "config")
    yosbrpath = os.path.join(instpath, "config", "yosbr")

    modstmp = os.path.join(tmp, "overrides", "mods")
    configtmp = os.path.join(tmp, "overrides", "config")

    # Remove old mods path and move updated mods to instance
    addText("[INFO] Moving updated mods into the provided instance location.", textbox)
    if (os.path.exists(modsdest)):
        shutil.rmtree(modsdest)
    shutil.move(modstmp, modsdest)

    # Remove yosbr and move updated configs to instance
    addText("[INFO] Moving updated configs into the provided instance location.", textbox)
    if (os.path.exists(yosbrpath)):
        shutil.rmtree(yosbrpath)

    for file_ in os.listdir(configtmp):
        filepath = os.path.join(configtmp, file_)

        # Handle directories recursively (if they're not yosbr)
        if (os.path.isdir(filepath) and file_ != "yosbr"):
            for root, _, files in os.walk(filepath):
                for name in files:
                    rootpath = os.path.join(root, name)

                    # Pass everything after config as arguments for os.path.join
                    targetpath = os.path.join(configdest, rootpath.replace(configtmp, "")[1:])
                    targetroot, _ = os.path.split(targetpath)

                    # Ensure file's root folder exists (shutil.move gets sad about nested folders not existing)
                    if (not os.path.exists(targetroot)):
                        os.makedirs(targetroot)

                    shutil.move(rootpath, targetpath)

        # Handle top-level files by simply moving them (overwrites if it exists)
        else:
            targetpath = os.path.join(configdest, file_)
            shutil.move(filepath, targetpath)

    return


def executeLauncher(textbox, exepath):
    _, exe_name = os.path.split(exepath)
    addText(f"[INFO] Launching {exe_name}.", textbox)
    try:
        subprocess.check_call([exepath])
        return True
    except Exception as error:
        addText(f"[ERROR] {error.strerror.replace('%1', exepath)}.", textbox)
        return False