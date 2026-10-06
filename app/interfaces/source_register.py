from typing import Protocol, List
from app.schemas.source import SourceMetadata

class SourceRegisterServiceInterface(Protocol):
    def get_all_sources(self) -> List[SourceMetadata]:
        ...
    
    def add_source(self, source: SourceMetadata) -> None:
        ...
