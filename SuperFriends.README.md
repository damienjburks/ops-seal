# Links for Super Friends Presentation Tomorrow

- https://www.chainguard.dev/solutions/golden-images
- https://images.chainguard.dev/
- https://www.chainguard.dev/containers

## Commands

### Building Images with Multiple Files

- docker build -t insecure-lambda -f Dockerfile.lambda.insecure .

### Scanning using Trivy

- trivy image insecure-python-img --format template --template "@contrib/html.tpl" -o results.html