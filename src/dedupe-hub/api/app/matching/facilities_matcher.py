from app.matching.process_match import ProcessMatch
from app.matching.reader import Reader
from app.matching.matcher.cumulative_matcher import CumulativeMatcher
from app.matching.writer import Writer



def matcher(source_id: int):
    cumulative_matcher = CumulativeMatcher()
    writer = Writer()

    def write(processed_data):
        # The item statuses staged by the matcher are written with the
        # match rows, never before them (OSDEV-3149).
        return writer.write(processed_data, cumulative_matcher.item_updates)

    return ProcessMatch(
        Reader(source_id).read,
        cumulative_matcher.process,
        write
    ).process()
