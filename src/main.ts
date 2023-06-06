import * as path from 'path';
import { App, Stack, StackProps, CustomResource, Duration } from 'aws-cdk-lib';
import * as acm from 'aws-cdk-lib/aws-certificatemanager';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as cr from 'aws-cdk-lib/custom-resources';
import { Construct } from 'constructs';

export interface R53StackProps extends StackProps {
  crossAccountR53RoleArn: string;
  crossAccountHostedZoneId: string;
  loadBalancerDnsName: string;
}

export class CrossAccountR53 extends Stack {
  constructor(scope: Construct, id: string, props: R53StackProps) {
    super(scope, id, props);

    const lambdaFn = new lambda.Function(this, 'CustomResourceHandler', {
      runtime: lambda.Runtime.PYTHON_3_10,
      handler: 'index.lambda_handler',
      code: lambda.Code.fromAsset(path.join(__dirname, './lambda')),
      timeout: Duration.seconds(120),
      initialPolicy: [
        new iam.PolicyStatement({
          actions: [
            'acm:DescribeCertificate',
            'acm:ListCertificates',
            'acm:DeleteCertificate',
            'acm:RequestCertificate',
          ],
          resources: ['*'],
        }),
        new iam.PolicyStatement({
          actions: ['sts:AssumeRole'],
          resources: [props.crossAccountR53RoleArn],
        }),
      ],
    });

    const customResource = new cr.Provider(this, 'CustomResourceProvider', {
      onEventHandler: lambdaFn,
    });

    const certificateArn = new CustomResource(this, 'CrossAccountCert', {
      serviceToken: customResource.serviceToken,
      properties: {
        TargetAccountRole: props.crossAccountR53RoleArn,
        HostedZoneId: props.crossAccountHostedZoneId,
        RecordName: 'placeholder',
        RecordType: 'CNAME',
        RecordValue: 'placeholder',
        RecordTTL: 300,
        AppName: 'test',
        Certificate: 'true',
        DomainName: 'example.com',
        CertName: 'test.example.com',
      },
    });

    const certificate = acm.Certificate.fromCertificateArn(this, 'CrossAccountCertCDK', certificateArn.getAttString('CertificateArn'));

    certificate.node.addDependency(certificateArn);

    new CustomResource(this, 'CrossAccountAlias', {
      serviceToken: customResource.serviceToken,
      properties: {
        TargetAccountRole: props.crossAccountR53RoleArn,
        HostedZoneId: props.crossAccountHostedZoneId,
        RecordName: 'test.example.com',
        RecordType: 'A',
        RecordValue: props.loadBalancerDnsName,
        RecordTTL: 300,
        AppName: 'test',
        Certificate: 'true',
        DomainName: 'example.com',
        CertName: 'test.example.com',
      },
    });
  }
}


const devEnv = {
  account: process.env.CDK_DEFAULT_ACCOUNT,
  region: process.env.CDK_DEFAULT_REGION,
};

const app = new App();

new CrossAccountR53(app, 'cross-account-route53-records', {
  env: devEnv,
  crossAccountR53RoleArn: 'arn:aws:iam::123456789012:role/CrossAccountRecordRole',
  crossAccountHostedZoneId: 'Z1234567890',
  loadBalancerDnsName: 'test-1234567890.us-east-2.elb.amazonaws.com',
});

app.synth();