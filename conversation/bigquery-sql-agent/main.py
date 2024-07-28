import os
import mesop as me
import mesop.labs as mel

from functions.nl2sql import generate_sql_and_retrieve_as_markdown

_current_dir = os.path.dirname(__file__)
GEN_TEMPLATE_FILE = os.path.join(
    _current_dir, "functions", "generation_prompt.template"
)
REFL_TEMPLATE_FILE = os.path.join(
    _current_dir, "functions", "reflection_prompt.template"
)


@me.stateclass
class State:
    gen_file_content: str
    refl_file_content: str
    gen_prompt_editor_content: str
    refl_prompt_editor_content: str
    gen_file_saved: bool
    refl_file_saved: bool


def on_gen_blur(e: me.InputBlurEvent):
    state = me.state(State)
    state.gen_prompt_editor_content = e.value


def on_refl_blur(e: me.InputBlurEvent):
    state = me.state(State)
    state.refl_prompt_editor_content = e.value


def save_gen_button_click(event: me.ClickEvent):
    state = me.state(State)
    save_file(GEN_TEMPLATE_FILE, state.gen_prompt_editor_content)
    state.gen_file_saved = True


def save_refl_button_click(event: me.ClickEvent):
    state = me.state(State)
    save_file(REFL_TEMPLATE_FILE, state.refl_prompt_editor_content)
    state.refl_file_saved = True


@me.page(
    path="/",
    title="SQL Agent UI",
)
def app():
    mel.text_to_text(
        get_data,
        title="SQL Agent",
    )


@me.page(
    path="/prompt",
    title="Prompt Editor",
)
def prompt():
    state = me.state(State)
    state.gen_file_content = read_file(GEN_TEMPLATE_FILE)
    state.refl_file_content = read_file(REFL_TEMPLATE_FILE)
    state.gen_file_saved = False
    state.refl_file_saved = False
    with me.box(
        style=me.Style(
            height=600,
            margin=me.Margin.all(16),
            border_radius=10,
        )
    ):
        me.textarea(
            label="Generator prompt",
            value=state.gen_file_content,
            on_blur=on_gen_blur,
            appearance="fill",
            autosize=True,
            style=me.Style(display="flex", flex_direction="row", gap=12),
        )
        with me.box(style=me.Style(display="flex", flex_direction="row", gap=12)):
            me.button(
                "Save", color="accent", type="flat", on_click=save_gen_button_click
            )

    with me.box(
        style=me.Style(
            height=600,
            margin=me.Margin.all(16),
            border_radius=10,
        )
    ):
        me.textarea(
            label="Reflection prompt",
            value=state.refl_file_content,
            on_blur=on_refl_blur,
            appearance="fill",
            autosize=True,
            style=me.Style(display="flex", flex_direction="row", gap=12),
        )

        with me.box(style=me.Style(display="flex", flex_direction="row", gap=12)):
            me.button(
                "Save", color="accent", type="flat", on_click=save_refl_button_click
            )


def get_data(user_input: str):
    return generate_sql_and_retrieve_as_markdown(user_input)


def read_file(filename: str):
    with open(filename, "r") as f:
        content = f.read()
    return content


def save_file(filename: str, content: str):
    with open(filename, "w") as f:
        f.write(content)
