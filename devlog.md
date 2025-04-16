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
