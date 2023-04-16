
# Mesh Support Report Generator

This is a simple python application to log in to various mesh device databases 
(currently UISP, UniFi, and uFiber), collect information on which devices are in an unhealthy
state, print a report, and optionally upload it to slack:

```sh
> mesh-support-report
**Outage Report - Tuesday, March 21, 2023 @ 18:17**

UISP - Currently In Outage (new last 7 days)
...


UNIFI - Currently In Outage (new last 7 days)
-- None --


UFIBER - Currently In Outage
...


UFIBER - Poor Signal (< -30 dBm)
...


UFIBER - Poor Experience (< 100%)
...


Posting to slack...
Posted to https://app.slack.com/client/xxxx/yyyy
```


## Usage

Pre-requisites: `python3` available via the shell

Setup by cloning, creating a virtual env, and installing the application
```sh
git clone https://github.com/nycmeshnet/support-report-generator
cd support-report-generator
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

Next, create a `.env` file and fill out the variables
```sh
cp .env_example .env
nano .env
```

then invoke the tool with the CLI command:
```sh
mesh-support-report
```

## Running the unit tests

Follow the instructions under "Usage" above, to clone a local copy of this application and activate
the virtual environment. Then installing the test dependencies with:
```sh
pip install -e ".[test]"
```

Finally, invoke the test suite using pytest:
```
pytest test/
```


## Building for AWS Lambda

This package is set up to be easily run via [AWS Lambda](https://aws.amazon.com/lambda/). Create
a ZIP build using the `bin/build.sh` script
```sh
source .venv/bin/activate
bin/build.sh
ls build/Lambda.zip # Created by the build script
```

The `build/Lambda.zip` should be immediately ready to upload to AWS Lambda. Set the handler to 
`mesh_support_report_generator.lambda_handler.lambda_handler`. Note that the AWS Lambda function will need
to run in an AWS VPC that has mesh IP-space access in order to function properly. The Lambda 
See https://github.com/Andrew-Dickinson/nyc-mesh-aws-vpn-cdk for help with setting that up.

## License

Distributed under the MIT License. See `LICENSE.txt` for more information.

## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request


## Acknowledgments
 * [Best-README-Template](https://github.com/othneildrew/Best-README-Template/)
