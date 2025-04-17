import sys
import os
import struct
import csv

BLOCK_SIZE = 512
MAGIC_NUMBER = b"4348PRJ3"
MIN_DEGREE = 10
MAX_KEYS = 2 * MIN_DEGREE - 1
MAX_CHILDREN = MAX_KEYS + 1

# Just a basic in-memory cache to avoid reading the same node multiple times
class NodeCache:
    def __init__(self, capacity=3):
        self.capacity = capacity
        self.cache = {}

    def get(self, block_id):
        return self.cache.get(block_id)

    def put(self, node):
        if len(self.cache) >= self.capacity and node.block_id not in self.cache:
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
        self.cache[node.block_id] = node

    def remove(self, block_id):
        if block_id in self.cache:
            del self.cache[block_id]

    def clear(self):
        self.cache.clear()


# One node in the B-tree
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
        struct.pack_into('>Q', data, 0, self.block_id)
        struct.pack_into('>Q', data, 8, self.parent_id)
        struct.pack_into('>Q', data, 16, self.num_keys)
        for i in range(MAX_KEYS):
            struct.pack_into('>Q', data, 24 + (i * 8), self.keys[i])
        for i in range(MAX_KEYS):
            struct.pack_into('>Q', data, 24 + (MAX_KEYS * 8) + (i * 8), self.values[i])
        for i in range(MAX_CHILDREN):
            struct.pack_into('>Q', data, 24 + (MAX_KEYS * 16) + (i * 8), self.children[i])
        return data

    @classmethod
    def from_bytes(cls, data):
        node = cls(0)
        node.block_id = struct.unpack_from('>Q', data, 0)[0]
        node.parent_id = struct.unpack_from('>Q', data, 8)[0]
        node.num_keys = struct.unpack_from('>Q', data, 16)[0]
        for i in range(MAX_KEYS):
            node.keys[i] = struct.unpack_from('>Q', data, 24 + (i * 8))[0]
        for i in range(MAX_KEYS):
            node.values[i] = struct.unpack_from('>Q', data, 24 + (MAX_KEYS * 8) + (i * 8))[0]
        for i in range(MAX_CHILDREN):
            node.children[i] = struct.unpack_from('>Q', data, 24 + (MAX_KEYS * 16) + (i * 8))[0]
        # Check if this is a leaf node by looking at children
        node.is_leaf = all(child == 0 for child in node.children)
        return node


def read_header(filename):
    with open(filename, 'rb') as f:
        header = f.read(BLOCK_SIZE)
    if header[0:8] != MAGIC_NUMBER:
        raise ValueError("Invalid magic number in " + filename)
    root_id = struct.unpack_from('>Q', header, 8)[0]
    next_block_id = struct.unpack_from('>Q', header, 16)[0]
    return root_id, next_block_id


def write_header(filename, root_id, next_block_id):
    header = bytearray(BLOCK_SIZE)
    header[0:8] = MAGIC_NUMBER
    struct.pack_into('>Q', header, 8, root_id)
    struct.pack_into('>Q', header, 16, next_block_id)
    with open(filename, 'r+b') as f:
        f.write(header)


def read_node(filename, block_id, node_cache):
    cached_node = node_cache.get(block_id)
    if cached_node:
        return cached_node
    if block_id == 0:
        return None
    with open(filename, 'rb') as f:
        f.seek(block_id * BLOCK_SIZE)
        data = f.read(BLOCK_SIZE)
    node = BTreeNode.from_bytes(data)
    node_cache.put(node)
    return node


def write_node(filename, node, node_cache):
    with open(filename, 'r+b') as f:
        f.seek(node.block_id * BLOCK_SIZE)
        f.write(node.to_bytes())
    node_cache.put(node)


def search(filename, key):
    node_cache = NodeCache()
    try:
        root_id, _ = read_header(filename)
        if root_id == 0:
            return None, -1
        node = read_node(filename, root_id, node_cache)
        while node:
            i = 0
            while i < node.num_keys and key > node.keys[i]:
                i += 1
            if i < node.num_keys and key == node.keys[i]:
                return node, i
            if node.is_leaf:
                return None, -1
            node = read_node(filename, node.children[i], node_cache)
        return None, -1
    except Exception as e:
        print("Search error: " + str(e))
        return None, -1


