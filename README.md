# Manga-Translator-GUI

## What is this?
The goal of this project is to enable general users to easily translate the text in images within a folder into their desired language, all at once.

This tool is based on the Batch operation support provided by the Docker image from the [zyddnys/manga-image-translator](https://github.com/zyddnys/manga-image-translator) project.

The project is designed to enable general users to access and use the Batch operation feature more easily.  
It directly depends on the above-mentioned project and is a non-commercial, purpose-built project.

---

## 1. Requirements

This project is built to operate on Linux via WSL2 or WSL-based Docker Desktop on Windows.

> The program's primary purpose is to create a Docker container by executing user-defined commands and to output results accurately.  
> Please ensure Docker Desktop is installed and verify that Docker commands can be executed successfully in the CMD console.

---

## 2. Optional Configurations

If WSL2 is installed as a Non-Distro setup without Docker Desktop, or if the PC supports Nvidia GPUs, you can configure the system accordingly for faster speeds and greater stability.

> Although running with a CPU provides similar results, running multiple processes simultaneously may cause the PC to slow down or freeze, depending on the operating environment.

---

## 3. Execution and Precautions

1. Run the executable file included in this project.  
2. When selecting a folder, **ensure the folder path does not contain spaces**, as this can cause the program to malfunction.

---

## Comments on Potential Computing Issues

### Docker Desktop Dependency
- Ensure Docker Desktop is properly configured. Some users may experience issues with Docker if Windows is not updated to the latest version or if WSL2 is not installed correctly.
- Use the command `wsl --list --verbose` to verify that WSL2 is active and correctly set up.
- If running on a CPU, simultaneous operations might cause resource exhaustion. Monitor system performance to avoid crashes.

### GPU Acceleration
- Nvidia GPU support requires the Nvidia Container Toolkit. Install it using [Nvidia's official documentation](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html).
- Confirm GPU compatibility with the `nvidia-smi` command. Unsupported GPUs or driver issues might result in fallback to CPU, significantly slowing down operations.

### File Path Issues
- Spaces in folder paths can disrupt Docker command execution. Consider sanitizing paths in the code or handling exceptions programmatically to alert users.

### Executable Restrictions
- Ensure the executable file has proper permissions and is not blocked by antivirus software. It is recommended to run the executable as an administrator for full functionality.

### Resource Management
- Docker containers consume significant resources, especially for image processing tasks. Ensure adequate system resources (RAM, CPU, and disk space) are available.
- Use the `docker stats` command to monitor resource usage and terminate containers if necessary.

### Cross-Platform Compatibility
- Non-Windows users may encounter issues if the project is tailored primarily for Windows with WSL2. Providing equivalent configurations or alternatives for Linux and macOS could enhance usability.

---

## Reporting Issues

If you encounter any errors, please leave a report in the **Issues** section of this project.  
We will review and address them as soon as possible.
