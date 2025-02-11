import os
import heapq
import zipfile
from collections import defaultdict

# ----------------- Huffman Compression -----------------
# Huffman Node class with deterministic tie-breaking using sorted order.
class HuffmanNode:
    def __init__(self, char, freq):
        self.char = char  # byte value (0-255) or None for internal nodes
        self.freq = freq
        self.left = None
        self.right = None

    def __lt__(self, other):
        # For equal frequencies, compare by the byte value (internal nodes are treated as 256)
        self_val = self.char if self.char is not None else 256
        other_val = other.char if other.char is not None else 256
        if self.freq == other.freq:
            return self_val < other_val
        return self.freq < other.freq

def validate_file_path(path, mode='r'):
    if mode == 'r' and not os.path.isfile(path):
        print(f"Error: File '{path}' not found.")
        return False
    directory = os.path.dirname(os.path.abspath(path)) or "."
    if mode == 'w' and not os.access(directory, os.W_OK):
        print(f"Error: Cannot write to path '{path}'.")
        return False
    return True

def build_frequency_table(data):
    frequency = defaultdict(int)
    for byte in data:
        frequency[byte] += 1
    return frequency

def build_huffman_tree(frequency):
    # Create nodes in deterministic order (sort by byte value)
    nodes = [HuffmanNode(byte, freq) for byte, freq in sorted(frequency.items()) if freq > 0]
    heapq.heapify(nodes)
    while len(nodes) > 1:
        left = heapq.heappop(nodes)
        right = heapq.heappop(nodes)
        merged = HuffmanNode(None, left.freq + right.freq)
        merged.left = left
        merged.right = right
        heapq.heappush(nodes, merged)
    return nodes[0] if nodes else None

def generate_codes(root, current_code="", codes=None):
    if codes is None:
        codes = {}
    if root is None:
        return codes
    # If only one unique byte exists, assign it a default code "0"
    if root.char is not None:
        codes[root.char] = current_code if current_code != "" else "0"
        return codes
    generate_codes(root.left, current_code + "0", codes)
    generate_codes(root.right, current_code + "1", codes)
    return codes

def compress(input_path, output_path):
    if not validate_file_path(input_path, 'r'):
        return

    with open(input_path, 'rb') as f:
        data = f.read()
    if not data:
        print("Error: Cannot compress an empty file.")
        return

    frequency = build_frequency_table(data)
    root = build_huffman_tree(frequency)
    codes = generate_codes(root)

    # Encode the data using the Huffman codes.
    encoded_bits = ''.join(codes[byte] for byte in data)
    padding = (8 - len(encoded_bits) % 8) % 8
    encoded_bits += '0' * padding
    encoded_bytes = bytearray(int(encoded_bits[i:i+8], 2) for i in range(0, len(encoded_bits), 8))

    try:
        with open(output_path, 'wb') as f:
            # Write frequency table: 256 values, each 4-byte big-endian.
            for byte in range(256):
                f.write(frequency.get(byte, 0).to_bytes(4, 'big'))
            # Write one byte for the padding length.
            f.write(padding.to_bytes(1, 'big'))
            # Write the encoded data.
            f.write(encoded_bytes)
        print(f"Compressed {os.path.getsize(input_path)} bytes to {os.path.getsize(output_path)} bytes.")
    except IOError:
        print("Error: Unable to write compressed file.")

def decompress(input_path, output_path):
    if not validate_file_path(input_path, 'r'):
        return
    try:
        with open(input_path, 'rb') as f:
            # Read the 256 * 4 byte frequency table.
            frequency = {byte: int.from_bytes(f.read(4), 'big') for byte in range(256)}
            padding = int.from_bytes(f.read(1), 'big')
            encoded_bytes = f.read()

        root = build_huffman_tree(frequency)
        if not root:
            print("Error: Invalid Huffman data.")
            return

        # Convert encoded bytes to bit string.
        encoded_bits = ''.join(f"{byte:08b}" for byte in encoded_bytes)
        if padding > 0:
            encoded_bits = encoded_bits[:-padding]

        decoded_data = bytearray()
        current_node = root
        for bit in encoded_bits:
            current_node = current_node.left if bit == '0' else current_node.right
            if current_node.char is not None:
                decoded_data.append(current_node.char)
                current_node = root

        with open(output_path, 'wb') as f:
            f.write(decoded_data)
        try:
            text = decoded_data.decode('utf-8')
            print(f"Decompressed to text file: '{output_path}'.")
        except UnicodeDecodeError:
            print(f"Decompressed to binary file: '{output_path}'.")
    except (IOError, ValueError) as e:
        print(f"Error: {e}")

