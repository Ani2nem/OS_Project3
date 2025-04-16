import sys
import os
import struct

BLOCK_SIZE = 512
MAGIC_NUMBER = b"4348PRJ3"
MIN_DEGREE = 10
MAX_KEYS = 2 * MIN_DEGREE - 1  # 19 keys
MAX_CHILDREN = MAX_KEYS + 1  # 20 children


class BTreeNode:
    def __init__(self, block_id, parent_id=0, is_leaf=True):
        self.block_id = block_id
        self.parent_id = parent_id
        self.num_keys = 0
        self.keys = [0] * MAX_KEYS
        self.values = [0] * MAX_KEYS
        self.children = [0] * MAX_CHILDREN
        self.is_leaf = is_leaf
    
    def to_bytes(self):
        data = bytearray(BLOCK_SIZE)
        
        # Block ID, Parent ID, and Number of keys
        struct.pack_into('>Q', data, 0, self.block_id)
        struct.pack_into('>Q', data, 8, self.parent_id)
        struct.pack_into('>Q', data, 16, self.num_keys)
        
        # keys and Values and children
        for i in range(MAX_KEYS):
            struct.pack_into('>Q', data, 24 + (i * 8), self.keys[i])
        for i in range(MAX_KEYS):
            struct.pack_into('>Q', data, 24 + (MAX_KEYS * 8) + (i * 8), self.values[i])
        for i in range(MAX_CHILDREN):
            struct.pack_into('>Q', data, 24 + (MAX_KEYS * 16) + (i * 8), self.children[i])
        
        return data
    

    """Create a node from bytes"""
    @classmethod
    def from_bytes(cls, data):
        node = cls(0)
        
        # Block ID, Parent ID,  Number of keys
        node.block_id = struct.unpack_from('>Q', data, 0)[0]
        node.parent_id = struct.unpack_from('>Q', data, 8)[0]
        node.num_keys = struct.unpack_from('>Q', data, 16)[0]
        
        # keys and Values and children
        for i in range(MAX_KEYS):
            node.keys[i] = struct.unpack_from('>Q', data, 24 + (i * 8))[0]
        for i in range(MAX_KEYS):
            node.values[i] = struct.unpack_from('>Q', data, 24 + (MAX_KEYS * 8) + (i * 8))[0]
        for i in range(MAX_CHILDREN):
            node.children[i] = struct.unpack_from('>Q', data, 24 + (MAX_KEYS * 16) + (i * 8))[0]
        
        # Determine if it's a leaf node
        node.is_leaf = all(child == 0 for child in node.children)
        
        return node


def create_index(filename):
    if os.path.exists(filename):
        print("Error: File " + filename + " already exists")
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

    def write_header(filename, root_id, next_block_id):
        # Create header and magic number
        header = bytearray(BLOCK_SIZE)
        header[0:8] = MAGIC_NUMBER
        
        # Root node ID and Block ID
        struct.pack_into('>Q', header, 8, root_id)
        struct.pack_into('>Q', header, 16, next_block_id)
        
        # Write to the file
        with open(filename, 'r+b') as f:
            f.write(header)

    def read_node(filename, block_id):
        if block_id == 0:
            return None
            
        with open(filename, 'rb') as f:
            f.seek(block_id * BLOCK_SIZE)
            node_data = f.read(BLOCK_SIZE)
            
        return BTreeNode.from_bytes(node_data)

    def write_node(filename, node):
        with open(filename, 'r+b') as f:
            f.seek(node.block_id * BLOCK_SIZE)
            f.write(node.to_bytes())


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