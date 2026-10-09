from __future__ import annotations
import argparse
from datetime import datetime, timezone
from pathlib import Path
import json
import re
import sys
import yaml
from lxml import html
from .network import SecClient, SessionLock, AccessPaused, AccessStopped, ResourceUnavailable


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, default=Path('.'))
    parser.add_argument('--as-of', required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    datetime.fromisoformat(args.as_of)
    config = yaml.safe_load((root / 'config.yaml').read_text())
    results = []
    with SessionLock(root, config['session_stale_minutes']) as lock:
        client = SecClient(root, config, args.as_of, lock)
        try:
            for url in config['network']['documentation_to_verify']:
                raw = client.get(url)
                tree = html.fromstring(raw)
                text = ' '.join(tree.itertext())
                checks = {}
                if 'programming-interfaces' in url:
                    checks = {'submissions_documented': 'submissions' in text.lower(),
                        'companyfacts_documented': 'companyfacts' in text.lower(),
                        'companyconcept_documented': 'companyconcept' in text.lower(),
                        'pagination_documented': '1,000' in text or '1000' in text}
                results.append({'url': url, 'bytes': len(raw), 'checks': checks})
                (root / 'work/documentation_checks.json').write_text(json.dumps(results, indent=2))
                print(json.dumps(results[-1]))
            print('Documentation reçue ; validation détaillée à effectuer avant la collecte.')
        except AccessPaused as exc:
            print(str(exc))
            return 75
        except (AccessStopped, ResourceUnavailable) as exc:
            print(str(exc))
            return 76
        finally:
            client.close()
    return 0


if __name__ == '__main__':
    sys.exit(main())
