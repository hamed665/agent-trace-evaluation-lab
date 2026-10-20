import argparse
import json
from pathlib import Path
from evaluate import evaluate, compare


def run(path=None):
    data=json.loads(Path(path or Path(__file__).with_name('sample.json')).read_text())
    baseline={k:evaluate(v['case'],v['baseline']) for k,v in data.items()}
    candidate={k:evaluate(v['case'],v['candidate']) for k,v in data.items()}
    return {'baseline':baseline,'candidate':candidate,'comparison':compare(baseline,candidate)}


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description='Evaluate recorded agent behavior without a model API.')
    parser.add_argument('--input',type=Path,help='JSON mapping case IDs to case, baseline and candidate')
    args=parser.parse_args()
    report=run(args.input)
    print(json.dumps(report,indent=2))
    raise SystemExit(1 if report['comparison']['regressions'] else 0)