# ----------------- Conversion Functions -----------------
def zip_to_huf(zip_path, output_path):
    if not validate_file_path(zip_path, 'r'):
        return
    with zipfile.ZipFile(zip_path, 'r') as zipf:
        for file_info in zipf.infolist():
            if file_info.filename.endswith('.huf'):
                with zipf.open(file_info) as huf_file:
                    content = huf_file.read()
                with open(output_path, 'wb') as f:
                    f.write(content)
                print(f"Extracted '{file_info.filename}' to '{output_path}'.")
                return
    print("No .huf file found in ZIP archive.")

def huf_to_txt(huf_path, output_path):
    temp_bin = "temp.bin"
    decompress(huf_path, temp_bin)
    try:
        with open(temp_bin, 'rb') as f:
            text_content = f.read().decode('utf-8')
        with open(output_path, 'w', encoding='utf-8') as txt_file:
            txt_file.write(text_content)
        print(f"Converted '{huf_path}' to text file '{output_path}'.")
    except UnicodeDecodeError:
        print("Error: Decompressed data is not valid UTF-8 text.")
    finally:
        if os.path.exists(temp_bin):
            os.remove(temp_bin)

def zip_to_txt(zip_path, output_path):
    temp_huf = "temp.huf"
    zip_to_huf(zip_path, temp_huf)
    huf_to_txt(temp_huf, output_path)
    if os.path.exists(temp_huf):
        os.remove(temp_huf)

def txt_to_zip(txt_path, zip_path):
    if not validate_file_path(txt_path, 'r'):
        return
    try:
        with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(txt_path, arcname=os.path.basename(txt_path))
        print(f"Created ZIP archive: '{zip_path}' containing '{txt_path}'.")
    except IOError:
        print("Error: Unable to create ZIP archive.")

def extract_txt_from_zip(zip_path, output_path):
    if not validate_file_path(zip_path, 'r'):
        return
    with zipfile.ZipFile(zip_path, 'r') as zipf:
        for file_info in zipf.infolist():
            if file_info.filename.endswith('.txt'):
                with zipf.open(file_info) as txt_file:
                    content = txt_file.read()
                with open(output_path, 'wb') as f:
                    f.write(content)
                print(f"Extracted '{file_info.filename}' to '{output_path}'.")
                return
    print("No .txt file found in ZIP archive.")

# ----------------- Main Menu -----------------
def main():
    while True:
        print("\n=== File Compressor and Converter ===")
        print("1. Compress file (Huffman)")
        print("2. Decompress .huf file")
        print("3. Convert .huf to .zip")
        print("4. Extract .huf from ZIP")
        print("5. Convert .huf to .txt")
        print("6. Convert ZIP (with .huf) to .txt")
        print("7. Convert .txt to .zip")
        print("8. Extract .txt from ZIP")
        print("9. Exit")
        choice = input("Enter choice: ")
        if choice == '1':
            input_file = input("Input file (any type): ")
            output_file = input("Output file (.huf): ")
            compress(input_file, output_file)
        elif choice == '2':
            input_file = input("Compressed file (.huf): ")
            output_file = input("Output file: ")
            decompress(input_file, output_file)
        elif choice == '3':
            huf_file = input("Input Huffman file (.huf): ")
            zip_file = input("Output ZIP file (.zip): ")
            try:
                with zipfile.ZipFile(zip_file, 'w', compression=zipfile.ZIP_DEFLATED) as zipf:
                    zipf.write(huf_file, arcname=os.path.basename(huf_file))
                print(f"Created ZIP archive: '{zip_file}'.")
            except IOError:
                print("Error: Unable to create ZIP archive.")
        elif choice == '4':
            zip_file = input("Input ZIP file (.zip): ")
            huf_file = input("Output .huf file: ")
            zip_to_huf(zip_file, huf_file)
        elif choice == '5':
            huf_file = input("Input Huffman file (.huf): ")
            txt_file = input("Output text file (.txt): ")
            huf_to_txt(huf_file, txt_file)
        elif choice == '6':
            zip_file = input("Input ZIP file (.zip): ")
            txt_file = input("Output text file (.txt): ")
            zip_to_txt(zip_file, txt_file)
        elif choice == '7':
            txt_file = input("Input text file (.txt): ")
            zip_file = input("Output ZIP file (.zip): ")
            txt_to_zip(txt_file, zip_file)
        elif choice == '8':
            zip_file = input("Input ZIP file (.zip): ")
            txt_file = input("Output text file (.txt): ")
            extract_txt_from_zip(zip_file, txt_file)
        elif choice == '9':
            print("Exiting the program.")
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main()
