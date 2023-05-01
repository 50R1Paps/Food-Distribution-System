from pyfingerprint.pyfingerprint import PyFingerprint

# Initialize the fingerprint sensor
f = PyFingerprint('/dev/ttyUSB0', 57600, 0xFFFFFFFF, 0x00000000)

# Check if the fingerprint sensor is connected
if not f.verifyPassword():
    raise ValueError('The given fingerprint sensor password is wrong!')

# Get the number of enrolled fingerprints
print('Currently %d fingerprints are enrolled.' % f.getTemplateCount())

# Enroll a new fingerprint
print('Place your finger on the sensor...')
while not f.readImage():
    pass
f.convertImage(0x01)
result = f.searchTemplate()
if result >= 0:
    print('This fingerprint already exists!')
    exit(0)
print('Remove your finger from the sensor...')
while f.readImage():
    pass
print('Place your finger on the sensor again...')
while not f.readImage():
    pass
f.convertImage(0x02)
if not f.compareCharacteristics():
    print('Fingerprints do not match!')
    exit(0)
f.createTemplate()
print('Fingerprint enrolled successfully!')

# Verify a fingerprint
print('Place your finger on the sensor...')
while not f.readImage():
    pass
f.convertImage(0x01)
result = f.searchTemplate()
if result < 0:
    print('Fingerprint not recognized!')
    exit(0)
print('Fingerprint recognized as template #%d.' % result)
