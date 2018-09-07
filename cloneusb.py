# Format drive to GPT one partition
# echo 'start=2048, type=7' | sudo sfdisk /dev/sdb

# Format to exFat, set custom label later
# sudo mkfs.exfat -f -L UDISK1 /dev/sdb1

# Get device info in JSON format
# More output formats: lsblk -h
# lsblk -J -o NAME,UUID,LABEL,FSTYPE,RM,TRAN

# ToDo list:
# [ ] Automatic format of correct usb drive
# [ ] Automatic copying of files from folder
# [ ] GUI (flask server? Qt?) for status and control
# [ ] Options in WebUI for ex. format drive, new files to copy mode.


from subprocess import run, Popen, STDOUT, PIPE
import json
from pprint import pprint

# Bash cmd for listing blockdevices
lsblkCMD = [
    "lsblk", "-p", "-J", "-o", "NAME,UUID,LABEL,FSTYPE,RM,TRAN"
]

# Clean drive with dd
cleanDriveCMD = [
    "dd", "if=/dev/zero", "of=#path", "bs=512", "count=1"
]

# Format drive to GPT one partition
createPartCMD = [
    [
        "echo",  "start=2048, type=7"
    ],
    [
        "sfdisk", "#path"
    ]
]

# MAY NOT WORK - UNTESTED
# Format to exFat, set custom label later
formatPartCMD = [
    "mkfs.exfat", "-n", "UDISK1", "#path"
]


def getUsbDevices():
    rawDeviceData = run(lsblkCMD, stdout=PIPE)
    devices = json.loads(rawDeviceData.stdout)
    usbDevices = {}
    # pprint(devices)

    # for device in devices['blockdevices']:
    for i in range(0, len(devices['blockdevices'])):
        device = devices['blockdevices'][i]
        # If device is not a removable or not usb
        if device['rm'] == '0' or device['tran'] != 'usb':
            continue

        parts = {}

        # If device has no partitions
        if "children" in device:
            for part in device['children']:
                parts[part['name']] = {
                    'uuid': part['uuid'],
                    'label': part['label'],
                    'fstype': part['fstype']
                }

        usbDevices[device['name']] = {
            'rm': device['rm'],
            'tran': device['tran'],
            'parts': parts
        }
        pass
    return usbDevices

def formatUSBDevice(path: str):

    # Assign temp variables for each cmd

    cleanDriveCMDtemp = list(cleanDriveCMD)
    createPartCMDtemp = list(createPartCMD)
    formatPartCMDtemp = list(formatPartCMD)
    
    # Replace "#path" with correct drive path for cleanDriveCMDtemp
    pathIndex = 0
    # Iterate through "cleanDriveCMDtemp" and find "#path"
    for i in range(len(cleanDriveCMDtemp)):
        item = cleanDriveCMDtemp[i]
        if "#path" in item:
            pathIndex = i
            cleanDriveCMDtemp[pathIndex] = cleanDriveCMDtemp[pathIndex].replace("#path", path)

    # Replace "#path" with correct drive path for createPartCMDtemp
    for i in range(len(createPartCMDtemp[1])):
        item = createPartCMDtemp[1][i]
        if "#path" in item:
            pathIndex = i
            createPartCMDtemp[1][pathIndex] = createPartCMDtemp[1][pathIndex].replace(
                "#path", path)
    #pathIndex = createPartCMDtemp[1].index("#path")
    

    # Replace "#path" with correct drive path for formatPartCMDtemp

    for i in range(len(formatPartCMDtemp)):
            item = formatPartCMDtemp[i]
            if "#path" in item:
                pathIndex = i
                formatPartCMDtemp[pathIndex] = formatPartCMDtemp[pathIndex].replace("#path", path)

    # pathIndex = formatPartCMDtemp.index("#path")
    # formatPartCMDtemp[pathIndex] = formatPartCMDtemp[pathIndex].replace(
    #     "#path", path + "1")


    # Clean the drive
    cleanDriveOutput = run(cleanDriveCMDtemp, stdout=PIPE)

    # Format drive to GPT
    # Pipe first commands output into second command
    createPartOutput = run(createPartCMDtemp[0], stdout=PIPE)
    createPartOutput = run(
        createPartCMDtemp[1], input=createPartOutput.stdout, stdout=PIPE)

    # Create one partition
    formatPartOutput = run(formatPartCMDtemp, stdout=PIPE)

    # TESTING with popen.
    # createPartOutput = Popen(createPartCMDtemp, stderr=STDOUT, stdout=PIPE)
    # cmdReturn = createPartOutput.communicate()[0],
    #   createPartOutput.returncode
    # cmdReturn = createPartOutput.communicate()
    # print(cmdReturn)
    # TESTING END

    formatStatus = {
        "cleanDrive": {
            "command": cleanDriveOutput.args,
            "returnCode": cleanDriveOutput.returncode
        },
        "createPart": {
            "command": createPartOutput.args,
            "returnCode": createPartOutput.returncode
        },
        "formatPart": {
            "command": formatPartCMDtemp,
            "returnCode": formatPartOutput.returncode
        }
    }

    return formatStatus


#pprint(formatUSBDevice("/dev/sdb"))

# pprint(getUsbDevices())

usbStorageDevices = getUsbDevices()

for device in usbStorageDevices:
    print("Formatting device: " + device)  
    formatStatus = formatUSBDevice(device)
    for cmd in formatStatus:
        print("Cmd: " + cmd + " - Return Code: " + str(formatStatus[cmd]["returnCode"]))