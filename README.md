# NSM Allvis API 

>  Script for gathering most relevant data from [NSM Allvis API](https://nsm.no/tjenester/allvis-nor/) written in python.



## Input and Output

Output: 
Currently the only outputs are write to file (json) and console/stdout.

## Build and Run

Instructions below are for Ubuntu 18.04 using Python 3.6.9 but should easily be converted to other operating systems and work on later versions of Python.

### Linux

1. Install [Python](https://www.python.org/)

2. Install pip3 and git

```
sudo apt-get install python3-pip git
```

3. Install [virtualenv](https://virtualenv.pypa.io/en/latest/)

```
sudo pip3 install virtualenv 
```

4. Clone this git-project

```
git clone https://github.com/strompa/nsm-allvis
```

5. Create new virtual env. We call it 'allvisenv'

```
virtualenv allvisenv --python=python3
```

6. Activate the fresh environement

```
source allvisenv/bin/activate
```

7. Install python requirements

```
pip install -r nsm-allvis/requirements.txt
```

8. Use editor of choice and enter organisation [API-ID and API-key](https://github.com/strompa/nsm-allvis/blob/4a882ddc5f2201037ca23d8a33ced1b3a0312ea3/allvis_api_v0_script_v01.py#L11) for Allvis service in the script.  

```
API_ID = 'apiid'
API_KEY = 'apikey'
```

9. Configure [outputs](https://github.com/strompa/nsm-allvis/blob/main/allvis_api_v0_script_v01.py#L24)


10. Run script
```
python3  nsm-allvis/allvis_api_v0_script_v01.py
```
