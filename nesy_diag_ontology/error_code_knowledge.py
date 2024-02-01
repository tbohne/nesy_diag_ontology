#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author Tim Bohne

from typing import List


class ErrorCodeKnowledge:
    """
    Representation of error-code-related expert knowledge.
    """

    def __init__(self, error_code: str, fault_condition: str, suspect_components: List[str]) -> None:
        """
        Initializes the error code knowledge.

        :param error_code: error code to be considered
        :param fault_condition: fault condition associated with the considered error code
        :param suspect_components: components that should be checked when this error code occurs
                                   (order defines suggestion priority)
        """
        self.error_code = error_code
        self.fault_condition = fault_condition
        self.suspect_components = suspect_components

    def __str__(self) -> str:
        """
        Returns a string representation of the error code knowledge.

        :return: string representation of error code knowledge
        """
        return "Error code: " + self.error_code + "\nFault Condition: " + self.fault_condition \
            + "\nSuspect Components: " + str(self.suspect_components)