def insert(filename, key, value):
    node_cache = NodeCache()
    try:
        root_id, next_block_id = read_header(filename)
        if root_id == 0:
            # First insert, so we create the root node
            root = BTreeNode(next_block_id)
            root.keys[0] = key
            root.values[0] = value
            root.num_keys = 1
            write_node(filename, root, node_cache)
            write_header(filename, next_block_id, next_block_id + 1)
            return True
        node, idx = search(filename, key)
        if node:
            node.values[idx] = value  # update if exists
            write_node(filename, node, node_cache)
            return True
        node_cache.clear()
        root = read_node(filename, root_id, node_cache)
        if root.num_keys == MAX_KEYS:
            new_root = BTreeNode(next_block_id)
            new_root.is_leaf = False
            new_root.children[0] = root_id
            root.parent_id = next_block_id
            split_child(filename, new_root, 0, root, node_cache, next_block_id + 1)
            write_header(filename, new_root.block_id, next_block_id + 2)
            return insert_non_full(filename, new_root, key, value, node_cache)
        else:
            return insert_non_full(filename, root, key, value, node_cache)
    except Exception as e:
        print("Insert error: " + str(e))
        return False


def insert_non_full(filename, node, key, value, node_cache):
    i = node.num_keys - 1
    if node.is_leaf:
        while i >= 0 and key < node.keys[i]:
            node.keys[i + 1] = node.keys[i]
            node.values[i + 1] = node.values[i]
            i -= 1
        node.keys[i + 1] = key
        node.values[i + 1] = value
        node.num_keys += 1
        write_node(filename, node, node_cache)
        return True
    else:
        while i >= 0 and key < node.keys[i]:
            i -= 1
        i += 1
        child = read_node(filename, node.children[i], node_cache)
        if child.num_keys == MAX_KEYS:
            _, next_block_id = read_header(filename)
            split_child(filename, node, i, child, node_cache, next_block_id)
            write_header(filename, node.block_id if node.parent_id == 0 else node.parent_id, next_block_id + 1)
            if key > node.keys[i]:
                i += 1
                child = read_node(filename, node.children[i], node_cache)
        return insert_non_full(filename, child, key, value, node_cache)


def split_child(filename, parent, index, child, node_cache, new_node_id):
    new_node = BTreeNode(new_node_id, parent.block_id, child.is_leaf)
    mid = MIN_DEGREE - 1
    for j in range(mid + 1, MAX_KEYS):
        new_node.keys[j - (mid + 1)] = child.keys[j]
        new_node.values[j - (mid + 1)] = child.values[j]
        child.keys[j] = 0
        child.values[j] = 0
    if not child.is_leaf:
        for j in range(mid + 1, MAX_CHILDREN):
            new_node.children[j - (mid + 1)] = child.children[j]
            child.children[j] = 0
    new_node.num_keys = MIN_DEGREE - 1
    child.num_keys = mid
    for j in range(parent.num_keys, index, -1):
        parent.children[j + 1] = parent.children[j]
    parent.children[index + 1] = new_node.block_id
    for j in range(parent.num_keys - 1, index - 1, -1):
        parent.keys[j + 1] = parent.keys[j]
        parent.values[j + 1] = parent.values[j]
    parent.keys[index] = child.keys[mid]
    parent.values[index] = child.values[mid]
    child.keys[mid] = 0
    child.values[mid] = 0
    parent.num_keys += 1
    write_node(filename, child, node_cache)
    write_node(filename, new_node, node_cache)
    write_node(filename, parent, node_cache)


def create_index(filename):
    if os.path.exists(filename):
        print("File " + filename + " already exists.")
        sys.exit(1)
    header = bytearray(BLOCK_SIZE)
    header[0:8] = MAGIC_NUMBER
    struct.pack_into('>Q', header, 8, 0)
    struct.pack_into('>Q', header, 16, 1)
    with open(filename, 'wb') as f:
        f.write(header)
    print("Index created: " + filename)


