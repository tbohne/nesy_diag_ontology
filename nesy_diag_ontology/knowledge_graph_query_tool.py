#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author Tim Bohne

from typing import List, Tuple

from termcolor import colored

from nesy_diag_ontology.config import ONTOLOGY_PREFIX, FUSEKI_URL
from nesy_diag_ontology.connection_controller import ConnectionController


class KnowledgeGraphQueryTool:
    """
    Library of numerous predefined SPARQL queries and response processing for accessing useful information stored in
    the knowledge graph hosted on a 'Fuseki' server.
    """

    def __init__(self, kg_url: str = FUSEKI_URL, verbose: bool = True) -> None:
        """
        Initializes the KG query tool.

        :param kg_url: URL of the server hosting the knowledge graph
        :param verbose: whether the KG query tool should log its actions
        """
        self.ontology_prefix = ONTOLOGY_PREFIX
        self.fuseki_connection = ConnectionController(namespace=ONTOLOGY_PREFIX, fuseki_url=kg_url, verbose=verbose)
        self.verbose = verbose

    def complete_ontology_entry(self, entry: str) -> str:
        """
        Completes the ontology entry for the specified concept / relation.

        :param entry: ontology entry (concept / relation) to be completed
        :return: completed ontology entry
        """
        return "<" + self.ontology_prefix.replace('#', '#' + entry) + ">"

    def query_fault_condition_by_error_code(self, error_code: str, verbose: bool = True) -> List[str]:
        """
        Queries the fault condition for the specified error code.

        :param error_code: error code to query fault condition for
        :param verbose: if true, logging is activated
        :return: fault condition
        """
        if verbose and self.verbose:
            print("########################################################################")
            print(colored("QUERY: fault condition description for " + error_code, "green", "on_grey", ["bold"]))
            print("########################################################################")
        error_code_entry = self.complete_ontology_entry('ErrorCode')
        represents_entry = self.complete_ontology_entry('represents')
        condition_desc_entry = self.complete_ontology_entry('condition_desc')
        code_entry = self.complete_ontology_entry('code')
        s = f"""
            SELECT ?condition_desc WHERE {{
                ?error_code a {error_code_entry} .
                ?error_code {represents_entry} ?condition .
                ?error_code {code_entry} ?error_code_code .
                ?condition {condition_desc_entry} ?condition_desc .
                FILTER(STR(?error_code_code) = "{error_code}")
            }}
            """
        return [row['condition_desc']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, verbose)]

    def query_fault_condition_by_description(self, desc: str) -> List[str]:
        """
        Queries the fault condition instance for the specified description.

        :param desc: description to query fault condition instance for
        :return: fault condition instance
        """
        if self.verbose:
            print("########################################################################")
            print(colored("QUERY: fault condition for " + desc, "green", "on_grey", ["bold"]))
            print("########################################################################")
        fault_condition_entry = self.complete_ontology_entry('FaultCondition')
        condition_desc_entry = self.complete_ontology_entry('condition_desc')
        s = f"""
            SELECT ?fc WHERE {{
                ?fc a {fault_condition_entry} .
                ?fc {condition_desc_entry} ?desc
                FILTER(STR(?desc) = "{desc}")
            }}
            """
        return [row['fc']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, True)]

    def query_suspect_components_by_error_code(self, error_code: str, verbose: bool = True) -> List[str]:
        """
        Queries the suspect components associated with the specified error code.

        :param error_code: error code to query suspect components for
        :param verbose: if true, logging is activated
        :return: suspect components
        """
        if verbose and self.verbose:
            print("########################################################################")
            print(colored("QUERY: suspect components for " + error_code, "green", "on_grey", ["bold"]))
            print("########################################################################")
        error_code_entry = self.complete_ontology_entry('ErrorCode')
        suspect_comp_entry = self.complete_ontology_entry('SuspectComponent')
        diag_association_entry = self.complete_ontology_entry('DiagnosticAssociation')
        points_to_entry = self.complete_ontology_entry('pointsTo')
        has_association_entry = self.complete_ontology_entry('hasAssociation')
        component_name_entry = self.complete_ontology_entry('component_name')
        code_entry = self.complete_ontology_entry('code')
        s = f"""
            SELECT ?comp_name WHERE {{
                ?error_code a {error_code_entry} .
                ?comp a {suspect_comp_entry} .
                ?comp {component_name_entry} ?comp_name .
                ?da a {diag_association_entry} .
                ?error_code {code_entry} "{error_code}" .
                ?da {points_to_entry} ?comp .
                ?error_code {has_association_entry} ?da .
            }}
            """
        return [row['comp_name']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, verbose)]

    def query_suspect_component_by_name(self, component_name: str) -> List[str]:
        """
        Queries a suspect component by its component name.

        :param component_name: name to query suspect component for
        :return: suspect component
        """
        if self.verbose:
            print("########################################################################")
            print(colored("QUERY: suspect components by name - " + component_name, "green", "on_grey", ["bold"]))
            print("########################################################################")
        suspect_comp_entry = self.complete_ontology_entry('SuspectComponent')
        component_name_entry = self.complete_ontology_entry('component_name')
        s = f"""
            SELECT ?comp WHERE {{
                ?comp a {suspect_comp_entry} .
                ?comp {component_name_entry} ?comp_name .
                FILTER(STR(?comp_name) = "{component_name}")
            }}
            """
        return [row['comp']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, True)]

    def query_component_set_by_name(self, set_name: str) -> List[str]:
        """
        Queries a component set by its name.

        :param set_name: name to query component set for
        :return: component set
        """
        if self.verbose:
            print("########################################################################")
            print(colored("QUERY: component set by name - " + set_name, "green", "on_grey", ["bold"]))
            print("########################################################################")
        component_set_entry = self.complete_ontology_entry('ComponentSet')
        set_name_entry = self.complete_ontology_entry('set_name')
        s = f"""
            SELECT ?comp_set WHERE {{
                ?comp_set a {component_set_entry} .
                ?comp_set {set_name_entry} ?set_name .
                FILTER(STR(?set_name) = "{set_name}")
            }}
            """
        return [row['comp_set']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, True)]

    def query_diag_entity_instance_by_id(self, entity_id: str) -> List[str]:
        """
        Queries a diagnosis entity instance by its ID.

        :param entity_id: ID to query diagnosis entity instance for
        :return: diag entity instance
        """
        if self.verbose:
            print("########################################################################")
            print(colored("QUERY: diag entity instance by ID " + entity_id, "green", "on_grey", ["bold"]))
            print("########################################################################")
        diag_entity_entry = self.complete_ontology_entry('DiagEntity')
        id_entry = self.complete_ontology_entry('entity_id')
        s = f"""
            SELECT ?diag_entity WHERE {{
                ?diag_entity a {diag_entity_entry} .
                ?diag_entity {id_entry} "{entity_id}" .
            }}
            """
        return [row['diag_entity']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, True)]

    def query_diag_entity_by_error_code(
            self, error_code: str, verbose: bool = True
    ) -> List[Tuple[str, str, str, str]]:
        """
        Queries diag entities in which the specified error code occurred in the past.

        :param error_code: error code to query diag entities for
        :param verbose: if true, logging is activated
        :return: diag entities
        """
        if verbose and self.verbose:
            print("########################################################################")
            print(
                colored("QUERY: diag entities associated with error code " + error_code, "green", "on_grey", ["bold"])
            )
            print("########################################################################")
        error_code_entry = self.complete_ontology_entry('ErrorCode')
        diag_log_entry = self.complete_ontology_entry('DiagLog')
        appears_in_entry = self.complete_ontology_entry('appearsIn')
        created_for_entry = self.complete_ontology_entry('createdFor')
        fault_cond_class = self.complete_ontology_entry('FaultCondition')
        diag_entity_class = self.complete_ontology_entry('DiagEntity')
        represents_entry = self.complete_ontology_entry('represents')
        entity_id_entry = self.complete_ontology_entry('entity_id')
        code_entry = self.complete_ontology_entry('code')
        s = f"""
            SELECT ?entity_id WHERE {{
                ?diag_log a {diag_log_entry} .
                ?error_code {appears_in_entry} ?diag_log .
                ?diag_log {created_for_entry} ?diag_entity .
                ?fc a {fault_cond_class} .
                ?diag_entity a {diag_entity_class} .
                ?error_code {represents_entry} ?fc .
                ?error_code a {error_code_entry} .
                ?error_code {code_entry} ?error_code_code .
                ?diag_entity {entity_id_entry} ?entity_id .
                FILTER(STR(?error_code_code) = "{error_code}")
            }}
            """
        return [(row['entity_id']['value']) for row in self.fuseki_connection.query_knowledge_graph(s, verbose)]

    def query_all_error_code_instances(self, verbose: bool = True) -> List[str]:
        """
        Queries all error code instances stored in the knowledge graph.

        :param verbose: if true, logging is activated
        :return: all error codes stored in the knowledge graph
        """
        if verbose and self.verbose:
            print("########################################################################")
            print(colored("QUERY: all error code instances:", "green", "on_grey", ["bold"]))
            print("########################################################################")
        error_code_entry = self.complete_ontology_entry('ErrorCode')
        code_entry = self.complete_ontology_entry('code')
        s = f"""
            SELECT ?error_code WHERE {{
                ?instance a {error_code_entry} .
                ?instance {code_entry} ?error_code .
            }}
            """
        return [row['error_code']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, verbose)]

    def query_all_fault_condition_instances(self, verbose: bool = True) -> List[str]:
        """
        Queries all fault condition instances stored in the knowledge graph.

        :param verbose: if true, logging is activated
        :return: all fault conditions stored in the knowledge graph
        """
        if verbose and self.verbose:
            print("########################################################################")
            print(colored("QUERY: all fault condition instances:", "green", "on_grey", ["bold"]))
            print("########################################################################")
        fault_condition_entry = self.complete_ontology_entry('FaultCondition')
        condition_desc_entry = self.complete_ontology_entry('condition_desc')
        s = f"""
            SELECT ?desc WHERE {{
                ?instance a {fault_condition_entry} .
                ?instance {condition_desc_entry} ?desc .
            }}
            """
        return [row['desc']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, verbose)]

    def query_fault_condition_instance_by_code(self, error_code: str) -> List[str]:
        """
        Queries the fault condition instance represented by the specified error code.

        :param error_code: error code to query fault condition instance for
        :return: fault condition instance
        """
        if self.verbose:
            print("########################################################################")
            print(colored("QUERY: fault condition instance by code " + error_code, "green", "on_grey", ["bold"]))
            print("########################################################################")
        error_code_entry = self.complete_ontology_entry('ErrorCode')
        code_entry = self.complete_ontology_entry('code')
        represents_entry = self.complete_ontology_entry('represents')
        s = f"""
            SELECT ?fault_cond WHERE {{
                ?error_code a {error_code_entry} .
                ?error_code {code_entry} "{error_code}" .
                ?error_code {represents_entry} ?fault_cond .
            }}
            """
        return [row['fault_cond']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, True)]

    def query_error_code_instance_by_code(self, code: str) -> List[str]:
        """
        Queries the error code instance for the specified code.

        :param code: code to query `ErrorCode` instance for
        :return: error code instance
        """
        if self.verbose:
            print("########################################################################")
            print(colored("QUERY: error code instance by code " + code, "green", "on_grey", ["bold"]))
            print("########################################################################")
        error_code_entry = self.complete_ontology_entry('ErrorCode')
        code_entry = self.complete_ontology_entry('code')
        s = f"""
            SELECT ?error_code WHERE {{
                ?error_code a {error_code_entry} .
                ?error_code {code_entry} "{code}" .
            }}
            """
        return [row['error_code']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, True)]

    def query_diag_association_instance_by_error_code_and_sus_comp(
            self, error_code: str, comp: str, verbose: bool = True
    ) -> List[str]:
        """
        Queries the diagnostic association instance for the specified code and suspect component.

        :param error_code: error code to query diagnostic association for
        :param comp: suspect component to query diagnostic association for
        :param verbose: if true, logging is activated
        :return: diagnostic association instance
        """
        if verbose and self.verbose:
            print("########################################################################")
            print(
                colored(
                    "QUERY: diagnostic association by error code + suspect component: " + error_code + ", " + comp,
                    "green", "on_grey", ["bold"]
                )
            )
            print("########################################################################")
        error_code_entry = self.complete_ontology_entry('ErrorCode')
        diag_association_entry = self.complete_ontology_entry('DiagnosticAssociation')
        suspect_component_entry = self.complete_ontology_entry('SuspectComponent')
        code_entry = self.complete_ontology_entry('code')
        has_association_entry = self.complete_ontology_entry('hasAssociation')
        comp_name_entry = self.complete_ontology_entry('component_name')
        points_to_entry = self.complete_ontology_entry('pointsTo')
        s = f"""
            SELECT ?diag_association WHERE {{
                ?diag_association a {diag_association_entry} .
                ?error_code a {error_code_entry} .
                ?error_code {code_entry} "{error_code}" .
                ?error_code {has_association_entry} ?diag_association .
                ?sus a {suspect_component_entry} .
                ?sus {comp_name_entry} "{comp}" .
                ?diag_association {points_to_entry} ?sus .
            }}
            """
        return [row['diag_association']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, verbose)]

    def query_priority_id_by_error_code_and_sus_comp(
            self, error_code: str, comp: str, verbose: bool = True
    ) -> List[str]:
        """
        Queries the priority ID of the diagnostic association for the specified code and suspect component.

        :param error_code: error code to query priority ID for
        :param comp: suspect component to query priority ID for
        :param verbose: if true, logging is activated
        :return: priority ID
        """
        if verbose and self.verbose:
            print("########################################################################")
            print(
                colored(
                    "QUERY: diagnostic association priority by error code + component: " + error_code + ", " + comp,
                    "green", "on_grey", ["bold"]
                )
            )
            print("########################################################################")
        error_code_entry = self.complete_ontology_entry('ErrorCode')
        diag_association_entry = self.complete_ontology_entry('DiagnosticAssociation')
        suspect_component_entry = self.complete_ontology_entry('SuspectComponent')
        code_entry = self.complete_ontology_entry('code')
        has_association_entry = self.complete_ontology_entry('hasAssociation')
        comp_name_entry = self.complete_ontology_entry('component_name')
        points_to_entry = self.complete_ontology_entry('pointsTo')
        prio_entry = self.complete_ontology_entry('priority_id')
        s = f"""
            SELECT ?prio WHERE {{
                ?diag_association a {diag_association_entry} .
                ?diag_association  {prio_entry} ?prio .
                ?error_code a {error_code_entry} .
                ?error_code {code_entry} "{error_code}" .
                ?error_code {has_association_entry} ?diag_association .
                ?sus a {suspect_component_entry} .
                ?sus {comp_name_entry} "{comp}" .
                ?diag_association {points_to_entry} ?sus .
            }}
            """
        return [row['prio']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, verbose)]

    def query_generated_heatmaps_by_error_code_and_sus_comp(
            self, error_code: str, comp: str, verbose: bool = True
    ) -> List[str]:
        """
        Queries the generated heatmaps for the specified code and suspect component.

        :param error_code: error code to query generated heatmaps for
        :param comp: suspect component to query generated heatmaps for
        :param verbose: if true, logging is activated
        :return: generated heatmaps
        """
        if verbose and self.verbose:
            print("########################################################################")
            print(colored(
                "QUERY: generated heatmaps by error code + suspect component: " + error_code + ", " + comp,
                "green", "on_grey", ["bold"]
            ))
            print("########################################################################")
        error_code_entry = self.complete_ontology_entry('ErrorCode')
        diag_association_entry = self.complete_ontology_entry('DiagnosticAssociation')
        suspect_component_entry = self.complete_ontology_entry('SuspectComponent')
        code_entry = self.complete_ontology_entry('code')
        has_association_entry = self.complete_ontology_entry('hasAssociation')
        comp_name_entry = self.complete_ontology_entry('component_name')
        points_to_entry = self.complete_ontology_entry('pointsTo')
        heatmap_entry = self.complete_ontology_entry('Heatmap')
        checks_entry = self.complete_ontology_entry('checks')
        signal_classification_entry = self.complete_ontology_entry('SignalClassification')
        produces_entry = self.complete_ontology_entry('produces')
        gen_heatmap_entry = self.complete_ontology_entry('generated_heatmap')
        s = f"""
            SELECT ?heatmap_entry WHERE {{
                ?diag_association a {diag_association_entry} .
                ?error_code a {error_code_entry} .
                ?sus a {suspect_component_entry} .
                ?signal_classification a {signal_classification_entry} .
                ?heatmap a {heatmap_entry} .
                ?error_code {has_association_entry} ?diag_association .
                ?diag_association {points_to_entry} ?sus .
                ?signal_classification {checks_entry} ?sus .
                ?signal_classification {produces_entry} ?heatmap .
                ?error_code {code_entry} "{error_code}" .
                ?sus {comp_name_entry} "{comp}" .
                ?heatmap {gen_heatmap_entry} ?heatmap_entry .
            }}
            """
        return [row['heatmap_entry']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, verbose)]

    def query_error_codes_by_entity_id(self, entity_id: str) -> List[str]:
        """
        Queries the error codes for the specified entity ID.

        :param entity_id: entity ID to query error codes for
        :return: error codes
        """
        if self.verbose:
            print("########################################################################")
            print(colored("QUERY: error codes by entity ID " + entity_id, "green", "on_grey", ["bold"]))
            print("########################################################################")
        error_code_entry = self.complete_ontology_entry('ErrorCode')
        diag_entity_entry = self.complete_ontology_entry('DiagEntity')
        code_entry = self.complete_ontology_entry('code')
        entity_id_entry = self.complete_ontology_entry('entity_id')
        s = f"""
            SELECT ?code WHERE {{
                ?error_code a {error_code_entry} .
                ?error_code {code_entry} ?code .
                ?diag_entity a {diag_entity_entry} .
                ?diag_entity {entity_id_entry} "{entity_id}" .
            }}
            """
        return [row['code']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, True)]

    def query_affected_by_relations_by_suspect_component(self, component_name: str, verbose: bool = True) -> List[str]:
        """
        Queries the affecting components for the specified suspect component.

        :param component_name: suspect component to query affected_by relations for
        :param verbose: if true, logging is activated
        :return: affecting components
        """
        if verbose and self.verbose:
            print("########################################################################")
            print(
                colored("QUERY: affecting components by component name " + component_name, "green", "on_grey", ["bold"])
            )
            print("########################################################################")
        comp_entry = self.complete_ontology_entry('SuspectComponent')
        name_entry = self.complete_ontology_entry('component_name')
        affected_by_entry = self.complete_ontology_entry('affected_by')
        s = f"""
            SELECT ?affected_by WHERE {{
                ?comp a {comp_entry} .
                ?comp {name_entry} "{component_name}" .
                ?comp {affected_by_entry} ?affected_by .
            }}
            """
        return [row['affected_by']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, False)]

    def query_verifies_relation_by_suspect_component(self, component_name: str, verbose: bool = True) -> List[str]:
        """
        Queries the component set that can be verified by the specified suspect component.

        :param component_name: suspect component to query verified component set for
        :param verbose: if true, logging is activated
        :return: component set name
        """
        if verbose and self.verbose:
            print("########################################################################")
            print(colored(
                "QUERY: verified component set by component name " + component_name, "green", "on_grey", ["bold"]
            ))
            print("########################################################################")
        comp_entry = self.complete_ontology_entry('SuspectComponent')
        name_entry = self.complete_ontology_entry('component_name')
        set_entry = self.complete_ontology_entry('ComponentSet')
        set_name_entry = self.complete_ontology_entry('set_name')
        verifies_entry = self.complete_ontology_entry('verifies')
        s = f"""
            SELECT ?set_name WHERE {{
                ?comp a {comp_entry} .
                ?comp {name_entry} "{component_name}" .
                ?set a {set_entry} .
                ?set {set_name_entry} ?set_name .
                ?comp {verifies_entry} ?set .
            }}
            """
        return [row['set_name']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, False)]

    def query_verifies_relations_by_component_set(self, set_name: str, verbose: bool = True) -> List[str]:
        """
        Queries the suspect components that can verify the specified component set.

        :param set_name: component set to query verifying suspect components for
        :param verbose: if true, logging is activated
        :return: suspect component names
        """
        if verbose and self.verbose:
            print("########################################################################")
            print(
                colored("QUERY: verifying components by component set name " + set_name, "green", "on_grey", ["bold"])
            )
            print("########################################################################")
        comp_entry = self.complete_ontology_entry('SuspectComponent')
        name_entry = self.complete_ontology_entry('component_name')
        component_set_entry = self.complete_ontology_entry('ComponentSet')
        set_name_entry = self.complete_ontology_entry('set_name')
        verifies_entry = self.complete_ontology_entry('verifies')
        s = f"""
            SELECT ?comp_name WHERE {{
                ?comp_set a {component_set_entry} .
                ?comp_set {set_name_entry} "{set_name}" .
                ?comp a {comp_entry} .
                ?comp {name_entry} ?comp_name .
                ?comp {verifies_entry} ?comp_set .
            }}
            """
        return [row['comp_name']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, False)]

    def query_includes_relation_by_component_set(self, comp_set_name: str, verbose: bool = True) -> List[str]:
        """
        Queries the suspect components that are included in the specified component set.

        :param comp_set_name: component set to query included suspect components for
        :param verbose: if true, logging is activated
        :return: component names
        """
        if verbose and self.verbose:
            print("########################################################################")
            print(colored("QUERY: components by component set name " + comp_set_name, "green", "on_grey", ["bold"]))
            print("########################################################################")
        comp_entry = self.complete_ontology_entry('SuspectComponent')
        name_entry = self.complete_ontology_entry('component_name')
        comp_set_entry = self.complete_ontology_entry('ComponentSet')
        set_name_entry = self.complete_ontology_entry('set_name')
        includes_entry = self.complete_ontology_entry('includes')
        s = f"""
            SELECT ?comp_name WHERE {{
                ?comp_set a {comp_set_entry} .
                ?comp_set {set_name_entry} "{comp_set_name}" .
                ?comp a {comp_entry} .
                ?comp {name_entry} ?comp_name .
                ?comp_set {includes_entry} ?comp .
            }}
            """
        return [row['comp_name']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, False)]

    def query_all_component_instances(self, verbose: bool = True) -> List[str]:
        """
        Queries all component instances stored in the knowledge graph.

        :param verbose: if true, logging is activated
        :return: all components stored in the knowledge graph
        """
        if verbose and self.verbose:
            print("####################################")
            print("QUERY: all component instances")
            print("####################################")
        comp_entry = self.complete_ontology_entry('SuspectComponent')
        name_entry = self.complete_ontology_entry('component_name')
        s = f"""
            SELECT ?name WHERE {{
                ?comp a {comp_entry} .
                ?comp {name_entry} ?name.
            }}
            """
        return [row['name']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, verbose)]

    def query_all_diag_entity_instances(self, verbose: bool = True) -> List[Tuple[str, str]]:
        """
        Queries all diag entity instances stored in the knowledge graph.

        :param verbose: if true, logging is activated
        :return: all diag entities stored in the knowledge graph
        """
        if verbose and self.verbose:
            print("####################################")
            print("QUERY: all diag entity instances")
            print("####################################")
        diag_entity_entry = self.complete_ontology_entry('DiagEntity')
        entity_id_entry = self.complete_ontology_entry('entity_id')
        s = f"""
            SELECT ?diag_entity ?entity_id WHERE {{
                ?diag_entity a {diag_entity_entry} .
                ?diag_entity {entity_id_entry} ?entity_id .
            }}
            """
        return [
            (row['diag_entity']['value'], row['entity_id']['value'])
            for row in self.fuseki_connection.query_knowledge_graph(s, verbose)
        ]

    def query_all_recorded_sensor_signals(self, verbose: bool = True) -> List[str]:
        """
        Queries all recorded sensor signals stored in the knowledge graph.

        :param verbose: if true, logging is activated
        :return: all rec sensor signals stored in the knowledge graph
        """
        if verbose and self.verbose:
            print("####################################")
            print("QUERY: all rec sensor signal instances")
            print("####################################")
        signal_entry = self.complete_ontology_entry('SensorSignal')
        s = f"""
            SELECT ?signal WHERE {{
                ?signal a {signal_entry} .
            }}
            """
        return [row['signal']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, verbose)]

    def query_all_signal_classifications(self, verbose: bool = True) -> List[str]:
        """
        Queries all signal classification instances stored in the knowledge graph.

        :param verbose: if true, logging is activated
        :return: all signal classifications stored in the knowledge graph
        """
        if verbose and self.verbose:
            print("####################################")
            print("QUERY: all signal classification instances")
            print("####################################")
        signal_classification_entry = self.complete_ontology_entry('SignalClassification')
        s = f"""
            SELECT ?signal_classification WHERE {{
                ?signal_classification a {signal_classification_entry} .
            }}
            """
        return [
            row['signal_classification']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, verbose)
        ]

    def query_signal_classification_by_heatmap(self, heatmap_id: str, verbose: bool = True) -> List[str]:
        """
        Queries the signal classification instance that produces the specified heatmap.

        :param heatmap_id: heatmap instance to query signal classification for
        :param verbose: if true, logging is activated
        :return: signal classification for the specified heatmap
        """
        if verbose and self.verbose:
            print("####################################")
            print("QUERY: signal classification instances for the specified heatmap:", heatmap_id)
            print("####################################")
        signal_classification_entry = self.complete_ontology_entry('SignalClassification')
        heatmap_entry = self.complete_ontology_entry('Heatmap')
        produces_entry = self.complete_ontology_entry('produces')
        id_entry = self.complete_ontology_entry(heatmap_id)
        id_entry = id_entry.replace('<', '').replace('>', '')
        s = f"""
            SELECT ?signal_classification WHERE {{
                ?signal_classification a {signal_classification_entry} .
                ?heatmap a {heatmap_entry} .
                ?signal_classification {produces_entry} ?heatmap .
                FILTER(STR(?heatmap) = "{id_entry}") .
            }}
            """
        return [
            row['signal_classification']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, verbose)
        ]

    def query_all_manual_inspection_instances(self, verbose: bool = True) -> List[str]:
        """
        Queries all manual inspection instances stored in the knowledge graph.

        :param verbose: if true, logging is activated
        :return: all manual inspections stored in the knowledge graph
        """
        if verbose and self.verbose:
            print("####################################")
            print("QUERY: all manual inspection instances")
            print("####################################")
        manual_inspection_entry = self.complete_ontology_entry('ManualInspection')
        s = f"""
            SELECT ?manual_inspection WHERE {{
                ?manual_inspection a {manual_inspection_entry} .
            }}
            """
        return [row['manual_inspection']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, verbose)]

    def query_all_diag_log_instances(self, verbose: bool = True) -> List[str]:
        """
        Queries all diag log instances stored in the knowledge graph.

        :param verbose: if true, logging is activated
        :return: all diag logs stored in the knowledge graph
        """
        if verbose and self.verbose:
            print("####################################")
            print("QUERY: all diag log instances")
            print("####################################")
        diag_log_entry = self.complete_ontology_entry('DiagLog')
        s = f"""
            SELECT ?diag_log WHERE {{
                ?diag_log a {diag_log_entry} .
            }}
            """
        return [row['diag_log']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, verbose)]

    def query_all_fault_path_instances(self, verbose: bool = True) -> List[str]:
        """
        Queries all fault path instances stored in the knowledge graph.

        :param verbose: if true, logging is activated
        :return: all fault paths stored in the knowledge graph
        """
        if verbose and self.verbose:
            print("####################################")
            print("QUERY: all fault path instances")
            print("####################################")
        fault_path_entry = self.complete_ontology_entry('FaultPath')
        s = f"""
            SELECT ?fault_path WHERE {{
                ?fault_path a {fault_path_entry} .
            }}
            """
        return [row['fault_path']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, verbose)]

    def query_model_id_by_signal_classification_id(
            self, signal_classification_id: str, verbose: bool = True
    ) -> List[str]:
        """
        Queries the model ID for the specified signal classification instance.

        :param signal_classification_id: ID of the signal classification instance to query model ID for
        :param verbose: if true, logging is activated
        :return: model ID for signal classification instance
        """
        if verbose and self.verbose:
            print("####################################")
            print("QUERY: model ID for the specified signal classification:", signal_classification_id)
            print("####################################")
        signal_classification_entry = self.complete_ontology_entry('SignalClassification')
        model_entry = self.complete_ontology_entry('Model')
        id_entry = self.complete_ontology_entry(signal_classification_id)
        id_entry = id_entry.replace('<', '').replace('>', '')
        model_id_entry = self.complete_ontology_entry('model_id')
        performs_entry = self.complete_ontology_entry('performs')
        s = f"""
            SELECT ?model_id WHERE {{
                ?signal_classification a {signal_classification_entry} .
                ?model a {model_entry} .
                ?model {performs_entry} ?signal_classification .
                FILTER(STR(?signal_classification) = "{id_entry}") .
                ?model {model_id_entry} ?model_id .
            }}
            """
        return [row['model_id']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, verbose)]

    def query_model_by_model_id(self, model_id: str, verbose: bool = True) -> List[str]:
        """
        Queries the model for the specified model ID.

        :param model_id: ID of the model to query instance for
        :param verbose: if true, logging is activated
        :return: model instance
        """
        if verbose and self.verbose:
            print("####################################")
            print("QUERY: model instance for the specified ID:", model_id)
            print("####################################")
        model_entry = self.complete_ontology_entry('Model')
        model_id_entry = self.complete_ontology_entry('model_id')
        s = f"""
            SELECT ?model WHERE {{
                ?model a {model_entry} .
                ?model {model_id_entry} ?model_id .
                FILTER(STR(?model_id) = "{model_id}")
            }}
            """
        return [row['model']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, verbose)]

    def query_suspect_component_name_by_id(self, component_id: str, verbose: bool = True) -> List[str]:
        """
        Queries the suspect component name for the specified component ID.

        :param component_id: ID of the component instance to query name for
        :param verbose: if true, logging is activated
        :return: component name for component instance
        """
        if verbose and self.verbose:
            print("####################################")
            print("QUERY: suspect component name for the specified instance:", component_id)
            print("####################################")
        suspect_comp_entry = self.complete_ontology_entry('SuspectComponent')
        id_entry = self.complete_ontology_entry(component_id)
        id_entry = id_entry.replace('<', '').replace('>', '')
        comp_name_entry = self.complete_ontology_entry('component_name')
        s = f"""
            SELECT ?comp_name WHERE {{
                ?sus_comp a {suspect_comp_entry} .
                FILTER(STR(?sus_comp) = "{id_entry}") .
                ?sus_comp {comp_name_entry} ?comp_name .
            }}
            """
        return [row['comp_name']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, verbose)]

    def query_uncertainty_by_signal_classification_id(
            self, signal_classification_id: str, verbose: bool = True
    ) -> List[str]:
        """
        Queries the uncertainty for the specified signal classification instance.

        :param signal_classification_id: ID of the signal classification instance to query uncertainty for
        :param verbose: if true, logging is activated
        :return: uncertainty for signal classification instance
        """
        if verbose and self.verbose:
            print("####################################")
            print("QUERY: uncertainty for the specified signal classification:", signal_classification_id)
            print("####################################")
        signal_classification_entry = self.complete_ontology_entry('SignalClassification')
        id_entry = self.complete_ontology_entry(signal_classification_id)
        id_entry = id_entry.replace('<', '').replace('>', '')
        uncertainty_entry = self.complete_ontology_entry('uncertainty')
        s = f"""
            SELECT ?uncertainty WHERE {{
                ?signal_classification a {signal_classification_entry} .
                FILTER(STR(?signal_classification) = "{id_entry}") .
                ?signal_classification {uncertainty_entry} ?uncertainty .
            }}
            """
        return [row['uncertainty']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, verbose)]

    def query_date_by_diag_log(self, diag_log_id: str, verbose: bool = True) -> List[str]:
        """
        Queries the date for the specified diag log instance.

        :param diag_log_id: ID of the diag log instance to query date for
        :param verbose: if true, logging is activated
        :return: date for diag log instance
        """
        if verbose and self.verbose:
            print("####################################")
            print("QUERY: date for the specified diag log:", diag_log_id)
            print("####################################")
        diag_log_entry = self.complete_ontology_entry('DiagLog')
        id_entry = self.complete_ontology_entry(diag_log_id)
        id_entry = id_entry.replace('<', '').replace('>', '')
        date_entry = self.complete_ontology_entry('date')
        s = f"""
            SELECT ?date WHERE {{
                ?diag_log a {diag_log_entry} .
                FILTER(STR(?diag_log) = "{id_entry}") .
                ?diag_log {date_entry} ?date .
            }}
            """
        return [row['date']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, verbose)]

    def query_resulted_in_by_fault_path(self, fault_path_id: str, verbose: bool = True) -> List[str]:
        """
        Queries the fault conditions resulting in the specified fault path instance.

        :param fault_path_id: ID of the fault path instance to query fault conditions for
        :param verbose: if true, logging is activated
        :return: fault conditions for fault path instance
        """
        if verbose and self.verbose:
            print("####################################")
            print("QUERY: fault conditions for the specified fault path:", fault_path_id)
            print("####################################")
        fault_path_entry = self.complete_ontology_entry('FaultPath')
        id_entry = self.complete_ontology_entry(fault_path_id)
        id_entry = id_entry.replace('<', '').replace('>', '')
        resulted_in_entry = self.complete_ontology_entry('resultedIn')
        s = f"""
            SELECT ?fault_cond WHERE {{
                ?fault_path a {fault_path_entry} .
                FILTER(STR(?fault_path) = "{id_entry}") .
                ?fault_cond {resulted_in_entry} ?fault_path .
            }}
            """
        return [row['fault_cond']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, verbose)]

    def query_error_codes_recorded_in_diag_entity(self, diag_entity_id: str, verbose: bool = True) -> List[str]:
        """
        Queries the error codes recorded in the specified diag entity.

        :param diag_entity_id: ID of the diag entity to retrieve error codes for
        :param verbose: if true, logging is activated
        :return: error codes for the diag entity instance
        """
        if verbose and self.verbose:
            print("####################################")
            print("QUERY: error codes for the specified diag entity:", diag_entity_id)
            print("####################################")
        error_code_entry = self.complete_ontology_entry('ErrorCode')
        diag_log_entry = self.complete_ontology_entry('DiagLog')
        diag_entity_entry = self.complete_ontology_entry('DiagEntity')
        id_entry = self.complete_ontology_entry(diag_entity_id)
        id_entry = id_entry.replace('<', '').replace('>', '')
        appears_in_entry = self.complete_ontology_entry('appearsIn')
        created_for_entry = self.complete_ontology_entry('createdFor')
        code_entry = self.complete_ontology_entry('code')
        s = f"""
            SELECT ?code WHERE {{
                ?diag_entity a {diag_entity_entry} .
                FILTER(STR(?diag_entity) = "{id_entry}") .
                ?diag_log a {diag_log_entry} .
                ?error_code a {error_code_entry} .
                ?error_code {appears_in_entry} ?diag_log .
                ?diag_log {created_for_entry} ?diag_entity .
                ?error_code {code_entry} ?code .
            }}
            """
        return [row['code']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, verbose)]

    def query_error_codes_by_diag_log(self, diag_log_id: str, verbose: bool = True) -> List[str]:
        """
        Queries the error codes for the specified diag log instance.

        :param diag_log_id: ID of the diag log instance to query error codes for
        :param verbose: if true, logging is activated
        :return: error codes for diag log instance
        """
        if verbose and self.verbose:
            print("####################################")
            print("QUERY: error codes for the specified diag log:", diag_log_id)
            print("####################################")
        diag_log_entry = self.complete_ontology_entry('DiagLog')
        id_entry = self.complete_ontology_entry(diag_log_id)
        id_entry = id_entry.replace('<', '').replace('>', '')
        appears_in_entry = self.complete_ontology_entry('appearsIn')
        s = f"""
            SELECT ?error_code WHERE {{
                ?diag_log a {diag_log_entry} .
                FILTER(STR(?diag_log) = "{id_entry}") .
                ?error_code {appears_in_entry} ?diag_log .
            }}
            """
        return [row['error_code']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, verbose)]

    def query_diag_steps_by_diag_log(self, diag_log_id: str, verbose: bool = True) -> List[str]:
        """
        Queries the diagnostic steps for the specified diag log instance.

        :param diag_log_id: ID of the diag log instance to query diag steps for
        :param verbose: if true, logging is activated
        :return: diag steps for diag log instance
        """
        if verbose and self.verbose:
            print("####################################")
            print("QUERY: diag steps for the specified diag log:", diag_log_id)
            print("####################################")
        diag_log_entry = self.complete_ontology_entry('DiagLog')
        id_entry = self.complete_ontology_entry(diag_log_id)
        id_entry = id_entry.replace('<', '').replace('>', '')
        diag_step_entry = self.complete_ontology_entry('diagStep')
        s = f"""
            SELECT ?classification WHERE {{
                ?diag_log a {diag_log_entry} .
                FILTER(STR(?diag_log) = "{id_entry}") .
                ?classification {diag_step_entry} ?diag_log .
            }}
            """
        return [row['classification']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, verbose)]

    def query_fault_path_by_diag_log(self, diag_log_id: str, verbose: bool = True) -> List[str]:
        """
        Queries the fault path for the specified diag log instance.

        :param diag_log_id: ID of the diag log instance to query fault path for
        :param verbose: if true, logging is activated
        :return: fault path for diag log instance
        """
        if verbose and self.verbose:
            print("####################################")
            print("QUERY: fault path for the specified diag log:", diag_log_id)
            print("####################################")
        diag_log_entry = self.complete_ontology_entry('DiagLog')
        id_entry = self.complete_ontology_entry(diag_log_id)
        id_entry = id_entry.replace('<', '').replace('>', '')
        entails_entry = self.complete_ontology_entry('entails')
        s = f"""
            SELECT ?fault_path WHERE {{
                ?diag_log a {diag_log_entry} .
                FILTER(STR(?diag_log) = "{id_entry}") .
                ?diag_log {entails_entry} ?fault_path .
            }}
            """
        return [row['fault_path']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, verbose)]

    def query_fault_path_description_by_id(self, fault_path_id: str, verbose: bool = True) -> List[str]:
        """
        Queries the fault path description for the specified fault path ID.

        :param fault_path_id: ID of the fault path instance to query description for
        :param verbose: if true, logging is activated
        :return: fault path description for the specified ID
        """
        if verbose and self.verbose:
            print("####################################")
            print("QUERY: fault path description for the specified ID:", fault_path_id)
            print("####################################")
        fault_path_entry = self.complete_ontology_entry('FaultPath')
        id_entry = self.complete_ontology_entry(fault_path_id)
        id_entry = id_entry.replace('<', '').replace('>', '')
        desc_entry = self.complete_ontology_entry('fault_path_desc')
        s = f"""
            SELECT ?path_desc WHERE {{
                ?fault_path a {fault_path_entry} .
                FILTER(STR(?fault_path) = "{id_entry}") .
                ?fault_path {desc_entry} ?path_desc .
            }}
            """
        return [row['path_desc']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, verbose)]

    def query_fault_condition_description_by_id(self, fault_condition_id: str, verbose: bool = True) -> List[str]:
        """
        Queries the fault condition description for the specified fault condition ID.

        :param fault_condition_id: ID of the fault condition instance to query description for
        :param verbose: if true, logging is activated
        :return: fault condition description for the specified ID
        """
        if verbose and self.verbose:
            print("####################################")
            print("QUERY: fault condition description for the specified ID:", fault_condition_id)
            print("####################################")
        fault_condition_entry = self.complete_ontology_entry('FaultCondition')
        id_entry = self.complete_ontology_entry(fault_condition_id)
        id_entry = id_entry.replace('<', '').replace('>', '')
        desc_entry = self.complete_ontology_entry('condition_desc')
        s = f"""
            SELECT ?cond_desc WHERE {{
                ?fault_cond a {fault_condition_entry} .
                FILTER(STR(?fault_cond) = "{id_entry}") .
                ?fault_cond {desc_entry} ?cond_desc .
            }}
            """
        return [row['cond_desc']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, verbose)]

    def query_diag_entity_by_diag_log(self, diag_log_id: str, verbose: bool = True) -> List[str]:
        """
        Queries the diag entity for the specified diag log instance.

        :param diag_log_id: ID of the diag log instance to query diag entity for
        :param verbose: if true, logging is activated
        :return: diag entity for diag log instance
        """
        if verbose and self.verbose:
            print("####################################")
            print("QUERY: diag entity for the specified diag log:", diag_log_id)
            print("####################################")
        diag_log_entry = self.complete_ontology_entry('DiagLog')
        id_entry = self.complete_ontology_entry(diag_log_id)
        id_entry = id_entry.replace('<', '').replace('>', '')
        created_for_entry = self.complete_ontology_entry('createdFor')
        s = f"""
            SELECT ?diag_entity WHERE {{
                ?diag_log a {diag_log_entry} .
                FILTER(STR(?diag_log) = "{id_entry}") .
                ?diag_log {created_for_entry} ?diag_entity .
            }}
            """
        return [row['diag_entity']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, verbose)]

    def query_signal_by_sensor_signal_instance(self, sensor_signal_id: str, verbose: bool = True) -> List[str]:
        """
        Queries the signal for the specified `SensorSignal` instance.

        :param sensor_signal_id: ID of the `SensorSignal` instance to query signal for
        :param verbose: if true, logging is activated
        :return: signal for `SensorSignal` instance
        """
        if verbose and self.verbose:
            print("####################################")
            print("QUERY: signal for the specified `SensorSignal`:", sensor_signal_id)
            print("####################################")
        sensor_signal_entry = self.complete_ontology_entry('SensorSignal')
        id_entry = self.complete_ontology_entry(sensor_signal_id)
        id_entry = id_entry.replace('<', '').replace('>', '')
        signal_entry = self.complete_ontology_entry('signal')
        s = f"""
            SELECT ?signal WHERE {{
                ?sensor_signal a {sensor_signal_entry} .
                FILTER(STR(?sensor_signal) = "{id_entry}") .
                ?sensor_signal {signal_entry} ?signal .
            }}
            """
        return [row['signal']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, verbose)]

    def query_sensor_signal_by_classification_instance(
            self, signal_classification_id: str, verbose: bool = True
    ) -> List[str]:
        """
        Queries the sensor signal instance for the specified classification.

        :param signal_classification_id: ID of signal classification instance
        :param verbose: if true, logging is activated
        :return: sensor signal instance
        """
        if verbose and self.verbose:
            print("####################################")
            print("QUERY: sensor signal instance for the specified classification:", signal_classification_id)
            print("####################################")
        signal_classification_entry = self.complete_ontology_entry('SignalClassification')
        id_entry = self.complete_ontology_entry(signal_classification_id)
        id_entry = id_entry.replace('<', '').replace('>', '')
        classifies_entry = self.complete_ontology_entry('classifies')
        s = f"""
            SELECT ?sensor_signal WHERE {{
                ?signal_classification a {signal_classification_entry} .
                FILTER(STR(?signal_classification) = "{id_entry}") .
                ?signal_classification {classifies_entry} ?sensor_signal .
            }}
            """
        return [row['sensor_signal']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, verbose)]

    def query_suspect_component_by_classification(self, classification_id: str, verbose: bool = True) -> List[str]:
        """
        Queries the suspect component for the specified classification.

        :param classification_id: ID of classification instance
        :param verbose: if true, logging is activated
        :return: suspect component
        """
        if verbose and self.verbose:
            print("####################################")
            print("QUERY: suspect component for the specified classification:", classification_id)
            print("####################################")
        signal_classification_entry = self.complete_ontology_entry('SignalClassification')
        manual_inspection_entry = self.complete_ontology_entry('ManualInspection')
        id_entry = self.complete_ontology_entry(classification_id)
        id_entry = id_entry.replace('<', '').replace('>', '')
        checks_entry = self.complete_ontology_entry('checks')
        s = f"""
            SELECT ?comp WHERE {{
                {{ ?classification a {signal_classification_entry} . }}
                UNION
                {{ ?classification a {manual_inspection_entry} . }}
                FILTER(STR(?classification) = "{id_entry}") .
                ?classification {checks_entry} ?comp .
            }}
            """
        return [row['comp']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, verbose)]

    def query_reason_for_classification(self, signal_classification_id: str, verbose: bool = True) -> List[str]:
        """
        Queries the reason (other classification) for the specified classification.

        :param signal_classification_id: ID of signal classification instance
        :param verbose: if true, logging is activated
        :return: classification reason
        """
        if verbose and self.verbose:
            print("####################################")
            print("QUERY: classification reason for the specified classification:", signal_classification_id)
            print("####################################")
        signal_classification_entry = self.complete_ontology_entry('SignalClassification')
        id_entry = self.complete_ontology_entry(signal_classification_id)
        id_entry = id_entry.replace('<', '').replace('>', '')
        reason_for_entry = self.complete_ontology_entry('reasonFor')
        s = f"""
            SELECT ?reason_for WHERE {{
                ?signal_classification a {signal_classification_entry} .
                FILTER(STR(?signal_classification) = "{id_entry}") .
                ?reason_for {reason_for_entry} ?signal_classification .
            }}
            """
        return [row['reason_for']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, verbose)]

    def query_led_to_for_classification(self, signal_classification_id: str, verbose: bool = True) -> List[str]:
        """
        Queries the reason (diag association) for the specified classification.

        :param signal_classification_id: ID of signal classification instance
        :param verbose: if true, logging is activated
        :return: classification reason
        """
        if verbose and self.verbose:
            print("####################################")
            print("QUERY: classification reason for the specified classification:", signal_classification_id)
            print("####################################")
        signal_classification_entry = self.complete_ontology_entry('SignalClassification')
        id_entry = self.complete_ontology_entry(signal_classification_id)
        id_entry = id_entry.replace('<', '').replace('>', '')
        led_to_entry = self.complete_ontology_entry('ledTo')
        s = f"""
            SELECT ?led_to WHERE {{
                ?signal_classification a {signal_classification_entry} .
                FILTER(STR(?signal_classification) = "{id_entry}") .
                ?led_to {led_to_entry} ?signal_classification .
            }}
            """
        return [row['led_to']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, verbose)]

    def query_reason_for_inspection(self, manual_inspection_id: str, verbose: bool = True) -> List[str]:
        """
        Queries the reason (other classification) for the specified inspection.

        :param manual_inspection_id: ID of manual inspection instance
        :param verbose: if true, logging is activated
        :return: classification reason
        """
        if verbose and self.verbose:
            print("####################################")
            print("QUERY: classification reason for the specified manual inspection:", manual_inspection_id)
            print("####################################")
        manual_inspection_entry = self.complete_ontology_entry('ManualInspection')
        id_entry = self.complete_ontology_entry(manual_inspection_id)
        id_entry = id_entry.replace('<', '').replace('>', '')
        reason_for_entry = self.complete_ontology_entry('reasonFor')
        s = f"""
            SELECT ?reason_for WHERE {{
                ?manual_inspection a {manual_inspection_entry} .
                FILTER(STR(?manual_inspection) = "{id_entry}") .
                ?reason_for {reason_for_entry} ?manual_inspection .
            }}
            """
        return [row['reason_for']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, verbose)]

    def query_led_to_for_inspection(self, manual_inspection_id: str, verbose: bool = True) -> List[str]:
        """
        Queries the reason (diag association) for the specified inspection.

        :param manual_inspection_id: ID of manual inspection instance
        :param verbose: if true, logging is activated
        :return: classification reason
        """
        if verbose and self.verbose:
            print("####################################")
            print("QUERY: classification reason for the specified manual inspection:", manual_inspection_id)
            print("####################################")
        manual_inspection_entry = self.complete_ontology_entry('ManualInspection')
        id_entry = self.complete_ontology_entry(manual_inspection_id)
        id_entry = id_entry.replace('<', '').replace('>', '')
        led_to_entry = self.complete_ontology_entry('ledTo')
        s = f"""
            SELECT ?led_to WHERE {{
                ?manual_inspection a {manual_inspection_entry} .
                FILTER(STR(?manual_inspection) = "{id_entry}") .
                ?led_to {led_to_entry} ?manual_inspection .
            }}
            """
        return [row['led_to']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, verbose)]

    def query_channel_by_name(self, chan_name: str) -> List[str]:
        """
        Queries a multivariate signal channel by its name.

        :param chan_name: name to query channel for
        :return: channel
        """
        print("########################################################################")
        print(colored("QUERY: signal channel by name - " + chan_name, "green", "on_grey", ["bold"]))
        print("########################################################################")
        chan_entry = self.complete_ontology_entry('Channel')
        chan_name_entry = self.complete_ontology_entry('channel_name')
        s = f"""
            SELECT ?chan WHERE {{
                ?chan a {chan_entry} .
                ?chan {chan_name_entry} ?chan_name .
                FILTER(STR(?chan_name) = "{chan_name}")
            }}
            """
        return [row['chan']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, True)]

    def query_sub_component_by_name(self, sub_component_name: str) -> List[str]:
        """
        Queries a subcomponent by its name.

        :param sub_component_name: name to query subcomponent for
        :return: subcomponent
        """
        print("########################################################################")
        print(colored("QUERY: subcomponents by name - " + sub_component_name, "green", "on_grey", ["bold"]))
        print("########################################################################")
        sub_comp_entry = self.complete_ontology_entry('SubComponent')
        component_name_entry = self.complete_ontology_entry('component_name')
        s = f"""
            SELECT ?sub_comp WHERE {{
                ?sub_comp a {sub_comp_entry} .
                ?sub_comp {component_name_entry} ?comp_name .
                FILTER(STR(?comp_name) = "{sub_component_name}")
            }}
            """
        return [row['sub_comp']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, True)]

    def query_prediction_by_classification(self, classification_id: str, verbose: bool = True) -> List[str]:
        """
        Queries the prediction for the specified classification.

        :param classification_id: ID of classification instance
        :param verbose: if true, logging is activated
        :return: prediction
        """
        if verbose and self.verbose:
            print("####################################")
            print("QUERY: prediction for the specified classification:", classification_id)
            print("####################################")
        signal_classification_entry = self.complete_ontology_entry('SignalClassification')
        manual_classification_entry = self.complete_ontology_entry('ManualInspection')
        id_entry = self.complete_ontology_entry(classification_id)
        id_entry = id_entry.replace('<', '').replace('>', '')
        pred_entry = self.complete_ontology_entry('prediction')
        s = f"""
            SELECT ?pred WHERE {{
                {{ ?classification a {signal_classification_entry} . }}
                UNION
                {{ ?classification a {manual_classification_entry} . }}
                FILTER(STR(?classification) = "{id_entry}") .
                ?classification {pred_entry} ?pred .
            }}
            """
        return [row['pred']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, verbose)]

    def query_heatmap_by_classification_instance(
            self, signal_classification_id: str, verbose: bool = True
    ) -> List[str]:
        """
        Queries the heatmap instance for the specified classification.

        :param signal_classification_id: ID of signal classification instance
        :param verbose: if true, logging is activated
        :return: generated heatmap
        """
        if verbose and self.verbose:
            print("####################################")
            print("QUERY: heatmap instance for the specified classification:", signal_classification_id)
            print("####################################")
        signal_classification_entry = self.complete_ontology_entry('SignalClassification')
        id_entry = self.complete_ontology_entry(signal_classification_id)
        id_entry = id_entry.replace('<', '').replace('>', '')
        produces_entry = self.complete_ontology_entry('produces')
        s = f"""
            SELECT ?heatmap WHERE {{
                ?signal_classification a {signal_classification_entry} .
                FILTER(STR(?signal_classification) = "{id_entry}") .
                ?signal_classification {produces_entry} ?heatmap .
            }}
            """
        return [row['heatmap']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, verbose)]

    def query_generation_method_by_heatmap(self, heatmap_id: str, verbose: bool = True) -> List[str]:
        """
        Queries the heatmap generation method for the specified heatmap instance.

        :param heatmap_id: ID of heatmap instance
        :param verbose: if true, logging is activated
        :return: heatmap generation method
        """
        if verbose and self.verbose:
            print("####################################")
            print("QUERY: heatmap generation method for the specified heatmap instance:", heatmap_id)
            print("####################################")
        heatmap_entry = self.complete_ontology_entry('Heatmap')
        id_entry = self.complete_ontology_entry(heatmap_id)
        id_entry = id_entry.replace('<', '').replace('>', '')
        generation_method_entry = self.complete_ontology_entry('generation_method')
        s = f"""
            SELECT ?gen_method WHERE {{
                ?heatmap a {heatmap_entry} .
                FILTER(STR(?heatmap) = "{id_entry}") .
                ?heatmap {generation_method_entry} ?gen_method .
            }}
            """
        return [row['gen_method']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, verbose)]

    def query_heatmap_string_by_heatmap(self, heatmap_id: str, verbose: bool = True) -> List[str]:
        """
        Queries the heatmap values for the specified heatmap instance.

        :param heatmap_id: ID of heatmap instance
        :param verbose: if true, logging is activated
        :return: heatmap values (string)
        """
        if verbose and self.verbose:
            print("####################################")
            print("QUERY: heatmap values for the specified heatmap instance:", heatmap_id)
            print("####################################")
        heatmap_entry = self.complete_ontology_entry('Heatmap')
        id_entry = self.complete_ontology_entry(heatmap_id)
        id_entry = id_entry.replace('<', '').replace('>', '')
        heatmap_values_entry = self.complete_ontology_entry('generated_heatmap')
        s = f"""
            SELECT ?gen_heatmap WHERE {{
                ?heatmap a {heatmap_entry} .
                FILTER(STR(?heatmap) = "{id_entry}") .
                ?heatmap {heatmap_values_entry} ?gen_heatmap .
            }}
            """
        return [row['gen_heatmap']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, verbose)]

    def query_all_heatmap_instances(self, verbose: bool = True) -> List[str]:
        """
        Queries all heatmap instances stored in the knowledge graph.

        :param verbose: if true, logging is activated
        :return: all heatmaps stored in the knowledge graph
        """
        if verbose and self.verbose:
            print("####################################")
            print("QUERY: all heatmap instances")
            print("####################################")
        heatmap_entry = self.complete_ontology_entry('Heatmap')
        s = f"""
            SELECT ?heatmap WHERE {{
                ?heatmap a {heatmap_entry} .
            }}
            """
        return [row['heatmap']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, verbose)]

    def query_all_component_set_instances(self, verbose: bool = True) -> List[str]:
        """
        Queries all component set instances stored in the knowledge graph.

        :param verbose: if true, logging is activated
        :return: all component sets stored in the knowledge graph
        """
        if verbose and self.verbose:
            print("####################################")
            print("QUERY: all component set instances")
            print("####################################")
        component_set_entry = self.complete_ontology_entry('ComponentSet')
        set_name_entry = self.complete_ontology_entry('set_name')
        s = f"""
            SELECT ?set_name WHERE {{
                ?comp_set a {component_set_entry} .
                ?comp_set {set_name_entry} ?set_name .
            }}
            """
        return [row['set_name']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, verbose)]

    @staticmethod
    def print_res(res: List[str]) -> None:
        """
        Prints the specified query results.

        :param res: list of query results
        """
        for row in res:
            print("--> ", row)


