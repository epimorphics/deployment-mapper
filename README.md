# GH Action for declaratively mapping deployments

This action supports a continuous deployment approach in which the mapping from a pushed commit or tag to a deployment environment is specified in a declarative mapping file, expressed in yaml.

It is designed for use with AWS ECR docker image repositories and for a pattern where there is a separate image repository for each target environment. The job of this action is determine if the pushed commit or tag should trigger an image build and if so which image name and respository to build.

## Inputs

| name | description | default |
|---|---|---|
| `ref` | the git reg to map | |
| `deploymentFile` | name of the file specifying the deployment pattern to use | `deployment.yaml` |

## Outputs

| name | description |
|---|---|
| `image` | name of environment-specific image to build |
| `accountid` | id of aws account to deploy to |
| `region` | description: aws region to deploy to |

## Example usage

todo

## Deployment specication file

A deployment pattern is specified in a yaml file with a structure like:

```yaml
image:        
  organisation: epimorphics
  name:         deployment-mapping-tester
aws:
  accountid:  "293385631482"
  region:     eu-west-1
deployments:
  - production:
      tag: "{ver}"
  - staging:
      tag: "{ver}-rc.*"
      branch: staging
  - dev:
      branch: "master|main"
```

The `deployments` section is a list of environment patterns. Each of which has the environment name as a key and a `tag` or `branch` regular expression. If the pushed git reference is a tag it will be matched against the tag patterns, otherwise it will be matched against the branch patterns. The patterns can include `{ver}` which is mapped to a loose regular expression for sequences of digits and `.` characters as used in normal semver tagging.

The first environment which matches the ref is chosen, if no envionment patterns match then no outputs are bound.

The generated `image` name follows the pattern:

    {organisation}/{env}/{name}

For example: `epimorphics/production/myapp`

The `image.organisation` value is optional and defaults to `epimorphics` but can be finer grain, e.g. `epimorphics/ea-eks-cluster`.

The `aws` information is extracted from the specification by this action just to avoid later workflow steps having to do a repeat parse. The `aws.region` is optional and defaults to `eu-west-1`.

