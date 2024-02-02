from app.matching.process_match import ProcessMatch
from app.matching.reader import Reader
from app.matching.matcher.cumulative_matcher import CumulativeMatcher
from app.matching.writer import Writer



def matcher(source_id: int):
    return ProcessMatch(
        Reader(source_id).read,
        CumulativeMatcher().process,
        Writer().write
    ).process()
