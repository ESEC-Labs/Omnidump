<!-- PROJECT LOGO -->
<br />
<div align="center">

  <h3 align="center">Omnidump</h3>

  <p align="center">
    The Memory Dumping CLI tool. Aimed at analyzing the memory of processes.
    <br />
    <a href="https://github.com/ESEC-Labs/Omnidump/wiki"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    &middot;
    <a href="https://github.com/ESEC-Labs/Omnidump/issues">Report Bug</a>
    &middot;
    <a href="https://github.com/ESEC-Labs/Omnidump/issues">Request Feature</a>
  </p>
</div>

<!-- About the project --> 
## Overiew
Omnidump provides detailed insight into processes, returning process metadata to the user. This data includes: 

* Memory Region/Address Range: Start and end virtual addresses.
* Permissions: Access rights to the region (read, write, private, or execute).
* Inode: ID of the mapped file that contains core file system metadata.
* Path Name: The file or resources backing the region.
* Offsets: Starting offset within the backing file.
* Major:Minor ID: Device where the backing file is stored. 
* Raw bytes: Raw bytes extracted from the memory region. 
* Strings from raw bytes: Strings extracted from the raw bytes of a memory region.

The tool empowers analysts, developers, and engineers to extract concrete evidence of application performance and indicators of compromise (IOC). 

<!-- Getting Started -->
## Getting Started 

The steps below provide instructions for installing the latest stable version of Omnidump (v0.1) via pip

### Prerequisites

Before proceeding, ensure your system meets the following requirements:

1. Python: Version 3.8 or newer must be installed
2. Pip: Ensure your Python package is up to date
3. Permissions: You may be required to have root/admin privileges.

### Installation

It is strongly recommended to use a virtual environment to avoid conflicts with system packages. 

0. Create Virtual Environment
   ```sh
   python3 -m venv omnidump-env
   ```
   ```sh
   source omnidump-env/bin/activate
   ```
1. Install the Package
  ```sh
  pip install omnidump
  ```
2. Verify the Installation
   ```sh
   omnidump --help 
   ```
If the installation was successful, this command will display the list of available Omnidump commands and options.

## Usage 

The commands below provide examples of how to use Omnidump. 

Note: The --self command uses the current PID of the executing command. This command allows new users to test new or existing features before trying them out on their intended application. 

0. Basic dump of every memory section
   ```sh
   omnidump dump pid --self --all
   ```
0.1. Basic dump of every memory section verbosely (shows inode, permissions, and strings of length 4). 
  ```sh
  omnidump dump pid --self --all --verbose 
  ```
0.2. Basic dump of executable section with including strings (of length 4). 
  ```sh
  omnidump dump pid --self -e --strings 
  ```
