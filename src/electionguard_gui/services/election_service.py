import json
from datetime import datetime
from bson import ObjectId
from pydantic.json import pydantic_encoder
from pymongo.database import Database
from electionguard.constants import ElectionConstants
from electionguard.election import CiphertextElectionContext
from electionguard.guardian import GuardianRecord
from electionguard.manifest import Manifest
from electionguard_gui.models import KeyCeremonyDto, ElectionDto
from electionguard_gui.services.eel_log_service import EelLogService
from electionguard_gui.services.service_base import ServiceBase
from electionguard_gui.services.authorization_service import AuthorizationService


class ElectionService(ServiceBase):
    """Responsible for functionality related to elections"""

    _log: EelLogService
    _auth_service: AuthorizationService

    def __init__(
        self, log_service: EelLogService, auth_service: AuthorizationService
    ) -> None:
        self._log = log_service
        self._auth_service = auth_service

    def create_election(
        self,
        db: Database,
        election_name: str,
        key_ceremony: KeyCeremonyDto,
        manifest: Manifest,
        context: CiphertextElectionContext,
        constants: ElectionConstants,
        guardian_records: list[GuardianRecord],
        encryption_package_file: str,
    ) -> str:
        context_raw = json.dumps(context, default=pydantic_encoder)
        manifest_raw = json.dumps(manifest, default=pydantic_encoder)
        constants_raw = json.dumps(constants, default=pydantic_encoder)
        guardian_records_raw = json.dumps(guardian_records, default=pydantic_encoder)
        election = {
            "election_name": election_name,
            "key_ceremony_id": key_ceremony.id,
            "guardians": context.number_of_guardians,
            "quorum": context.quorum,
            "manifest": {
                "raw": manifest_raw,
                "name": manifest.get_name(),
                "scope": manifest.election_scope_id,
                "geopolitical_units": len(manifest.geopolitical_units),
                "parties": len(manifest.parties),
                "candidates": len(manifest.candidates),
                "contests": len(manifest.contests),
                "ballot_styles": len(manifest.ballot_styles),
            },
            "context": context_raw,
            "constants": constants_raw,
            "guardian_records": guardian_records_raw,
            # Mongo has a max size of 16MG, consider using GridFS https://www.mongodb.com/docs/manual/core/gridfs/
            "encryption_package_file": encryption_package_file,
            "created_by": self._auth_service.get_user_id(),
            "created_at": datetime.utcnow(),
        }
        self._log.trace(f"inserting election: {election}")
        inserted_id = db.elections.insert_one(election).inserted_id
        return str(inserted_id)

    def get(self, db: Database, election_id: str) -> ElectionDto:
        self._log.trace(f"getting election {election_id}")
        election = db.elections.find_one({"_id": ObjectId(election_id)})
        if not election:
            raise Exception(f"Election not found: {election_id}")
        return ElectionDto(election)

    def get_all(self, db: Database) -> list[ElectionDto]:
        self._log.trace("getting all elections")
        elections = db.elections.find()
        return [ElectionDto(election) for election in elections]
