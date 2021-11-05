# Salazar, Jacob Israel - NSSECU3
import os
import string
from sys import platform
import psutil
import os.path
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk
from subprocess import run, PIPE
import queue
import threading

destFolder = 'recoveryfolder' #name of the folder where the recovery files will reside
q = queue.Queue() #Queue for the worker threads

def func(q,threadno):
    while True:
        try:
            task = q.get()
            filetype = task[0]
            startSector = task[1]
            recoveredDir = task[2]
            driveText = task[3]
            fileHeaders = task[4]
            number = task[5]
            maxFileSize = 10000000

            with open(driveText, 'rb') as drive:
                sectorSize = 512
                # Prints the type of file signature that was found and its sector
                print(filetype.upper() + 'Found at sector', startSector)

                # Iterate the corresponding Dictionary Counter to indicate number of a specific file type found
                # recoveredCtr[filetype] += 1

                completeName = os.path.join(recoveredDir,
                                            destFolder + 'no.' + str(number) + filetype)

                # Creates a new file in the recoveredDir folder and allows to write in bytes
                recoveredFile = open(completeName, 'wb')

                # Boolean value used to determine if a file is currently being recovered
                recovering = True

                # Reinitialize the pointer of the drive to the particular drive sector to start recovery
                drive.seek(startSector * sectorSize)

                # maxFileSizeCtr is used as a limiter just in case the recovered file is larger than the maxFileSize or was a false positive
                # Used to truncate the file based on the maxFileSize because it found a header but did not find the corresponding footer within the range
                maxFileSizeCtr = 0

                # Initialize the sectorFileFooter to be matched with the footer of the detected filetype
                fileFooterLen = len(fileHeaders[filetype][1])
                sectorFileFooter = b'\x00' * fileFooterLen

                # Iterate while a file is being recovered or while the current size has not exceeded the maxFileSize
                while recovering and maxFileSizeCtr < maxFileSize:

                    # Reads one byte at a time from the drive
                    read = drive.read(1)

                    # Builds the footer string by removing the first byte and adding the newly read byte, used for checking if the footer is found
                    sectorFileFooter = sectorFileFooter[1:fileFooterLen] + read

                    # Writes the newly read byte to the new file, recreating the deleted file
                    recoveredFile.write(read)

                    # Checks if the footer signature of the current file type being evaluated was found, while recovery iterates through the bytes

                    if sectorFileFooter == fileHeaders[filetype][1] and filetype == '.docx':
                        print("filetype = " + filetype)
                        # Set the recovering boolean value to false to end the loop
                        recovering = False
                        fileList.insert(END, recoveredDir + 'no.' + str(
                            number) + filetype + ' = ' + "Success")

                        # Close the recoveredFile properly to save the file
                        recoveredFile.close()

                        # Prints a recovery successful message to indicate that a file was recovered based on a found header and footer
                        print(" - Recovery Successful!")
                    elif sectorFileFooter == fileHeaders[filetype][1] and filetype == '.xlsx':
                        print("filetype = " + filetype)
                        # Set the recovering boolean value to false to end the loop
                        recovering = False
                        fileList.insert(END, recoveredDir + 'no.' + str(
                            number) + "." + filetype + ' = ' + "Success")

                        # Close the recoveredFile properly to save the file
                        recoveredFile.close()

                        # Prints a recovery successful message to indicate that a file was recovered based on a found header and footer
                        print(" - Recovery Successful!")
                    if sectorFileFooter == fileHeaders[filetype][1] and filetype == '.pptx':
                        print("filetype = " + filetype)
                        # Set the recovering boolean value to false to end the loop
                        recovering = False
                        fileList.insert(END, recoveredDir + 'no.' + str(
                            number) + "." + filetype + ' = ' + "Success")

                        # Close the recoveredFile properly to save the file
                        recoveredFile.close()

                        # Prints a recovery successful message to indicate that a file was recovered based on a found header and footer
                        print(" - Recovery Successful!")
                    elif sectorFileFooter == fileHeaders[filetype][1]:
                        # Set the recovering boolean value to false to end the loop
                        recovering = False
                        fileList.insert(END, recoveredDir + 'no.' + str(
                            number) + "." + filetype + ' = ' + "Success")

                        # Close the recoveredFile properly to save the file
                        recoveredFile.close()

                        # Prints a recovery successful message to indicate that a file was recovered based on a found header and footer
                        print(" - Recovery Successful!")

                    # Increment the limiter to act stop recovery in the event that a footer was not found within the provided size
                    maxFileSizeCtr += 1

                # In the event that the arbitrary maxFileSize value is reached, it would safely close the recoveredFile indicate a failed in recovery
                # This happens if the footer was not found within the range provided, which may indicate that it just so happes that a header had a
                # match but it was not actually a file, that the filesize was larger than that of the maxFileSize value, or that the file is discontiguous
                if maxFileSizeCtr >= maxFileSize:
                    recoveredFile.close()
                    fileList.insert(END,
                                    recoveredDir + 'no.' + str(number) + "." + filetype + ' = ' + "fail")
                    print(" - Recovery Failed")
        except:
            pass



