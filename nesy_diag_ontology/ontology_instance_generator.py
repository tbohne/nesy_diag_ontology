#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author Tim Bohne

import uuid
from typing import List

from owlready2 import *
from rdflib import Namespace, RDF

from nesy_diag_ontology.config import ONTOLOGY_PREFIX, FUSEKI_URL
from nesy_diag_ontology.connection_controller import ConnectionController
from nesy_diag_ontology.fact import Fact
from nesy_diag_ontology.knowledge_graph_query_tool import KnowledgeGraphQueryTool


class OntologyInstanceGenerator:
    """
    Enhances the KG with diagnosis-specific instance data, i.e., it connects the diag data recorded in a particular
    diag subject, as well as sensor readings, classifications, etc. generated during the diagnostic process, with
    corresponding background knowledge stored in the KG.
    """

    def __init__(self, kg_url: str = FUSEKI_URL, verbose: bool = True) -> None:
        """
        Initializes the ontology instance generator.

        :param kg_url: URL for the knowledge graph server
        :param verbose: whether the ontology instance generator should log its actions
        """
        # establish connection to Apache Jena Fuseki server
        self.fuseki_connection = ConnectionController(namespace=ONTOLOGY_PREFIX, fuseki_url=kg_url, verbose=verbose)
        self.knowledge_graph_query_tool = KnowledgeGraphQueryTool(kg_url=kg_url, verbose=verbose)
        self.onto_namespace = Namespace(ONTOLOGY_PREFIX)
        self.verbose = verbose

    def extend_knowledge_graph_with_diag_subject_data(self, subject_id: str) -> None:
        """
        Extends the knowledge graph with semantic facts based on the present diag subject information.

        :param subject_id: ID of the diagnostic subject
        """
        diag_subject_uuid = "diag_subject_" + str(uuid.uuid4())
        fact_list = []
        diag_subject_instance = self.knowledge_graph_query_tool.query_diag_subject_instance_by_id(subject_id)
        if len(diag_subject_instance) > 0:
            if self.verbose:
                print("Diag. subject (" + subject_id + ") already part of the KG")
        else:
            fact_list = [
                Fact((diag_subject_uuid, RDF.type, self.onto_namespace["DiagSubject"].toPython())),
                Fact((diag_subject_uuid, self.onto_namespace.subject_id, subject_id), property_fact=True)
            ]
        self.fuseki_connection.extend_knowledge_graph(fact_list)

    def extend_knowledge_graph_with_diag_log(
            self, diag_date: str, error_code_instances: List[str], fault_path_instances: List[str],
            classification_instances: List[str], diag_subject_id: str
    ) -> str:
        """
        Extends the knowledge graph with semantic facts for a diagnosis log.

        :param diag_date: date of the diagnosis
        :param error_code_instances: error code instances part of the diagnosis
        :param fault_path_instances: IDs of fault path instances part of the diagnosis
        :param classification_instances: IDs of classification instances part of the diagnosis
        :param diag_subject_id: ID of the diagnostic subject the diag log is created for
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
        fact_list.append(Fact((diag_log_uuid, self.onto_namespace.createdFor, diag_subject_id)))
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

    def extend_knowledge_graph_with_signal_classification(self, prediction: bool, classification_reason: str,
                                                          comp: str, uncertainty: float, model_id: str,
                                                          ts_id: str, heatmap_id: str) -> str:
        """
        Extends the knowledge graph with semantic facts for a signal classification.

        :param prediction: prediction for the considered signal (classification result)
        :param classification_reason: either a different classification or a diagnostic association
        :param comp: classified component
        :param uncertainty: uncertainty of the prediction
        :param model_id: ID of the used classification model
        :param ts_id: ID of the classified time series
        :param heatmap_id: ID of the generated heatmap
        :return ID of signal classification instance
        """
        # either ID of DA or ID of another classification
        assert "diag_association_" in classification_reason or "manual_inspection_" in classification_reason \
               or "signal_classification_" in classification_reason
        comp_id = self.knowledge_graph_query_tool.query_suspect_component_by_name(comp)[0].split("#")[1]

        classification_uuid = "signal_classification_" + uuid.uuid4().hex
        fact_list = [
            Fact((classification_uuid, RDF.type, self.onto_namespace["SignalClassification"].toPython())),
            # properties
            Fact((classification_uuid, self.onto_namespace.prediction, prediction), property_fact=True),
            Fact((classification_uuid, self.onto_namespace.uncertainty, uncertainty), property_fact=True),
            Fact((classification_uuid, self.onto_namespace.model_id, model_id), property_fact=True),
            # relations
            Fact((classification_uuid, self.onto_namespace.checks, comp_id)),
            Fact((classification_uuid, self.onto_namespace.classifies, ts_id)),
            Fact((classification_uuid, self.onto_namespace.produces, heatmap_id))
        ]
        if "diag_association_" in classification_reason:
            fact_list.append(Fact((classification_reason, self.onto_namespace.ledTo, classification_uuid)))
        else:  # the reason is a classification instance (manual or osci)
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

    def extend_knowledge_graph_with_time_series(self, time_series: List[float]) -> str:
        """
        Extends the knowledge graph with semantic facts for a time series.

        :param time_series: time series, i.e., the signal
        :return: time series ID
        """
        osci_uuid = "time_series_" + uuid.uuid4().hex
        fact_list = [
            Fact((osci_uuid, RDF.type, self.onto_namespace["TimeSeries"].toPython())),
            Fact((osci_uuid, self.onto_namespace.time_series, str(time_series)), property_fact=True)
        ]
        self.fuseki_connection.extend_knowledge_graph(fact_list)
        return osci_uuid

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
        else:  # the reason is a classification instance (manual or osci)
            fact_list.append(Fact((classification_reason, self.onto_namespace.reasonFor, classification_uuid)))
        self.fuseki_connection.extend_knowledge_graph(fact_list)
        return classification_uuid


if __name__ == '__main__':
    instance_gen = OntologyInstanceGenerator()
    instance_gen.extend_knowledge_graph_with_diag_subject_data("1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    # create some test instances
    causing_error_code = "E0"
    fault_cond_uuid = instance_gen.knowledge_graph_query_tool.query_fault_condition_instance_by_code(
        causing_error_code)[0].split("#")[1]
    list_of_error_codes = ["E0", "E1", "E2", "E3"]
    fault_path = "C45 -> C1 -> C2"
    ts = [13.3, 13.6, 14.6, 16.7, 8.5, 9.7, 5.5, 3.6, 12.5, 12.7]
    test_heatmap = [0.4, 0.3, 0.7, 0.7, 0.8, 0.9, 0.3, 0.2]
    sus_comp = "C45"
    manual_sus_comp = "C1"
    test_ts_id = instance_gen.extend_knowledge_graph_with_time_series(ts)
    test_heatmap_id = instance_gen.extend_knowledge_graph_with_heatmap("GradCAM", test_heatmap)
    test_fault_path_id = instance_gen.extend_knowledge_graph_with_fault_path(fault_path, fault_cond_uuid)

    test_classification_instances = [
        instance_gen.extend_knowledge_graph_with_signal_classification(
            True, "diag_association_3592495", sus_comp, 0.45, "test_model_id", test_ts_id, test_heatmap_id
        ),
        instance_gen.extend_knowledge_graph_with_signal_classification(
            True, "signal_classification_3543595", sus_comp, 0.85, "test_model_id", test_ts_id, test_heatmap_id
        ),
        instance_gen.extend_knowledge_graph_with_manual_inspection(
            False, "signal_classification_45395859345", manual_sus_comp
        )
    ]
    log_uuid = instance_gen.extend_knowledge_graph_with_diag_log(
        "01.02.2024", list_of_error_codes, [test_fault_path_id], test_classification_instances,
        "diag_subject_39458359345382458"
    )
