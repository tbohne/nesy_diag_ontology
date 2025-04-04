#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author Tim Bohne

import uuid
from typing import List, Union

from owlready2 import *
from rdflib import Namespace, RDF

from nesy_diag_ontology.config import ONTOLOGY_PREFIX, FUSEKI_URL
from nesy_diag_ontology.connection_controller import ConnectionController
from nesy_diag_ontology.expert_knowledge_enhancer import ExpertKnowledgeEnhancer
from nesy_diag_ontology.fact import Fact
from nesy_diag_ontology.knowledge_graph_query_tool import KnowledgeGraphQueryTool


class OntologyInstanceGenerator:
    """
    Enhances the KG with diagnosis-specific instance data, i.e., it connects the diag data recorded in a particular
    diag entity, as well as sensor readings, classifications, etc. generated during the diagnostic process, with
    corresponding background knowledge stored in the KG.
    """

    def __init__(self, kg_url: str = FUSEKI_URL, verbose: bool = True) -> None:
        """
        Initializes the ontology instance generator.

        :param kg_url: URL of the knowledge graph server
        :param verbose: whether the ontology instance generator should log its actions
        """
        # establish connection to Apache Jena Fuseki server
        self.fuseki_connection = ConnectionController(namespace=ONTOLOGY_PREFIX, fuseki_url=kg_url, verbose=verbose)
        self.knowledge_graph_query_tool = KnowledgeGraphQueryTool(kg_url=kg_url, verbose=verbose)
        self.onto_namespace = Namespace(ONTOLOGY_PREFIX)
        self.verbose = verbose

    def extend_knowledge_graph_with_diag_entity_data(self, entity_id: str) -> None:
        """
        Extends the knowledge graph with semantic facts based on the present diag entity information.

        :param entity_id: ID of the diagnostic entity
        """
        diag_entity_uuid = "diag_entity_" + str(uuid.uuid4())
        fact_list = []
        diag_entity_instance = self.knowledge_graph_query_tool.query_diag_entity_instance_by_id(entity_id)
        if len(diag_entity_instance) > 0:
            if self.verbose:
                print("Diag. entity (" + entity_id + ") already part of the KG")
        else:
            fact_list = [
                Fact((diag_entity_uuid, RDF.type, self.onto_namespace["DiagEntity"].toPython())),
                Fact((diag_entity_uuid, self.onto_namespace.entity_id, entity_id), property_fact=True)
            ]
        self.fuseki_connection.extend_knowledge_graph(fact_list)

    def extend_knowledge_graph_with_diag_log(
            self, diag_date: str, error_code_instances: List[str], fault_path_instances: List[str],
            classification_instances: List[str], diag_entity_id: str
    ) -> str:
        """
        Extends the knowledge graph with semantic facts for a diagnosis log.

        :param diag_date: date of the diagnosis
        :param error_code_instances: error code instances part of the diagnosis
        :param fault_path_instances: IDs of fault path instances part of the diagnosis
        :param classification_instances: IDs of classification instances part of the diagnosis
        :param diag_entity_id: ID of the diagnostic entity the diag log is created for
        :return ID of diagnosis log
        """
        diag_log_uuid = "diag_log_" + uuid.uuid4().hex
        fact_list = [
            Fact((diag_log_uuid, RDF.type, self.onto_namespace["DiagLog"].toPython())),
            Fact((diag_log_uuid, self.onto_namespace.date, diag_date), property_fact=True)
        ]
        for error_code in error_code_instances:
            error_code_uuid = self.knowledge_graph_query_tool.query_error_code_instance_by_code(error_code)
            if len(error_code_uuid) == 1:
                fact_list.append(
                    Fact((error_code_uuid[0].split("#")[1], self.onto_namespace.appearsIn, diag_log_uuid))
                )
        for fault_path_id in fault_path_instances:
            fact_list.append(Fact((diag_log_uuid, self.onto_namespace.entails, fault_path_id)))
        for classification_id in classification_instances:
            fact_list.append(Fact((classification_id, self.onto_namespace.diagStep, diag_log_uuid)))
        fact_list.append(Fact((diag_log_uuid, self.onto_namespace.createdFor, diag_entity_id)))
        self.fuseki_connection.extend_knowledge_graph(fact_list)
        return diag_log_uuid

    def extend_knowledge_graph_with_fault_path(self, description: str, fault_cond_id: str) -> str:
        """
        Extends the knowledge graph with semantic facts for a fault path.

        :param description: fault path description
        :param fault_cond_id: UUID of fault condition
        :return: fault path UUID
        """
        fault_path_uuid = "fault_path_" + uuid.uuid4().hex
        fact_list = [
            Fact((fault_path_uuid, RDF.type, self.onto_namespace["FaultPath"].toPython())),
            Fact((fault_path_uuid, self.onto_namespace.fault_path_desc, description), property_fact=True),
            Fact((fault_cond_id, self.onto_namespace.resultedIn, fault_path_uuid))
        ]
        self.fuseki_connection.extend_knowledge_graph(fact_list)
        return fault_path_uuid

    def extend_knowledge_graph_with_signal_classification(
            self, prediction: bool, classification_reason: str, comp: str, uncertainty: float, model_id: str,
            signal_ids: Union[str, List[str]], heatmap_ids: Union[str, List[str]]
    ) -> str:
        """
        Extends the knowledge graph with semantic facts for a signal classification.

        :param prediction: prediction for the considered signal (classification result)
        :param classification_reason: either a different classification or a diagnostic association
        :param comp: classified component
        :param uncertainty: uncertainty of the prediction
        :param model_id: ID of the used classification model
        :param signal_ids: ID(s) of the classified sensor signal(s)
        :param heatmap_ids: ID(s) of the generated heatmap(s)
        :return ID of signal classification instance
        """
        # either ID of DA or ID of another classification
        assert "diag_association_" in classification_reason or "manual_inspection_" in classification_reason \
               or "signal_classification_" in classification_reason
        comp_uuid = self.knowledge_graph_query_tool.query_suspect_component_by_name(comp)[0].split("#")[1]
        classification_uuid = "signal_classification_" + uuid.uuid4().hex
        model_res = self.knowledge_graph_query_tool.query_model_by_model_id(model_id)
        if len(model_res) == 0:
            print("warning: model", model_id, "not part of kg; creating it..")
            expert_knowledge_enhancer = ExpertKnowledgeEnhancer()
            expert_knowledge_enhancer.add_model_to_knowledge_graph(42, "z-norm", "measure x", model_id, comp, [], "CNN")
            model_res = self.knowledge_graph_query_tool.query_model_by_model_id(model_id)
        model_uuid = model_res[0].split("#")[1]

        fact_list = [
            Fact((classification_uuid, RDF.type, self.onto_namespace["SignalClassification"].toPython())),
            # properties
            Fact((classification_uuid, self.onto_namespace.prediction, prediction), property_fact=True),
            Fact((classification_uuid, self.onto_namespace.uncertainty, uncertainty), property_fact=True),
            # relations
            Fact((classification_uuid, self.onto_namespace.checks, comp_uuid)),
            Fact((model_uuid, self.onto_namespace.performs, classification_uuid))
        ]
        if isinstance(signal_ids, str):
            signal_ids = [signal_ids]
        if isinstance(heatmap_ids, str):
            heatmap_ids = [heatmap_ids]
        for signal_id in signal_ids:
            fact_list.append(Fact((classification_uuid, self.onto_namespace.classifies, signal_id)))
        for heatmap_id in heatmap_ids:
            fact_list.append(Fact((classification_uuid, self.onto_namespace.produces, heatmap_id)))

        if "diag_association_" in classification_reason:
            fact_list.append(Fact((classification_reason, self.onto_namespace.ledTo, classification_uuid)))
        else:  # the reason is a classification instance (manual or signal)
            fact_list.append(Fact((classification_reason, self.onto_namespace.reasonFor, classification_uuid)))
        self.fuseki_connection.extend_knowledge_graph(fact_list)
        return classification_uuid

    def extend_knowledge_graph_with_heatmap(self, gen_method: str, heatmap: List[float]) -> str:
        """
        Extends the knowledge graph with semantic facts for a heatmap.

        :param gen_method: used heatmap generation method, e.g., GradCAM
        :param heatmap: generated heatmap (values)
        :return: heatmap ID
        """
        heatmap_uuid = "heatmap_" + uuid.uuid4().hex
        fact_list = [
            Fact((heatmap_uuid, RDF.type, self.onto_namespace["Heatmap"].toPython())),
            Fact((heatmap_uuid, self.onto_namespace.generation_method, gen_method), property_fact=True),
            Fact((heatmap_uuid, self.onto_namespace.generated_heatmap, str(heatmap)), property_fact=True)
        ]
        self.fuseki_connection.extend_knowledge_graph(fact_list)
        return heatmap_uuid

    def extend_knowledge_graph_with_sensor_signal(
            self, sensor_signal: List[float], parallel_rec_set_id: str = ""
    ) -> str:
        """
        Extends the knowledge graph with semantic facts for a sensor signal.

        :param sensor_signal: sensor signal
        :param parallel_rec_set_id: optional ID of a set of parallel recordings this signal should be assigned to
        :return: signal ID
        """
        signal_uuid = "sensor_signal_" + uuid.uuid4().hex
        fact_list = [
            Fact((signal_uuid, RDF.type, self.onto_namespace["SensorSignal"].toPython())),
            Fact((signal_uuid, self.onto_namespace.signal, str(sensor_signal)), property_fact=True)
        ]
        if parallel_rec_set_id != "":  # signal part of parallelly recorded set?
            fact_list.append(Fact((signal_uuid, self.onto_namespace.partOf, parallel_rec_set_id)))
        self.fuseki_connection.extend_knowledge_graph(fact_list)
        return signal_uuid

    def extend_knowledge_graph_with_overlays_relation(self, heatmap_id: str, signal_id: str) -> None:
        """
        Extends the knowledge graph with semantic facts for 'overlays' relations between heatmaps and signals.

        :param heatmap_id: ID of the heatmap that overlays the signal
        :param signal_id: ID of the signal
        """
        fact_list = [Fact((heatmap_id, self.onto_namespace.overlays, signal_id))]
        self.fuseki_connection.extend_knowledge_graph(fact_list)

    def extend_knowledge_graph_with_parallel_rec_signal_set(self) -> str:
        """
        Extends the knowledge graph with semantic facts for a set of parallel recorded signals.

        :return: signal set ID
        """
        signal_set_uuid = "parallel_rec_signal_set_" + uuid.uuid4().hex
        fact_list = [Fact((signal_set_uuid, RDF.type, self.onto_namespace["ParallelRecSignalSet"].toPython()))]
        self.fuseki_connection.extend_knowledge_graph(fact_list)
        return signal_set_uuid

    def extend_knowledge_graph_with_manual_inspection(
            self, prediction: bool, classification_reason: str, comp: str
    ) -> str:
        """
        Extends the knowledge graph with semantic facts for a manual inspection.

        :param prediction: prediction for the considered component (classification result)
        :param classification_reason: either a different classification or a diagnostic association
        :param comp: classified component
        :return ID of manual inspection instance
        """
        # either ID of DA or ID of another classification
        assert "diag_association_" in classification_reason or "manual_inspection_" in classification_reason \
               or "signal_classification_" in classification_reason

        comp_id = self.knowledge_graph_query_tool.query_suspect_component_by_name(comp)[0].split("#")[1]
        classification_uuid = "manual_inspection_" + uuid.uuid4().hex
        fact_list = [
            Fact((classification_uuid, RDF.type, self.onto_namespace["ManualInspection"].toPython())),
            Fact((classification_uuid, self.onto_namespace.prediction, prediction), property_fact=True),
            Fact((classification_uuid, self.onto_namespace.checks, comp_id))
        ]
        if "diag_association_" in classification_reason:
            fact_list.append(Fact((classification_reason, self.onto_namespace.ledTo, classification_uuid)))
        else:  # the reason is a classification instance (manual or signal)
            fact_list.append(Fact((classification_reason, self.onto_namespace.reasonFor, classification_uuid)))
        self.fuseki_connection.extend_knowledge_graph(fact_list)
        return classification_uuid