if __name__ == '__main__':
    qt = KnowledgeGraphQueryTool()

    error_code = "E0"
    suspect_comp_name = "C45"
    fault_cond_desc = "FC0"
    comp_set_name = "S0"
    dummy_id = "1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    qt.print_res(qt.query_fault_condition_by_error_code(error_code))
    qt.print_res(qt.query_fault_condition_by_description(fault_cond_desc))
    qt.print_res(qt.query_suspect_components_by_error_code(error_code))
    qt.print_res(qt.query_suspect_component_by_name(suspect_comp_name))
    qt.print_res(qt.query_component_set_by_name(comp_set_name))
    qt.print_res(qt.query_diag_entity_instance_by_id(dummy_id))
    qt.print_res(qt.query_diag_entity_by_error_code(error_code))
    qt.print_res(qt.query_all_error_code_instances())
    qt.print_res(qt.query_all_fault_condition_instances())
    qt.print_res(qt.query_fault_condition_instance_by_code(error_code))
    qt.print_res(qt.query_error_code_instance_by_code(error_code))
    qt.print_res(qt.query_diag_association_instance_by_error_code_and_sus_comp(error_code, suspect_comp_name))
    qt.print_res(qt.query_priority_id_by_error_code_and_sus_comp(error_code, suspect_comp_name))
    qt.print_res(qt.query_generated_heatmaps_by_error_code_and_sus_comp(error_code, suspect_comp_name))
    qt.print_res(qt.query_error_codes_by_entity_id(dummy_id))
    qt.print_res(qt.query_affected_by_relations_by_suspect_component(suspect_comp_name))
    qt.print_res(qt.query_verifies_relation_by_suspect_component(suspect_comp_name))
    qt.print_res(qt.query_verifies_relations_by_component_set(comp_set_name))
    qt.print_res(qt.query_includes_relation_by_component_set(comp_set_name))
    qt.print_res(qt.query_all_component_instances())
    qt.print_res(qt.query_all_diag_entity_instances())
    qt.print_res(qt.query_all_recorded_sensor_signals())
    qt.print_res(qt.query_all_signal_classifications())
    qt.print_res(qt.query_signal_classification_by_heatmap(dummy_id))
    qt.print_res(qt.query_all_manual_inspection_instances())
    qt.print_res(qt.query_all_diag_log_instances())
    qt.print_res(qt.query_all_fault_path_instances())
    qt.print_res(qt.query_model_id_by_signal_classification_id(dummy_id))
    qt.print_res(qt.query_suspect_component_name_by_id(dummy_id))
    qt.print_res(qt.query_uncertainty_by_signal_classification_id(dummy_id))
    qt.print_res(qt.query_date_by_diag_log(dummy_id))
    qt.print_res(qt.query_resulted_in_by_fault_path(dummy_id))
    qt.print_res(qt.query_error_codes_recorded_in_diag_entity(dummy_id))
    qt.print_res(qt.query_error_codes_by_diag_log(dummy_id))
    qt.print_res(qt.query_diag_steps_by_diag_log(dummy_id))
    qt.print_res(qt.query_fault_path_by_diag_log(dummy_id))
    qt.print_res(qt.query_fault_path_description_by_id(dummy_id))
    qt.print_res(qt.query_fault_condition_description_by_id(dummy_id))
    qt.print_res(qt.query_diag_entity_by_diag_log(dummy_id))
    qt.print_res(qt.query_signal_by_sensor_signal_instance(dummy_id))
    qt.print_res(qt.query_sensor_signal_by_classification_instance(dummy_id))
    qt.print_res(qt.query_suspect_component_by_classification(dummy_id))
    qt.print_res(qt.query_reason_for_classification(dummy_id))
    qt.print_res(qt.query_led_to_for_classification(dummy_id))
    qt.print_res(qt.query_reason_for_inspection(dummy_id))
    qt.print_res(qt.query_led_to_for_inspection(dummy_id))
    qt.print_res(qt.query_prediction_by_classification(dummy_id))
    qt.print_res(qt.query_heatmap_by_classification_instance(dummy_id))
    qt.print_res(qt.query_generation_method_by_heatmap(dummy_id))
    qt.print_res(qt.query_heatmap_string_by_heatmap(dummy_id))
    qt.print_res(qt.query_all_heatmap_instances(False))
    qt.print_res(qt.query_all_component_set_instances(False))
    qt.print_res(qt.query_model_by_model_id("42qq#34"))
