import boto3


def create_table():
  dynamodb = boto3.resource('dynamodb')

  # NOTE: To reduce costs, enable auto scaling for provisioned throughput via AWS console

  table = dynamodb.create_table(
      TableName='uav_wvi',
      KeySchema=[
          {
              'AttributeName': 'data_type',
              'KeyType': 'HASH'  # Partition key
          },
          {
              'AttributeName': 'timestamp',
              'KeyType': 'RANGE'  # Sort key
          }
      ],
      AttributeDefinitions=[
          {
              'AttributeName': 'data_type',
              'AttributeType': 'S'
          },
          {
              'AttributeName': 'timestamp',
              'AttributeType': 'N'
          },

      ],
      ProvisionedThroughput={
          'ReadCapacityUnits': 10,
          'WriteCapacityUnits': 10
      }
  )
  return table


if __name__ == '__main__':
    table = create_table()
    print("Table status:", table.table_status)