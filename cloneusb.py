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
# [ ] WebUI (flask server?) for status and control
# [ ] Options in WebUI for ex. format drive, new files to copy mode.


import subprocess
import json
from pprint import pprint

# Bash cmd for listing blockdevices
lsblkCMD = [
    "lsblk", "-p", "-J", "-o", "NAME,UUID,LABEL,FSTYPE,RM,TRAN"
]

# MAY NOT WORK - UNTESTED
# Format drive to GPT one partition
formatDriveCMD = [
    "echo",  "'start=2048, type=7'", "|", "sudo", "sfdisk", "/dev/sdb"
]

# MAY NOT WORK - UNTESTED
# Format to exFat, set custom label later
formatPartCMD = [
    "sudo", "mkfs.exfat", "-f", "-L", "UDISK1", "/dev/sdb1"
]


def getUsbDevices():
    rawDeviceData = subprocess.run(lsblkCMD, stdout=subprocess.PIPE)
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


pprint(getUsbDevices())


def formatUSBDevice(path: str):

    pass
