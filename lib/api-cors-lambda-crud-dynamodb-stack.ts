import {
  aws_lambda as Lambda,
  aws_dynamodb as Dynamodb,
  Stack, StackProps, RemovalPolicy
} from 'aws-cdk-lib';
import { IResource, LambdaIntegration, MockIntegration, PassthroughBehavior, RestApi } from 'aws-cdk-lib/aws-apigateway';
import { Construct } from 'constructs';
import { join } from 'path'

export class ApiCorsLambdaCrudDynamodbStack extends Stack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    // The code that defines your stack goes here

    // example resource
    // const queue = new sqs.Queue(this, 'ApiCorsLambdaCrudDynamodbQueue', {
    //   visibilityTimeout: cdk.Duration.seconds(300)
    // });
    const dynamoTable = new Dynamodb.Table(this, 'Books', {
      tableName: 'BooksTable',
      partitionKey: {
        name: 'isbn',
        type: Dynamodb.AttributeType.STRING
      },
      readCapacity: 1,
      writeCapacity: 1,
      removalPolicy: RemovalPolicy.DESTROY, // NOT recommended for production code
    });

    const baseLambdaProps = {
      environment: {
        table: DYNAMO_TABLE.tableName
      },
      runtime: Lambda.Runtime.PYTHON_3_8
    };
  }
}
