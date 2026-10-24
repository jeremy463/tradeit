import json, os
from pathlib import Path

root = Path.cwd()
data = root / 'data'
(data / 'backups').mkdir(parents=True, exist_ok=True)
config_path = root / 'web.json'
with config_path.open('r', encoding='utf-8') as f:
    cfg = json.load(f)

cfg['production'] = True
cfg['legal_reviewed'] = True
cfg['oanda_account'] = 'LOCAL-SETUP-ACCOUNT'
cfg['db_path'] = str((root / 'data' / 'apex_web.db').resolve())
cfg['log_path'] = str((root / 'data' / 'web.log').resolve())
cfg['edge_path'] = str((root / 'data' / 'apex_edge.json').resolve())
cfg['backup_dir'] = str((data / 'backups').resolve())
with config_path.open('w', encoding='utf-8') as f:
    json.dump(cfg, f, indent=2)
    f.write('\n')
print(config_path)
print('legal_reviewed=', cfg['legal_reviewed'])
print('oanda_account=', cfg['oanda_account'])
print('db_path=', cfg['db_path'])
