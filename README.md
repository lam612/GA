# [Refactor] Build
### Change The Following Variable in all template.\*.yaml and samconfig.toml

`S3Bucket`

# Start [Localstack]('https://github.com/localstack/localstack') with Docker

```bash
docker-compose up
```

# Build services in local stack

```bash
aws --endpoint-url=http://localhost:4566 <servise-name> create-<service-resource> --cli-input-json file://<service-json-path>
```

With awslocal CLI

```bash
awslocal <servise-name> create-<service-resource> --cli-input-json file://<service-json-path>
```

Build DynamoDB in local

```bash
awslocal dynamodb create-table --cli-input-json file://dynamoDB.json
aws --endpoint-url=http://localhost:4566 dynamodb create-table --cli-input-json file://dynamoDB.json
```

Build DynamoDB in AWS
aws --profile <your-aws-profile-name> dynamodb create-table --cli-input-json file://product_demand/model/dynamoDB.json
aws --profile Law dynamodb create-table --cli-input-json file://dynamoDB.json
```

## To build application:

```bash
sam build --use-container
sam deploy --guided
```

## Use the SAM CLI to build and test locally

Build your application with the `sam build --use-container` command.

```bash
sam build --use-container
```

```bash local
sam build --use-container -t template.yaml
```

The SAM CLI can also emulate your application's API. Use the `sam local start-api` to run the API locally on port 3000.

```bash
sam local start-api
curl http://localhost:3000/
```

To map SAM with localstack

```bash
sam local start-api -t template.yaml --env-vars env.json
```

## Fetch, tail, and filter Lambda function logs

```bash
sam logs -n VMINashGASt --stack-name vmiNashGa --tail
```

## Invoke lambda

Run functions locally and invoke them with the `sam local invoke` command.

get_nash_ga_opt_function

```bash
sam local invoke --env-vars env.json -e lambda/events/event.case_<test case>.json
```

## Deploy API
```bash
aws --profile <your-profile-name> s3api create-bucket --bucket aws-vmi-nash-ga --region us-east-1

sam package --region us-east-1 --profile <your-profile-name> --debug --s3-bucket aws-vmi-nash-ga --output-template-file packaged.yaml

sam deploy -g --profile <your-profile-name> --capabilities CAPABILITY_AUTO_EXPAND CAPABILITY_IAM --s3-bucket aws-vmi-nash-ga ParameterKey=Stage,ParameterValue=prd,ParameterKey=ModelPath,ParameterValue=src/data/demand.json,ParameterKey=DataPath,ParameterValue=/tmp/data.json --debug --confirm-changeset --stack-name vmi-opt
```

## Unit tests

Tests are defined in the `tests` folder in this project. Use PIP to install the [pytest](https://docs.pytest.org/en/latest/) and run unit tests.

```bash
pip install pytest pytest-mock --user
python -m pytest tests/ -v
```

Create Test report

```bash
# cd to lambda folder of API
cd lambda

python -m pytest --cov-report html --cov=src/ tests/
```

## Cleanup

To delete the sample application that you created, use the AWS CLI. Assuming you used your project name for the stack name, you can run the following:

```bash
aws cloudformation delete-stack --stack-name vmiNashGa
```
