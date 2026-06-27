"""
Browser renderer — writes a self-contained HTML file with the current game state
embedded as inline JavaScript. No server, no dependencies, zero-config.
"""
import json
import os
from engine.state_exporter import export_state


_TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), "renderer_template.html")
_OUTPUT_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "game_view.html")


def render_to_file(game, output_path=None):
    """Export game state to JSON, embed it into the HTML template, write to file."""
    if output_path is None:
        output_path = _OUTPUT_PATH

    state = export_state(game)
    state_json = json.dumps(state)

    # Read template and inject state
    template_path = _TEMPLATE_PATH
    with open(template_path, "r", encoding="utf-8") as f:
        html = f.read()

    # Replace the placeholder with the live state
    placeholder = "// __GAME_STATE_PLACEHOLDER__"
    html = html.replace(placeholder, f"const GAME_STATE = {state_json};\nrender(GAME_STATE);")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    return output_path
