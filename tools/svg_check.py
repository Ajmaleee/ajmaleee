import xml.etree.ElementTree as ET
for p in ["assets/generated/system-dark.svg","assets/generated/system-light.svg"]:
    ET.parse(p); print("ok",p)
