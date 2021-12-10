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
  
    // Define Lambda initial configuration
    const baseLambdaProps = {
      environment: {
        table: dynamoTable.tableName
      },
      runtime: Lambda.Runtime.PYTHON_3_8
    };

    // Create a Lambda function for each of the CRUD operations
    const getBookLambda = new Lambda.Function(this, 'getOneBookFunction', {
      code: Lambda.Code.fromAsset(join(__dirname, '../src')),
      handler: 'get_book.lambda_handler',
      ...baseLambdaProps,
    });
    const listBooksLambda = new Lambda.Function(this, 'getAllBookssFunction', {
      code: Lambda.Code.fromAsset(join(__dirname, '../src')),
      handler: 'list_books.lambda_handler',
      ...baseLambdaProps,
    });
    const createBookLambda = new Lambda.Function(this, 'createBookFunction', {
      code: Lambda.Code.fromAsset(join(__dirname, '../src')),
      handler: 'create_book.lambda_handler',
      ...baseLambdaProps,
    });
    const updateBookLambda = new Lambda.Function(this, 'updateBookFunction', {
      code: Lambda.Code.fromAsset(join(__dirname, '../src')),
      handler: 'update_books.lambda_handler',
      ...baseLambdaProps,
    });
    const deleteBookLambda = new Lambda.Function(this, 'deleteBookFunction', {
      code: Lambda.Code.fromAsset(join(__dirname, '../src')),
      handler: 'delete_book.lambda_handler',
      ...baseLambdaProps,
    });

    // Grant the Lambda function read and write access to the DynamoDB table
    // TODO: Use least privilege principle
    dynamoTable.grantReadWriteData(getBookLambda);
    dynamoTable.grantReadWriteData(listBooksLambda);
    dynamoTable.grantReadWriteData(createBookLambda);
    dynamoTable.grantReadWriteData(updateBookLambda);
    dynamoTable.grantReadWriteData(deleteBookLambda);

    // Integrate the Lambda functions with the API Gateway resource
    const getBookIntegration = new LambdaIntegration(getBookLambda);
    const createBookIntegration = new LambdaIntegration(listBooksLambda);
    const listBookIntegration = new LambdaIntegration(createBookLambda);
    const updateBookIntegration = new LambdaIntegration(updateBookLambda);
    const deleteBookIntegration = new LambdaIntegration(deleteBookLambda);

  }
}
