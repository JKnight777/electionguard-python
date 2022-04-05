from typing import List, Optional

from electionguard.ballot import PlaintextBallot
from electionguard.guardian import Guardian
from electionguard.manifest import InternationalizedText, Manifest
from electionguard_tools.factories.ballot_factory import BallotFactory
from electionguard_tools.factories.election_factory import (
    ElectionFactory,
)

from ..cli_models.e2e_inputs import E2eInputs
from .e2e_step_base import E2eStepBase


class InputRetrievalStep(E2eStepBase):
    """Responsible for retrieving and displaying user provided inputs."""

    def get_ballots(self) -> List[PlaintextBallot]:
        ballots: List[PlaintextBallot] = BallotFactory().get_simple_ballots_from_file()
        return ballots

    def print_manifest(self, manifest: Manifest) -> None:
        def get_first_value(text: Optional[InternationalizedText]) -> str:
            return "" if text is None else text.text[0].value

        manifest_name = get_first_value(manifest.name)
        self.print_value("Name", manifest_name)
        self.print_value("Scope", manifest.election_scope_id)
        self.print_value("Geopolitical Units", len(manifest.geopolitical_units))
        self.print_value("Parties", len(manifest.parties))
        self.print_value("Candidates", len(manifest.candidates))
        self.print_value("Contests", len(manifest.contests))
        self.print_value("Ballot Styles", len(manifest.ballot_styles))

    def get_manifest(self) -> Manifest:
        self.print_header("Retrieving manifest")
        manifest: Manifest = ElectionFactory().get_simple_manifest_from_file()
        if not manifest.is_valid():
            raise ValueError("manifest file is invalid")
        self.print_manifest(manifest)
        return manifest

    def get_guardians(self, number_of_guardians: int, quorum: int) -> List[Guardian]:
        guardians: List[Guardian] = []
        for i in range(number_of_guardians):
            guardians.append(
                Guardian(
                    str(i + 1),
                    i + 1,
                    number_of_guardians,
                    quorum,
                )
            )
        return guardians

    def get_inputs(self, guardian_count: int, quorum: int) -> E2eInputs:
        self.print_header("Retrieving Inputs")
        guardians = self.get_guardians(guardian_count, quorum)
        manifest: Manifest = self.get_manifest()
        ballots = self.get_ballots()
        self.print_value("Guardians", guardian_count)
        self.print_value("Quorum", quorum)
        return E2eInputs(guardian_count, quorum, guardians, manifest, ballots)