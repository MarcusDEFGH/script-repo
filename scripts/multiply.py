import argparse
parser = argparse.ArgumentParser(description='Multiply numbers')
parser.add_argument("first_number", help="int: First number")
parser.add_argument("second_number", help="int: Second number")
args = parser.parse_args()
print(args.first_number * args.second_number)
