import hashlib
import json
import uuid
from datetime import datetime
from os import path

from _version import __version__

"""
This script holds the objects used for exporting information regarding SQLite carving process to CASE format. 
Information about the CASE Cyber Ontology can be found at: https://caseontology.org/
"""


def hash_file(file_path, hash_algo=hashlib.sha256()):
    """
    Generates a hash of a file by chunking it and utilizing the Python hashlib library.
    """
    # Ensure the file path exists
    if not path.exists(file_path):
        raise IOError("The file path {} is not valid, the file does not exist".format(file_path))

    with open(file_path, 'rb') as f:
        while True:
            # Reading is buffered, so we can read smaller chunks.
            chunk = f.read(hash_algo.block_size)
            if not chunk:
                break
            hash_algo.update(chunk)
    return hash_algo.hexdigest()


def guid_list_to_objects(guids):
    """
    Converts a list of string GUIDs to the object notation with an ID prefix
    """
    if guids is None:
        return []
    else:
        return list(map(lambda g: {"@id": g}, guids))


class CaseExporter(object):
    # Define the formatted logger that is provided by the main.py execution path
    logger = None

    result_guids = []

    # Defines the initial structure for the CASE export. This will be supplemented with various methods that get called
    # from the main.py execution path.
    case = {
        '@context': {
            "@vocab": "http://example.org/ontology/local#",
            "case-investigation": "https://ontology.caseontology.org/case/investigation/",
            "drafting": "http://example.org/ontology/drafting#",
            "kb": "http://example.org/kb/",
            "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
            "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
            "uco-action": "https://unifiedcyberontology.org/ontology/uco/action#",
            "uco-core": "https://unifiedcyberontology.org/ontology/uco/core#",
            "uco-identity": "https://unifiedcyberontology.org/ontology/uco/identity#",
            "uco-location": "https://unifiedcyberontology.org/ontology/uco/location#",
            "uco-observable": "https://unifiedcyberontology.org/ontology/uco/observable#",
            "uco-tool": "https://unifiedcyberontology.org/ontology/uco/tool#",
            "uco-types": "https://unifiedcyberontology.org/ontology/uco/types#",
            "uco-vocabulary": "https://unifiedcyberontology.org/ontology/uco/vocabulary#",
            "xsd": "http://www.w3.org/2001/XMLSchema#"
        },
        '@graph': []
    }
    start_datetime = None
    end_datetime = None

    def __init__(self, logger):
        self.logger = logger

    def register_options(self, options):
        """
        Adds the command line options provided as the configuration values provided and outputting them in the schema
        defined in the uco-tool namespace.

        Ontology Source: https://github.com/ucoProject/UCO/blob/master/uco-tool/tool.ttl
        """
        configuration_options = []

        # Loop through the list of provided options and add each configuration option to the CASE output
        for option in vars(options):
            if getattr(options, option) is not None and len(str(getattr(options, option))) > 0:
                configuration_options.append({
                    "@type": "uco-tool:ConfigurationSettingType",
                    "uco-tool:itemName": option,
                    "uco-tool:itemValue": str(getattr(options, option))
                })

        # Build the configuration wrapper which includes the facet for the configuration
        configuration = [
            {
                "@type": "uco-tool:ToolConfigurationTypeFacet",
                "uco-tool:configurationSettings": configuration_options
            }
        ]

        # Add the configuration facet to the in progress CASE object
        self.case['@graph'][0]['uco-core:hasFacet'] = configuration

    def add_observable_file(self, filepath, filetype=None):
        """
        Adds the file specified in the provided filepath as an ObservableObject in the CASE export. This method handles
        calculation of filesize, extension, MD5 hash, SHA1 hash, and other metadata expected in the Observable TTL spec.

        Ontology source: https://github.com/ucoProject/UCO/blob/master/uco-observable/observable.ttl.
        """
        if path.exists(filepath) and path.isfile(filepath):
            # Get the full path we need for reference
            filepath = path.abspath(filepath)

            # Since the extension may take some additional logic checks, compute it out of the main JSON block
            extension = path.splitext(filepath)[1]
            if len(extension) > 0:
                extension = extension[1:]

            # Generate the UUID which will be returned as a reference
            if filetype is None:
                guid = ("kb:" + str(uuid.uuid4()))
            else:
                guid = ("kb:" + filetype + "-" + str(uuid.uuid4()))

            # Parse the file and get the attributes we need
            self.case['@graph'].append({
                "@id": guid,
                "@type": "uco-observable:ObservableObject",
                "uco-observable:hasChanged": False,
                "uco-core:hasFacet": [
                    {
                        "@type": "uco-observable:FileFacet",
                        "uco-observable:observableCreatedTime": {
                            "@type": "xsd:dateTime",
                            "@value": datetime.fromtimestamp(path.getctime(filepath)).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                        },
                        "uco-observable:modifiedTime": {
                            "@type": "xsd:dateTime",
                            "@value": datetime.fromtimestamp(path.getmtime(filepath)).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                        },
                        "uco-observable:accessedTime": {
                            "@type": "xsd:dateTime",
                            "@value": datetime.fromtimestamp(path.getatime(filepath)).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                        },
                        "uco-observable:extension": extension,
                        "uco-observable:fileName": path.basename(filepath),
                        "uco-observable:filePath": filepath,
                        "uco-observable:isDirectory": False,
                        "uco-observable:sizeInBytes": path.getsize(filepath)
                    },
                    {
                        "@type": "uco-observable:ContentDataFacet",
                        "uco-observable:hash": [
                            {
                                "@type": "uco-types:Hash",
                                "uco-types:hashMethod": {
                                    "@type": "uco-vocabulary:HashNameVocab",
                                    "@value": "MD5"
                                },
                                "uco-types:hashValue": {
                                    "@type": "xsd:hexBinary",
                                    "@value": hash_file(filepath, hashlib.md5())
                                }
                            },
                            {
                                "@type": "uco-types:Hash",
                                "uco-types:hashMethod": {
                                    "@type": "uco-vocabulary:HashNameVocab",
                                    "@value": "SHA1"
                                },
                                "uco-types:hashValue": {
                                    "@type": "xsd:hexBinary",
                                    "@value": hash_file(filepath, hashlib.sha1())
                                }
                            },
                            {
                                "@type": "uco-types:Hash",
                                "uco-types:hashMethod": {
                                    "@type": "uco-vocabulary:HashNameVocab",
                                    "@value": "SHA256"
                                },
                                "uco-types:hashValue": {
                                    "@type": "xsd:hexBinary",
                                    "@value": hash_file(filepath, hashlib.sha256())
                                }
                            },
                            {
                                "@type": "uco-types:Hash",
                                "uco-types:hashMethod": {
                                    "@type": "uco-vocabulary:HashNameVocab",
                                    "@value": "SHA512"
                                },
                                "uco-types:hashValue": {
                                    "@type": "xsd:hexBinary",
                                    "@value": hash_file(filepath, hashlib.sha512())
                                }
                            }
                        ]
                    }
                ]
            })

            return guid
        else:
            self.logger.critical('Attempting to add invalid filepath to CASE Observable export: {}'.format(filepath))

    def link_observable_relationship(self, source_guid, target_guid, relationship):
        self.case['@graph'].append({
            "@id": ("kb:export-artifact-relationship-" + str(uuid.uuid4())),
            "@type": "uco-observable:ObservableRelationship",
            "uco-core:source": {
                "@id": source_guid
            },
            "uco-core:target": {
                "@id": target_guid
            },
            "uco-core:kindOfRelationship": {
                "@type": "uco-vocabulary:ObservableObjectRelationshipVocab",
                "@value": relationship
            },
            "uco-core:isDirectional": True
        })

    def add_export_artifacts(self, export_paths=None):
        """
        Loops through the list of provided export artifact paths and adds them as observables and links them to the
        original observable artifact
        """
        if export_paths is None:
            export_paths = []

        for export_path in export_paths:
            # Add the observable object and get the GUID for linking
            export_guid = self.add_observable_file(export_path, "export-file")
            # Add the export result GUID to the list to be extracted
            self.result_guids.append(export_guid)

    def generate_provenance_record(self, description, guids):
        """
        Generates a provenance record for the tool and returns the GUID for the new object
        """

        # Ensure there is at least one GUID else don't add anything
        if len(guids) > 0:
            # Generate the UUID which will be returned as a reference
            guid = ("kb:provenance-record-" + str(uuid.uuid4()))

            record = {
                "@id": guid,
                "@type": "case-investigation:ProvenanceRecord",
                "uco-core:description": description,
                "uco-core:object": guid_list_to_objects(guids)
            }
            self.case['@graph'].append(record)
            return guid
        else:
            return None

    def generate_header(self):
        """
        Generates the header for the tool and returns the GUID for the ObservableRelationships
        """
        # Generate the UUID which will be returned as a reference
        guid = ("kb:sqlite-dissect-" + str(uuid.uuid4()))

        self.case['@graph'].append({
            "@id": guid,
            "@type": "uco-tool:Tool",
            "uco-core:name": "SQLite Dissect",
            "uco-tool:description": "A SQLite parser with recovery abilities over SQLite databases and their "
                                    "accompanying journal files. https://github.com/Defense-Cyber-Crime-Center/sqlite"
                                    "-dissect",
            "uco-tool:toolType": "Extraction",
            "uco-tool:creator": "Department of Defense Cyber Crime Center (DC3)",
            "uco-tool:version": __version__,
        })

        return guid

    def generate_investigation_action(self, source_guids, tool_guid):
        """
        Builds the investigative action object as defined in the CASE ontology. This also takes in the start and end
        datetimes from the analysis.

        Ontology source: https://github.com/casework/CASE/blob/master/ontology/investigation/investigation.ttl
        """
        source_provenance_guid = self.generate_provenance_record("SQLite source artifacts", source_guids)
        if source_provenance_guid is not None:
            source_guids.append(source_provenance_guid)
        result_provenance_guid = self.generate_provenance_record("SQLite Dissect output artifacts", self.result_guids)
        if result_provenance_guid is not None:
            self.result_guids.append(result_provenance_guid)

        action = {
            "@id": ("kb:investigative-action" + str(uuid.uuid4())),
            "@type": "case-investigation:InvestigativeAction",
            "uco-core:hasFacet": []
        }

        if self.start_datetime:
            action["uco-action:startTime"] = {
                "@type": "xsd:dateTime",
                "@value": self.start_datetime.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            }
        if self.end_datetime:
            action["uco-action:endTime"] = {
                "@type": "xsd:dateTime",
                "@value": self.end_datetime.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            }
        # Loop through and add the results to the ActionReferencesFacet
        action_facet = {
            "@type": "uco-action:ActionReferencesFacet",
            "uco-action:instrument": guid_list_to_objects([tool_guid]),
            "uco-action:object": guid_list_to_objects(source_guids),
            "uco-action:result": guid_list_to_objects(self.result_guids)
        }
        action["uco-core:hasFacet"].append(action_facet)
        self.case['@graph'].append(action)

    def export_case_file(self, export_path='output/case.json'):
        """
        Exports the built CASE object to the path specified in the export_path parameter.
        """

        # Write the CASE export to the filesystem
        with open(export_path, 'w') as f:
            json.dump(self.case, f, ensure_ascii=False, indent=4)
            self.logger.info('CASE formatted file has been exported to {}'.format(export_path))
