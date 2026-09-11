"""Search a run's effective file index without loading it all into memory."""
import argparse
from pathlib import Path
import json

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run',type=Path)
    parser.add_argument('query')
    parser.add_argument('--limit',type=int,default=40)
    args=parser.parse_args()
    if args.limit<0:parser.error('Limit must be nonnegative')
    matches=0
    with (args.run/'raw/files.jsonl').open(encoding='utf-8') as stream:
        for line in stream:
            row=json.loads(line)
            if args.query.casefold() not in row['path'].casefold():continue
            matches+=1
            if matches<=args.limit:print(f"{row['path']}\t{row['archive']}\t{row['bytes']} bytes")
    print(f'{matches} matching paths; {min(matches,args.limit)} displayed')

if __name__=='__main__':main()
