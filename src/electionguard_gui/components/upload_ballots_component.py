import traceback
from typing import Any
import eel
from electionguard_gui.components.component_base import ComponentBase
from electionguard_gui.eel_utils import eel_fail, eel_success
from electionguard_gui.services import ElectionService, BallotUploadService


class UploadBallotsComponent(ComponentBase):
    """Responsible for uploading ballots to an election via the GUI"""

    _election_service: ElectionService
    _ballot_upload_service: BallotUploadService

    def __init__(
        self,
        election_service: ElectionService,
        ballot_upload_service: BallotUploadService,
    ) -> None:
        self._election_service = election_service
        self._ballot_upload_service = ballot_upload_service

    def expose(self) -> None:
        eel.expose(self.create_ballot_upload)
        eel.expose(self.upload_ballot)

    def create_ballot_upload(
        self, election_id: str, device_file_name: str, device_file_contents: str
    ) -> dict[str, Any]:
        try:
            db = self._db_service.get_db()
            self._log.debug(f"creating upload for {election_id}")
            election = self._election_service.get(db, election_id)
            if election is None:
                return eel_fail(f"Election {election_id} not found")
            ballot_upload_id = self._ballot_upload_service.create(
                db, election_id, device_file_name, device_file_contents
            )
            return eel_success(ballot_upload_id)
        # pylint: disable=broad-except
        except Exception as e:
            self._log.error(e)
            traceback.print_exc()
            return eel_fail(str(e))

    def upload_ballot(
        self, ballot_upload_id: str, file_name: str, file_contents: str
    ) -> dict[str, Any]:
        try:
            db = self._db_service.get_db()
            self._log.debug(f"adding ballot {file_name} to {ballot_upload_id}")
            self._ballot_upload_service.add_ballot(
                db, ballot_upload_id, file_name, file_contents
            )
            return eel_success()
        # pylint: disable=broad-except
        except Exception as e:
            self._log.error(e)
            traceback.print_exc()
            return eel_fail(str(e))
