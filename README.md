# cross-account-route53-records

This is repo is intended to be widely reused as a template for cross account certificate validation & Alias A record creation.

Read more about this repo and how you can best use it here: https://jeremyritchie.com/posts/11/

## Support

| Record type | Supported | Comments                                                                                                                                              |
|-------------|-----------|-------------------------------------------------------------------------------------------------------------------------------------------------------|
| A           | ✅         |                                                                                                                                                       |
| Alias       | ✅         |                                                                                                                                                       |
| CNAME       | ✅         |                                                                                                                                                       |
| TXT         | ❔         | Untested - High likely hood of support without any changes.                                                                                           |
| NS          | ❌         | AWS already supports this - read more here: https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_route53.CrossAccountZoneDelegationRecord.html |

## Prerequisites

* Python3
* AWS CDK Toolkit (CLI)
  ```sh
  npm i -g aws-cdk
  ```
* Typescript
  ```sh
  npm i typescript
  ```
* Projen
  ```sh
  npm i projen
  ```


## How to use

The code here should be extracted and used within your own project.
While it does compile alone, it's not intended to drop into an existing project.

## Useful commands

 * `cdk ls`          list all stacks in the app
 * `cdk synth`       emits the synthesized CloudFormation template
 * `cdk deploy`      deploy this stack to your default AWS account/region
 * `cdk diff`        compare deployed stack with current state
 * `cdk docs`        open CDK documentation
 * `projen build`    build changes from projen

Enjoy!
