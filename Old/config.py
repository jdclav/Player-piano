import configparser

configFile = configparser.ConfigParser()

configFile.add_section("Kinematics")

configFile.set("Kinematics", "max_acceleration", "3000")
configFile.set("Kinematics", "max_velocity", "300")

configFile.add_section("Key Characters")

configFile.set("Key Characters", "closed_solenoid", "\u03A6")
configFile.set("Key Characters", "open_solenoid", "\U0000039F")
configFile.set("Key Characters", "key", "\U0000203E")
configFile.set("Key Characters", "pressed_key", "\U00002534")

configFile.add_section("Piano Properties")

configFile.set("Piano Properties", "key_width", "22")
configFile.set("Piano Properties", "key_count", "76 ")

with open(r"config.ini", "w") as configFileObj:
    configFile.write(configFileObj)
    configFileObj.flush()
    configFileObj.close()

readFile = open(r"config.ini", "r")
print(readFile.read())
readFile.flush()
readFile.close()