def createThreadWorkers():
    for i in range(int(threadCount.get())):
        worker = threading.Thread(target=func, args=(q, i,), daemon=True)
        worker.start()

def recover():
    try:
        # Create the directory which would contain the recovered files
        driveText = driveSelected.get()
        recoveryFolder = destFolder
        save_path = destText.get()
        recoveredDir = save_path + '/' + recoveryFolder
        if not os.path.exists(recoveredDir):
            os.makedirs(recoveredDir)

        filelist = [file for file in os.listdir(recoveredDir) if
                    file.endswith(('.jpg', '.png', '.pdf', '.docx', '.pptx', '.xlsx', '.rtf'))]
        progressLabel.configure(text="setting up directory..........")
        for f in filelist:
            os.remove(os.path.join(recoveredDir, f))
            print("removed!")
        # Contains the list of file headers with their corresponding header and footer
        fileHeaders = {}
        if jpgVal.get() == "on":
            fileHeaders['.jpg'] = [b'\xFF\xD8', b'\xFF\xD9']
        if pngVal.get() == "on":
            fileHeaders['.png'] = [b'\x89\x50\x4E\x47\x0D\x0A\x1A\x0A', b'\x49\x45\x4E\x44\xAE\x42\x60\x82']
        if pdfVal.get() == "on":
            fileHeaders['.pdf'] = [b'\x25\x50\x44\x46', b'\x0A\x25\x25\x45\x4F\x46']
        if rtfVal.get() == "on":
            fileHeaders['.rtf'] = [b'\x7B\x5C\x72\x74\x66', b'\x7D']
        if docxpptxVal.get() == "on":
            fileHeaders['.docx'] = [b'\x50\x4B\x03\x04\x14\x00\x08\x08\x08\x00', b'\x50\x4B\x05\x06']
            fileHeaders['.xlsx'] = [b'\x50\x4B\x03\x04\x14\x00\x08\x08\x08\x00', b'\x50\x4B\x05\x06']
        if pptxVal.get() == "on":
            fileHeaders['.pptx'] = [b'\x50\x4B\x03\x04\x14\x00\x06\x00', b'\x50\x4B\x05\x06']
        print(fileHeaders)

        # Open the Drive D folder in windows. Use /dev/sdb for Linux or /dev/disk1 for Mac
        with open(driveText, 'rb') as drive:

            # Define the start and end sectorSize where the file carving would take place
            startSector = 0
            endSector = 100000

            # Use sector/block/cluster sizes to skip bytes based on the size, we'll use the term sector
            # 512B/sector is the traditional sector size for HDDs, but nowadays HDDs use 4096B/sector
            sectorSize = 512

            # Dictionary Counter used to iterate the number of recovered files per file type
            recoveredCtr = dict((key, 0) for key in fileHeaders.keys())

            # Arbitrary value to end recovery just so happens that a header pattern was found
            maxFileSize = 10000000

            # Iterate through all sectors from the startSector to endSector
            while startSector < endSector:
                try:
                    progress = startSector / endSector
                    progress = progress * 100
                    progressBar['value'] = progress
                    progressLabel.configure(text=f"Recovering files {round(progress)}% ..........")
                    # Navigate to the particular drive sector
                    drive.seek(startSector * sectorSize)

                    # Temporary variable to contain the first few bytes of a sector
                    sectorFileHeader = ''

                    # Reads the first 32 bytes of each sector, used to match with a particular file header pattern
                    sectorFileHeader = drive.read(32)

                    # Iterate through all file types in the fileHeader dictionary
                    for filetype in fileHeaders:
                        if sectorFileHeader[:len(fileHeaders[filetype][0])] == fileHeaders[filetype][0]:
                            recoveredCtr[filetype] += 1
                            file_task = [filetype, startSector, recoveredDir, driveText, fileHeaders,
                                         recoveredCtr[filetype]]
                            q.put(file_task)
                    if startSector + 1 == endSector:
                        progressLabel.configure(text="Recovering Process Completed 100%")
                        stringResult = "Result:"
                        sum = 0
                        for filetype in fileHeaders:
                            sum +=recoveredCtr[filetype]
                            stringResult =stringResult+ filetype+": " + str(recoveredCtr[filetype])+" "
                        result.configure(text = stringResult)
                        result.grid(row=5,column=3,columnspan=4)
                        total.configure(text="Total files recovered:"+str(sum))
                        total.grid(row=6,column=3,columnspan=4)
                except:
                    pass
                # increment the startSector to move from one sector to another
                startSector += 1
    except:
        messagebox.showerror('Invalid Drive or Directory', 'Please type in a legit drive/directory')
        progressLabel.configure(text="System is idle")
        pass

