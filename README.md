# Data by Doing workflows

Public, versioned verification workflows for Data by Doing learner projects.
This repository contains test automation and public behavioral tests. It never
contains challenge solutions, application code, credentials, or learner data.

## Stage 1

`.github/workflows/stage-1.yml` checks out the learner repository and the
controlled stage 1 tests separately. Both the reusable workflow and its test
suite are referenced by immutable, full commit SHAs.

The workflow:

- requests only `contents: read`;
- uses no learner secrets;
- does not persist checkout credentials;
- pins every third-party action by full commit SHA; and
- runs pytest and dbt inside the learner project's locked `uv` environment.

Callers must reference a reviewed commit SHA. Branches and tags such as `main`
or `v1` are not accepted evidence.

## Publishing an update

1. Publish and review test changes in their own signed commit.
2. Update the reusable workflow to pin that exact test commit.
3. Validate the starter failure path and the private reference success path.
4. Publish the reusable workflow in a signed commit.
5. Update callers to pin the new reusable workflow SHA.

Keeping the test and workflow revisions separate avoids circular pins and makes
the complete verification chain auditable.
Versioned verification workflows for Data by Doing learner projects