def load_csv(filename, csv_filename):
    if not os.path.exists(filename):
        print("Can't find index file " + filename)
        sys.exit(1)
    if not os.path.exists(csv_filename):
        print("Can't find CSV file " + csv_filename)
        sys.exit(1)
    try:
        read_header(filename)
    except ValueError as e:
        print("Header check failed: " + str(e))
        sys.exit(1)
    with open(csv_filename, 'r') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if len(row) >= 2:
                try:
                    key = int(row[0])
                    value = int(row[1])
                    insert(filename, key, value)
                except ValueError:
                    print("Skipping row: " + str(row))
    print("CSV loaded into " + filename)


def print_index(filename):
    if not os.path.exists(filename):
        print("File not found: " + filename)
        sys.exit(1)
    try:
        root_id, _ = read_header(filename)
    except ValueError as e:
        print("Header issue: " + str(e))
        sys.exit(1)
    if root_id == 0:
        print("Nothing in index yet.")
        return
    node_cache = NodeCache()
    pairs = []

    def inorder_traverse(node_id):
        if node_id == 0:
            return
        node = read_node(filename, node_id, node_cache)
        for i in range(node.num_keys):
            if not node.is_leaf:
                inorder_traverse(node.children[i])
            pairs.append((node.keys[i], node.values[i]))
        if not node.is_leaf:
            inorder_traverse(node.children[node.num_keys])

    inorder_traverse(root_id)
    for key, value in pairs:
        print(str(key) + ": " + str(value))


def extract_index(filename, output_filename):
    if not os.path.exists(filename):
        print("Index file " + filename + " not found.")
        sys.exit(1)
    if os.path.exists(output_filename):
        print("Output file already exists: " + output_filename)
        sys.exit(1)
    try:
        root_id, _ = read_header(filename)
    except ValueError as e:
        print("Header issue: " + str(e))
        sys.exit(1)
    node_cache = NodeCache()
    pairs = []

    def inorder_traverse(node_id):
        if node_id == 0:
            return
        node = read_node(filename, node_id, node_cache)
        for i in range(node.num_keys):
            if not node.is_leaf:
                inorder_traverse(node.children[i])
            pairs.append((node.keys[i], node.values[i]))
        if not node.is_leaf:
            inorder_traverse(node.children[node.num_keys])

    if root_id != 0:
        inorder_traverse(root_id)
    with open(output_filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        for key, value in pairs:
            writer.writerow([key, value])
    print("Data written to " + output_filename)


def main():
    if len(sys.argv) < 2:
        print("Missing command.")
        return
    command = sys.argv[1].lower()
    if command == "create" and len(sys.argv) >= 3:
        create_index(sys.argv[2])
    elif command == "insert" and len(sys.argv) >= 5:
        filename = sys.argv[2]
        try:
            key = int(sys.argv[3])
            value = int(sys.argv[4])
            if not os.path.exists(filename):
                print("Index file not found: " + filename)
                sys.exit(1)
            if insert(filename, key, value):
                print("Inserted " + str(key) + " -> " + str(value))
            else:
                print("Insert failed for key " + str(key))
        except ValueError:
            print("Key and value must be numbers.")
            sys.exit(1)
    elif command == "search" and len(sys.argv) >= 4:
        filename = sys.argv[2]
        try:
            key = int(sys.argv[3])
            if not os.path.exists(filename):
                print("Index file not found: " + filename)
                sys.exit(1)
            node, idx = search(filename, key)
            if node:
                print("Found: " + str(key) + " => " + str(node.values[idx]))
            else:
                print(str(key) + " not found.")
        except ValueError:
            print("Invalid key. Should be a number.")
            sys.exit(1)
    elif command == "load" and len(sys.argv) >= 4:
        load_csv(sys.argv[2], sys.argv[3])
    elif command == "print" and len(sys.argv) >= 3:
        print_index(sys.argv[2])
    elif command == "extract" and len(sys.argv) >= 4:
        extract_index(sys.argv[2], sys.argv[3])
    else:
        print("Unknown or incorrect command.")
        print("Usage:")
        print("  project3 create <index_file>")
        print("  project3 insert <index_file> <key> <value>")
        print("  project3 search <index_file> <key>")
        print("  project3 load <index_file> <csv_file>")
        print("  project3 print <index_file>")
        print("  project3 extract <index_file> <output_file>")


if __name__ == "__main__":
    main()
