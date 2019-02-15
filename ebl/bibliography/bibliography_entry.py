NAME_SCHEMA = {
    "type": "object",
    "properties": {
        "family": {
            "type": "string"
        },
        "given": {
            "type": "string"
        },
        "dropping-particle": {
            "type": "string"
        },
        "non-dropping-particle": {
            "type": "string"
        },
        "suffix": {
            "type": "string"
        },
        "comma-suffix": {
            "type": [
                "string",
                "number",
                "boolean"
            ]
        },
        "static-ordering": {
            "type": [
                "string",
                "number",
                "boolean"
            ]
        },
        "literal": {
            "type": "string"
        },
        "parse-names": {
            "type": [
                "string",
                "number",
                "boolean"
            ]
        }
    },
    "additionalProperties": False
}


DATE_SCHEMA = {
    "type": "object",
    "properties": {
        "date-parts": {
            "type": "array",
            "items": {
                "type": "array",
                "items": {
                    "type": [
                        "string",
                        "number"
                    ]
                },
                "maxItems": 3
            },
            "maxItems": 2
        },
        "season": {
            "type": [
                "string",
                "number"
            ]
        },
        "circa": {
            "type": [
                "string",
                "number",
                "boolean"
            ]
        },
        "literal": {
            "type": "string"
        },
        "raw": {
            "type": "string"
        }
    },
    "additionalProperties": False
}


CSL_JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "type": {
            "type": "string",
            "enum": [
                "article",
                "article-journal",
                "article-magazine",
                "article-newspaper",
                "bill",
                "book",
                "broadcast",
                "chapter",
                "dataset",
                "entry",
                "entry-dictionary",
                "entry-encyclopedia",
                "figure",
                "graphic",
                "interview",
                "legal_case",
                "legislation",
                "manuscript",
                "map",
                "motion_picture",
                "musical_score",
                "pamphlet",
                "paper-conference",
                "patent",
                "personal_communication",
                "post",
                "post-weblog",
                "report",
                "review",
                "review-book",
                "song",
                "speech",
                "thesis",
                "treaty",
                "webpage"
            ]
        },
        "id": {
            "type": "string",
            "pattern": r"^[^/]+$"
        },
        "categories": {
            "type": "array",
            "items": {
                "type": "string"
            }
        },
        "language": {
            "type": "string"
        },
        "journalAbbreviation": {
            "type": "string"
        },
        "shortTitle": {
            "type": "string"
        },
        "author": {
            "type": "array",
            "items": NAME_SCHEMA
        },
        "collection-editor": {
            "type": "array",
            "items": NAME_SCHEMA
        },
        "composer": {
            "type": "array",
            "items": NAME_SCHEMA
        },
        "container-author": {
            "type": "array",
            "items": NAME_SCHEMA
        },
        "director": {
            "type": "array",
            "items": NAME_SCHEMA
        },
        "editor": {
            "type": "array",
            "items": NAME_SCHEMA
        },
        "editorial-director": {
            "type": "array",
            "items": NAME_SCHEMA
        },
        "interviewer": {
            "type": "array",
            "items": NAME_SCHEMA
        },
        "illustrator": {
            "type": "array",
            "items": NAME_SCHEMA
        },
        "original-author": {
            "type": "array",
            "items": NAME_SCHEMA
        },
        "recipient": {
            "type": "array",
            "items": NAME_SCHEMA
        },
        "reviewed-author": {
            "type": "array",
            "items": NAME_SCHEMA
        },
        "translator": {
            "type": "array",
            "items": NAME_SCHEMA
        },
        "accessed": DATE_SCHEMA,
        "container": DATE_SCHEMA,
        "event-date": DATE_SCHEMA,
        "issued": DATE_SCHEMA,
        "original-date": DATE_SCHEMA,
        "submitted": DATE_SCHEMA,
        "abstract": {
            "type": "string"
        },
        "annote": {
            "type": "string"
        },
        "archive": {
            "type": "string"
        },
        "archive_location": {
            "type": "string"
        },
        "archive-place": {
            "type": "string"
        },
        "authority": {
            "type": "string"
        },
        "call-number": {
            "type": "string"
        },
        "chapter-number": {
            "type": "string"
        },
        "citation-number": {
            "type": "string"
        },
        "citation-label": {
            "type": "string"
        },
        "collection-number": {
            "type": "string"
        },
        "collection-title": {
            "type": "string"
        },
        "container-title": {
            "type": "string"
        },
        "container-title-short": {
            "type": "string"
        },
        "dimensions": {
            "type": "string"
        },
        "DOI": {
            "type": "string"
        },
        "edition": {
            "type": [
                "string",
                "number"
            ]
        },
        "event": {
            "type": "string"
        },
        "event-place": {
            "type": "string"
        },
        "first-reference-note-number": {
            "type": "string"
        },
        "genre": {
            "type": "string"
        },
        "ISBN": {
            "type": "string"
        },
        "ISSN": {
            "type": "string"
        },
        "issue": {
            "type": [
                "string",
                "number"
            ]
        },
        "jurisdiction": {
            "type": "string"
        },
        "keyword": {
            "type": "string"
        },
        "locator": {
            "type": "string"
        },
        "medium": {
            "type": "string"
        },
        "note": {
            "type": "string"
        },
        "number": {
            "type": [
                "string",
                "number"
            ]
        },
        "number-of-pages": {
            "type": "string"
        },
        "number-of-volumes": {
            "type": [
                "string",
                "number"
            ]
        },
        "original-publisher": {
            "type": "string"
        },
        "original-publisher-place": {
            "type": "string"
        },
        "original-title": {
            "type": "string"
        },
        "page": {
            "type": "string"
        },
        "page-first": {
            "type": "string"
        },
        "PMCID": {
            "type": "string"
        },
        "PMID": {
            "type": "string"
        },
        "publisher": {
            "type": "string"
        },
        "publisher-place": {
            "type": "string"
        },
        "references": {
            "type": "string"
        },
        "reviewed-title": {
            "type": "string"
        },
        "scale": {
            "type": "string"
        },
        "section": {
            "type": "string"
        },
        "source": {
            "type": "string"
        },
        "status": {
            "type": "string"
        },
        "title": {
            "type": "string"
        },
        "title-short": {
            "type": "string"
        },
        "URL": {
            "type": "string"
        },
        "version": {
            "type": "string"
        },
        "volume": {
            "type": [
                "string",
                "number"
            ]
        },
        "year-suffix": {
            "type": "string"
        }
    },
    "required": ['type', 'id'],
    "additionalProperties": False
}
