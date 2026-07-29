# Stage 1 verification

This directory contains the public, versioned verification suite for raw data
ingestion. It tests the learner's project without containing a reference
implementation.

The reusable workflow checks out this suite at an immutable commit SHA. Changes
to tests in a learner repository therefore cannot change the evidence produced
by the controlled workflow.
