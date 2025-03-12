#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author Tim Bohne

import uuid
from typing import List, Tuple

from rdflib import Namespace, RDF

from nesy_diag_ontology.component_knowledge import ComponentKnowledge
from nesy_diag_ontology.component_set_knowledge import ComponentSetKnowledge
from nesy_diag_ontology.config import ONTOLOGY_PREFIX, FUSEKI_URL
from nesy_diag_ontology.connection_controller import ConnectionController
from nesy_diag_ontology.error_code_knowledge import ErrorCodeKnowledge
from nesy_diag_ontology.fact import Fact
from nesy_diag_ontology.knowledge_graph_query_tool import KnowledgeGraphQueryTool


class ExpertKnowledgeEnhancer:
    """
    Extends the knowledge graph hosted by the 'Fuseki' server with diag-entity-agnostic expert knowledge.

    The acquisition of expert knowledge is accomplished via a web interface (collaborative knowledge acquisition
    component) through which the knowledge is entered, stored in the Resource Description Framework (RDF) format,
    and hosted on an 'Apache Jena Fuseki' server.

    This class deals with semantic fact generation for the diag-entity-agnostic expert knowledge.
    """

    def __init__(self, kg_url: str = FUSEKI_URL, verbose: bool = True) -> None:
        """
        Initializes the expert knowledge enhancer.

        :param kg_url: URL of the knowledge graph server
        :param verbose: whether the expert knowledge enhancer should log its actions
        """
        # establish connection to 'Apache Jena Fuseki' server
        self.fuseki_connection = ConnectionController(namespace=ONTOLOGY_PREFIX, fuseki_url=kg_url, verbose=verbose)
        self.onto_namespace = Namespace(ONTOLOGY_PREFIX)
        self.knowledge_graph_query_tool = KnowledgeGraphQueryTool(verbose=verbose)
        self.verbose = verbose

    def generate_condition_description_fact(self, fc_uuid: str, fault_cond: str, prop: bool) -> Fact:
        """
        Generates a `condition_desc` fact (RDF) based on the provided properties.

        :param fc_uuid: UUID of the fault condition instance to generate fact for
        :param fault_cond: the fault condition description
        :param prop: determines whether it's a property fact
        :return: generated fact
        """
        return Fact((fc_uuid, self.onto_namespace.condition_desc, fault_cond), property_fact=prop)

    def generate_generated_heatmap_fact(self, heatmap_uuid: str, heatmap: str, prop: bool) -> Fact:
        """
        Generates a `generated_heatmap` fact (RDF) based on the provided properties.

        :param heatmap_uuid: UUID of the heatmap to generate fact for
        :param heatmap: heatmap string
        :param prop: determines whether it's a property fact
        :return: generated fact
        """
        return Fact((heatmap_uuid, self.onto_namespace.generated_heatmap, heatmap), property_fact=prop)

    def generate_signal_fact(self, signal_uuid: str, signal: str, prop: bool) -> Fact:
        """
        Generates a `signal` fact (RDF) based on the provided properties.

        :param signal_uuid: UUID of the `SensorSignal` to generate fact for
        :param signal: sensor signal string
        :param prop: determines whether it's a property fact
        :return: generated fact
        """
        return Fact((signal_uuid, self.onto_namespace.signal, signal), property_fact=prop)

    def generate_heatmap_generation_method_fact(self, heatmap_uuid: str, gen_method: str, prop: bool) -> Fact:
        """
        Generates a `generation_method` fact (RDF) based on the provided properties.

        :param heatmap_uuid: UUID of the heatmap to generate fact for
        :param gen_method: heatmap generation method (e.g., tf-keras-gradcam)
        :param prop: determines whether it's a property fact
        :return: generated fact
        """
        return Fact((heatmap_uuid, self.onto_namespace.generation_method, gen_method), property_fact=prop)

    def generate_has_association_fact(self, error_code_uuid: str, da_uuid: str, prop: bool) -> Fact:
        """
        Generates a `hasAssociation` fact (RDF) based on the provided properties.

        :param error_code_uuid: UUID of the error code to generate fact for
        :param da_uuid: UUID of the diagnostic association to generate fact for
        :param prop: determines whether it's a property fact
        :return: generated fact
        """
        return Fact((error_code_uuid, self.onto_namespace.hasAssociation, da_uuid), property_fact=prop)

    def generate_points_to_fact(self, da_uuid: str, comp_uuid: str, prop: bool) -> Fact:
        """
        Generates a `pointsTo` fact (RDF) based on the provided properties.

        :param da_uuid: UUID of the diagnostic association to generate fact for
        :param comp_uuid: UUID of the suspect component to generate fact for
        :param prop: determines whether it's a property fact
        :return: generated fact
        """
        return Fact((da_uuid, self.onto_namespace.pointsTo, comp_uuid), property_fact=prop)

    def generate_diagnostic_association_fact(self, da_uuid: str, prop: bool) -> Fact:
        """
        Generates a `DiagnosticAssociation` fact (RDF) based on the provided properties.

        :param da_uuid: UUID of the diagnostic association to generate fact for
        :param prop: determines whether it's a property fact
        :return: generated fact
        """
        return Fact(
            (da_uuid, "http://www.w3.org/1999/02/22-rdf-syntax-ns#type", self.onto_namespace.DiagnosticAssociation),
            property_fact=prop
        )

    def generate_heatmap_fact(self, heatmap_uuid: str, prop: bool) -> Fact:
        """
        Generates a `Heatmap` fact (RDF) based on the provided properties.

        :param heatmap_uuid: UUID of the heatmap to generate fact for
        :param prop: determines whether it's a property fact
        :return: generated fact
        """
        return Fact(
            (heatmap_uuid, "http://www.w3.org/1999/02/22-rdf-syntax-ns#type", self.onto_namespace.Heatmap),
            property_fact=prop
        )

    def generate_sensor_signal_fact(self, signal_uuid: str, prop: bool) -> Fact:
        """
        Generates a `SensorSignal` fact (RDF) based on the provided properties.

        :param signal_uuid: UUID of the sensor signal to generate fact for
        :param prop: determines whether it's a property fact
        :return: generated fact
        """
        return Fact(
            (signal_uuid, "http://www.w3.org/1999/02/22-rdf-syntax-ns#type", self.onto_namespace.SensorSignal),
            property_fact=prop
        )

    def generate_produces_fact(self, classification_uuid: str, heatmap_uuid: str, prop: bool) -> Fact:
        """
        Generates a `produces` fact (RDF) based on the provided properties.

        :param classification_uuid: UUID of the signal classification to generate fact for
        :param heatmap_uuid: UUID of the heatmap to generate fact for
        :param prop: determines whether it's a property fact
        :return: generated fact
        """
        return Fact((classification_uuid, self.onto_namespace.produces, heatmap_uuid), property_fact=prop)

    def generate_classifies_fact(self, signal_classification_id: str, signal_id: str, prop: bool) -> Fact:
        """
        Generates a `classifies` fact (RDF) based on the provided properties.

        :param signal_classification_id: UUID of the signal classification to generate fact for
        :param signal_id: UUID of the sensor signal to generate fact for
        :param prop: determines whether it's a property fact
        :return: generated fact
        """
        return Fact((signal_classification_id, self.onto_namespace.classifies, signal_id), property_fact=prop)

    def generate_includes_fact(self, component_set_uuid: str, comp_uuid: str, prop: bool) -> Fact:
        """
        Generates an `includes` fact (RDF) based on the provided properties.

        :param component_set_uuid: UUID of the component set to generate fact for
        :param comp_uuid: UUID of the suspect component to generate fact for
        :param prop: determines whether it's a property fact
        :return: generated fact
        """
        return Fact((component_set_uuid, self.onto_namespace.includes, comp_uuid), property_fact=prop)

    def generate_verifies_fact(self, comp_uuid: str, comp_set_uuid: str, prop: bool) -> Fact:
        """
        Generates a `verifies` fact (RDF) based on the provided properties.

        :param comp_uuid: UUID of the component to generate fact for
        :param comp_set_uuid: UUID of the component set to generate fact for
        :param prop: determines whether it's a property fact
        :return: generated fact
        """
        return Fact((comp_uuid, self.onto_namespace.verifies, comp_set_uuid), property_fact=prop)

    def generate_affected_by_fact(self, comp_uuid: str, comp_name: str, prop: bool) -> Fact:
        """
        Generates an `affected_by` fact (RDF) based on the provided properties.

        :param comp_uuid: UUID of the component to generate fact for
        :param comp_name: name of the affecting component
        :param prop: determines whether it's a property fact
        :return: generated fact
        """
        return Fact((comp_uuid, self.onto_namespace.affected_by, comp_name), property_fact=prop)

    def generate_error_code_facts(self, error_code_knowledge: ErrorCodeKnowledge) -> Tuple[str, List[Fact]]:
        """
        Generates the error-code-related facts to be entered into the knowledge graph.

        :param error_code_knowledge: parsed error code knowledge
        :return: (error code UUID, generated fact list)
        """
        error_code_uuid = "error_code_" + uuid.uuid4().hex
        fact_list = []
        # check whether error code to be added is already part of the KG
        error_code_instance = self.knowledge_graph_query_tool.query_error_code_instance_by_code(
            error_code_knowledge.error_code
        )
        if len(error_code_instance) > 0:
            if self.verbose:
                print("Specified error code (" + error_code_knowledge.error_code + ") already present in KG")
            error_code_uuid = error_code_instance[0].split("#")[1]
        else:
            fact_list = [
                Fact((error_code_uuid, RDF.type, self.onto_namespace["ErrorCode"].toPython())),
                Fact((error_code_uuid, self.onto_namespace.code, error_code_knowledge.error_code), property_fact=True)
            ]
        return error_code_uuid, fact_list

    def generate_fault_cond_facts(
            self, error_code_uuid: str, error_code_knowledge: ErrorCodeKnowledge
    ) -> Tuple[str, List[Fact]]:
        """
        Generates the `FaultCondition`-related facts to be entered into the knowledge graph.

        :param error_code_uuid: error code UUID used to draw the connection to the error code
        :param error_code_knowledge: parsed error code knowledge
        :return: (fault condition UUID, generated fact list)
        """
        fault_cond_uuid = "fault_cond_" + uuid.uuid4().hex
        fault_cond = error_code_knowledge.fault_condition
        fact_list = []
        # check whether fault condition to be added is already part of the KG
        fault_cond_instance = self.knowledge_graph_query_tool.query_fault_condition_by_description(fault_cond)
        if len(fault_cond_instance) > 0:
            if self.verbose:
                print("Specified fault condition (" + fault_cond + ") already present in KG, updating description")
            fault_cond_uuid = fault_cond_instance[0].split("#")[1]
            fact_list.append(
                Fact((fault_cond_uuid, self.onto_namespace.condition_desc, fault_cond), property_fact=True)
            )
        else:
            fact_list = [
                Fact((fault_cond_uuid, RDF.type, self.onto_namespace["FaultCondition"].toPython())),
                Fact((fault_cond_uuid, self.onto_namespace.condition_desc, fault_cond), property_fact=True),
                Fact((error_code_uuid, self.onto_namespace.represents, fault_cond_uuid))
            ]
        return fault_cond_uuid, fact_list

    def generate_facts_to_connect_components_and_error_code(
            self, error_code_uuid: str, error_code_knowledge: ErrorCodeKnowledge
    ) -> List[Fact]:
        """
        Generates the facts that connect the present error code with associated suspect components, i.e., generating
        the diagnostic associations.

        :param error_code_uuid: error code UUID used to draw the connection to the error code
        :param error_code_knowledge: parsed error code knowledge
        :return: generated fact list
        """
        fact_list = []
        # there can be more than one suspect component instance per error code
        for idx, comp in enumerate(error_code_knowledge.suspect_components):
            component_by_name = self.knowledge_graph_query_tool.query_suspect_component_by_name(comp)
            # ensure that all the suspect components considered here are already part of the KG
            assert len(component_by_name) == 1
            comp_uuid = component_by_name[0].split("#")[1]
            # making sure that there is only one diagnostic association, i.e., one priority ID, between any pair
            # of error code and suspect component
            diag_association = self.knowledge_graph_query_tool.query_priority_id_by_error_code_and_sus_comp(
                error_code_knowledge.error_code, comp
            )
            if len(diag_association) > 0:
                print(
                    "Diagnostic association between", error_code_knowledge.error_code,
                    "and", comp, "already defined in KG"
                )
            else:
                # TODO: shouldn't the diagnostic association be deletable, too?
                # creating diagnostic association between `ErrorCode` and `SuspectComponent`
                diag_association_uuid = "diag_association_" + uuid.uuid4().hex
                fact_list.append(
                    Fact((diag_association_uuid, RDF.type, self.onto_namespace["DiagnosticAssociation"].toPython()))
                )
                fact_list.append(Fact((error_code_uuid, self.onto_namespace.hasAssociation, diag_association_uuid)))
                fact_list.append(
                    Fact((diag_association_uuid, self.onto_namespace.priority_id, idx), property_fact=True)
                )
                fact_list.append(Fact((diag_association_uuid, self.onto_namespace.pointsTo, comp_uuid)))
        return fact_list

    def generate_suspect_component_facts(self, comp_knowledge_list: List[ComponentKnowledge]) -> List[Fact]:
        """
        Generates the `SuspectComponent`-related facts to be entered into the knowledge graph.

        :param comp_knowledge_list: list of parsed suspect components
        :return: generated fact list
        """
        fact_list = []
        for comp_knowledge in comp_knowledge_list:
            comp_name = comp_knowledge.suspect_component
            comp_uuid = "comp_" + uuid.uuid4().hex
            # check whether component to be added is already part of the KG
            comp_instance = self.knowledge_graph_query_tool.query_suspect_component_by_name(comp_name)
            if len(comp_instance) > 0:
                if self.verbose:
                    print("Specified component (" + comp_name + ") already present in KG")
                comp_uuid = comp_instance[0].split("#")[1]
            else:
                fact_list.append(Fact((comp_uuid, RDF.type, self.onto_namespace["SuspectComponent"].toPython())))
                fact_list.append(Fact((comp_uuid, self.onto_namespace.component_name, comp_name), property_fact=True))
            for comp in comp_knowledge.affected_by:
                # all components in the affected_by list should be defined in the KG, i.e., should have ex. 1 result
                assert len(self.knowledge_graph_query_tool.query_suspect_component_by_name(comp)) == 1
                fact_list.append(Fact((comp_uuid, self.onto_namespace.affected_by, comp), property_fact=True))
        return fact_list

    def generate_component_set_facts(self, comp_set_knowledge: ComponentSetKnowledge) -> List[Fact]:
        """
        Generates component set facts to be entered into the knowledge graph.

        :param comp_set_knowledge: parsed component set knowledge
        :return: generated fact list
        """
        fact_list = []
        comp_set_name = comp_set_knowledge.component_set
        comp_set_uuid = "component_set_" + uuid.uuid4().hex
        # check whether component set to be added is already part of the KG
        comp_set_instance = self.knowledge_graph_query_tool.query_component_set_by_name(comp_set_name)
        if len(comp_set_instance) > 0:
            if self.verbose:
                print("Specified component set (" + comp_set_name + ") already present in KG")
            comp_set_uuid = comp_set_instance[0].split("#")[1]
        else:
            fact_list = [
                Fact((comp_set_uuid, RDF.type, self.onto_namespace["ComponentSet"].toPython())),
                Fact((comp_set_uuid, self.onto_namespace.set_name, comp_set_name), property_fact=True)
            ]
        for containing_comp in comp_set_knowledge.includes:
            # relate knowledge to already existing facts
            sus_comp = self.knowledge_graph_query_tool.query_suspect_component_by_name(containing_comp)
            # should already be defined in KG
            assert len(sus_comp) == 1
            comp_uuid = sus_comp[0].split("#")[1]
            fact_list.append(Fact((comp_set_uuid, self.onto_namespace.includes, comp_uuid)))

        assert isinstance(comp_set_knowledge.verified_by, list)
        for verifying_comp in comp_set_knowledge.verified_by:
            # relate knowledge to already existing facts
            verifying_comp_instance = self.knowledge_graph_query_tool.query_suspect_component_by_name(verifying_comp)
            assert len(verifying_comp_instance) == 1
            verifying_comp_uuid = verifying_comp_instance[0].split("#")[1]
            fact_list.append(Fact((verifying_comp_uuid, self.onto_namespace.verifies, comp_set_uuid)))

        return fact_list

    def generate_error_code_related_facts(self, error_code_knowledge: ErrorCodeKnowledge) -> List[Fact]:
        """
        Generates all facts obtained from the error code form / template to be entered into the knowledge graph.

        :param error_code_knowledge: parsed error code knowledge
        :return: generated fact list
        """
        error_code_uuid, error_code_facts = self.generate_error_code_facts(error_code_knowledge)
        fault_cond_uuid, fault_cond_facts = self.generate_fault_cond_facts(error_code_uuid, error_code_knowledge)
        diag_association_facts = self.generate_facts_to_connect_components_and_error_code(
            error_code_uuid, error_code_knowledge
        )
        fact_list = error_code_facts + fault_cond_facts + diag_association_facts
        return fact_list

    def add_error_code_to_knowledge_graph(
            self, error_code: str, fault_condition: str, suspect_components: List[str]
    ) -> None:
        """
        Adds an error code instance with the given properties to the knowledge graph.

        :param error_code: error code to be considered
        :param fault_condition: fault condition associated with the considered error code
        :param suspect_components: components that should be checked when this error code occurs
                                   (order defines suggestion priority)
        """
        assert isinstance(error_code, str)
        assert isinstance(fault_condition, str)
        assert isinstance(suspect_components, list)

        new_error_code_knowledge = ErrorCodeKnowledge(
            error_code=error_code, fault_condition=fault_condition, suspect_components=suspect_components
        )
        fact_list = self.generate_error_code_related_facts(new_error_code_knowledge)
        self.fuseki_connection.extend_knowledge_graph(fact_list)

    def add_component_to_knowledge_graph(self, suspect_component: str, affected_by: List[str]) -> None:
        """
        Adds a component instance with the given properties to the knowledge graph.

        :param suspect_component: component to be checked
        :param affected_by: list of components whose misbehavior could affect the correct functioning of the component
                            under consideration
        """
        assert isinstance(suspect_component, str)
        assert isinstance(affected_by, list)

        new_component_knowledge = ComponentKnowledge(suspect_component=suspect_component, affected_by=affected_by)
        fact_list = self.generate_suspect_component_facts([new_component_knowledge])
        self.fuseki_connection.extend_knowledge_graph(fact_list)

    def add_component_set_to_knowledge_graph(
            self, component_set: str, includes: List[str], verified_by: List[str]
    ) -> None:
        """
        Adds a component set instance to the knowledge graph.

        :param component_set: component set to be represented
        :param includes: suspect components assigned to this component set
        :param verified_by: component set can be verified by checking this suspect component
        """
        assert isinstance(component_set, str)
        assert isinstance(includes, list)
        assert isinstance(verified_by, list)

        new_comp_set_knowledge = ComponentSetKnowledge(
            component_set=component_set, includes=includes, verified_by=verified_by
        )
        fact_list = self.generate_component_set_facts(new_comp_set_knowledge)
        self.fuseki_connection.extend_knowledge_graph(fact_list)


if __name__ == '__main__':
    expert_knowledge_enhancer = ExpertKnowledgeEnhancer()
