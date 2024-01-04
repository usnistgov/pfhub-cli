from zenodo_client import Creator, Metadata, ensure_zenodo
from pprint import pprint
import uuid

def upload_to_zenodo(path):
    data = Metadata(
        title='Wheeler test',
        upload_type='dataset',
        description='test description',
        creators=[
            Creator(
                name='Daniel Wheeler',
                affiliation='Harvard Medical School',
                orcid='0000-0003-4423-4370',
            ),
        ],
    )

    res = ensure_zenodo(
        key=str(uuid.uuid4()), #.strip('-'),  # this is a unique key you pick that will be used to store
                      # the numeric deposition ID on your local system's cache
        data=data,
        paths=[
            path,
        ],
        sandbox=True,  # remove this when you're ready to upload to real Zenodo
    )

    return res.json()['links']['html']
