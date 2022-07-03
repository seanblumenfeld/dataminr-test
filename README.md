# Dataminr

The command line interface is provided via Makefile targets. To view all the available 
command line options run `make help` in the root of the repo.

## Build
To build the application run:
```
make build
```
The first time you run this a `.env` file will be generated for you. Feel free to change any values necessary in this 
file.

Once you have done this you will be able to run the application with: 
```
make up
```

You should then have a running api (inside docker) mapped to a localhost port 8001

## Test
We use the pytest test runner. Run the test suit with: 
```
make test
```

## Lint
We use a few example linters. Ideally a few more can be added. Run the linters using: 
```
make lint
```

## Usage
### API
#### POST weather alert
You can post a weather request to the api like this:
```
curl -X POST -H "Content-Type: application/json" -d '{"destination": "person@place.com", "lat": "1", "lon": 3, "alerts": {"min_temp": 50, "max_temp": 50}}' 0.0.0.0:8001/weather/
```

If your request triggers an alert then an alert line will be added to 
an `alerts.csv` file in the root of the repo.

## Deploy
To deploy the application in the foreground run 
```
make up
```
This will also print logging from all services to the blocking terminal.
Logs are not saved anywhere. A future action would be to integrate a logging service which would push application logs 
to a decoupled application such as Splunk or Grafana. 
