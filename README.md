# Batchup

An unnecessary backup utility.

This project emerged as a tool to back up files from a computer to a slow external drive.
The main idea was that only files that have changed since the last backup would be copied, making the process much faster.
In addition, the user would have large control over which files and directories to back up.

I later learned that `rsync` is a much better tool for the job, and this project thus became obsolete.
However, the code contains some features that are interesting enough to keep around:
- generators and lazy evaluation make it possible to show progress in real time
- a two-tier keyboard interrupt system makes it possible to stop the backup process while still waiting for the current file to finish copying
- everything is designed to run both on Windows and Unix-like systems, taking into account the differences in file systems
