import sys
import os
import struct

BLOCK_SIZE = 512
MAGIC_NUMBER = b"4348PRJ3"


def create_index(filename):
    if os.path.exists(filename):
        print(f"Error: File {filename} already exists")
        sys.exit(1)


    # Create header and magic number
    header = bytearray(BLOCK_SIZE)
    header[0:8] = MAGIC_NUMBER
    
    # Root node ID (0 for empty tree), next block ID (1, as header is block 0)
    struct.pack_into('>Q', header, 8, 0)
    struct.pack_into('>Q', header, 16, 1)

    # Write to the file
    with open(filename, 'wb') as f:
        f.write(header)

    print("Index File " + filename + " has been created!")


def main():
    if len(sys.argv) < 2:
        print("Error: No command provided")
        return

    command = sys.argv[1].lower()
    
    if command == "create" and len(sys.argv) >= 3:
        create_index(sys.argv[2])
    else:
        print("Error: Invalid command or arguments")


if __name__ == "__main__":
    main()