#!/bin/python3
import sys, signal, time, subprocess;

# Set this to the number of fans your NVIDIA gpu has.
numberOfGpuFans = 2

# Temperatures (celsius)
offTemp = 35; # Fan will turn off completely when this temperature is reached
onTemp = 50; # Fan will turn on at minimum power when this temperature is reached
maxTemp = 75; # Fan reaches maximum power at this temperature

# Fan power, percentage represented as an integer between 0-100
# Note: For the EVGA RTX 3060 XC, I noted that the fans will generally not turn on if set to a power value much less than 40
minFanPower = 40; # Fan power starts at this percentage
maxFanPower = 100; # Fan power maxes out at this percentage
offFanPower = 0; # Fan power percentage when fans are "off". Set this to something besides 0 if you want this script to idle the fans at a specific power rather than turn them off.

# Desired fan speed percent must drop at least this much before the fan speed is actually reduced
speedDownDifference = 10;

# Prints output about what the program is doing. Set this to False once you have everything tweaked right and just want this script to quietly do its thing.
outputDebug = True;


def exitCleanup(signal, frame):
	debugPrint("Returning fan control to default");
	subprocess.run(['nvidia-settings', '-a', 'GPUFanControlState=0'], capture_output = True, encoding = "UTF-8");
	sys.exit(0);

try:
	def getGpuTemp():
		gpuInfo = subprocess.run(['nvidia-smi', '--query-gpu=temperature.gpu', '--format=csv,noheader,nounits'], capture_output = True, encoding = "UTF-8")
		gpuInfo = gpuInfo.stdout
		temperature = int(gpuInfo);

		return temperature;

	def getGpuFanSpeed():
		gpuInfo = subprocess.run(['nvidia-smi', '--query-gpu=fan.speed', '--format=csv,noheader,nounits'], capture_output = True, encoding = "UTF-8")
		gpuInfo = gpuInfo.stdout
		temperature = int(gpuInfo);

		return temperature;

	def setGpuFanSpeed(percentPower: int):
		for i in range(numberOfGpuFans):
			subprocess.run(['nvidia-settings', '-a', '[fan:' + str(i) + ']/GPUTargetFanSpeed=' + str(percentPower)], capture_output = True, encoding = "UTF-8");

		debugPrint("Setting fan speed to " + str(percentPower) + "%");
		time.sleep(1.5);

	# Curve function to keep fan increases relatively minor until higher temperatures
	def easeInQuad(ratio: float):
		if ratio > 1.0:
			return 1.0;
		elif ratio < 0.0:
			return 0.0;

		return ratio**2;

	def debugPrint(string: str):
		if outputDebug:
			print("(" + str(getGpuTemp()) + "°C) " + string);

	if __name__ == '__main__':
		# Main program
		signal.signal(signal.SIGINT, exitCleanup);

		debugPrint("Enabling manual fan control");
		subprocess.run(['nvidia-settings', '-a', 'GPUFanControlState=1'], capture_output = True, encoding = "UTF-8");

		setGpuFanSpeed(offFanPower);
		fansOn = False;

		while True:
			temperature = getGpuTemp();
			fanSpeed = getGpuFanSpeed();
			temperatureRatio = (temperature - onTemp) / (maxTemp - onTemp);

			if temperatureRatio < 0.0:
				temperatureRatio = 0.0;
			if temperatureRatio > 1.0:
				temperatureRatio = 1.0;

			if temperature <= offTemp:
				if fanSpeed != offFanPower:
					debugPrint("Turning the fan off.");
					setGpuFanSpeed(offFanPower);
					fansOn = False;
			else:
				fanPower = int(minFanPower + ((maxFanPower - minFanPower) * easeInQuad(temperatureRatio)));

				if fansOn and fanPower > (fanSpeed + 1):
					debugPrint("Speeding up the fan. The current fan speed is " + str(fanSpeed) + "%.");
					setGpuFanSpeed(fanPower);
				elif temperature >= onTemp and not fansOn:
					debugPrint("Turning the fan on.");
					setGpuFanSpeed(fanPower);
					fansOn = True;
				elif fansOn and fanPower < fanSpeed - speedDownDifference:
					debugPrint("Speeding down the fan. The current fan speed is " + str(fanSpeed) + "%.");
					setGpuFanSpeed(fanPower);

			time.sleep(0.5);
except Exception as error:
	print(error, file=sys.stderr);
finally:
	exitCleanup(None, None);