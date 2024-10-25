from dataclasses import dataclass, field
from re import compile
from copy import deepcopy

@dataclass
class DialogueTag:
    name: str = ""
    start: int = 0
    end: int = 0

    def range(self):
        return range(self.start, self.end)

class BaseDialogueItem:
    completed: bool = False

    def __repr__(self) -> str:
        return f"BaseDialogueItem()"

class DialogueAction(BaseDialogueItem):
    name: str = ""
    index: int = -1

    def __init__(self, name: str, index: str):
        self.name = name
        self.index = index

    def __repr__(self) -> str:
        return f"DialogueAction(\'{self.name}\', {self.index})"

class DialogueTextLineBreak(BaseDialogueItem):
    def __repr__(self) -> str:
        return f"DialogueTextLineBreak()"

class DialogueTextChunk(BaseDialogueItem):
    text: str = ""
    tags: list[str] = field(default_factory=list)
    position: int = 0

    def __init__(self, text: str, tags: list[str]):
        self.text = text
        self.tags = tags

    def __len__(self) -> int:
        return len(self.text)

    def __repr__(self) -> str:
        return f"DialogueTextChunk(\'{self.text}\', {self.tags}, {self.position})"

class DialoguePage:
    commands: list[BaseDialogueItem]
    current_item: int

    def __init__(self, commands: list[BaseDialogueItem]):
        self.commands = commands

    def __repr__(self) -> str:
        return f"DialoguePage({self.commands})"

    def get_current_item(self):
        for command in self.commands:
            if (command is not None) and (not command.completed):
                return command
        return None

    def __len__(self) -> int:
        lens = []
        for command in self.commands:
            if isinstance(command, DialogueTextChunk):
                lens.append(len(command))
        return sum(lens)

    def get_raw_text(self) -> str:
        texts = []
        for command in self.commands:
            if isinstance(command, DialogueTextChunk):
                texts.append(command.text)
        return ''.join(texts)

    def get_visible_text(self, visible_chars: int = 10) -> 'DialoguePage':
        """
        Iterate through each line, and within each line, its chunks.
        Count the characters and keep adding to a variable.
        Once the variable hits visible_chars, stop counting.
        The chunks we read should be added to a list, and the chunk we're reading right now
        should be cut off to its correct length before being added.
        """
        read_everything = True
        chars_remaining = visible_chars
        new_lines = []
        for line in self.commands:
            new_line = []
            for chunk in line:
                if chars_remaining >= len(chunk):
                    new_line.append(deepcopy(chunk))
                    chars_remaining -= len(chunk)
                elif chars_remaining > 0:
                    partial_copy = deepcopy(chunk)
                    partial_copy.text = partial_copy.text[:chars_remaining]
                    new_line.append(partial_copy)
                    chars_remaining = 0
                    break
                else:
                    break
            new_lines.append(new_line)
            if chars_remaining <= 0:
                break

        d = DialoguePage(new_lines)
        # print("output from get_visible_text", d)
        return d

    def condense_chunks(self) -> 'DialoguePage':
        chunks = []
        current_string = ""
        current_tags = None
        for chunk in self.commands:
            if isinstance(chunk, DialogueTextChunk) and (current_tags is None or chunk.tags == current_tags):
                current_string += chunk.text
                if current_tags is None:
                    current_tags = chunk.tags.copy()
            elif isinstance(chunk, DialogueTextChunk):
                chunks.append(DialogueTextChunk(current_string, current_tags))
                current_string = chunk.text
                current_tags = chunk.tags.copy()
            elif isinstance(chunk, DialogueAction):
                if len(current_string) > 0:
                    chunks.append(DialogueTextChunk(current_string, current_tags))
                chunks.append(chunk)
                current_string = ""
                current_tags = None
            elif isinstance(chunk, DialogueTextLineBreak):
                if len(current_string) > 0:
                    chunks.append(DialogueTextChunk(current_string, current_tags))
                chunks.append(chunk)
                current_string = ""
                current_tags = None
        if len(current_string) > 0:
            chunks.append(DialogueTextChunk(current_string, current_tags))

        d = DialoguePage(chunks)
        # print("condensed chunks:", d)
        return d

@dataclass
class DialogueTextContent:
    cleaned_lines: str
    tags: list[DialogueTag]
    actions: list[DialogueAction]

__tag_matcher = compile(r"\[(.*?)\]")
def parse_line(text: str) -> DialoguePage:
    current_line_width = 0.0

    page_content: list[BaseDialogueItem] = []

    remaining_text = text
    while len(remaining_text) > 0:
        re_match = __tag_matcher.match(remaining_text)
        if re_match is not None:
            # Tag found at beginning of string, let's get it
            match_content = re_match.group(1)

            if match_content == "br":
                page_content.append(DialogueTextLineBreak())
            else:
                page_content.append(DialogueAction(match_content, 0))
            remaining_text = remaining_text[len(re_match.group(0)):]
        else:
            char = remaining_text[0]
            page_content.append(DialogueTextChunk(char, []))

            # Uncomment for auto line breaking (but its stinky)
            # char_width = get_text_width(char, font=get_best_font(char, FONT_ARRAY))
            # current_line_width += char_width
            # if current_line_width > MAX_WIDTH:
            #     page_content.append(DialogueTextLineBreak())
            #     current_line_width = 0.0
                
            remaining_text = remaining_text[1:]

    return page_content