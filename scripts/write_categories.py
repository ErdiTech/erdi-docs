"""Write the _category_.json sidebar files."""
import json, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CATS = {
    "get-started": {"label": "Get started", "position": 2, "collapsed": False},
    "models": {"label": "Models", "position": 3, "link": {"type": "doc", "id": "models/index"}},
    "protocols": {"label": "Protocols", "position": 4, "collapsed": False},
    "platforms": {"label": "Platforms", "position": 5, "collapsed": False},
    "compatibility": {"label": "Compatibility", "position": 6, "link": {"type": "doc", "id": "compatibility/index"}},
    "tools": {"label": "Tools", "position": 7, "collapsed": False},
    "guides": {"label": "Guides", "position": 7.5},
}
for d, c in CATS.items():
    os.makedirs(os.path.join(ROOT, "docs", d), exist_ok=True)
    json.dump(c, open(os.path.join(ROOT, "docs", d, "_category_.json"), "w"), indent=1)
print("ok")