app = Tk()
options = [] #detected drives for windows
devices =[] #detected devices for Linux/Mac



def physical_drives():
    command = ['lsblk -d -o name -n']
    output = run(command, shell=True, stdout=PIPE)
    output_string = output.stdout.decode('utf-8')
    output_string = output_string.strip()
    results = output_string.split('\n')
    return results

if platform == "linux" or platform == "linux2" or platform == "darwin":
    try:
        results = physical_drives()
        for drive in results:
            drive = '/dev/' + drive
            devices.append(drive)
        for p in psutil.disk_partitions(all=False):
            devices.append(p.device)
        print(devices)
        if len(devices) == 0:
            devices = ["not available"]
    except:
        print("no partitions found")
        devices = ["not available"]
    options = ["not available"]
    driveLabel = Label(app, text='Detected OS: Linux', font=('italic', 10),padx=0)
    driveLabel.grid(row=0, column=1, sticky=W)
elif platform == "win32":
    drives = ['%s:' % d for d in string.ascii_uppercase if os.path.exists('%s:' % d)]
    if len(drives) == 0:
        options = ["not available"]
    else:
        for d in drives:
            d = '\\\\.\\' + d
            options.append(d)
    devices = ["not available"]
    driveLabel = Label(app, text='Detected OS: Windows', font=('italic', 10), padx=0)
    driveLabel.grid(row=0, column=1, sticky=W)

def click():
    driveDirectory = filedialog.askdirectory()
    driveEntry.delete(0, END)
    driveEntry.insert(END, driveDirectory)

def click1():
    destFolderDirectory = filedialog.askdirectory()
    destEntry.delete(0, END)
    destEntry.insert(END, destFolderDirectory)

def click2():
    progressBar['value'] = 0
    progressLabel.configure(text="System is idle")
    result.grid_remove()
    total.grid_remove()
    if jpgVal.get() == "off" and pngVal.get() == "off" and pdfVal.get() == "off" and docxpptxVal.get() == "off" and rtfVal.get() == "off":
        messagebox.showerror('Required Fields', 'Please include all fields')
        return
    elif driveSelected.get() == "" or destText.get() == "":
        messagebox.showerror('Required Fields', 'Please include all fields')
        return
    elif driveSelected.get() == "Type or Select Drive":
        messagebox.showerror('Required Fields', 'Please type in a legit drive/disk')
        return

    print("hello"+driveSelected.get(), destText.get())
    progressLabel.configure(text="creating worker threads..........")
    createThreadWorkers()
    threading.Thread(target=recover).start()

def clickClearHistory():
    fileList.delete(0, END)



titleApp = Label(app, text = 'Recovery Tool',font=('bold',14), pady=10)
titleApp.grid(row=0,column=0,sticky=W)



driveSelected = StringVar(app)
driveSelected.set("Type or Select Drive")

driveLabel = Label(app, text = 'Drive Path',font=('bold',12), pady=10)
driveLabel.grid(row=1,column=0,sticky=W)
driveEntry = Entry(app,textvariable= driveSelected)
driveEntry.grid(row=1,column=1)

destText = StringVar()
destLabel = Label(app, text = 'Destination Folder',font=('bold',12), pady=10)
destLabel.grid(row=2,column=0,sticky=W)
destEntry = Entry(app,textvariable=destText)
destEntry.grid(row=2,column=1)

threadWorkerCount = ["1","5","10","15","20","25","30","35","40","45","50","60","70","80","90","100","200","300","400","500"]
threadCount = StringVar()
threadCount.set("1")
threadLabel = Label(app, text = 'Thread Count',font=('bold',12), pady=10)
threadLabel.grid(row=2,column=3,sticky=W)
worker_menu = OptionMenu(app, threadCount, *threadWorkerCount)
worker_menu.grid(row=2, column=4, pady=10,sticky=W)


