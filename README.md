# cross-account-route53-records

This is repo is intended to be widely reused as a template for cross account certificate validation & Alias A record creation.


Read more about this repo and how you can best use it here: https://jeremyritchie.com/posts/11/

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
