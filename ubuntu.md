To include Ubuntu in the Windows Boot Manager for dual-booting on Windows 11, follow these steps

### 1. Install Ubuntu alongside Windows
   If you haven't installed Ubuntu yet, you'll need to install it alongside Windows. When installing, ensure that you select the option to install Ubuntu alongside Windows.

   - Create a bootable USB drive with Ubuntu.
   - Boot from the USB and start the Ubuntu installation.
   - During the partitioning stage, choose Install Ubuntu alongside Windows or manually partition the drive if necessary.
   - Finish the installation and reboot the system.

### 2. Set Windows Boot Manager to recognize Ubuntu
   After installing Ubuntu, you need to configure the Windows Boot Manager to include Ubuntu. By default, Ubuntu uses GRUB (the Linux bootloader), but you can add an entry in the Windows Boot Manager using a tool like `bcdedit` in Windows or `EasyBCD`.

#### Option 1 Using `bcdedit` (Command Line Method)

1. Boot into Windows 11 and open Command Prompt as an administrator.

2. Run the following command to list the current boot entries
   ```bash
   bcdedit enum
   ```

3. Note the identifier for your Windows Boot Loader and check if there's already an entry for Ubuntu. If not, proceed with the following steps to add it.

4. Use `bcdedit` to add a new boot entry for Ubuntu. You'll need to know the location of your Ubuntu partition
   ```bash
   bcdedit create d Ubuntu application bootsector
   ```

5. Use the following command to set the partition for Ubuntu
   ```bash
   bcdedit set {identifier} device partition=X
   ```
   Replace `{identifier}` with the one returned in the previous step and `X` with the drive where Ubuntu is installed.

6. Specify the path to GRUB (Ubuntu's bootloader)
   ```bash
   bcdedit set {identifier} path EFIubuntugrubx64.efi
   ```

7. Finally, add the Ubuntu entry to the boot menu
   ```bash
   bcdedit displayorder {identifier} addlast
   ```

8. Reboot, and the Windows Boot Manager should now include an option to boot into Ubuntu.

#### Option 2 Using EasyBCD (Graphical Method)

1. Download and install [EasyBCD](httpsneosmart.netEasyBCD).

2. Open EasyBCD and navigate to Add New Entry.

3. In the LinuxBSD tab
   - Type Select GRUB 2 from the dropdown.
   - Name Type Ubuntu.
   - Device Choose the partition where Ubuntu is installed.

4. Click Add Entry and then Save Settings.

5. Reboot, and you'll see Ubuntu as an option in the Windows Boot Manager.

### 3. Test the Boot Entry
   Reboot your system to ensure that both Windows and Ubuntu appear in the boot menu. Select Ubuntu to check if it boots correctly.

Let me know if you encounter any issues!