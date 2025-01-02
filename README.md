# Transfer

Transffering data from the old MySQL and PHP website to the new MongoDB and FastAPI

## Installation

Instructions on how to install and set up the project.

```bash
# Clone the repository
git clone https://github.com/alpha-phi-omega-ez/transfer.git

# Navigate to the project directory
cd transfer

# Install dependencies
pip3 install -r requirements.txt
```

## Usage

To download data first created the json config file `dbs.json` in this format:

```json
[
  {
    "user": "user",
    "password": "password",
    "host": "host",
    "database": "database"
  },
  {
    "user": "user",
    "password": "password",
    "host": "host",
    "database": "database"
  }
]
```

Then run `pull.py` to download the data

```bash
python3 pull.py
```

To push the data to MongoDB run

```bash
python3 push.py true
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.