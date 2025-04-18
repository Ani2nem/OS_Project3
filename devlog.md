# Development Log

## April 16, 2025 - 10:00 am

### Initial Thoughts
Starting Project 3 today. It's this B-tree index file thing where we have to build a command line program to do a bunch of operations with index files. Looks like I need to make something that can create files, add key/value pairs, search for stuff, load from CSV files, and print everything out.

From what I understand, I'm working with B-trees that have a minimum degree of 10, which means... I think up to 19 key/value pairs per node? The file structure has these 512-byte blocks and there's all this specific formatting for headers and nodes. Oh, and I can only have 3 nodes in memory at once, which sounds annoying to manage.

### Plan for the Project
I need to:
1. Get my repo set up first (learned the lesson from last time about not submitting the Git repo)
2. Figure out how to handle these file formats with all the bytes and stuff
3. Get the B-tree operations working (insert and search look tricky)
4. Set up all the command line stuff
5. Do the CSV file handling
6. Test it to make sure it doesn't crash
7. Write up some docs so the TA knows what I did

### Plan for this Session
Today I'll try to:
1. Set up my repo
2. Make a simple placeholder file just to get started
3. Start coding the command line interface, that seems like the easiest part
4. Maybe start figuring out the file format stuff if I have time

The byte order stuff looks like a pain, and I'm not really sure how the B-tree is supposed to work exactly. That's probably going to be the hardest part.

Just gotta put some code on, so I can figure stuff out as I go. 


### Progress So Far
Got the basic structure of my program set up. Started with implementing the 'create' command since it seemed like the simplest one to get working first. The create command:
1. Checks if the file already exists (and errors if it does)
2. Creates a 512-byte header block with:
   - The magic number "4348PRJ3"
   - Root node ID (0 for empty tree)
   - Next block ID (1, since header is block 0)
3. Writes this header to a new file

Tested it and it seems to create files correctly. The command line interface is basic but working.

### Next Steps
For my next session, I'll implement:
1. The BTreeNode class to represent nodes in the B-tree
2. Basic file operations for reading/writing nodes
3. The 'insert' command to add key/value pairs to the index

I'm still not entirely sure how to implement the B-tree operations efficiently while keeping only 3 nodes in memory at a time. Need to think more about this.




## April 16, 2025 - 2:00 pm

### Thoughts So Far
I've been thinking about how to implement this B-tree thing. From what I can tell, I need a way to represent the nodes and handle reading/writing them to the file. The tricky part is going to be making sure I don't have more than 3 nodes in memory at once.

I think I'll start by creating a BTreeNode class that can convert between the memory representation and the byte representation for storage. Then I'll add functions to read and write those nodes to the file.

The project spec has all these details about how the data should be stored in blocks, like how the first 8 bytes are the block ID, the next 8 bytes are the parent ID, and so on. I'll need to make sure I follow that format exactly.

### Plan for this Session
1. Implement the BTreeNode class that can convert to/from bytes
2. Add functions to read and write the header
3. Add functions to read and write nodes
4. Test these functions to make sure they work correctly

I'm not going to worry about the actual B-tree operations yet, just getting the file format stuff working first. It'll be a bunch of pass functions, I'll get back to impolementation later, I got class soon. 

### Progress So Far
Finished implementing the BTreeNode class and the file operations. Here's what I got down in code:

1. Created the BTreeNode class:
   - It has fields for block_id, parent_id, num_keys, keys, values, and children
   - Added to_bytes() method to convert a node to the specified byte format
   - Added from_bytes() class method to create a node from bytes

2. Implemented file operations:
   - read_header: Reads and validates the header, returns root_id and next_block_id
   - write_header: Updates the header in the file
   - read_node: Reads a node from the file given its block ID
   - write_node: Writes a node back to the file

The tricky part was getting all the byte packing right. I'm using struct.pack_into and struct.unpack_from with the '>Q' format to handle 8-byte big-endian integers as specified in the project.

Did some basic testing and it looks like the file operations are working correctly. I can create a file, read its header, and the magic number all look solid.


### Next Steps
For my next session:
1. Implement the actual B-tree operations (insert and search)
2. Add the remaining command-line options
3. Figure out how to manage the "3 nodes in memory" restriction

The B-tree operations are going to be the hard part. I need to make sure I understand how B-trees work before I start coding that part.



## April 17, 2025 - 10:30 am

### Thoughts So Far
I've been reviewing B-tree algorithms since last session. The basic operations are:

Searching which is - Start from root, binary search within a node to find key or the child where it would be
Inserting which is - Find where the key should go, insert it, and split nodes if they get too full
Deleting which is - Find the key, remove it and rebalance if needed (though we don't need to implement delete)

The tricky part is implementing this with only 3 nodes in memory at a time. I'll need to be careful about loading and unloading nodes from disk.

## Plan for this Session
Implementing the B-tree search operation
Implementing the B-tree insert operation (including node splitting)
Making sure these operations work with the "3 nodes in memory" restriction
Adding the search and insert commands to the CLI

I think the search operation will be simpler to implement first, so I'll start with that. Then I'll tackle the insert operation, which is harder because it needs to handle node splitting when a node gets full.


## Progress So Far

Everything's mostly done. 

For the load command: Python's csv module is a lifesaver. Just read in the file line by line, convert stuff to ints, and call my insert function. Added some error handling for bad files and data that can't be converted to numbers. Already had most of the hard stuff done since insert was working.

For printing, Had to write this recursive inorder traversal thing. Start at the root, recurse on the left children, print the current node's keys, then recurse on the right children. Makes everything come out in sorted order. Only tricky part was making sure I wasn't loading too many nodes into memory at once.

Extract was basically the same as print but writing to a file instead of the screen. Reused most of the same code.

Fixed up the command line interfacee to handle all the commands properly. Added a bunch of error messages so when someone does something stupid, they at least know what they did wrong.

Hit some weird bugs along the way:

Had this issue where the traverse function wasn't handling leaf nodes right
Found a dumb bug in my split_child where I wasn't zeroing out the keys after splitting
Had to fix some edge cases with empty trees

Seems solid now though. Tested a bunch of different cases and it all works


## Next Steps

Getting close to the finish line! I just need to:

Test a bit more, especially edge cases
Clean up all my sloppy code and add some comments
Write a readme so the TA knows how to use this thing
Double-check the project requirements
Submit and pray for a good grade (Please give me a good grade)

Pretty happy with how this turned out, honestly. B-trees are a pain but kinda cool once you get them working.



## April 18, 2025 - 10:30 am

### Thoughts So Far
Program's basically done! Got all the commands working, and the B-tree stuff seems solid. Just need to finish testing everything, make sure the README is good, and submit this thing.

### Plan for this Session

Test all the commands one more time
Check edge cases (empty trees, node splitting, etc.)
Finish the README
Double-check project requirements
Submit proj

### Progress So Far
Spent the morning testing everything:

Basic stuff works (create, insert, search)
Edge cases pass (empty trees, node splitting)
CSV loading/extracting works great
Error messages show up when they should

README's done! Made it clear how to run everything and what each command does. I think the TA will be able to figure it out pretty easily.
Checked against the project requirements:

All the required commands work
B-tree with degree 10 is done correctly
File format has 512-byte blocks
Never more than 3 nodes in memory (thanks to my NodeCache)
Error handling is also pretty solid after I tested it
Finished the README and devlog so TA can follow

Pretty happy with how this turned out! The B-tree stuff was definitely the hardest part, especially with that 3-node memory limit. But I think my solution is solid.

This is the link to the github page:
`https://github.com/Ani2nem/OS_Project3`