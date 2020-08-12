import yaml, re, sys

DEFAULT_REGION = "eu-west-1"
DEFAULT_ORGANISATION = "epimorphics"

def main():
    if len(sys.argv) != 3:
        report_and_exit("Usage: deployment-mapper ref-to-deploy deployment-spec-file.yaml")
    ref = sys.argv[1]
    deployment_spec = sys.argv[2]
    try:
        with open(deployment_spec) as file:
            spec = yaml.load(file, Loader=yaml.FullLoader)
            organisation, name, accountid, region = validate(spec)
            env = find_deployment(spec, ref)
            if env:
                print(f'::set-output name=image::{organisation}/{env}/{name}')
                print(f'::set-output name=accountid::{accountid}')
                print(f'::set-output name=region::{region}')
    except FileNotFoundError:
        report_and_exit( f'Could not file deployment specification {deployment_spec}' )

def find_deployment(spec, ref):
    target = re.sub('refs/(tags|heads)/','', ref)
    for deployment in spec.get('deployments'):
        for k, p in deployment.items():
            pattern = p.get('tag') if ref.startswith("refs/tags/") else p.get('branch')
            if (pattern):
                pattern = pattern.replace("{ver}", "[0-9\\.]+")
                if re.fullmatch(pattern, target):
                    return k
    return None

def legal_env_spec(es):
    if isinstance(es, dict):
        for env, spec in es.items():
            if spec.get('tag') or spec.get('branch'):
                return True
            else:
                report_and_exit(f'Problem with deployment spec: {env} does not specific tag or branch pattern')
    return False

def validate(spec):
    image = spec.get('image')
    if not isinstance(image, dict):
        report_and_exit("Problem with deployment spec: couldn't find image spec")
    organisation = image.get('organisation') or DEFAULT_ORGANISATION
    name = image.get('name') or report_and_exit("Problem with deployment spec: couldn't find image.name")
    aws = spec.get('aws')
    if not isinstance(aws, dict):
        report_and_exit("Problem with deployment spec: couldn't find aws spec")
    accountid = aws.get('accountid') or report_and_exit("Problem with deployment spec: couldn't find aws.accountid")
    region = aws.get('region') or DEFAULT_REGION
    deployments = spec.get('deployments')
    if not deployments:
        report_and_exit("Problem with deployment spec: couldn't find deployments")
    if not isinstance(deployments, list):
        report_and_exit("Problem with deployment spec: deployments should be an ordered list of environments")
    if not all( legal_env_spec(es) for es in deployments):
        report_and_exit("Problem with deployment spec: each environment spec should have a tag or branch specified")
    return organisation, name, accountid, region

def report_and_exit(message):
    print(message, file=sys.stderr)
    sys.exit(1)

if __name__ == "__main__":
    main()
    