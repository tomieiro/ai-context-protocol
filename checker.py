import argparse
import re
import sys
from dataclasses import dataclass

ATOM_RE = re.compile(r"^[A-Za-z0-9_.:/@+\-*]+$")
PATH_RE = re.compile(r"^[^\s\x00]+$")
URI_RE = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*://[^\s]+$")
KEY_RE = re.compile(r"^[A-Za-z0-9_.:/@+\-*]+$")
DIRECTIVE_RE = re.compile(r"^@[A-Za-z0-9_.:/@+\-*]+$")
TYPE_NAMES = {
    "atom", "id", "nsid", "string", "text", "int", "float", "bool", "enum",
    "list", "set", "pair", "map", "path", "glob", "uri", "ref", "semver",
    "date", "datetime", "duration", "range", "regex", "hash"
}

@dataclass
class Error:
    path: str
    line: int
    col: int
    message: str

    def __str__(self):
        return f"{self.path}:{self.line}:{self.col}: {self.message}"

@dataclass
class Record:
    directive: str
    line: int
    positionals: list
    fields: dict

class AICPChecker:
    def __init__(self, path):
        self.path = path
        self.errors = []
        self.records = []

    def error(self, line, col, message):
        self.errors.append(Error(self.path, line, col, message))

    def check(self):
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                lines = f.readlines()
        except OSError as e:
            self.error(1, 1, str(e))
            return self.errors

        for line_no, text in self.collect_records(lines):
            self.parse_record(text, line_no)

        self.check_global()
        return self.errors

    def collect_records(self, lines):
        records = []
        buf = []
        start = 0
        in_text = False

        for i, raw in enumerate(lines, 1):
            line = raw.rstrip("\n")
            stripped = line.strip()

            if not buf and (not stripped or stripped.startswith("#")):
                continue

            if not buf:
                start = i

            buf.append(line)
            in_text = self.toggle_text_state(line, in_text)

            if not in_text:
                records.append((start, "\n".join(buf)))
                buf = []

        if buf:
            self.error(start, 1, "unterminated triple-quoted text block")

        return records

    def toggle_text_state(self, line, in_text):
        i = 0
        while i < len(line):
            if line.startswith('"""', i):
                in_text = not in_text
                i += 3
            elif line[i] == '"':
                i += 1
                while i < len(line):
                    if line[i] == "\\":
                        i += 2
                    elif line[i] == '"':
                        i += 1
                        break
                    else:
                        i += 1
            else:
                i += 1
        return in_text

    def parse_record(self, text, line):
        stripped = text.lstrip()
        col = len(text) - len(stripped) + 1

        if not stripped.startswith("@"):
            self.error(line, col, "record must start with @directive")
            return

        try:
            tokens = self.split_tokens(stripped, line)
        except ValueError as e:
            self.error(line, col, str(e))
            return

        if not tokens:
            return

        directive = tokens[0]
        if not DIRECTIVE_RE.match(directive):
            self.error(line, col, f"invalid directive: {directive}")
            return

        positionals = []
        fields = {}
        seen_field = False

        for token in tokens[1:]:
            k, v = self.split_field(token)
            if k is None:
                if seen_field:
                    self.error(line, 1, f"positional value after fields: {token}")
                    continue
                if not self.check_value(token, line):
                    continue
                positionals.append(token)
                continue

            seen_field = True
            if not KEY_RE.match(k):
                self.error(line, 1, f"invalid field key: {k}")
                continue
            if k in fields:
                self.error(line, 1, f"duplicate field: {k}")
                continue
            if not v:
                self.error(line, 1, f"empty value for field: {k}")
                continue
            if self.check_value(v, line):
                fields[k] = v

        self.records.append(Record(directive[1:], line, positionals, fields))

    def split_tokens(self, text, line):
        tokens = []
        token = []
        stack = []
        i = 0
        in_string = False
        in_text = False
        in_regex = False

        while i < len(text):
            ch = text[i]

            if in_text:
                token.append(ch)
                if text.startswith('"""', i):
                    token.extend(['"', '"'])
                    i += 3
                    in_text = False
                else:
                    i += 1
                continue

            if in_string:
                token.append(ch)
                if ch == "\\":
                    i += 1
                    if i < len(text):
                        token.append(text[i])
                    i += 1
                elif ch == '"':
                    in_string = False
                    i += 1
                else:
                    i += 1
                continue

            if in_regex:
                token.append(ch)
                if ch == "\\":
                    i += 1
                    if i < len(text):
                        token.append(text[i])
                    i += 1
                elif ch == "/":
                    in_regex = False
                    i += 1
                else:
                    i += 1
                continue

            if text.startswith('"""', i):
                token.append('"""')
                i += 3
                in_text = True
                continue

            if ch == '"':
                token.append(ch)
                in_string = True
                i += 1
                continue

            if ch == "/" and self.looks_like_regex_start(text, i, token):
                token.append(ch)
                in_regex = True
                i += 1
                continue

            if ch in "[{(":
                stack.append(ch)
                token.append(ch)
                i += 1
                continue

            if ch in "]})":
                if not stack:
                    raise ValueError(f"unexpected closing delimiter: {ch}")
                opening = stack.pop()
                if {"[": "]", "{": "}", "(": ")"}[opening] != ch:
                    raise ValueError(f"mismatched delimiter: {opening}{ch}")
                token.append(ch)
                i += 1
                continue

            if ch.isspace() and not stack:
                if token:
                    tokens.append("".join(token))
                    token = []
                i += 1
                continue

            token.append(ch)
            i += 1

        if in_string:
            raise ValueError("unterminated string")
        if in_text:
            raise ValueError("unterminated triple-quoted text")
        if in_regex:
            raise ValueError("unterminated regex")
        if stack:
            raise ValueError(f"unclosed delimiter: {stack[-1]}")
        if token:
            tokens.append("".join(token))
        return tokens

    def looks_like_regex_start(self, text, i, token):
        if not token:
            return True
        prev = token[-1]
        return prev in "=:[,{"

    def split_field(self, token):
        i = self.find_top_level(token, "=")
        if i == -1:
            return None, None
        return token[:i], token[i + 1:]

    def check_value(self, value, line, expected_type=None):
        value = value.strip()
        if not value:
            self.error(line, 1, "empty value")
            return False

        typed = self.split_typed_value(value)
        if typed:
            typ, inner = typed
            if not self.check_type_expr(typ):
                self.error(line, 1, f"invalid type expression: {typ}")
                return False
            return self.check_value(inner, line, typ)

        base_type = self.base_type(expected_type)
        if base_type and self.check_expected_value(base_type, value, line):
            return True

        if value.startswith('"""'):
            if not value.endswith('"""') or len(value) < 6:
                self.error(line, 1, "invalid text literal")
                return False
            return True

        if value.startswith('"'):
            if not self.valid_string(value):
                self.error(line, 1, "invalid string literal")
                return False
            return True

        if value.startswith("["):
            return self.check_list(value, line)

        if value.startswith("{"):
            return self.check_map(value, line)

        if value.startswith("/"):
            if not self.valid_regex(value):
                self.error(line, 1, "invalid regex literal")
                return False
            return True

        range_i = self.find_top_level(value, "..")
        if range_i != -1:
            left = value[:range_i]
            right = value[range_i + 2:]
            if not left or not right:
                self.error(line, 1, "invalid range literal")
                return False
            return self.check_value(left, line) and self.check_value(right, line)

        if self.looks_like_path(value):
            return True

        if not ATOM_RE.match(value):
            self.error(line, 1, f"invalid atom: {value}")
            return False
        return True

    def base_type(self, typ):
        if not typ:
            return None
        if "[" in typ:
            return typ.split("[", 1)[0]
        return typ

    def list_item_type(self, list_value):
        return None

    def map_item_types(self, map_value):
        return None, None

    def check_expected_value(self, typ, value, line):
        if typ in {"path", "glob"}:
            if PATH_RE.match(value):
                return True
            self.error(line, 1, f"invalid {typ}: {value}")
            return False
        if typ == "uri":
            if URI_RE.match(value):
                return True
            self.error(line, 1, f"invalid uri: {value}")
            return False
        return False

    def looks_like_path(self, value):
        if not value or any(ch.isspace() for ch in value):
            return False
        if value.startswith(("http://", "https://")):
            return False
        return "/" in value or "*" in value or bool(re.search(r"\.[A-Za-z0-9]+$", value))

    def split_typed_value(self, value):
        i = self.find_top_level(value, ":")
        if i <= 0:
            return None
        prefix = value[:i]
        rest = value[i + 1:]
        if self.check_type_expr(prefix):
            return prefix, rest
        return None

    def check_type_expr(self, text):
        text = text.strip()
        if not text:
            return False
        if "[" not in text:
            return text in TYPE_NAMES
        name, rest = text.split("[", 1)
        if name not in TYPE_NAMES or not rest.endswith("]"):
            return False
        inner = rest[:-1]
        if not inner:
            return False
        return all(self.check_type_expr(part) for part in self.split_commas(inner))

    def check_list(self, value, line):
        if not value.endswith("]"):
            self.error(line, 1, "list must end with ]")
            return False
        inner = value[1:-1].strip()
        if not inner:
            return True
        ok = True
        expected_item_type = self.list_item_type(value)
        for item in self.split_commas(inner):
            if not self.check_value(item, line, expected_item_type):
                ok = False
        return ok

    def check_map(self, value, line):
        if not value.endswith("}"):
            self.error(line, 1, "map must end with }")
            return False
        inner = value[1:-1].strip()
        if not inner:
            return True
        ok = True
        keys = set()
        for pair in self.split_commas(inner):
            i = self.find_top_level(pair, ":")
            if i == -1:
                self.error(line, 1, f"map entry missing colon: {pair}")
                ok = False
                continue
            key = pair[:i].strip()
            val = pair[i + 1:].strip()
            if key in keys:
                self.error(line, 1, f"duplicate map key: {key}")
                ok = False
            keys.add(key)
            expected_key_type, expected_val_type = self.map_item_types(value)
            if not self.check_value(key, line, expected_key_type):
                ok = False
            if not self.check_value(val, line, expected_val_type):
                ok = False
        return ok

    def split_commas(self, text):
        out = []
        start = 0
        stack = []
        in_string = False
        in_text = False
        in_regex = False
        i = 0

        while i < len(text):
            ch = text[i]
            if in_text:
                if text.startswith('"""', i):
                    in_text = False
                    i += 3
                else:
                    i += 1
                continue
            if in_string:
                if ch == "\\":
                    i += 2
                elif ch == '"':
                    in_string = False
                    i += 1
                else:
                    i += 1
                continue
            if in_regex:
                if ch == "\\":
                    i += 2
                elif ch == "/":
                    in_regex = False
                    i += 1
                else:
                    i += 1
                continue
            if text.startswith('"""', i):
                in_text = True
                i += 3
                continue
            if ch == '"':
                in_string = True
                i += 1
                continue
            if ch == "/" and (i == start or text[i - 1] in "=:[,{,"):
                in_regex = True
                i += 1
                continue
            if ch in "[{(":
                stack.append(ch)
                i += 1
                continue
            if ch in "]})":
                if stack:
                    stack.pop()
                i += 1
                continue
            if ch == "," and not stack:
                out.append(text[start:i].strip())
                start = i + 1
            i += 1

        out.append(text[start:].strip())
        return [x for x in out if x]

    def find_top_level(self, text, needle):
        stack = []
        in_string = False
        in_text = False
        in_regex = False
        i = 0

        while i < len(text):
            ch = text[i]
            if in_text:
                if text.startswith('"""', i):
                    in_text = False
                    i += 3
                else:
                    i += 1
                continue
            if in_string:
                if ch == "\\":
                    i += 2
                elif ch == '"':
                    in_string = False
                    i += 1
                else:
                    i += 1
                continue
            if in_regex:
                if ch == "\\":
                    i += 2
                elif ch == "/":
                    in_regex = False
                    i += 1
                else:
                    i += 1
                continue
            if text.startswith('"""', i):
                in_text = True
                i += 3
                continue
            if ch == '"':
                in_string = True
                i += 1
                continue
            if ch == "/" and (i == 0 or text[i - 1] in "=:[,{,"):
                in_regex = True
                i += 1
                continue
            if ch in "[{(":
                stack.append(ch)
                i += 1
                continue
            if ch in "]})":
                if stack:
                    stack.pop()
                i += 1
                continue
            if not stack and text.startswith(needle, i):
                return i
            i += 1
        return -1

    def valid_string(self, value):
        if len(value) < 2 or value[0] != '"' or value[-1] != '"':
            return False
        i = 1
        while i < len(value) - 1:
            if value[i] == "\\":
                i += 2
            elif value[i] == '"':
                return False
            else:
                i += 1
        return True

    def valid_regex(self, value):
        if len(value) < 2 or value[0] != "/" or value[-1] != "/":
            return False
        i = 1
        while i < len(value) - 1:
            if value[i] == "\\":
                i += 2
            elif value[i] == "/":
                return False
            else:
                i += 1
        try:
            re.compile(value[1:-1])
            return True
        except re.error:
            return False

    def check_global(self):
        aicp = [r for r in self.records if r.directive == "aicp"]
        if len(aicp) != 1:
            self.error(1, 1, f"expected exactly one @aicp record, found {len(aicp)}")

        seen = set()
        for r in self.records:
            if not r.positionals:
                continue
            key = (r.directive, r.positionals[0])
            if key in seen:
                self.error(r.line, 1, f"duplicate @{r.directive} id: {r.positionals[0]}")
            seen.add(key)


def main():
    parser = argparse.ArgumentParser(prog="aicp_check.py")
    parser.add_argument("files", nargs="+")
    args = parser.parse_args()

    all_errors = []
    for path in args.files:
        checker = AICPChecker(path)
        all_errors.extend(checker.check())

    if all_errors:
        for err in all_errors:
            print(err, file=sys.stderr)
        return 1

    for path in args.files:
        print(f"OK {path}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
