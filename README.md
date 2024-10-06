# **forport**

forport is a simple cross-platform command-line tool for port forwarding. It works on both Windows and Linux, allowing you to easily forward a source port to a destination port with a simple command.  
Prerequisites:

```
Python 3 must be installed on your machine.
```

## Important Note:

The Project includes a batch(.bat) file for Windows to be used as a wrapper for the python script.  
this is irrelevant for Linux users as the script can be executed directly.

### Installation:

**Windows**

1.  Ensure Python 3 is Installed
2.  Download the project via git clone or download the zip file.
3.  Enter the path of the project folder into the environment variables by running the following command in the command prompt.

```
SET PATH=%PATH%;C:\path\to\forport
```

### **Linux**

1.  Ensure Python 3 is Installed
2.  Download the forport.py script from this repository.
3.  Save it to /usr/local/bin/forport or another directory in your PATH.
4.  Make the Script Executable by running the following command.

```
sudo chmod +x /usr/local/bin/forport
```

## Usage

Use the forport command with the following format:  
Forward a port from one to another

```
forport <source_port>-><destination_port>
```

List all forwarded ports

```
forport list
```

Remove a forwarded port

```
forport remove/delete <source_port> or all
```

How It Works

```
On Windows, forport uses netsh to forward ports.
On Linux, it uses iptables to redirect traffic from one port to another.
```

Contributing

Contributions are welcome! If you encounter any issues or have suggestions, feel free to open a pull request or submit an issue on GitHub.  
License

This project is licensed under the MIT License.

This tool simplifies port forwarding on both Linux and Windows systems. If you find it helpful, please give it a star on GitHub!