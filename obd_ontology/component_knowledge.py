#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author Tim Bohne

from typing import List


class ComponentKnowledge:
    """
    Representation of component-related expert knowledge.
    """

    def __init__(self, suspect_component: str, affected_by: List[str]) -> None:
        """
        Initializes the component knowledge.

        :param suspect_component: component to be checked
        :param affected_by: list of components whose misbehavior could affect the correct functioning of the component
                            under consideration
        """
        self.suspect_component = suspect_component
        self.affected_by = affected_by

    def __str__(self) -> str:
        """
        Returns a string representation of the component knowledge.

        :return: string representation of component knowledge
        """
        return "Suspect Component: " + self.suspect_component + "\nAffected By: " + str(self.affected_by)
