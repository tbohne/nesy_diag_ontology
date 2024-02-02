#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author Tim Bohne

import argparse

from termcolor import colored

from knowledge_graph_query_tool import KnowledgeGraphQueryTool


def knowledge_snapshot_error_code_perspective() -> None:
    """
    Presents a snapshot of the knowledge currently stored in the KG from an error-code-centric perspective.
    """
    print("###########################################################################")
    print("KNOWLEDGE SNAPSHOT - ERROR CODE PERSPECTIVE")
    print("###########################################################################\n")
    for error_code in qt.query_all_error_code_instances(False):
        print(colored(error_code, "yellow", "on_grey", ["bold"]))
        print(colored("\t- fault condition:", "blue", "on_grey", ["bold"]),
              qt.query_fault_condition_by_error_code(error_code, False)[0])
        print(colored("\t- diag subject occurrences:", "blue", "on_grey", ["bold"]))
        diag_subject_occurrences = qt.query_diag_subject_by_error_code(error_code, False)
        for diag_subject_occ in diag_subject_occurrences:
            print("\t\t-", diag_subject_occ)

        print(colored("\t- ordered suspect components:", "blue", "on_grey", ["bold"]))

        suspect_components = qt.query_suspect_components_by_error_code(error_code, False)
        ordered_sus_comp = {int(qt.query_priority_id_by_error_code_and_sus_comp(error_code, comp, False)[0]): comp for
                            comp
                            in suspect_components}
        for i in range(len(suspect_components)):
            print(colored("\t\t- " + ordered_sus_comp[i], "yellow", "on_grey", ["bold"]))
            print(colored("\t\t\taffected by:", "blue", "on_grey", ["bold"]),
                  qt.query_affected_by_relations_by_suspect_component(ordered_sus_comp[i], False))
            print(colored("\t\t\tverifies:", "blue", "on_grey", ["bold"]),
                  qt.query_verifies_relation_by_suspect_component(ordered_sus_comp[i], False))
        print()
    print("\n----------------------------------------------------------------------\n")


def knowledge_snapshot_component_set_perspective() -> None:
    """
    Presents a snapshot of the knowledge currently stored in the KG from a component-set-centric perspective.
    """
    print("###########################################################################")
    print("KNOWLEDGE SNAPSHOT - COMPONENT SET PERSPECTIVE")
    print("###########################################################################\n")
    for comp_set in qt.query_all_component_set_instances(False):
        print(colored(comp_set, "yellow", "on_grey", ["bold"]))
        print(colored("\t- verified by:", "blue", "on_grey", ["bold"]),
              qt.query_verifies_relations_by_component_set(comp_set, False))
        print(colored("\t- includes:", "blue", "on_grey", ["bold"]),
              qt.query_includes_relation_by_component_set(comp_set, False))
    print("\n----------------------------------------------------------------------\n")


def knowledge_snapshot_component_perspective() -> None:
    """
    Presents a snapshot of the knowledge currently stored in the KG from a component-centric perspective.
    """
    print("###########################################################################")
    print("KNOWLEDGE SNAPSHOT - COMPONENT PERSPECTIVE")
    print("###########################################################################\n")
    for comp in qt.query_all_component_instances(False):
        print(colored(comp, "yellow", "on_grey", ["bold"]))
        print(colored("\t- affected by:", "blue", "on_grey", ["bold"]),
              qt.query_affected_by_relations_by_suspect_component(comp, False))
        print(colored("\t- verifies:", "blue", "on_grey", ["bold"]),
              qt.query_verifies_relation_by_suspect_component(comp, False))
    print("\n----------------------------------------------------------------------\n")


def knowledge_snapshot_signal_perspective() -> None:
    """
    Presents a snapshot of the knowledge currently stored in the KG regarding time series signals.
    """
    print("###########################################################################")
    print("KNOWLEDGE SNAPSHOT - TIME SERIES SIGNAL PERSPECTIVE")
    print("###########################################################################\n")
    for signal in qt.query_all_recorded_time_series(False):
        signal_id = signal.split("#")[1]
        print(colored("signal: " + signal.split("#")[1], "yellow", "on_grey", ["bold"]))
        time_series = qt.query_time_series_by_ts_instance(signal_id, False)[0]
        print(colored("\t- time series excerpt:", "blue", "on_grey", ["bold"]), time_series[:50], "...")
    print("\n----------------------------------------------------------------------\n")


