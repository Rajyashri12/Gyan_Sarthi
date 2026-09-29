from pathlib import Path


SUBJECT_MAP = {
    "general_aptitude": {
        "name": "General Aptitude",
        "code": "GA",
    },
    "dbms": {
        "name": "Database Management Systems",
        "code": "DBMS",
    },
    "os": {
        "name": "Operating Systems",
        "code": "OS",
    },
    "cn": {
        "name": "Computer Networks",
        "code": "CN",
    },
}


def extract_metadata(file_path: str) -> dict:
    path = Path(file_path)
    parts = path.parts

    metadata = {
        "exam": "GATE_CSE",
        "subject": "Unknown",
        "subject_code": "UNKNOWN",
        "topic": path.stem,
        "topic_slug": path.stem.lower().replace(" ", "_"),
        "source_file": path.name,
    }

    for folder_name, subject_info in SUBJECT_MAP.items():

        if folder_name in parts:

            metadata["subject"] = subject_info["name"]
            metadata["subject_code"] = subject_info["code"]

            # Folder immediately before the file is treated
            # as the canonical topic folder.
            try:
                subject_index = parts.index(folder_name)

                if subject_index + 1 < len(parts) - 1:
                    topic_folder = parts[subject_index + 1]

                    metadata["topic"] = topic_folder
                    metadata["topic_slug"] = (
                        topic_folder
                        .lower()
                        .replace(" ", "_")
                        .replace("-", "_")
                    )

            except ValueError:
                pass

            break

    return metadata