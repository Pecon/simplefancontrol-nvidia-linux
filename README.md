# simplefancontrol-nvidia-linux
A dead-simple python script for overriding your nvidia GPU's fan control.

## Requirements
`python3` must be installed and you need the `nvidia-smi` command available. The latter should come with your driver.

## How to use
First, read over the variables near the top of the script and change them as desired. If you want your fans to idle instead of shutting off completely, you should set the offFanPower variable to the power percentage you want your fan to idle at. (Note: Make sure you test the percentages you choose, since lower values could result in the fan not overcoming its own inertia.)

Run the script by simply doing `./gpu_fan_override`. Exiting the script with ctrl+c should automatically restore your fans to default behavior.
Automate running the script via an @reboot cron job, or via any other means that make sense in your system's environment.