def knowledge_snapshot_signal_classification_perspective() -> None:
    """
    Presents a snapshot of the knowledge currently stored in the KG regarding signal classifications.
    """
    print("###########################################################################")
    print("KNOWLEDGE SNAPSHOT - SIGNAL CLASSIFICATION PERSPECTIVE")
    print("###########################################################################\n")
    for signal_classification in qt.query_all_signal_classifications(False):
        signal_classification_id = signal_classification.split("#")[1]
        print(colored(signal_classification_id, "yellow", "on_grey", ["bold"]))
        print(colored("\t- model id:", "blue", "on_grey", ["bold"]),
              qt.query_model_id_by_signal_classification_id(signal_classification_id, False)[0])
        print(colored("\t- uncertainty:", "blue", "on_grey", ["bold"]),
              qt.query_uncertainty_by_signal_classification_id(signal_classification_id, False)[0])
        time_series_instance = qt.query_time_series_by_classification_instance(signal_classification_id, False)
        print(colored("\t- classifies:", "blue", "on_grey", ["bold"]),
              time_series_instance[0].split("#")[1] if len(time_series_instance) > 0 else "")

        heatmap_instance = qt.query_heatmap_by_classification_instance(signal_classification_id, False)
        heatmap_id = heatmap_instance[0].split("#")[1] if len(heatmap_instance) > 0 else ""
        if len(heatmap_id) > 0:
            print(colored("\t- produces:", "blue", "on_grey", ["bold"]), heatmap_id)
            print(colored("\t\t- generation_method:", "blue", "on_grey", ["bold"]),
                  qt.query_generation_method_by_heatmap(heatmap_id, False)[0])
            print(colored("\t\t- generated heatmap:", "blue", "on_grey", ["bold"]),
                  qt.query_heatmap_string_by_heatmap(heatmap_id, False)[0])

        suspect_comp_instance = qt.query_suspect_component_by_classification(signal_classification_id, False)
        suspect_comp_id = suspect_comp_instance[0].split("#")[1] if len(suspect_comp_instance) > 0 else ""
        print(colored("\t- checks:", "blue", "on_grey", ["bold"]), suspect_comp_id)

        reason_for_instance = qt.query_reason_for_classification(signal_classification_id, False)
        reason_for_id = reason_for_instance[0].split("#")[1] if len(reason_for_instance) > 0 else ""
        if reason_for_id == "":
            reason_for_instance = qt.query_led_to_for_classification(signal_classification_id, False)
            reason_for_id = reason_for_instance[0].split("#")[1] if len(reason_for_instance) > 0 else ""
        print(colored("\t- reason for classification:", "blue", "on_grey", ["bold"]), reason_for_id)
        prediction = qt.query_prediction_by_classification(signal_classification_id, False)
        print(colored("\t- prediction:", "blue", "on_grey", ["bold"]), prediction[0] if len(prediction) > 0 else "")
    print("\n----------------------------------------------------------------------\n")


def knowledge_snapshot_manual_inspection_perspective() -> None:
    """
    Presents a snapshot of the knowledge currently stored in the KG regarding manual inspections.
    """
    print("###########################################################################")
    print("KNOWLEDGE SNAPSHOT - MANUAL INSPECTION PERSPECTIVE")
    print("###########################################################################\n")
    for manual_inspection in qt.query_all_manual_inspection_instances(False):
        manual_inspection_id = manual_inspection.split("#")[1]
        print(colored(manual_inspection_id, "yellow", "on_grey", ["bold"]))
        suspect_comp_instance = qt.query_suspect_component_by_classification(manual_inspection_id, False)
        suspect_comp_id = suspect_comp_instance[0].split("#")[1] if len(suspect_comp_instance) > 0 else ""
        print(colored("\t- checks:", "blue", "on_grey", ["bold"]), suspect_comp_id)
        reason_for_instance = qt.query_reason_for_inspection(manual_inspection_id, False)
        reason_for_id = reason_for_instance[0].split("#")[1] if len(reason_for_instance) > 0 else ""
        if reason_for_id == "":
            reason_for_instance = qt.query_led_to_for_inspection(manual_inspection_id, False)
            reason_for_id = reason_for_instance[0].split("#")[1] if len(reason_for_instance) > 0 else ""
        print(colored("\t- reason for inspection:", "blue", "on_grey", ["bold"]), reason_for_id)
        prediction = qt.query_prediction_by_classification(manual_inspection_id, False)
        print(colored("\t- prediction:", "blue", "on_grey", ["bold"]), prediction[0] if len(prediction) > 0 else "")
    print("\n----------------------------------------------------------------------\n")


