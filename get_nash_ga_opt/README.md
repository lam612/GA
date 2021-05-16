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
awslocal dynamodb create-table --cli-input-json file://common_resources/localstack/dynamoDB.json
aws --endpoint-url=http://localhost:4566 dynamodb create-table --cli-input-json file://common_resources/localstack/dynamoDB.json

aws --profile <your-aws-profile-name> dynamodb create-table --cli-input-json file://product_demand/model/dynamoDB.json
aws --profile Law dynamodb create-table --cli-input-json file://product_demand/model/dynamoDB.json
```

Build S3 in local

```
awslocal s3api create-bucket --bucket aws-sam-cli-gr
aws --endpoint-url=http://localhost:4566 s3api create-bucket --bucket aws-sam-cli-gr
```

View Localstack S3 file

```bash
aws --endpoint-url=http://localhost:4566 s3api list-objects --bucket aws-sam-cli-gr
```

http://localhost:4566/<backet-name>/<s3-file-path>

```browser web
http://localhost:4566/aws-sam-cli-gr/data/demand.csv
```

aws --endpoint-url=http://localhost:4566 s3 cp <file_path> s3://aws-sam-cli-gr/<file-path>
```Upload file
# Upload csv data
aws --endpoint-url=http://localhost:4566 s3 cp ./data/demand.csv s3://aws-sam-cli-gr/data/demand.csv
aws --profile Law s3 cp ./data/demand.csv s3://aws-sam-cli-gr/data/demand.csv

# Upload sav model
aws --endpoint-url=http://localhost:4566 s3 cp ./model/demand.sav s3://aws-sam-cli-gr/model/demand.sav
aws --profile Law  s3 cp ./model/demand.sav s3://aws-sam-cli-gr/model/demand.sav
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
sam local start-api -t template.yaml --docker-network host --env-vars env.json
```

## Fetch, tail, and filter Lambda function logs

```bash
sam logs -n VideoDLFunction --stack-name vidClip --tail
```

## Invoke lambda

Run functions locally and invoke them with the `sam local invoke` command.

check_dl_job_function

```bash
sam local invoke --docker-network host --env-vars env.json -e lambda/events/event.case_<test case>.json
```

```
# video_dl_function
sam local start-lambda --docker-network host --debug --env-vars env.json

sam local invoke --docker-network host --env-vars env.json -e lambda/events/event.case_1.json
```

## Deploy API
```bash
aws --profile Law s3api create-bucket --bucket aws-sam-cli-gr --region us-east-1

sam package --region us-east-1 --profile Law --debug --s3-bucket aws-sam-cli-gr --output-template-file packaged.yaml

sam deploy -g --profile Law --capabilities CAPABILITY_AUTO_EXPAND CAPABILITY_IAM --s3-bucket --s3-bucket aws-sam-cli-gr ParameterKey=Stage,ParameterValue=prd --debug --confirm-changeset --stack-name prd-predict-demand
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
aws cloudformation delete-stack --stack-name vidClip
```

]