if __name__ == '__main__':
    instance_gen = OntologyInstanceGenerator()
    instance_gen.extend_knowledge_graph_with_diag_entity_data("1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    # create some test instances
    causing_error_code = "E0"
    fault_cond_uuid = instance_gen.knowledge_graph_query_tool.query_fault_condition_instance_by_code(
        causing_error_code
    )[0].split("#")[1]
    list_of_error_codes = ["E0", "E1", "E2", "E3"]
    fault_path = "C45 -> C1 -> C2"
    signal = [13.3, 13.6, 14.6, 16.7, 8.5, 9.7, 5.5, 3.6, 12.5, 12.7]
    test_heatmap = [0.4, 0.3, 0.7, 0.7, 0.8, 0.9, 0.3, 0.2]
    sus_comp = "C45"
    manual_sus_comp = "C1"
    test_signal_id = instance_gen.extend_knowledge_graph_with_sensor_signal(signal)
    test_heatmap_id = instance_gen.extend_knowledge_graph_with_heatmap("GradCAM", test_heatmap)
    test_fault_path_id = instance_gen.extend_knowledge_graph_with_fault_path(fault_path, fault_cond_uuid)

    test_classification_instances = [
        instance_gen.extend_knowledge_graph_with_signal_classification(
            True, "diag_association_3592495", sus_comp, 0.45, "42qq#34", test_signal_id, test_heatmap_id
        ),
        instance_gen.extend_knowledge_graph_with_signal_classification(
            True, "signal_classification_3543595", sus_comp, 0.85, "42qq#34", test_signal_id, test_heatmap_id
        ),
        instance_gen.extend_knowledge_graph_with_manual_inspection(
            False, "signal_classification_45395859345", manual_sus_comp
        )
    ]
    log_uuid = instance_gen.extend_knowledge_graph_with_diag_log(
        "01.02.2024", list_of_error_codes, [test_fault_path_id], test_classification_instances,
        "diag_subject_39458359345382458"
    )