def knowledge_snapshot_diag_log_perspective() -> None:
    """
    Presents a snapshot of the knowledge currently stored in the KG regarding diagnosis logs.
    """
    print("###########################################################################")
    print("KNOWLEDGE SNAPSHOT - DIAGNOSIS LOG PERSPECTIVE")
    print("###########################################################################\n")
    for diag_log in qt.query_all_diag_log_instances(False):
        diag_log_id = diag_log.split("#")[1]
        print(colored(diag_log_id, "yellow", "on_grey", ["bold"]))
        print(colored("\t- date:", "blue", "on_grey", ["bold"]), qt.query_date_by_diag_log(diag_log_id, False)[0])
        print(colored("\t- appearing error codes:", "blue", "on_grey", ["bold"]))

        appearing_error_codes = qt.query_error_codes_by_diag_log(diag_log_id, False)
        for error_code in appearing_error_codes:
            print("\t\t-", error_code.split("#")[1])

        fault_path_instance = qt.query_fault_path_by_diag_log(diag_log_id, False)
        fault_path_id = fault_path_instance[0].split("#")[1] if len(fault_path_instance) > 0 else ""
        print(colored("\t- entails fault path:", "blue", "on_grey", ["bold"]), fault_path_id)

        diag_subject_instance = qt.query_diag_subject_by_diag_log(diag_log_id, False)
        diag_subject_id = diag_subject_instance[0].split("#")[1]
        print(colored("\t- created for diag subject:", "blue", "on_grey", ["bold"]), diag_subject_id)

        print(colored("\t- diagnostic steps:", "blue", "on_grey", ["bold"]))
        diag_steps = qt.query_diag_steps_by_diag_log(diag_log_id, False)
        for diag_step in diag_steps:
            print("\t\t-", diag_step.split("#")[1])
    print("\n----------------------------------------------------------------------\n")


def knowledge_snapshot_fault_path_perspective() -> None:
    """
    Presents a snapshot of the knowledge currently stored in the KG regarding fault paths.
    """
    print("###########################################################################")
    print("KNOWLEDGE SNAPSHOT - FAULT PATH PERSPECTIVE")
    print("###########################################################################\n")
    for fault_path in qt.query_all_fault_path_instances(False):
        fault_path_id = fault_path.split("#")[1]
        fault_path_desc = qt.query_fault_path_description_by_id(fault_path_id, False)
        print(colored("fault path: " + fault_path_id, "yellow", "on_grey", ["bold"]))
        print(colored("\t- path description:" + str(fault_path_desc), "blue", "on_grey", ["bold"]))
        print(colored("\t- fault conditions that resulted in this fault path:", "blue", "on_grey", ["bold"]))
        fault_conditions = qt.query_resulted_in_by_fault_path(fault_path_id, False)
        for fc in fault_conditions:
            fault_condition_desc = qt.query_fault_condition_description_by_id(fc.split("#")[1], False)[0]
            print("\t\t-", fault_condition_desc)
    print("\n----------------------------------------------------------------------\n")


def knowledge_snapshot_diag_subject_perspective() -> None:
    """
    Presents a snapshot of the knowledge currently stored in the KG regarding diag subjects.
    """
    print("###########################################################################")
    print("KNOWLEDGE SNAPSHOT - DIAG SUBJECT PERSPECTIVE")
    print("###########################################################################\n")
    for diag_subject_instance_id, subject_id in qt.query_all_diag_subject_instances(False):
        diag_subject_instance_id = diag_subject_instance_id.split("#")[1]
        print(colored(diag_subject_instance_id, "yellow", "on_grey", ["bold"]))
        print(colored("\t- subject ID: " + subject_id, "blue", "on_grey", ["bold"]))
        print(colored("\t- error codes recorded in this diag subject:", "blue", "on_grey", ["bold"]))
        error_codes = qt.query_error_codes_recorded_in_diag_subject(diag_subject_instance_id, False)
        for code in error_codes:
            print("\t\t-", code)
    print("\n----------------------------------------------------------------------\n")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Knowledge snapshot - shows current content of KG')
    parser.add_argument('--perspective', type=str, help='perspective of snapshot [expert | diag]',
                        required=False, default='expert')
    args = parser.parse_args()
    qt = KnowledgeGraphQueryTool()

    if args.perspective == 'expert':  # expert knowledge
        print("###########################################################################")
        print("###########################################################################")
        print("#################### EXPERT KNOWLEDGE STORED IN THE KG ####################")
        print("###########################################################################")
        print("###########################################################################\n")
        knowledge_snapshot_error_code_perspective()
        knowledge_snapshot_component_perspective()
        knowledge_snapshot_component_set_perspective()
    elif args.perspective == 'diag':  # diagnosis
        print("###########################################################################")
        print("###########################################################################")
        print("################## DIAGNOSIS KNOWLEDGE STORED IN THE KG ###################")
        print("###########################################################################")
        print("###########################################################################\n")
        knowledge_snapshot_signal_perspective()
        knowledge_snapshot_signal_classification_perspective()
        knowledge_snapshot_manual_inspection_perspective()
        knowledge_snapshot_diag_log_perspective()
        knowledge_snapshot_fault_path_perspective()
        knowledge_snapshot_diag_subject_perspective()
