# File Manager
## Summary
## Introduction
File manager is an api that allows to convert and compress. No authentification, no premium subsription, just what you need.
## Setup
### Requirements
To ensure the full working api, there are some tools needed :
<ul>
    <li>Python interpreter (3.12 or more required)</li>
    <li>Exiftool</li>
    <li>Pandoc</li>
    <li>Ffmpeg</li>
</ul>

### Installation
First, install the environnement for Python.
```cmd
python --venv MyEnv
```

Then, install the required packages in cmd :
```cmd
pip install requirements.txt
```

Finnaly, you can run the api by launching Uvicorn : 

```cmd
uvicorn main:api --host 0.0.0.0 --port 8081 --reload
```
## Contribution
Please refer to the [contributing guide here](./.github/CONTRIBUTING.md)