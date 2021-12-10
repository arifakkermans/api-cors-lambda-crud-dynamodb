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
    const createBookIntegration = new LambdaIntegration(createBookLambda);
    const listBookIntegration = new LambdaIntegration(listBooksLambda);
    const updateBookIntegration = new LambdaIntegration(updateBookLambda);
    const deleteBookIntegration = new LambdaIntegration(deleteBookLambda);

    // Create an API Gateway resource for each of the CRUD operations
    const api = new RestApi(this, 'bookApi', {
      restApiName: 'Book API Service'
    });

    const items = api.root.addResource('books');
    items.addMethod('GET', listBookIntegration);
    items.addMethod('POST', createBookIntegration);
    addCorsOptions(items);

    const singleItem = items.addResource('{id}');
    singleItem.addMethod('GET', getBookIntegration);
    singleItem.addMethod('PATCH', updateBookIntegration);
    singleItem.addMethod('DELETE', deleteBookIntegration);
    addCorsOptions(singleItem);

  }
}
 // Add CORS to restrict cross-origin HTTP requests
export function addCorsOptions(apiResource: IResource) {
  apiResource.addMethod('OPTIONS', new MockIntegration({
    integrationResponses: [{
      statusCode: '200',
      responseParameters: {
        'method.response.header.Access-Control-Allow-Headers': "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token,X-Amz-User-Agent'",
        'method.response.header.Access-Control-Allow-Origin': "'*'",
        'method.response.header.Access-Control-Allow-Credentials': "'false'",
        'method.response.header.Access-Control-Allow-Methods': "'OPTIONS,GET,PUT,POST,DELETE'",
      },
    }],
    passthroughBehavior: PassthroughBehavior.NEVER,
    requestTemplates: {
      "application/json": "{\"statusCode\": 200}"
    },
  }), {
    methodResponses: [{
      statusCode: '200',
      responseParameters: {
        'method.response.header.Access-Control-Allow-Headers': true,
        'method.response.header.Access-Control-Allow-Methods': true,
        'method.response.header.Access-Control-Allow-Credentials': true,
        'method.response.header.Access-Control-Allow-Origin': true,
      },
    }]
  })
}