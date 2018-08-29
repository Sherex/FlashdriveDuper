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

# MAY NOT WORK - UNTESTED
# Format drive to GPT one partition
formatDriveCMD = [
    "echo",  "'start=2048, type=7'", "|", "sudo", "sfdisk", "#path"
]

# MAY NOT WORK - UNTESTED
# Format to exFat, set custom label later
formatPartCMD = [
    "sudo", "mkfs.exfat", "-n", "UDISK1", "#path"
]


def getUsbDevices():
    rawDeviceData = run(lsblkCMD, stdout=PIPE)
    devices = json.loads(rawDeviceData.stdout)
    usbDevices = []
    # pprint(devices)

    # for device in devices['blockdevices']:
    for i in range(0, len(devices['blockdevices'])):
        device = devices['blockdevices'][i]
        if device['rm'] == '0' or device['tran'] != 'usb':
            continue
        parts = {}
        for part in device['children']:
            parts[part['name']] = {
                'uuid': part['uuid'],
                'label': part['label'],
                'fstype': part['fstype']
            }

        usbDevices.append({
            device['name']: {
                'rm': device['rm'],
                'tran': device['tran'],
                'parts': parts
            }
        })
        pass
    return usbDevices


def formatUSBDevice(path: str):
    # Replace "#path" with correct drive path for cleanDriveCMD
    pathIndex = 0
    # Iterate through "cleanDriveCMD" and find "#path"
    for i in range(len(cleanDriveCMD)):
        item = cleanDriveCMD[i]
        if "#path" in item:
            pathIndex = i

    cleanDriveCMD[pathIndex] = cleanDriveCMD[pathIndex].replace("#path", path)

    # Replace "#path" with correct drive path for formatDriveCMD
    pathIndex = formatDriveCMD.index("#path")
    formatDriveCMD[pathIndex] = formatDriveCMD[pathIndex].replace(
        "#path", path + "1")

    # Replace "#path" with correct drive path for formatPartCMD
    pathIndex = formatPartCMD.index("#path")
    formatPartCMD[pathIndex] = formatPartCMD[pathIndex].replace(
        "#path", path)

    # Clean the drive
    cleanDriveOutput = run(cleanDriveCMD, stdout=PIPE)

    # Format drive to GPT
    formatDriveOutput = run(formatDriveCMD, stdout=PIPE)

    # Create one partition
    formatPartOutput = run(formatPartCMD, stdout=PIPE)

    # formatDriveOutput = Popen(formatDriveCMD, stderr=STDOUT, stdout=PIPE)
    # cmdReturn = formatDriveOutput.communicate()[0],
    #   formatDriveOutput.returncode
    # cmdReturn = formatDriveOutput.communicate()

    # print(cmdReturn)
    print(cleanDriveOutput)
    print(formatDriveOutput)
    print(formatPartOutput)

    pass


formatUSBDevice("/dev/sdb")

# pprint(getUsbDevices())
