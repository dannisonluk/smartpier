
# Smartpier

A smart system designed for the Civil Engineering and Development Department to monitor the major piers in Hong Kong. The system collects the signals returned from the infrared and the vibration sensors to determine whether there exist collisions in the piers. The data is then being analysed for further works and synchronized to the official [SMARTPIER](https://smartpier.hkscd.net/) website.




## Used By

This project is used by the following department:

- Civil Engineering and Development Department, HKSAR


## Run Locally

Clone the project

```bash
  git clone https://github.com/csluk2001/smartpier
```

Go to the project directory

```bash
  cd smartpier
```

To allow the program to have access to the wireless digital acquisition card
You need to gain access for the program by loading new udev rules

```bash
   sudo udevadm control --reload-rules
```
Then unplug and replug the USB device to apply the new rule

## License

[Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0)

