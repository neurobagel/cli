from pathlib import Path
from typing import Iterable

import pydantic
import typer
from pydantic import ValidationError

from bagel import models
from bagel.mappings import ALL_NAMESPACES, NB

from . import file_utils as futil


def generate_context():
    # Direct copy of the dandi-schema context generation function
    # https://github.com/dandi/dandi-schema/blob/c616d87eaae8869770df0cb5405c24afdb9db096/dandischema/metadata.py
    field_preamble = {
        namespace.pf: namespace.url for namespace in ALL_NAMESPACES
    }
    fields = {}
    for val in dir(models):
        klass = getattr(models, val)
        if not isinstance(klass, pydantic.main.ModelMetaclass):
            continue
        fields[klass.__name__] = f"{NB.pf}:{klass.__name__}"
        for name, field in klass.__fields__.items():
            if name == "schemaKey":
                fields[name] = "@type"
            elif name == "identifier":
                fields[name] = "@id"
            elif name not in fields:
                fields[name] = {"@id": f"{NB.pf}:{name}"}

    field_preamble.update(**fields)

    return {"@context": field_preamble}


def add_context_to_graph_dataset(dataset: models.Dataset) -> dict:
    """Add the Neurobagel context to a graph-ready dataset to form a JSONLD dictionary."""
    context = generate_context()
    # We can't just exclude_unset here because the identifier and schemaKey
    # for each instance are created as default values and so technically are never set
    # TODO: we should revisit this because there may be reasons to have None be meaningful in the future
    return {**context, **dataset.dict(exclude_none=True)}


def get_subs_missing_from_pheno_data(
    subjects: Iterable, pheno_subjects: Iterable
) -> list:
    """Check a list of subject IDs and return any not found in the provided phenotypic subject list."""
    return list(set(subjects).difference(pheno_subjects))


def confirm_subs_match_pheno_data(
    subjects: Iterable, subject_source_for_err: str, pheno_subjects: Iterable
):
    """
    Return an error if not all subjects in the subject list are found in the provided phenotypic subject list.
    """
    missing_subs = get_subs_missing_from_pheno_data(
        subjects=subjects,
        pheno_subjects=pheno_subjects,
    )

    if len(missing_subs) > 0:
        raise LookupError(
            f"The specified {subject_source_for_err} contains subject IDs not found in "
            "the provided json-ld file:\n"
            f"{missing_subs}\n"
            "Subject IDs are case sensitive. "
            f"Please check that the {subject_source_for_err} corresponds to the dataset in the provided .jsonld."
        )


def extract_and_validate_jsonld_dataset(file_path: Path) -> models.Dataset:
    """
    Strip the context from a user-provided JSONLD and validate the remaining contents
    against the data model for a Neurobagel dataset.
    """
    jsonld = futil.load_json(file_path)
    jsonld.pop("@context")
    try:
        jsonld_dataset = models.Dataset.parse_obj(jsonld)
    except ValidationError as err:
        typer.echo(
            typer.style(
                (
                    f"Error: {file_path} is not a valid Neurobagel JSONLD dataset. "
                    "Please ensure to provide a valid JSONLD file generated by Neurobagel CLI commands.\n"
                    f"Validation errors: {str(err)}"
                ),
                fg=typer.colors.RED,
            ),
            err=True,
        )
        raise typer.Exit(code=1) from err

    return jsonld_dataset


def get_subject_instances(dataset: models.Dataset) -> dict:
    """
    Return a dictionary of subjects for a given Neurobagel dataset from JSONLD data,
    where keys are subject labels and values are the subject objects.
    """
    return {
        subject.hasLabel: subject for subject in getattr(dataset, "hasSamples")
    }


def get_imaging_session_instances(
    jsonld_subject: models.Subject,
) -> dict:
    """
    Return a dictionary of imaging sessions for a given subject from JSONLD data,
    where the keys are the session labels and values are the session objects.
    """
    jsonld_sub_sessions_dict = {}
    for jsonld_sub_ses in getattr(jsonld_subject, "hasSession"):
        if jsonld_sub_ses.schemaKey == "ImagingSession":
            jsonld_sub_sessions_dict[jsonld_sub_ses.hasLabel] = jsonld_sub_ses

    return jsonld_sub_sessions_dict
