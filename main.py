import os
import re
import codecs


# Function to read SRT file content
def read_srt_file(file_path):
    """
    Reads an SRT file and returns a list of subtitle blocks, handling different line endings.

    Args:
    file_path (str): Path to the SRT file.

    Returns:
    list: A list of subtitle blocks.
    """
    with codecs.open(file_path, 'r', 'utf-8-sig') as file:
        content = file.read()

    # Normalize line endings to Unix-style
    content = content.replace('\r\n', '\n')

    # Splitting the content into blocks
    blocks = re.split(r'\n\n+', content)
    return blocks


# Function to process each subtitle block
def process_subtitle_blocks(blocks, max_length=25):
    processed_blocks = []
    for block in blocks:
        processed_block = process_block(block, max_length)
        processed_blocks.append(processed_block)
    return processed_blocks


# Function to process a single subtitle block and split timecodes if necessary
def process_block(block, max_length):
    """
    Processes a single subtitle block, splitting it into multiple lines and adjusting timecodes.

    Args:
    block (str): A block of subtitle text.
    max_length (int): Maximum length of each subtitle line.

    Returns:
    str: Processed subtitle block with split lines and adjusted timecodes.
    """
    lines = block.split('\n')

    # Skip the numeric identifier if present
    if lines[0].isdigit():
        lines = lines[1:]

    # Check if the block has at least 2 lines (timecode and text)
    if len(lines) < 2:
        return '', 0

    timecode = lines[0]

    # Validate timecode format
    if ' --> ' not in timecode:
        return '', 0

    text_lines = lines[1:]
    split_lines = [split_line(line, max_length) for line in text_lines]
    split_lines_flat = [line for sublist in split_lines for line in sublist]

    processed_timecodes = split_timecode(timecode, len(split_lines_flat))

    processed_block = []
    for i, line in enumerate(split_lines_flat):
        processed_block.append(processed_timecodes[i] + '\n' + line)

    # Return both the processed block and the number of lines it contains
    return '\n\n'.join(processed_block), len(split_lines_flat)


# Function to split a line into multiple lines if it exceeds max_length
def split_line(line, max_length):
    """
    Splits a line into multiple lines, each not exceeding the maximum length.

    Args:
    line (str): The line of text to be split.
    max_length (int): The maximum length of each split line.

    Returns:
    list: A list of split lines.
    """
    words = line.split()
    split_lines = []
    current_line = ""

    for word in words:
        if len(current_line + ' ' + word) <= max_length:
            current_line += ' ' + word if current_line else word
        else:
            split_lines.append(current_line)
            current_line = word
    if current_line:
        split_lines.append(current_line)

    return split_lines


# Function to split a timecode into equal parts based on the number of splits
def split_timecode(timecode, num_splits):
    """
    Splits a timecode into multiple intervals based on the number of text lines.

    Args:
    timecode (str): The original timecode for the subtitle block.
    num_splits (int): The number of lines after splitting the text.

    Returns:
    list: A list of timecodes for each split line.
    """
    start, end = timecode.split(' --> ')
    start_ms = convert_to_ms(start)
    end_ms = convert_to_ms(end)
    duration_per_split = (end_ms - start_ms) / num_splits

    split_timecodes = []
    for i in range(num_splits):
        new_start_ms = start_ms + i * duration_per_split
        new_end_ms = start_ms + (i + 1) * duration_per_split
        split_timecodes.append(f"{convert_to_str(new_start_ms)} --> {convert_to_str(new_end_ms)}")

    return split_timecodes


# Helper function to convert a time string to milliseconds
def convert_to_ms(time_str):
    """
    Converts a time string in the format 'HH:MM:SS,mmm' to milliseconds.

    Args:
    time_str (str): Time string in 'HH:MM:SS,mmm' format.

    Returns:
    int: Time in milliseconds.
    """
    h, m, s = time_str.split(':')
    s, ms = s.split(',')
    return int(h) * 3600000 + int(m) * 60000 + int(s) * 1000 + int(ms)


# Helper function to convert milliseconds to a time string
def convert_to_str(ms):
    """
    Converts milliseconds to a time string in the format 'HH:MM:SS,mmm'.

    Args:
    ms (int): Time in milliseconds.

    Returns:
    str: Time string in 'HH:MM:SS,mmm' format.
    """
    h = int(ms // 3600000)
    m = int((ms % 3600000) // 60000)
    s = int((ms % 60000) // 1000)
    ms = int(ms % 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def main(input_file_path, max_length=25):
    """
    Main function to process an SRT file and write the processed content to a new file.
    The output file will be named with 'split' appended before the file extension of the input file.

    Args:
    input_file_path (str): Path to the input SRT file.
    """
    try:
        # Construct the output file path
        file_name, file_extension = os.path.splitext(input_file_path)
        output_file_path = f"{file_name}_split{file_extension}"

        blocks = read_srt_file(input_file_path)
        subtitle_number = 1
        with codecs.open(output_file_path, 'w', 'utf-8-sig') as file:
            for block in blocks:
                processed_block, num_lines = process_block(block, max_length)
                if processed_block:
                    block_lines = processed_block.split('\n\n')
                    for line in block_lines:
                        file.write(f"{subtitle_number}\n{line}\n\n")
                        subtitle_number += 1

        print(f"Processed subtitles written to {output_file_path}")
    except Exception as e:
        print(f"An error occurred: {e}")
