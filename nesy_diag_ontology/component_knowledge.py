#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author Tim Bohne

from typing import List


class ComponentKnowledge:
    """
    Representation of component-related expert knowledge.
    """

    def __init__(
            self, suspect_component: str, affected_by: List[str], associated_chan: List[str] = [],
            chan_of_interest: List[str] = []
    ) -> None:
        """
        Initializes the component knowledge.

        Associated channels can also be part of COI. The associated channels are only further information for
        knowing where (at which component) to measure. The COI are the ones that are used for classification.

        :param suspect_component: component to be checked
        :param affected_by: list of components whose misbehavior could affect the correct functioning of the component
                            under consideration
        :param associated_chan: channels associated with the component, i.e., 'hasChannel' relation
        :param chan_of_interest: proposed channels of interest, i.e., 'hasCOI' relation
        """
        self.suspect_component = suspect_component
        self.affected_by = affected_by
        self.associated_chan = associated_chan
        self.chan_of_interest = chan_of_interest

    def __str__(self) -> str:
        """
        Returns a string representation of the component knowledge.

        :return: string representation of component knowledge
        """
        return (
                "Suspect Component: " + self.suspect_component
                + "\nAffected By: " + str(self.affected_by)
                + "\nAssociated Channels: " + str(self.associated_chan)
                + "\nCOI: " + str(self.chan_of_interest)
        )
