# GH Action for declaratively mapping deployments

This action supports a continuous deployment approach in which the mapping from a pushed commit or tag to a deployment environment is specified in a declarative mapping file, expressed in yaml.

It is designed for use with AWS ECR docker image repositories and for a pattern where there is a separate image repository for each target environment. The job of this action is determine if the pushed commit or tag should trigger an image build and if so which image name and repository to build and push to.

## Inputs

| name | description | default |
|---|---|---|
| `ref` | the git ref which triggered the action | |
| `deploymentFile` | name of the file specifying the deployment pattern to use | `deployment.yaml` |

## Outputs

| name | description |
|---|---|
| `image` | name of environment-specific image to build |
| `region` | description: aws region to deploy to |

If the push should not trigger a build then the action will still succeed but `image` will not be bound.

## Example usage

```yaml
name: Mapped deployment
on:
  push: {}

jobs:
  mapped-deploy:
    name: mapped-deployment
    runs-on: ubuntu-18.04
    steps:
    - uses: actions/checkout@v2
    - name: "Check for mapped deployment"
      id: mapper
      uses: epimorphics/deployment-mapper@1.1
      with:
        ref: "${{github.ref}}"

    - name: "Build and push image"
      if: steps.mapper.outputs.image != ''
      uses: epimorphics/mapped-deployment-action@1.1
      with:
        image: "${{ steps.mapper.outputs.image }}"
        region: "${{ steps.mapper.outputs.region }}"
        access_key_id: ${{ secrets.BUILD_EPI_EXPT_AWS_ACCESS_KEY_ID }}
        secret_access_key: ${{ secrets.BUILD_EPI_EXPT_AWS_SECRET_ACCESS_KEY }}

```

## Deployment specification file

A deployment pattern is specified in a yaml file with a structure like:

```yaml
name:  epimorphics/myapp
aws:
  region:  "eu-west-1"   # Optional
deployments:
  - production:
      tag: "{ver}"
  - staging:
      tag: "{ver}-rc.*"
      branch: staging
  - dev:
      branch: "master|main"
```

The `deployments` section is a list of environment patterns. Each of which has the environment name as a key and a `tag` or `branch` regular expression (or both). If the pushed git reference is a tag it will be matched against the tag patterns, otherwise it will be matched against the branch patterns. The patterns can include `{ver}` which is mapped to a loose regular expression for sequences of digits and `.` characters as used in semver tagging.

The first environment which matches the ref is chosen, if no environment patterns match then no outputs are bound.

The generated `image` name follows the pattern

    {name}/{env}

For example: `epimorphics/myapp/production`

The `aws` information is extracted from the specification by this action just to avoid later workflow steps having to do a repeat parse. The `aws.region` is optional and defaults to `eu-west-1`.
