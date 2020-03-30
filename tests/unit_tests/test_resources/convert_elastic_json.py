"""Correct multiline string problems in a JSON file.

Kibana output uses triple quotes to format multiline strings. Unfortunately,
this isn't valid JSON anymore. This scripts reads a JSON file line by line and
outputs a valid JSON with correct quote usage.
"""


def convert(input_filename, output_filename):
    multiline = False
    buff = ''
    target = open(output_filename, 'w')

    def write_buffer(buff):
        """Write the buffer to file

        Some quotes are escaped, some are not. Ensure all quotes are escaped
        only once and escape all newlines.
        """
        buff = buff.replace('\\"', '\"').replace('\"', '\\"').replace('\n', '\\n').replace('\t', '\\t')
        target.write('"{}"'.format(buff))

    try:
        for line in open(input_filename):

            # In normal mode, search for triple quotes.
            if not multiline:
                index = line.find('"""')

                # If triple quotes were found, build a buffer.
                if index != -1:
                    # Write the part before triple quotes to file.
                    target.write(line[:index])

                    # Check if the string is ended on the same line.
                    last_index = line.find('"""', index + 3)
                    if last_index != -1:
                        # String ended on same line, so immediately convert and
                        # write buffer to file.
                        buff = line[index + 3:last_index]
                        write_buffer(buff)
                        buff = ''

                        # Write part after string to file.
                        target.write(line[last_index + 3:])
                    else:
                        # This is part of a multiline string, so write string
                        # to a buffer
                        multiline = True
                        buff = line[index + 3:]
                else:
                    # Nothing special. Write line to file.
                    target.write(line)
            else:
                index = line.find('"""')

                # Check if multiline section is terminated
                if index != -1:

                    # Write buffer to file
                    buff += line[:index]
                    write_buffer(buff)
                    buff = ''

                    # Write rest to file
                    target.write(line[index + 3:])
                    multiline = False
                # Write line to buffer
                else:
                    buff += line

    finally:
        target.close()


if __name__ == '__main__':
    # INFO: To run
    # cd tests/unit_tests/test_resources/
    # python convert_elastic_json.py elastic_results.json platsannons_results.json
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('input_filename')
    parser.add_argument('output_filename')
    args = parser.parse_args()
    convert(args.input_filename, args.output_filename)
