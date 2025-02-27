# FILE-COMPRESSOR
This project implements a file compression utility using Huffman coding—a lossless data compression technique that assigns variable-length binary codes to bytes based on their frequencies. The utility not only compresses and decompresses files but also supports conversion between different file formats such as .huf, .zip, and .txt. It is designed to work with text and binary files, ensuring that the original data is perfectly recoverable after decompression.

Features

Huffman Compression:
Reads any input file and builds a frequency table.
Constructs a deterministic Huffman tree using a priority queue.
Generates a prefix-free binary code for each byte.
Compresses file contents into a compact binary format with header information.

Huffman Decompression:
Reconstructs the Huffman tree from header data.
Decodes the bitstream to recover the original file content.

File Conversion:
Convert a compressed .huf file to a ZIP archive and extract .huf from ZIP.
Convert a .huf file to a plain text (.txt) file.
Convert a plain text (.txt) file directly to a ZIP archive.
Extract .txt files from a ZIP archive.

Robust and Efficient:
Handles files of various sizes and types.
Operates in O(n) time and space complexity with respect to the file size.

How It Works
Compression Process:
The input file is read to build a frequency table of its bytes.
A Huffman tree is built based on these frequencies.
Codes are generated by traversing the tree (left edges contribute a '0' and right edges a '1').
The original file is encoded by replacing each byte with its corresponding Huffman code.
The encoded data, along with header information (such as the frequency table), is written to a .huf file.

Decompression Process:
The frequency table and header are read from the compressed file.
The Huffman tree is reconstructed.
The encoded bitstream is decoded by traversing the tree to retrieve the original bytes.
The decoded bytes are written back to an output file.
Conversion Functions:

Additional functions wrap the core compression/decompression logic to convert between .huf, .zip, and .txt formats using standard file I/O and ZIP operations.
