# B-Tree Index File Manager

## Overview
This is a program that manages things called B-trees in index files. I had to make it so you can create files, add stuff to them, search through them, and do a bunch of other operations. The hardest part was definitely making sure I never had more than 3 nodes in memory at once (that was super annoying).

## My Files

- **Project3.py**: This is where all the actual code lives. It has:
  - A class for B-tree nodes 
  - This cache thing to make sure I don't keep more than 3 nodes in memory
  - A bunch of functions to read/write stuff to files
  - All the B-tree logic (search, insert, node splitting, etc.)
  - Command stuff so you can actually use it

- **devlog.md**: My development journal where I kept track of everything I did, problems I ran into, and how I fixed them.

- **README.md**: You're reading it right now! Just telling you how to use my program.

## How To Run It

You need Python 3 for this to work. Just run it from the command line with one of these commands:

### Commands You Can Use

1. **Make a new index file**:
   ```
   python3 Project3.py create test.idx
   ```
   This makes a new empty B-tree file.

2. **Add a key/value pair**:
   ```
   python3 Project3.py insert test.idx 15 100
   ```
   This adds the number 15 (key) and links it to 100 (value).

3. **Look for a key**:
   ```
   python3 Project3.py search test.idx 15
   ```
   This will check if 15 is in the file and tell you what value it has.

4. **Load from a CSV file**:
   ```
   python3 Project3.py load test.idx input.csv
   ```
   If you have a bunch of key/value pairs in a CSV, this will add them all at once.

5. **Print everything in the file**:
   ```
   python3 Project3.py print test.idx
   ```
   Shows you all the key/value pairs in the index.

6. **Save everything to a CSV file**:
   ```
   python3 Project3.py extract test.idx output.csv
   ```
   Dumps all the data into a CSV file.

## Some Technical Stuff

- The B-tree has a minimum degree of 10, which means each node can hold up to 19 key/value pairs
- Everything's stored in 512-byte blocks
- The first block has this magic number "4348PRJ3" and some other important info
- All the numbers are stored as 8-byte big-endian values (whatever that means)
- I made sure to limit memory usage with a cache thing

## Limitations

- Can't delete stuff once it's in there
- Only works with integer keys and values

## How I Tested It

I just tried all the commands to make sure they worked:
1. Created a file
2. Added some stuff
3. Searched for it to make sure it was there
4. Made a CSV file and loaded that in
5. Printed everything to check it was all sorted right
6. Saved it all back to a CSV

Hope you like it! It was a pain to code but kinda cool once it started working.