chooseTypeLabel = Label(app, text = 'Choose File Type',font=('bold',14), pady=10)
chooseTypeLabel.grid(row=3,column=0,sticky=W)

jpgVal = StringVar()
jpgCheckBtn = Checkbutton(app, text = '.jpg',font=('bold',14), variable=jpgVal,onvalue = "on",offvalue="off")
jpgCheckBtn.deselect()
jpgCheckBtn.grid(row=4,column=0,sticky=W)

pngVal = StringVar()
pngCheckBtn = Checkbutton(app, text = '.png',font=('bold',14), variable=pngVal,onvalue = "on",offvalue="off")
pngCheckBtn.deselect()
pngCheckBtn.grid(row=4,column=1,sticky=W)

pdfVal = StringVar()
pdfCheckBtn = Checkbutton(app, text = '.pdf',font=('bold',14), variable=pdfVal,onvalue = "on",offvalue="off")
pdfCheckBtn.deselect()
pdfCheckBtn.grid(row=4,column=2,sticky=W)

recoverBtn = Button(app, text=' Recover Data', width=12, command=click2)
recoverBtn.grid(row=4, column=3, pady=10,sticky=W)

progressLabel = Label(app, text = 'Recovery Progress',font=('bold',12), pady=10)
progressLabel.grid(row=3,column=4,sticky=W)

progressBar = ttk.Progressbar(app, orient=HORIZONTAL, length = 200,mode='determinate')
progressBar.grid(row=4, column=4,sticky=N)



rtfVal = StringVar()
rtfCheckBtn = Checkbutton(app, text = '.rtf',font=('bold',14), variable=rtfVal,onvalue = "on",offvalue="off")
rtfCheckBtn.deselect()
rtfCheckBtn.grid(row=5,column=0,sticky=W)

docxpptxVal = StringVar()
docxpptxCheckBtn = Checkbutton(app, text = '.docx,.xlsx',font=('bold',14), variable=docxpptxVal,onvalue = "on",offvalue="off")
docxpptxCheckBtn.deselect()
docxpptxCheckBtn.grid(row=5,column=1,sticky=W)

pptxVal = StringVar()
pptxCheckBtn = Checkbutton(app, text = '.pptx',font=('bold',14), variable=pptxVal,onvalue = "on",offvalue="off")
pptxCheckBtn.deselect()
pptxCheckBtn.grid(row=5,column=2,sticky=W)

result = Label(app, text = '',font=('bold',12))
result.grid(row=5,column=3,sticky=W)
result.grid_remove()

total = Label(app, text = '',font=('bold',13))
total.grid(row=6,column=3,sticky=W)
total.grid_remove()



driveLabelWindows = Label(app, text = 'For Windows: Drives',font=('light',9), pady=10,padx=5)
driveLabelWindows.grid(row=1,column=2,sticky=W)

#driveAddBtn = Button(app, text='Windows: Select Drive', width=12, command=click)
question_menu = OptionMenu(app, driveSelected, *options)
question_menu.grid(row=1, column=3, pady=10)

driveLabelLinux = Label(app, text = 'For Linux: Disks/Partitions',font=('light',9), pady=10,padx=5)
driveLabelLinux.grid(row=1,column=4,sticky=W)

question_menuLinux = OptionMenu(app, driveSelected, *devices)
question_menuLinux.grid(row=1, column=5, pady=10,sticky=NSEW)


destFolderBtn = Button(app, text='Select Directory', width=12, command=click1)
destFolderBtn.grid(row=2, column=2, pady=10)




historyLabel = Label(app, text = 'Recover History List',font=('bold',14), pady=10)
historyLabel.grid(row=6,column=0,sticky=W)

clearHistory = Button(app, text='Clear History', width=15, command=clickClearHistory)
clearHistory.grid(row=6, column=1)


# Recovered Files List (Listbox)
fileList = Listbox(app, height=8, width=50, border=0)
fileList.grid(row=7, column=0, columnspan=5, rowspan=12, pady=10, padx=5,sticky=W)
# Create scrollbar
scrollbar = Scrollbar(app)
scrollbar.grid(row=7, column=5)
# Set scroll to listbox
fileList.configure(yscrollcommand=scrollbar.set)
scrollbar.configure(command=fileList.yview)


app.title("DIGITAL FORENSICS - RECOVERY TOOL ©Jacob Salazar, 2021")
app.geometry('1000x500')

app.mainloop()