# Install!

This code creates a convenient way to experiment with latent semantic indexing on top of some proved C numerical libraries. You'll need to go through a few extra steps to get these libraries installed locally:

1. Run Elasticsearch
2. Install system prereqs for [SciPy](http://www.scipy.org/install.html)
3. Install prereqs into pyvenv

```bash
pyvenv venv
source ven/bin/activate
pip install -r requirements.txt
```

# Run!

```bash
python createStackExchange.py
python indexStackExchange.py
python stackexchange.py
```

# Play!
1. Play with createstackexchange to alter analysis and mapping settings
2. Play with stackexchange.py to alter how the term-doc matrix is constructed
3. Play with how the semantic index is interacted with to see how different approaches work
